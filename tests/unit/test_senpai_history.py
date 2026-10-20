"""Persistent Senpai history contracts for RAG and chat-management Lambdas."""
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import test_knowhow_api


REPO = Path(__file__).resolve().parents[2]
CHAT_APP = REPO / "lambda" / "chat" / "chat-management" / "app.py"


def _load_chat_app():
    os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("ADMIN_GROUP_NAME", "admin")
    with patch("boto3.resource") as resource:
        table = MagicMock()
        resource.return_value.Table.return_value = table
        name = "chat_mgmt_senpai_history_test"
        spec = importlib.util.spec_from_file_location(name, str(CHAT_APP))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        mod.chatlogs_table = table
        return mod, table


def _chat_event(path, *, qs=None, sub="owner-1", groups="admin", path_params=None):
    return {
        "httpMethod": "GET",
        "path": path,
        "pathParameters": path_params or {},
        "queryStringParameters": qs or {},
        "requestContext": {"authorizer": {"claims": {
            "sub": sub,
            "cognito:groups": groups,
        }}},
    }


def _tagged_message(session_id="normal-1", role="user", content="質問", **extra):
    return {
        "sessionId": session_id,
        "messageId": f"{session_id}-{role}",
        "userId": "owner-1",
        "role": role,
        "ragMode": "normal",
        "content": content,
        "timestamp": "2026-10-20T01:00:00Z",
        "ttl": 1_800_000_000,
        "senpaiConversationId": "11111111-1111-4111-8111-111111111111",
        "senpaiTurnId": "22222222-2222-4222-8222-222222222222",
        **extra,
    }


def test_normal_session_list_hides_senpai_tagged_records():
    mod, table = _load_chat_app()
    regular = _tagged_message("regular-1")
    regular.pop("senpaiConversationId")
    regular.pop("senpaiTurnId")
    table.query.return_value = {"Items": [
        _tagged_message(),
        regular,
    ]}

    response = mod.lambda_handler(_chat_event("/chat/sessions"), None)

    assert response["statusCode"] == 200
    sessions = json.loads(response["body"])["sessions"]
    assert [row["sessionId"] for row in sessions] == ["regular-1"]


def test_senpai_list_returns_grouped_owner_scoped_context():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [
        _tagged_message(role="assistant", content="回答", timestamp="2026-10-20T01:01:00Z"),
        _tagged_message(role="user", content="最初の質問"),
        {**_tagged_message("law-1", role="user", content="最初の質問"), "ragMode": "law"},
    ]}

    response = mod.lambda_handler(
        _chat_event("/chat/sessions", qs={"context": "senpai"}), None
    )

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["context"] == "senpai"
    assert body["complete"] is True
    session = body["sessions"][0]
    assert isinstance(session["daysUntilDeletion"], int)
    assert {key: value for key, value in session.items() if key != "daysUntilDeletion"} == {
        "conversationId": "11111111-1111-4111-8111-111111111111",
        "title": "最初の質問",
        "createdAt": "2026-10-20T01:00:00Z",
        "lastMessageTime": "2026-10-20T01:01:00Z",
        "messageCount": 1,
    }
    assert table.query.call_args.kwargs["IndexName"] == "userId-timestamp-index"


def test_senpai_grouped_detail_cannot_be_read_by_admin_for_another_owner():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [{
        **_tagged_message(),
        "userId": "another-owner",
    }]}

    response = mod.lambda_handler(
        _chat_event(
            "/chat/sessions/11111111-1111-4111-8111-111111111111/messages",
            qs={"context": "senpai"},
            sub="admin-user",
            path_params={"sessionId": "11111111-1111-4111-8111-111111111111"},
        ), None
    )

    assert response["statusCode"] == 404
    assert table.query.call_args.kwargs["IndexName"] == "userId-timestamp-index"


def test_non_admin_owner_cannot_read_tagged_session_through_generic_detail_route():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [_tagged_message()]}

    response = mod.lambda_handler(
        _chat_event(
            "/chat/sessions/normal-1/messages",
            sub="owner-1",
            groups="users",
            path_params={"sessionId": "normal-1"},
        ), None
    )

    assert response["statusCode"] == 404


