"""RAG のセッション確認・履歴取得: 削除済み／TTL 切れの行を有効なものとして扱わない。"""
import importlib.util
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = ROOT / "lambda" / "rag" / "rag-function"

os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
os.environ.setdefault("KB_SOURCE_BUCKET", "kb-source-bucket")
os.environ.setdefault("KB_SOURCE_PREFIX", "docs/")
os.environ.setdefault("DOCUMENTS_BUCKET", "documents-test")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, RAG_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_load("rag_telemetry_mod_session_integrity", "telemetry.py")
with patch("boto3.client"), patch("boto3.resource"):
    rag = _load("rag_app_session_integrity", "app.py")


class _PagedTable:
    """Limit 件ごとにページを返す。FilterExpression は無視する（アプリ側の再確認も検証するため）。"""

    def __init__(self, items):
        self.items = items
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        start = (kwargs.get("ExclusiveStartKey") or {}).get("i", 0)
        limit = kwargs.get("Limit", 1000)
        page = self.items[start:start + limit]
        out = {"Items": page}
        if start + limit < len(self.items):
            out["LastEvaluatedKey"] = {"i": start + limit}
        return out


def _row(**kw):
    return {"userId": "u1", "role": "user", **kw}


def test_owns_session_rejects_session_with_only_deleted_rows(monkeypatch):
    table = _PagedTable([_row(deleted=True), _row(deleted=True)])
    monkeypatch.setattr(rag, "chatlogs_table", table)
    assert rag.owns_session("s1", "u1") is False


def test_owns_session_pages_until_live_row_found(monkeypatch):
    items = [_row(deleted=True) for _ in range(120)] + [_row()]
    table = _PagedTable(items)
    monkeypatch.setattr(rag, "chatlogs_table", table)
    assert rag.owns_session("s1", "u1") is True
    assert len(table.calls) > 1


def test_owns_session_ignores_expired_rows(monkeypatch):
    now = int(time.time())
    table = _PagedTable([_row(ttl=now - 10)])
    monkeypatch.setattr(rag, "chatlogs_table", table)
    assert rag.owns_session("s1", "u1") is False
    monkeypatch.setattr(rag, "chatlogs_table", _PagedTable([_row(ttl=now + 1000)]))
    assert rag.owns_session("s1", "u1") is True
    monkeypatch.setattr(rag, "chatlogs_table", _PagedTable([_row()]))  # ttl 属性なしは有効
    assert rag.owns_session("s1", "u1") is True


def test_owns_session_rejects_other_users_live_row(monkeypatch):
    monkeypatch.setattr(rag, "chatlogs_table", _PagedTable([{"userId": "other"}]))
    assert rag.owns_session("s1", "u1") is False


def test_session_queries_use_consistent_read(monkeypatch):
    table = _PagedTable([_row(ragMode="normal")])
    monkeypatch.setattr(rag, "chatlogs_table", table)
    rag.owns_session("s1", "u1")
    rag.get_session_rag_mode("s1")
    rag.get_session_senpai_conversation_id("s1")
    rag.get_chat_history("s1")
    assert table.calls and all(call.get("ConsistentRead") is True for call in table.calls)


def test_chat_history_excludes_expired_rows(monkeypatch):
    now = int(time.time())
    items = [
        {"role": "user", "content": "old", "ttl": now - 5},
        {"role": "user", "content": "keep-no-ttl"},
        {"role": "user", "content": "keep-future", "ttl": now + 500},
    ]
    monkeypatch.setattr(rag, "chatlogs_table", _PagedTable(items))
    contents = [m["content"] for m in rag.get_chat_history("s1")]
    assert "old" not in contents
    assert set(contents) == {"keep-no-ttl", "keep-future"}


def test_chat_history_filter_expression_excludes_expired(monkeypatch):
    table = _PagedTable([])
    monkeypatch.setattr(rag, "chatlogs_table", table)
    rag.get_chat_history("s1")
    assert "ttl" in table.calls[0]["FilterExpression"]


class _EmptyClient:
    def converse(self, **kwargs):
        return {"output": {"message": {"content": [{"text": "  \n"}]}}}


def test_blank_generation_is_not_returned_as_success(monkeypatch):
    monkeypatch.setattr(rag, "BEDROCK_MODEL_ID", "global.openai.gpt-6-luna")
    monkeypatch.setattr(rag, "select_retrieval_results", lambda *a, **k: [])
    monkeypatch.setattr(rag, "build_claude_messages", lambda *a, **k: [{"role": "user", "content": "q"}])
    monkeypatch.setattr(rag, "bedrock_runtime", _EmptyClient())
    with pytest.raises(rag.EmptyGenerationError):
        rag.generate_response_with_claude("質問", {"retrievalResults": []}, search_query="質問")
