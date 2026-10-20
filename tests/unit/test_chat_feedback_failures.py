"""chat-management: feedback 理由と admin 失敗一覧の単体テスト。"""
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path(__file__).resolve().parents[2]
APP_PATH = REPO / "lambda" / "chat" / "chat-management" / "app.py"


def load_app(monkeypatch=None):
    os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("ADMIN_GROUP_NAME", "admin")
    # boto3 resource を import 時に触るので Table をモック
    with patch("boto3.resource") as resource:
        table = MagicMock()
        resource.return_value.Table.return_value = table
        spec = importlib.util.spec_from_file_location("chat_mgmt_test", str(APP_PATH))
        mod = importlib.util.module_from_spec(spec)
        # 再読込対策
        sys.modules.pop("chat_mgmt_test", None)
        spec.loader.exec_module(mod)
        mod.chatlogs_table = table
        return mod, table


def _event(method, path, *, body=None, qs=None, sub="user-1", groups="admin", path_params=None):
    return {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "queryStringParameters": qs or {},
        "body": json.dumps(body) if isinstance(body, dict) else body,
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": sub,
                    "cognito:groups": groups,
                }
            }
        },
    }


def test_is_admin_accepts_list_and_csv():
    mod, _ = load_app()
    assert mod.is_admin(_event("GET", "/x", groups="admin"))
    assert mod.is_admin(_event("GET", "/x", groups=["admin", "other"]))
    assert not mod.is_admin(_event("GET", "/x", groups="user"))


def test_get_sessions_filters_by_rag_mode():
    mod, table = load_app()
    table.query.return_value = {"Items": [
        {
            "sessionId": "law-session",
            "userId": "user-1",
            "role": "user",
            "ragMode": "law",
            "timestamp": "2026-10-02T01:00:00Z",
            "ttl": 1790900000,
            "content": "建築基準法の質問",
        },
        {
            "sessionId": "normal-session",
            "userId": "user-1",
            "role": "user",
            "ragMode": "normal",
            "timestamp": "2026-10-02T02:00:00Z",
            "ttl": 1790900000,
            "content": "通常質問",
        },
        {
            "sessionId": "legacy-session",
            "userId": "user-1",
            "role": "user",
            "timestamp": "2026-10-02T03:00:00Z",
            "ttl": 1790900000,
            "content": "旧形式の通常質問",
        },
    ]}

    sessions = mod.get_sessions_by_user("user-1", mode="law")

    assert [session["sessionId"] for session in sessions] == ["law-session"]


def test_get_sessions_paginates_until_requested_mode_is_found():
    mod, table = load_app()

    def query(**kwargs):
        if "ExclusiveStartKey" not in kwargs:
            return {
                "Items": [{
                    "sessionId": "normal-session",
                    "userId": "user-1",
                    "role": "user",
                    "ragMode": "normal",
                    "timestamp": "2026-10-02T02:00:00Z",
                    "ttl": 1790900000,
                    "content": "通常質問",
                }],
                "LastEvaluatedKey": {"userId": "user-1", "timestamp": "2"},
            }
        return {
            "Items": [{
                "sessionId": "law-session",
                "userId": "user-1",
                "role": "user",
                "ragMode": "law",
                "timestamp": "2026-10-02T01:00:00Z",
                "ttl": 1790900000,
                "content": "法令質問",
            }]
        }

    table.query.side_effect = query

    sessions = mod.get_sessions_by_user("user-1", limit=1, mode="law")

    assert [session["sessionId"] for session in sessions] == ["law-session"]
    assert table.query.call_count == 2


def test_get_session_messages_rejects_different_rag_mode():
    mod, table = load_app()
    table.query.side_effect = [
        {"Items": [{"sessionId": "law-session", "userId": "user-1"}]},
        {"Items": [{
            "sessionId": "law-session",
            "messageId": "message-1",
            "role": "user",
            "ragMode": "law",
            "content": "法令質問",
            "timestamp": "2026-10-02T01:00:00Z",
        }]},
    ]

    response = mod.lambda_handler(_event(
        "GET",
        "/chat/sessions/law-session/messages",
        qs={"mode": "normal"},
        groups="user",
        path_params={"sessionId": "law-session"},
    ), None)

    assert response["statusCode"] == 409
    assert json.loads(response["body"])["error"] == "SessionModeMismatch"