def test_non_admin_owner_cannot_read_legacy_history_with_saved_knowhow_payload():
    mod, table = _load_chat_app()
    message = _tagged_message(knowhow={"matches": [{"body": "private markdown"}]})
    message.pop("senpaiConversationId")
    message.pop("senpaiTurnId")
    table.query.return_value = {"Items": [message]}

    response = mod.lambda_handler(
        _chat_event(
            "/chat/sessions/normal-1/messages",
            sub="owner-1",
            groups="users",
            path_params={"sessionId": "normal-1"},
        ), None
    )

    assert response["statusCode"] == 404


def test_rag_message_writer_persists_both_senpai_identifiers(rag_app):
    table = MagicMock()
    rag_app.chatlogs_table = table

    rag_app.save_message_to_dynamodb(
        session_id="normal-1",
        user_id="owner-1",
        role="assistant",
        content="保存当時の回答",
        senpai_conversation_id="11111111-1111-4111-8111-111111111111",
        senpai_turn_id="22222222-2222-4222-8222-222222222222",
        knowhow={"indexVersion": "sha256:" + "a" * 64, "status": "matched"},
    )

    saved = table.put_item.call_args.kwargs["Item"]
    assert saved["senpaiConversationId"] == "11111111-1111-4111-8111-111111111111"
    assert saved["senpaiTurnId"] == "22222222-2222-4222-8222-222222222222"
    assert saved["knowhow"]["indexVersion"] == "sha256:" + "a" * 64


def test_rag_message_writer_does_not_persist_knowhow_without_senpai_tags(rag_app):
    table = MagicMock()
    rag_app.chatlogs_table = table

    rag_app.save_message_to_dynamodb(
        session_id="legacy-session",
        user_id="owner-1",
        role="assistant",
        content="legacy answer",
        knowhow={"matches": [{"body": "private markdown"}]},
    )

    saved = table.put_item.call_args.kwargs["Item"]
    assert "knowhow" not in saved


@pytest.mark.parametrize("rag_mode", ["normal", "law"])
def test_tagged_assistant_writer_persists_empty_response_arrays(rag_app, rag_mode):
    table = MagicMock()
    rag_app.chatlogs_table = table

    rag_app.save_message_to_dynamodb(
        session_id=f"{rag_mode}-session",
        user_id="owner-1",
        role="assistant",
        content="not found",
        response_type="not_found",
        rag_mode=rag_mode,
        source_documents=[],
        page_candidates=[],
        clarify_questions=[],
        senpai_conversation_id="11111111-1111-4111-8111-111111111111",
        senpai_turn_id="22222222-2222-4222-8222-222222222222",
    )

    saved = table.put_item.call_args.kwargs["Item"]
    assert saved["ragMode"] == rag_mode
    assert saved["responseType"] == "not_found"
    assert saved["sourceDocuments"] == []
    assert saved["pageCandidates"] == []
    assert saved["clarifyQuestions"] == []


def test_tagged_clarify_path_persists_complete_response_arrays(rag_app, monkeypatch):
    writer = rag_app.save_message_to_dynamodb
    test_knowhow_api._configure_successful_pipeline(rag_app, monkeypatch, clarify=True)
    monkeypatch.setattr(rag_app, "save_message_to_dynamodb", writer)
    table = MagicMock()
    rag_app.chatlogs_table = table
    conversation_id = "11111111-1111-4111-8111-111111111111"
    turn_id = "22222222-2222-4222-8222-222222222222"

    response = rag_app.handle_rag_request(
        test_knowhow_api._event({
            "query": "対象機種と発生条件は？",
            "includeKnowhow": True,
            "senpaiConversationId": conversation_id,
            "senpaiTurnId": turn_id,
        }), None, 0,
    )

    assert response["statusCode"] == 200
    saved = table.put_item.call_args_list[-1].kwargs["Item"]
    assert saved["role"] == "assistant"
    assert saved["senpaiConversationId"] == conversation_id
    assert saved["senpaiTurnId"] == turn_id
    assert saved["sourceDocuments"] == []
    assert saved["pageCandidates"] == []
    assert saved["clarifyQuestions"] == ["機種と発生条件"]


def test_rag_tag_pair_is_required_and_uuid_validated(rag_app):
    for body in (
        {"query": "質問", "senpaiConversationId": "11111111-1111-4111-8111-111111111111"},
        {"query": "質問", "senpaiConversationId": "bad", "senpaiTurnId": "also-bad"},
    ):
        response = rag_app.handle_rag_request(test_knowhow_api._event(body), None, 0)
        assert response["statusCode"] == 400


