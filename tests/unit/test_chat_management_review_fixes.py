"""chat-management: レビュー指摘の回帰テスト。"""
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parents[2]
APP_PATH = REPO / "lambda" / "chat" / "chat-management" / "app.py"


def load_app():
    os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    with patch("boto3.resource") as resource:
        table = MagicMock()
        resource.return_value.Table.return_value = table
        spec = importlib.util.spec_from_file_location("chat_mgmt_review_fixes_test", str(APP_PATH))
        mod = importlib.util.module_from_spec(spec)
        sys.modules.pop("chat_mgmt_review_fixes_test", None)
        spec.loader.exec_module(mod)
        mod.chatlogs_table = table
        return mod, table


def test_save_product_wish_ids_do_not_collide_within_same_millisecond():
    mod, table = load_app()
    random_values = iter((b"\x12\x34\x56\x78", b"\xab\xcd\xef\x12"))
    with patch.object(mod.time, "time", return_value=1_800_000_000), patch(
        "os.urandom",
        side_effect=lambda size: next(random_values),
    ):
        first = mod.save_product_wish("user-1", "要望1")
        second = mod.save_product_wish("user-1", "要望2")

    assert first["messageId"].startswith("wish-1800000000000-")
    assert second["messageId"].startswith("wish-1800000000000-")
    assert first["messageId"] != second["messageId"]
    assert table.put_item.call_count == 2
    for call in table.put_item.call_args_list:
        assert call.kwargs["ConditionExpression"] == "attribute_not_exists(messageId)"


def test_get_session_messages_returns_latest_visible_limit_in_ascending_order():
    mod, table = load_app()
    visible_messages = []
    visible_pages = []
    for start in (101, 1):
        page = []
        for number in range(start + 99, start - 1, -1):
            message = {"messageId": f"msg_{number:03d}", "role": "user", "timestamp": str(number)}
            if number % 8 == 0:
                message.update({"deleted": True})
            elif number % 8 == 1:
                message["role"] = "product_wish"
            else:
                visible_messages.append(message)
            page.append(message)
        visible_pages.append([
            message for message in page
            if not message.get("deleted") and message["role"] != "product_wish"
        ])
    assert len(visible_messages) == 150
    responses = [
        {"Items": visible_pages[0], "LastEvaluatedKey": {"messageId": "cursor-1"}},
        {"Items": visible_pages[1]},
    ]
    table.query.side_effect = responses

    messages = mod.get_session_messages("s1", limit=100)

    assert table.query.call_count == 2
    assert all(call.kwargs["ScanIndexForward"] is False for call in table.query.call_args_list)
    assert [message["messageId"] for message in messages] == [
        message["messageId"]
        for message in sorted(visible_messages, key=lambda item: item["messageId"])[-100:]
    ]


def test_get_session_messages_fetch_all_keeps_all_messages_ascending():
    mod, table = load_app()
    table.query.side_effect = [
        {
            "Items": [
                {"messageId": "msg_001", "role": "user"},
                {"messageId": "msg_002", "role": "assistant"},
            ],
            "LastEvaluatedKey": {"messageId": "cursor-1"},
        },
        {"Items": [{"messageId": "msg_003", "role": "user"}]},
    ]

    messages = mod.get_session_messages("s1", limit=1, fetch_all=True)

    assert table.query.call_count == 2
    assert all(call.kwargs["ScanIndexForward"] is True for call in table.query.call_args_list)
    assert [message["messageId"] for message in messages] == ["msg_001", "msg_002", "msg_003"]


def test_failure_user_query_uses_full_cached_session_for_old_and_new_assistants():
    mod, table = load_app()
    messages = []
    for number in range(250):
        role = "user" if number % 2 == 0 else "assistant"
        message = {
            "messageId": f"msg_{number:03d}",
            "role": role,
            "timestamp": f"2026-01-01T00:{number:03d}:00Z",
            "content": f"発話{number}" if role == "user" else "回答",
        }
        if number == 1:
            message["responseType"] = "clarify"
        messages.append(message)
    pages = [messages[0:100], messages[100:200], messages[200:250]]

    def query(**kwargs):
        page_number = len(table.query.call_args_list) - 1
        response = {"Items": pages[page_number]}
        if page_number < 2:
            response["LastEvaluatedKey"] = {"messageId": pages[page_number][-1]["messageId"]}
        return response

    table.query.side_effect = query
    cache = {}

    assert mod._session_user_query_before("s1", messages[3]["timestamp"], cache) == "発話2"
    assert mod._session_user_query_before("s1", messages[249]["timestamp"], cache) == "発話248"
    assert mod._previous_assistant_was_clarify("s1", messages[3]["timestamp"], cache)
    assert table.query.call_count == 3
    assert all(call.kwargs["ScanIndexForward"] is True for call in table.query.call_args_list)
