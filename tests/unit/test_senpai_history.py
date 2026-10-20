"""Persistent Senpai history contracts for RAG and chat-management Lambdas."""
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


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
    table.query.return_value = {"Items": [
        _tagged_message(),
        {**_tagged_message("regular-1"), "senpaiConversationId": None, "senpaiTurnId": None},
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
    ]}

    response = mod.lambda_handler(
        _chat_event("/chat/sessions", qs={"context": "senpai"}), None
    )

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["context"] == "senpai"
    assert body["complete"] is True
    assert body["sessions"] == [{
        "conversationId": "11111111-1111-4111-8111-111111111111",
        "title": "最初の質問",
        "createdAt": "2026-10-20T01:00:00Z",
        "lastMessageTime": "2026-10-20T01:01:00Z",
        "messageCount": 1,
        "daysUntilDeletion": pytest.approx(1),
    }]
    assert table.query.call_args.kwargs["IndexName"] == "userId-timestamp-index"


def test_senpai_grouped_detail_cannot_be_read_by_admin_for_another_owner():
    mod, table = _load_chat_app()
    table.query.return_value = {"Items": [{
        **_tagged_message(),
        "userId": "another-owner",
    }]}

    response = mod.lambda_handler(
        _chat_event(
            "/chat/sessions/normal-1/messages",
            qs={"context": "senpai"},
            sub="admin-user",
            path_params={"sessionId": "normal-1"},
        ), None
    )

    assert response["statusCode"] == 404
    assert table.query.call_args.kwargs["IndexName"] == "userId-timestamp-index"


def test_generic_owner_session_response_strips_senpai_tags_for_non_admin():
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

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "senpaiConversationId" not in body["messages"][0]
    assert "senpaiTurnId" not in body["messages"][0]


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