def test_rag_tagged_request_echoes_and_saves_same_pair_on_both_rows(rag_app, monkeypatch):
    test_knowhow_api._configure_successful_pipeline(rag_app, monkeypatch)
    saved_rows = []
    monkeypatch.setattr(
        rag_app,
        "save_message_to_dynamodb",
        lambda **kwargs: saved_rows.append(kwargs) or f"message-{len(saved_rows)}",
    )
    conversation_id = "11111111-1111-4111-8111-111111111111"
    turn_id = "22222222-2222-4222-8222-222222222222"
    response = rag_app.handle_rag_request(
        test_knowhow_api._event({
            "query": "かごの走行中振動",
            "includeKnowhow": True,
            "senpaiConversationId": conversation_id,
            "senpaiTurnId": turn_id,
        }), None, 0,
    )

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["senpaiConversationId"] == conversation_id
    assert body["senpaiTurnId"] == turn_id
    assert [row["role"] for row in saved_rows] == ["user", "assistant"]
    assert all(row["senpai_conversation_id"] == conversation_id for row in saved_rows)
    assert all(row["senpai_turn_id"] == turn_id for row in saved_rows)
    assert saved_rows[1]["knowhow"]["indexVersion"] == "sha256:" + "a" * 64


def test_rag_rejects_plain_or_different_conversation_on_tagged_session(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", True, raising=False)
    monkeypatch.setattr(rag_app, "owns_session", lambda *_args: True)
    monkeypatch.setattr(rag_app, "get_session_rag_mode", lambda *_args: "normal")
    monkeypatch.setattr(
        rag_app,
        "get_session_senpai_conversation_id",
        lambda *_args: (True, "11111111-1111-4111-8111-111111111111"),
    )
    monkeypatch.setattr(
        rag_app,
        "get_chat_history",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("history loaded")),
    )
    for extra in (
        {},
        {
            "includeKnowhow": True,
            "senpaiConversationId": "33333333-3333-4333-8333-333333333333",
            "senpaiTurnId": "44444444-4444-4444-8444-444444444444",
        },
    ):
        response = rag_app.handle_rag_request(
            test_knowhow_api._event({"query": "続き", "sessionId": "normal-1", **extra}),
            None,
            0,
        )
        assert response["statusCode"] == 409


