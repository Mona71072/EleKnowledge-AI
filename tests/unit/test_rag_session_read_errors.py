"""セッション読取の DynamoDB 失敗と、非同期の見出しタスクのログ契約。

- 読取失敗は 404 にせず、一般化した 500（rag_error）にする。
- 内部の見出しタスクは HTTP リクエストではないので rag_request を出さない。
"""
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = ROOT / "lambda" / "rag" / "rag-function"

os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
os.environ.setdefault("KB_SOURCE_BUCKET", "kb-source-bucket")
os.environ.setdefault("KB_SOURCE_PREFIX", "docs/")
os.environ.setdefault("DOCUMENTS_BUCKET", "documents-test")

SECRET_TEXT = "s3://secret/path private question internal detail"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, RAG_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_load("rag_telemetry_mod_session_read", "telemetry.py")
with patch("boto3.client"), patch("boto3.resource"):
    rag = _load("rag_app_session_read", "app.py")


def _client_error(op="Query", code="ProvisionedThroughputExceededException"):
    return ClientError({"Error": {"Code": code, "Message": SECRET_TEXT}}, op)


class _FailingTable:
    def query(self, **kwargs):
        raise _client_error()


class _Table:
    def __init__(self, items):
        self.items = items

    def query(self, **kwargs):
        return {"Items": self.items}


def _event(session_id="sensitive-session-id"):
    return {
        "httpMethod": "POST",
        "requestContext": {
            "requestId": "req-read",
            "authorizer": {"claims": {"sub": "sensitive-sub"}},
        },
        "body": json.dumps({"sessionId": session_id, "query": "private question"}),
    }


def _log_lines(output):
    return [json.loads(line) for line in output.splitlines() if line.startswith("{")]


def _assert_generic_500(resp, output):
    assert resp["statusCode"] == 500
    body = json.loads(resp["body"])
    assert body["error"] == "InternalServerError"
    assert body["requestId"] == "req-read"
    for sensitive in (SECRET_TEXT, "private question", "sensitive-session-id", "sensitive-sub"):
        assert sensitive not in resp["body"]
        assert sensitive not in output
    kinds = [line["event"] for line in _log_lines(output)]
    assert "rag_error" in kinds
    err = next(line for line in _log_lines(output) if line["event"] == "rag_error")
    assert err["errorCode"] == "ProvisionedThroughputExceededException"


# ------------------------------------------------------------------ 単体: 例外は握りつぶさない
def test_owns_session_propagates_read_failure(monkeypatch):
    monkeypatch.setattr(rag, "chatlogs_table", _FailingTable())
    with pytest.raises(ClientError):
        rag.owns_session("s1", "u1")


def test_owns_session_false_for_missing_or_other_users_session(monkeypatch):
    monkeypatch.setattr(rag, "chatlogs_table", _Table([]))
    assert rag.owns_session("s1", "u1") is False
    monkeypatch.setattr(rag, "chatlogs_table", _Table([{"userId": "other"}]))
    assert rag.owns_session("s1", "u1") is False


def test_get_session_rag_mode_propagates_read_failure(monkeypatch):
    monkeypatch.setattr(rag, "chatlogs_table", _FailingTable())
    with pytest.raises(ClientError):
        rag.get_session_rag_mode("s1")


def test_get_session_rag_mode_none_when_session_has_no_rows(monkeypatch):
    monkeypatch.setattr(rag, "chatlogs_table", _Table([]))
    assert rag.get_session_rag_mode("s1") is None


def test_get_chat_history_propagates_read_failure(monkeypatch):
    monkeypatch.setattr(rag, "chatlogs_table", _FailingTable())
    with pytest.raises(ClientError):
        rag.get_chat_history("s1")


# ------------------------------------------------------------------ ハンドラ: 404 ではなく 500
def test_handler_returns_500_not_404_when_ownership_read_fails(monkeypatch, capsys):
    monkeypatch.setattr(rag, "get_caller_id", lambda event: "sensitive-sub")
    monkeypatch.setattr(rag, "chatlogs_table", _FailingTable())
    resp = rag.lambda_handler(_event(), None)
    _assert_generic_500(resp, capsys.readouterr().out)


def test_handler_returns_500_not_404_when_session_mode_read_fails(monkeypatch, capsys):
    monkeypatch.setattr(rag, "get_caller_id", lambda event: "sensitive-sub")
    monkeypatch.setattr(rag, "owns_session", lambda s, u: True)

    def fail(session_id):
        raise _client_error()

    monkeypatch.setattr(rag, "get_session_rag_mode", fail)
    resp = rag.lambda_handler(_event(), None)
    _assert_generic_500(resp, capsys.readouterr().out)


def test_handler_returns_500_when_history_read_fails(monkeypatch, capsys):
    monkeypatch.setattr(rag, "get_caller_id", lambda event: "sensitive-sub")
    monkeypatch.setattr(rag, "owns_session", lambda s, u: True)
    monkeypatch.setattr(rag, "get_session_rag_mode", lambda s: "normal")

    def fail(*args, **kwargs):
        raise _client_error()

    monkeypatch.setattr(rag, "get_chat_history", fail)
    resp = rag.lambda_handler(_event(), None)
    _assert_generic_500(resp, capsys.readouterr().out)


def test_handler_still_returns_404_for_missing_session(monkeypatch):
    monkeypatch.setattr(rag, "get_caller_id", lambda event: "sensitive-sub")
    monkeypatch.setattr(rag, "owns_session", lambda s, u: False)
    resp = rag.lambda_handler(_event(), None)
    assert resp["statusCode"] == 404
    assert json.loads(resp["body"])["error"] == "NotFound"


def test_handler_returns_404_when_session_mode_is_none(monkeypatch):
    monkeypatch.setattr(rag, "get_caller_id", lambda event: "sensitive-sub")
    monkeypatch.setattr(rag, "owns_session", lambda s, u: True)
    monkeypatch.setattr(rag, "get_session_rag_mode", lambda s: None)
    resp = rag.lambda_handler(_event(), None)
    assert resp["statusCode"] == 404


# ------------------------------------------------------------------ 見出しタスクは rag_request を出さない
def test_session_title_task_does_not_emit_rag_request(monkeypatch, capsys):
    monkeypatch.setattr(rag, "generate_session_title", lambda query, deadline=None: "見出し")
    updates = []
    monkeypatch.setattr(rag, "update_session_title", lambda *args: updates.append(args))
    task = {
        "_internalTask": "session-title",
        "sessionId": "s1", "messageId": "m1", "userId": "u1", "query": "private question",
    }
    result = rag.lambda_handler(task, None)
    assert result == {"ok": True}
    assert updates == [("s1", "m1", "u1", "見出し")]
    output = capsys.readouterr().out
    assert "rag_request" not in output
    assert "private question" not in output
