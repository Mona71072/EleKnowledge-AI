"""rag-function: セッション見出し（generate_session_title）の単体テスト。

履歴一覧で会話を見分けられるよう、最初の質問から短い体言止めの見出しを Claude に作らせる。
Bedrock が落ちても回答自体は返す必要があるため、フォールバックを重点的に確認する。
"""
import importlib.util
import json
import os
import sys

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")


@pytest.fixture(scope="module")
def rag():
    os.environ.setdefault("CHATLOGS_TABLE", "test-chatlogs")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("BEDROCK_MODEL_ID", "jp.anthropic.claude-haiku-4-5-20251001-v1:0")
    path = os.path.normpath(os.path.join(BASE, "lambda/rag/rag-function/app.py"))
    name = "rag_session_title_app"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class _Body:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _stub_invoke(rag, monkeypatch, text, capture=None):
    def fake_invoke_model(modelId=None, body=None):
        if capture is not None:
            capture["modelId"] = modelId
            capture["body"] = json.loads(body)
        return {"body": _Body({"content": [{"text": text}]})}

    monkeypatch.setattr(rag.bedrock_runtime, "invoke_model", fake_invoke_model)


def test_title_uses_model_output(rag, monkeypatch):
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "jp.anthropic.claude-haiku-4-5-20251001-v1:0")
    capture = {}
    _stub_invoke(rag, monkeypatch, "溶接脚長の判断基準", capture)

    title = rag.generate_session_title("溶接の脚長が基準外となる判断基準は？")

    assert title == "溶接脚長の判断基準"
    # 質問文は指示ではなく資料として渡す（プロンプトインジェクション対策）
    assert "<question>" in capture["body"]["messages"][0]["content"]
    assert capture["body"]["max_tokens"] <= 64


def test_title_strips_quotes_prefix_and_extra_lines(rag, monkeypatch):
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")
    _stub_invoke(rag, monkeypatch, "  「乗場ドアの異音対処」\n他の案: ドア異音  ")

    assert rag.generate_session_title("乗場のドアから異音がします") == "乗場ドアの異音対処"


def test_title_truncates_long_model_output(rag, monkeypatch):
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")
    _stub_invoke(rag, monkeypatch, "あ" * 100)

    assert len(rag.generate_session_title("質問")) == rag.SESSION_TITLE_MAX_LENGTH


def test_title_falls_back_when_bedrock_fails(rag, monkeypatch):
    """Bedrock が落ちても見出し生成でリクエストを失敗させない。"""
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")

    def boom(**kwargs):
        raise RuntimeError("bedrock down")

    monkeypatch.setattr(rag.bedrock_runtime, "invoke_model", boom)

    assert rag.generate_session_title("溶接の脚長は？") == "溶接の脚長は？"


def test_title_falls_back_when_model_returns_empty(rag, monkeypatch):
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")
    _stub_invoke(rag, monkeypatch, "   ")

    assert rag.generate_session_title("溶接の脚長は？") == "溶接の脚長は？"


def test_title_llm_can_be_disabled(rag, monkeypatch):
    """SESSION_TITLE_LLM=false で従来どおり質問文の切り詰めに戻せる。"""
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", False)

    def unexpected(**kwargs):  # pragma: no cover - 呼ばれたら失敗させる
        raise AssertionError("LLM は呼ばない")

    monkeypatch.setattr(rag.bedrock_runtime, "invoke_model", unexpected)

    long_query = "あ" * 60
    title = rag.generate_session_title(long_query)
    assert title == "あ" * 50 + "..."


def test_title_empty_query(rag):
    assert rag.generate_session_title("") == "Untitled"


def test_save_message_persists_session_title(rag, monkeypatch):
    """生成した見出しは最初のユーザーメッセージに保存する（一覧はこれを読む）。"""
    saved = {}

    class _Table:
        def put_item(self, Item=None):
            saved.update(Item)

    monkeypatch.setattr(rag, "chatlogs_table", _Table())

    rag.save_message_to_dynamodb(
        session_id="s1",
        user_id="u1",
        role="user",
        content="溶接の脚長が基準外となる判断基準は？",
        session_title="溶接脚長の判断基準",
    )

    assert saved["sessionTitle"] == "溶接脚長の判断基準"