def test_tagged_rag_request_requires_verified_admin(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", True, raising=False)
    body = {
        "query": "質問",
        "senpaiConversationId": "11111111-1111-4111-8111-111111111111",
        "senpaiTurnId": "22222222-2222-4222-8222-222222222222",
    }
    response = rag_app.handle_rag_request(
        test_knowhow_api._event(body, groups="users"), None, 0
    )
    assert response["statusCode"] == 403


def test_tagged_law_request_does_not_depend_on_normal_knowhow_flag(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", False, raising=False)
    monkeypatch.setattr(rag_app, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag_app, "LAW_KNOWLEDGE_BASE_ID", "law-test")
    monkeypatch.setattr(rag_app, "get_chat_history", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(rag_app.telemetry, "stamp_reformulation", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        rag_app,
        "query_law_knowledge_base",
        lambda *_args, **_kwargs: {"retrievalResults": [{"score": 0.9, "content": {"text": "law"}, "metadata": {}}]},
    )
    monkeypatch.setattr(rag_app, "is_weak_retrieval", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(rag_app, "select_retrieval_results", lambda results, **_kwargs: results)
    monkeypatch.setattr(rag_app, "prepare_law_references", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(rag_app, "generate_response_with_claude", lambda *_args, **_kwargs: "法令回答")
    monkeypatch.setattr(rag_app, "extract_citations", lambda *_args, **_kwargs: ([], []))
    saved_rows = []
    monkeypatch.setattr(
        rag_app,
        "save_message_to_dynamodb",
        lambda **kwargs: saved_rows.append(kwargs) or f"message-{len(saved_rows)}",
    )
    body = {
        "query": "法令確認",
        "mode": "law",
        "senpaiConversationId": "11111111-1111-4111-8111-111111111111",
        "senpaiTurnId": "22222222-2222-4222-8222-222222222222",
    }

    response = rag_app.handle_rag_request(test_knowhow_api._event(body), None, 0)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["senpaiConversationId"] == body["senpaiConversationId"]
    assert [row["role"] for row in saved_rows] == ["user", "assistant"]


def test_senpai_list_marks_page_limit_as_incomplete():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [], "LastEvaluatedKey": {"timestamp": "older"}}

    response = mod.lambda_handler(
        _chat_event("/chat/sessions", qs={"context": "senpai"}), None
    )

    assert json.loads(response["body"])["complete"] is False
    assert table.query.call_count == 25


def test_senpai_detail_returns_only_self_owned_explicitly_tagged_rows():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [_tagged_message()]}
    conversation_id = "11111111-1111-4111-8111-111111111111"

    response = mod.lambda_handler(
        _chat_event(
            f"/chat/sessions/{conversation_id}/messages",
            qs={"context": "senpai"},
            path_params={"sessionId": conversation_id},
        ), None,
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["context"] == "senpai"
    assert body["conversationId"] == conversation_id
    assert body["readOnly"] is False
    assert body["messages"][0]["senpaiTurnId"] == "22222222-2222-4222-8222-222222222222"
    assert table.query.call_args.kwargs["IndexName"] == "userId-timestamp-index"


def _read_detail(mod, table, items):
    table.query.return_value = {"Items": items}
    conversation_id = "11111111-1111-4111-8111-111111111111"
    response = mod.lambda_handler(
        _chat_event(
            f"/chat/sessions/{conversation_id}/messages",
            qs={"context": "senpai"},
            path_params={"sessionId": conversation_id},
        ), None,
    )
    assert response["statusCode"] == 200
    return json.loads(response["body"])["messages"]


def test_senpai_model_types_match_rag_ui_model_filters(rag_app):
    mod, _table = _load_chat_app()

    assert set(mod.SENPAI_MODEL_TYPES) == set(rag_app.UI_MODEL_FILTERS)


def test_senpai_detail_exposes_saved_model_type_on_normal_assistant_row():
    mod, table = _load_chat_app()
    messages = _read_detail(mod, table, [
        _tagged_message(),
        _tagged_message(role="assistant", content="回答", queryFilters={"modelType": "AXIEZ-LINKs"}),
    ])

    by_role = {row["role"]: row for row in messages}
    assert by_role["assistant"]["modelType"] == "AXIEZ-LINKs"
    assert "modelType" not in by_role["user"]


@pytest.mark.parametrize("bogus", [
    "未知の機種", "", "AXIEZ\n", "A" * 65, 123, ["AXIEZ"], None,
])
def test_senpai_detail_drops_unknown_or_malformed_saved_model_type(bogus):
    mod, table = _load_chat_app()
    messages = _read_detail(mod, table, [
        _tagged_message(),
        _tagged_message(role="assistant", content="回答", queryFilters={"modelType": bogus}),
    ])

    assert all("modelType" not in row for row in messages)


def test_senpai_detail_ignores_model_type_without_filters_and_in_law_lane():
    mod, table = _load_chat_app()
    messages = _read_detail(mod, table, [
        _tagged_message(),
        _tagged_message(role="assistant", content="回答"),
        _tagged_message("law-1", ragMode="law"),
        _tagged_message("law-1", role="assistant", ragMode="law", queryFilters={"modelType": "AXIEZ"}),
    ])

    assert len(messages) == 4
    assert all("modelType" not in row for row in messages)


def test_senpai_detail_drops_orphan_assistants_and_marks_partial_turns():
    mod, table = _load_chat_app()
    conversation_id = "11111111-1111-4111-8111-111111111111"
    user_turn = "22222222-2222-4222-8222-222222222222"
    orphan_turn = "33333333-3333-4333-8333-333333333333"
    unanswered_turn = "44444444-4444-4444-8444-444444444444"
    table.query.return_value = {"Items": [
        _tagged_message("n1", "user", "質問", senpaiTurnId=user_turn),
        _tagged_message("n1", "assistant", "回答", senpaiTurnId=user_turn),
        _tagged_message("n2", "assistant", "質問が期限切れ", senpaiTurnId=orphan_turn),
        _tagged_message("n3", "user", "未回答", senpaiTurnId=unanswered_turn),
    ]}

    response = mod.lambda_handler(
        _chat_event(
            f"/chat/sessions/{conversation_id}/messages",
            qs={"context": "senpai"},
            path_params={"sessionId": conversation_id},
        ), None,
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["complete"] is False
    assert {row["senpaiTurnId"] for row in body["messages"]} == {user_turn, unanswered_turn}
    assert {row["role"] for row in body["messages"] if row["senpaiTurnId"] == user_turn} == {
        "user", "assistant",
    }
    assert [row["role"] for row in body["messages"] if row["senpaiTurnId"] == unanswered_turn] == ["user"]


def test_user_only_lane_does_not_make_complete_history_incomplete():
    mod, table = _load_chat_app()
    conversation_id = "11111111-1111-4111-8111-111111111111"
    turn_id = "22222222-2222-4222-8222-222222222222"
    table.query.return_value = {"Items": [
        _tagged_message("normal", "user", "質問", ragMode="normal", senpaiTurnId=turn_id),
        _tagged_message("normal", "assistant", "回答", ragMode="normal", senpaiTurnId=turn_id),
        _tagged_message("law", "user", "質問", ragMode="law", senpaiTurnId=turn_id),
    ]}

    response = mod.lambda_handler(
        _chat_event(
            f"/chat/sessions/{conversation_id}/messages",
            qs={"context": "senpai"},
            path_params={"sessionId": conversation_id},
        ), None,
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["complete"] is True
    assert {row["role"] for row in body["messages"] if row["ragMode"] == "normal"} == {
        "user", "assistant",
    }
    assert [row["role"] for row in body["messages"] if row["ragMode"] == "law"] == ["user"]


def test_senpai_detail_size_limit_drops_oldest_whole_turn_group():
    mod, table = _load_chat_app()
    conversation_id = "11111111-1111-4111-8111-111111111111"
    older_turn = "22222222-2222-4222-8222-222222222222"
    newest_turn = "33333333-3333-4333-8333-333333333333"
    large_text = "x" * 550_000
    table.query.return_value = {"Items": [
        _tagged_message("n1", "user", large_text, senpaiTurnId=older_turn),
        _tagged_message("n1", "assistant", large_text, senpaiTurnId=older_turn),
        _tagged_message("n2", "user", large_text, senpaiTurnId=newest_turn),
        _tagged_message("n2", "assistant", large_text, senpaiTurnId=newest_turn),
    ]}

    response = mod.lambda_handler(
        _chat_event(
            f"/chat/sessions/{conversation_id}/messages",
            qs={"context": "senpai"},
            path_params={"sessionId": conversation_id},
        ), None,
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["complete"] is False
    assert len(response["body"].encode("utf-8")) <= 2 * 1024 * 1024
    assert len(body["messages"]) == 2
    assert {row["senpaiTurnId"] for row in body["messages"]} == {newest_turn}


def test_senpai_detail_message_count_limit_keeps_whole_turn_groups():
    mod, table = _load_chat_app()
    conversation_id = "11111111-1111-4111-8111-111111111111"
    rows = []
    for index in range(202):
        turn_id = f"00000000-0000-4000-8000-{index:012d}"
        rows.extend([
            _tagged_message(f"n{index}", "user", f"Q{index}", senpaiTurnId=turn_id),
            _tagged_message(f"n{index}", "assistant", f"A{index}", senpaiTurnId=turn_id),
        ])
    table.query.return_value = {"Items": rows}

    response = mod.lambda_handler(
        _chat_event(
            f"/chat/sessions/{conversation_id}/messages",
            qs={"context": "senpai"},
            path_params={"sessionId": conversation_id},
        ), None,
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["complete"] is False
    assert len(body["messages"]) == 400
    turns = {row["senpaiTurnId"] for row in body["messages"]}
    assert len(turns) == 200
    assert all({row["role"] for row in body["messages"] if row["senpaiTurnId"] == turn} == {"user", "assistant"} for turn in turns)
    assert "00000000-0000-4000-8000-000000000201" in turns
    assert "00000000-0000-4000-8000-000000000001" not in turns


def test_senpai_list_skips_assistant_only_conversation_groups():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [
        _tagged_message(role="assistant", content="question expired"),
    ]}

    response = mod.lambda_handler(
        _chat_event("/chat/sessions", qs={"context": "senpai"}), None
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["sessions"] == []
    assert body["complete"] is False


def test_unknown_history_context_is_rejected():
    mod, table = _load_chat_app()
    response = mod.lambda_handler(
        _chat_event("/chat/sessions", qs={"context": "other"}), None
    )

    assert response["statusCode"] == 400
    table.query.assert_not_called()


def test_senpai_grouped_detail_rejects_invalid_conversation_id():
    mod, table = _load_chat_app()
    response = mod.lambda_handler(
        _chat_event(
            "/chat/sessions/not-a-uuid/messages",
            qs={"context": "senpai"},
            path_params={"sessionId": "not-a-uuid"},
        ), None,
    )
    assert response["statusCode"] == 400
    table.query.assert_not_called()


def test_senpai_list_excludes_expired_deleted_or_malformed_records():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [
        _tagged_message("expired", ttl=1),
        _tagged_message("deleted", deleted=True),
        _tagged_message("partial", senpaiTurnId="not-a-uuid"),
        _tagged_message("wish-record", role="product_wish"),
    ]}
    response = mod.lambda_handler(
        _chat_event("/chat/sessions", qs={"context": "senpai"}), None
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["sessions"] == []


def test_moto_writer_to_grouped_handlers_preserves_saved_senpai_payload(rag_app):
    from moto import mock_aws
    import boto3

    conversation_id = "11111111-1111-4111-8111-111111111111"
    turn_id = "22222222-2222-4222-8222-222222222222"
    knowhow_snapshot = {
        "indexVersion": "index-2026-10-20",
        "matches": [{"knowledgeId": "KH-42", "cardVersion": 7, "body": "保存時点の本文"}],
    }

    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        table = dynamodb.create_table(
            TableName="senpai-history-integration",
            KeySchema=[
                {"AttributeName": "sessionId", "KeyType": "HASH"},
                {"AttributeName": "messageId", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "sessionId", "AttributeType": "S"},
                {"AttributeName": "messageId", "AttributeType": "S"},
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[{
                "IndexName": "userId-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "userId", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }],
            BillingMode="PAY_PER_REQUEST",
        )
        rag_app.chatlogs_table = table
        chatmod, _ = _load_chat_app()
        chatmod.chatlogs_table = table

        # Normal and law share the user turn identity but persist separate lane rows.
        for mode, session_id in (("normal", "normal-session"), ("law", "law-session")):
            for role, content in (("user", "質問"), ("assistant", f"{mode}回答")):
                rag_app.save_message_to_dynamodb(
                    session_id=session_id,
                    user_id="owner-1",
                    role=role,
                    content=content,
                    rag_mode=mode,
                    senpai_conversation_id=conversation_id,
                    senpai_turn_id=turn_id,
                    source_documents=[] if role == "assistant" else None,
                    page_candidates=[] if role == "assistant" else None,
                    clarify_questions=[] if role == "assistant" else None,
                    response_type="pages" if role == "assistant" and mode == "normal" else None,
                    knowhow=knowhow_snapshot if role == "assistant" and mode == "normal" else None,
                )

        # Another owner can use the same conversation UUID, but remains invisible here.
        rag_app.save_message_to_dynamodb(
            session_id="other-owner-session",
            user_id="owner-2",
            role="user",
            content="他の人の質問",
            senpai_conversation_id=conversation_id,
            senpai_turn_id="33333333-3333-4333-8333-333333333333",
        )

        list_response = chatmod.lambda_handler(
            _chat_event("/chat/sessions", qs={"context": "senpai"}), None
        )
        detail_response = chatmod.lambda_handler(
            _chat_event(
                f"/chat/sessions/{conversation_id}/messages",
                qs={"context": "senpai"},
                path_params={"sessionId": conversation_id},
            ), None,
        )

    listed = json.loads(list_response["body"])
    detail = json.loads(detail_response["body"])
    assert list_response["statusCode"] == detail_response["statusCode"] == 200
    assert listed["complete"] is True
    assert len(listed["sessions"]) == 1
    assert listed["sessions"][0]["conversationId"] == conversation_id
    assert listed["sessions"][0]["messageCount"] == 1
    assert detail["conversationId"] == conversation_id
    assert detail["complete"] is True
    assert len(detail["messages"]) == 4
    assert {row["userId"] for row in detail["messages"]} == {"owner-1"}
    normal_answer = next(
        row for row in detail["messages"]
        if row["ragMode"] == "normal" and row["role"] == "assistant"
    )
    assert normal_answer["senpaiConversationId"] == conversation_id
    assert normal_answer["senpaiTurnId"] == turn_id
    assert normal_answer["sourceDocuments"] == []
    assert normal_answer["pageCandidates"] == []
    assert normal_answer["clarifyQuestions"] == []
    assert normal_answer["responseType"] == "pages"
    assert normal_answer["knowhow"]["matches"][0]["cardVersion"] == 7
    assert normal_answer["knowhow"]["matches"][0]["body"] == "保存時点の本文"

