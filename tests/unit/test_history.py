"""history Lambda のユニットテスト"""
import importlib.util
import os
import json
import pytest
from unittest.mock import MagicMock
from decimal import Decimal

BASE = os.path.join(os.path.dirname(__file__), "../..")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


history = _load("history_app", "lambda/troubleshooting/history/app.py")


def _event(user_id="user-001", session_id=None):
    return {
        "requestContext": {"authorizer": {"userId": user_id}},
        "queryStringParameters": {"sessionId": session_id} if session_id else None,
    }


def _make_table_mock():
    return MagicMock()


# ---------------------------------------------------------------------------
# 認証チェック
# ---------------------------------------------------------------------------

def test_no_user_id_returns_401(mocker):
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=_make_table_mock())
    resp = history.lambda_handler(_event(user_id=""), None)
    assert resp["statusCode"] == 401


# ---------------------------------------------------------------------------
# セッション詳細取得（sessionId 指定あり）
# ---------------------------------------------------------------------------

def test_get_detail_own_session(mocker):
    mock_table = _make_table_mock()
    mock_table.get_item.return_value = {
        "Item": {
            "session_id": "sess-001",
            "userId": "user-001",
            "timestamp": "2026-05-22T10:00:00+00:00",
            "result": "回答テキスト",
            "sourceDocuments": [],
        }
    }
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001", session_id="sess-001"), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["session_id"] == "sess-001"


def test_get_detail_other_users_session_returns_404(mocker):
    mock_table = _make_table_mock()
    mock_table.get_item.return_value = {
        "Item": {
            "session_id": "sess-002",
            "userId": "other-user",
            "result": "回答",
            "sourceDocuments": [],
        }
    }
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001", session_id="sess-002"), None)
    assert resp["statusCode"] == 404


def test_get_detail_not_found_returns_404(mocker):
    mock_table = _make_table_mock()
    mock_table.get_item.return_value = {}
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001", session_id="nonexistent"), None)
    assert resp["statusCode"] == 404


# ---------------------------------------------------------------------------
# セッション一覧取得（sessionId 指定なし）
# ---------------------------------------------------------------------------

def test_list_sessions(mocker):
    mock_table = _make_table_mock()
    mock_table.query.return_value = {
        "Items": [
            {
                "session_id": "sess-003",
                "timestamp": "2026-05-22T11:00:00+00:00",
                "input": {"model": "KE-LG", "troubleDescription": "停止"},
                "result": "回答テキスト",
            }
        ]
    }
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001"), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert len(body["sessions"]) == 1
    assert body["sessions"][0]["sessionId"] == "sess-003"
    assert body["sessions"][0]["preview"] == "回答テキスト"


def test_list_sessions_empty(mocker):
    mock_table = _make_table_mock()
    mock_table.query.return_value = {"Items": []}
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001"), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["sessions"] == []


def test_list_sessions_result_none_preview_empty(mocker):
    mock_table = _make_table_mock()
    mock_table.query.return_value = {
        "Items": [
            {
                "session_id": "sess-004",
                "timestamp": "2026-05-22T12:00:00+00:00",
                "input": {},
                "result": None,
            }
        ]
    }
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001"), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["sessions"][0]["preview"] == ""


def test_list_preview_truncated_to_100_chars(mocker):
    long_result = "あ" * 200
    mock_table = _make_table_mock()
    mock_table.query.return_value = {
        "Items": [{"session_id": "s", "timestamp": "t", "input": {}, "result": long_result}]
    }
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001"), None)
    body = json.loads(resp["body"])
    assert len(body["sessions"][0]["preview"]) == 100


def test_decimal_in_source_documents_serialized(mocker):
    mock_table = _make_table_mock()
    mock_table.get_item.return_value = {
        "Item": {
            "session_id": "sess-005",
            "userId": "user-001",
            "timestamp": "2026-05-22T10:00:00+00:00",
            "result": "回答",
            "sourceDocuments": [{"relevance": Decimal("0.87")}],
        }
    }
    mocker.patch.object(history.dynamodb_resource, "Table", return_value=mock_table)

    resp = history.lambda_handler(_event(user_id="user-001", session_id="sess-005"), None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["sourceDocuments"][0]["relevance"] == pytest.approx(0.87)