def test_feedback_bad_with_reason(monkeypatch):
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "user-1", "sessionId": "s1"}]}

    event = _event(
        "PUT",
        "/chat/messages/msg1/feedback",
        body={"sessionId": "s1", "feedback": "bad", "reason": "wrong_doc"},
        path_params={"messageId": "msg1"},
        groups="user",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    kwargs = table.update_item.call_args.kwargs
    assert kwargs["ExpressionAttributeValues"][":feedback"] == "bad"
    assert kwargs["ExpressionAttributeValues"][":reason"] == "wrong_doc"
    assert "ConditionExpression" in kwargs
    assert "#role" in kwargs["ExpressionAttributeNames"]


def test_feedback_bad_with_unresolved():
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "user-1", "sessionId": "s1"}]}

    event = _event(
        "PUT",
        "/chat/messages/msg1/feedback",
        body={"sessionId": "s1", "feedback": "bad", "reason": "unresolved"},
        path_params={"messageId": "msg1"},
        groups="user",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    kwargs = table.update_item.call_args.kwargs
    assert kwargs["ExpressionAttributeValues"][":reason"] == "unresolved"


def test_feedback_bad_with_comment():
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "user-1", "sessionId": "s1"}]}

    event = _event(
        "PUT",
        "/chat/messages/msg1/feedback",
        body={
            "sessionId": "s1",
            "feedback": "bad",
            "comment": "手順の順番が違う",
        },
        path_params={"messageId": "msg1"},
        groups="user",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    kwargs = table.update_item.call_args.kwargs
    assert kwargs["ExpressionAttributeValues"][":comment"] == "手順の順番が違う"


def test_get_session_messages_excludes_product_wish():
    mod, table = load_app()

    def _query(**kwargs):
        assert "FilterExpression" in kwargs
        assert kwargs["ExpressionAttributeValues"][":wish"] == "product_wish"
        # DynamoDB が FilterExpression を適用した結果を模倣
        return {
            "Items": [
                {"sessionId": "s1", "messageId": "u1", "role": "user", "content": "q"},
                {"sessionId": "s1", "messageId": "a1", "role": "assistant", "content": "a"},
            ],
        }

    table.query.side_effect = _query
    msgs = mod.get_session_messages("s1", fetch_all=True)
    roles = [m.get("role") for m in msgs]
    assert "product_wish" not in roles
    assert roles == ["user", "assistant"]


def test_feedback_rejects_legacy_wrong_page():
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "user-1", "sessionId": "s1"}]}

    event = _event(
        "PUT",
        "/chat/messages/msg1/feedback",
        body={"sessionId": "s1", "feedback": "bad", "reason": "wrong_page"},
        path_params={"messageId": "msg1"},
        groups="user",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 400
    table.update_item.assert_not_called()


def test_feedback_missing_message_returns_404():
    from botocore.exceptions import ClientError

    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "user-1", "sessionId": "s1"}]}
    table.update_item.side_effect = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException", "Message": "x"}},
        "UpdateItem",
    )
    event = _event(
        "PUT",
        "/chat/messages/missing/feedback",
        body={"sessionId": "s1", "feedback": "good"},
        path_params={"messageId": "missing"},
        groups="user",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 404


def test_feedback_rejects_invalid_reason():
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "user-1", "sessionId": "s1"}]}
    event = _event(
        "PUT",
        "/chat/messages/msg1/feedback",
        body={"sessionId": "s1", "feedback": "bad", "reason": "nope"},
        path_params={"messageId": "msg1"},
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 400


def test_admin_failures_forbidden_for_non_admin():
    mod, _ = load_app()
    event = _event("GET", "/chat/admin/failures", groups="user")
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 403


def test_list_failure_messages_joins_user_query():
    mod, table = load_app()

    assistant = {
        "sessionId": "s1",
        "messageId": "msg_200",
        "role": "assistant",
        "timestamp": "2026-07-29T12:00:00",
        "feedback": "bad",
        "feedbackReason": "wrong_doc",
        "responseType": "pages",
        "content": "回答本文",
        "queryFilters": {"modelType": "AXIEZ"},
        "pageCandidates": [{"documentName": "C-123.pdf"}],
    }
    table.scan.return_value = {"Items": [assistant], "ScannedCount": 1}
    table.query.return_value = {
        "Items": [
            {
                "sessionId": "s1",
                "messageId": "msg_100",
                "role": "user",
                "timestamp": "2026-07-29T11:59:00",
                "content": "火災管制の解除条件は？",
            },
            assistant,
        ]
    }

    out = mod.list_failure_messages(kind="bad", limit=10)
    assert out["count"] == 1
    assert out["incomplete"] is False
    assert out["failures"][0]["userQuery"] == "火災管制の解除条件は？"
    assert out["failures"][0]["feedbackReason"] == "wrong_doc"
    assert out["failures"][0]["topDocuments"] == ["C-123.pdf"]


def test_submit_product_wish():
    mod, table = load_app()
    saved = mod.save_product_wish("user-1", "候補をもっと上に", "session-abc")
    table.put_item.assert_called_once()
    item = table.put_item.call_args.kwargs["Item"]
    assert item["role"] == "product_wish"
    assert item["content"] == "候補をもっと上に"
    assert item["contextSessionId"] == "session-abc"
    assert item["sessionId"] == "wish-user-1"
    assert saved["messageId"].startswith("wish-")


def test_submit_product_wish_rejects_empty():
    mod, _ = load_app()
    with pytest.raises(ValueError):
        mod.save_product_wish("user-1", "   ")


def test_post_suggestions_route():
    mod, table = load_app()
    event = _event(
        "POST",
        "/chat/suggestions",
        body={"text": "機種なしでも検索してほしい"},
        groups="user",
        sub="user-42",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 201
    table.put_item.assert_called_once()


def test_admin_suggestions_forbidden():
    mod, _ = load_app()
    event = _event("GET", "/chat/admin/suggestions", groups="user")
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 403


def test_list_product_wishes():
    mod, table = load_app()
    table.scan.return_value = {
        "Items": [
            {
                "messageId": "wish-1",
                "userId": "u1",
                "content": "こうしてほしい",
                "timestamp": "2026-07-29T13:00:00",
                "role": "product_wish",
            }
        ],
        "ScannedCount": 1,
    }
    out = mod.list_product_wishes(limit=10)
    assert out["count"] == 1
    assert out["wishes"][0]["text"] == "こうしてほしい"


def test_admin_can_read_other_users_session_messages():
    # PDCA: admin は失敗一覧からの照合のため他人セッションを読み取り可（Major 2）
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "other-user", "sessionId": "s1"}]}
    event = _event(
        "GET",
        "/chat/sessions/s1/messages",
        path_params={"sessionId": "s1"},
        sub="admin-user",
        groups="admin",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["readOnly"] is True


def test_non_admin_cannot_read_other_users_session_messages():
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "other-user", "sessionId": "s1"}]}
    event = _event(
        "GET",
        "/chat/sessions/s1/messages",
        path_params={"sessionId": "s1"},
        sub="user-1",
        groups="user",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 404


def test_owner_session_messages_not_readonly():
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "user-1", "sessionId": "s1"}]}
    event = _event(
        "GET",
        "/chat/sessions/s1/messages",
        path_params={"sessionId": "s1"},
        sub="user-1",
        groups="user",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["readOnly"] is False


def test_admin_cannot_delete_other_users_session():
    # 読み取りのみの緩和であり、削除は従来どおり所有者限定
    mod, table = load_app()
    table.query.return_value = {"Items": [{"userId": "other-user", "sessionId": "s1"}]}
    event = _event(
        "DELETE",
        "/chat/sessions/s1",
        path_params={"sessionId": "s1"},
        sub="admin-user",
        groups="admin",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 404


def test_suggestions_route_records_law_mode_of_owned_session():
    mod, table = load_app()
    table.query.return_value = {"Items": [
        {"userId": "user-42", "sessionId": "s-law", "role": "user", "ragMode": "law"},
    ]}
    event = _event(
        "POST",
        "/chat/suggestions",
        body={"text": "法令の条文をもっと上に", "sessionId": "s-law"},
        groups="user",
        sub="user-42",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 201
    item = table.put_item.call_args.kwargs["Item"]
    assert item["contextSessionId"] == "s-law"
    assert item["contextRagMode"] == "law"
    # 所有確認とモード取得は同じ Query 1 回で済ませる
    assert table.query.call_count == 1


def test_suggestions_route_skips_mode_of_other_users_session():
    mod, table = load_app()
    table.query.return_value = {"Items": [
        {"userId": "other-user", "sessionId": "s-other", "role": "user", "ragMode": "law"},
    ]}
    event = _event(
        "POST",
        "/chat/suggestions",
        body={"text": "他人のセッション", "sessionId": "s-other"},
        groups="user",
        sub="user-42",
    )
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 201
    item = table.put_item.call_args.kwargs["Item"]
    assert "contextSessionId" not in item
    assert "contextRagMode" not in item


def test_suggestions_route_without_session_does_not_query():
    mod, table = load_app()
    event = _event("POST", "/chat/suggestions", body={"text": "機種を増やして"}, groups="user", sub="user-42")
    resp = mod.lambda_handler(event, None)
    assert resp["statusCode"] == 201
    table.query.assert_not_called()
    item = table.put_item.call_args.kwargs["Item"]
    assert "contextRagMode" not in item


def test_list_product_wishes_ragmode_law_normal_and_legacy():
    mod, table = load_app()
    table.scan.return_value = {
        "Items": [
            {"messageId": "wish-3", "userId": "u1", "content": "a", "timestamp": "2026-10-03T00:00:00",
             "role": "product_wish", "contextSessionId": "s-law", "contextRagMode": "law"},
            {"messageId": "wish-2", "userId": "u1", "content": "b", "timestamp": "2026-10-02T00:00:00",
             "role": "product_wish", "contextSessionId": "s-normal", "contextRagMode": "normal"},
            {"messageId": "wish-1", "userId": "u1", "content": "c", "timestamp": "2026-10-01T00:00:00",
             "role": "product_wish", "contextSessionId": "s-old"},
        ],
        "ScannedCount": 3,
    }
    out = mod.list_product_wishes(limit=10)
    assert [w["ragMode"] for w in out["wishes"]] == ["law", "normal", "normal"]
