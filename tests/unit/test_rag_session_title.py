"""rag-function: セッション見出し（generate_session_title）の単体テスト。

履歴一覧で会話を見分けられるよう、最初の質問から短い体言止めの見出しを Claude に作らせる。
Bedrock が落ちても回答自体は返す必要があるため、フォールバックを重点的に確認する。
"""
import importlib.util
import inspect
import json
import os
import sys
import time

import pytest
from botocore.exceptions import ClientError, ReadTimeoutError

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

    monkeypatch.setattr(rag.bedrock_runtime_title, "invoke_model", fake_invoke_model)


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


def test_title_uses_sonnet5_compatible_request(rag, monkeypatch):
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "global.anthropic.claude-sonnet-5")
    capture = {}
    _stub_invoke(rag, monkeypatch, "見出し", capture)

    assert rag.generate_session_title("質問") == "見出し"
    assert "temperature" not in capture["body"]
    assert capture["body"]["thinking"] == {"type": "disabled"}


def test_title_uses_effort_low_and_falls_back_when_thinking_uses_budget(rag, monkeypatch):
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "global.anthropic.claude-sonnet-5-5")
    captured = {}

    def thinking_only(modelId=None, body=None):
        captured.update(json.loads(body))
        return {"body": _Body({"content": [{"type": "thinking", "thinking": "reason"}]})}

    monkeypatch.setattr(rag.bedrock_runtime_title, "invoke_model", thinking_only)

    assert rag.generate_session_title("溶接の脚長は？") == "溶接の脚長は？"
    assert "thinking" not in captured
    assert captured["output_config"] == {"effort": "low"}
    assert captured["max_tokens"] == 64


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

    monkeypatch.setattr(rag.bedrock_runtime_title, "invoke_model", boom)

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

    monkeypatch.setattr(rag.bedrock_runtime_title, "invoke_model", unexpected)

    long_query = "あ" * 60
    title = rag.generate_session_title(long_query)
    assert title == "あ" * 50 + "..."


def test_title_empty_query(rag):
    assert rag.generate_session_title("") == "Untitled"


# --- 遅い失敗でも回答を止めない（PR #84 レビュー: 補助処理に回答期限より短い上限を設ける） ---


def test_title_client_has_short_timeout_and_no_retry(rag):
    """見出し生成は専用クライアント。既定（read 60 秒・legacy リトライ）を使わない。"""
    cfg = rag.bedrock_runtime_title.meta.config
    assert cfg.read_timeout == rag.SESSION_TITLE_READ_TIMEOUT_SECONDS
    assert cfg.connect_timeout == rag.SESSION_TITLE_CONNECT_TIMEOUT_SECONDS
    assert cfg.retries.get("total_max_attempts") == 1  # botocore が mode を補うので鍵だけ見る
    # 読取期限 + 予備時間が応答予算に収まる（= 1 回の見出し生成で 29 秒を越えない）
    assert (
        rag.SESSION_TITLE_READ_TIMEOUT_SECONDS + rag.SESSION_TITLE_RESERVE_SECONDS
        < rag.RESPONSE_TIME_BUDGET_SECONDS
    )
    assert rag.RESPONSE_TIME_BUDGET_SECONDS < 29
    # 回答本体のクライアントとは別インスタンス
    assert rag.bedrock_runtime_title is not rag.bedrock_runtime


def test_title_falls_back_when_bedrock_stalls_and_times_out(rag, monkeypatch):
    """Bedrock が停滞して読取期限で切れた場合も、期限内にフォールバック見出しを返す。"""
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")
    calls = {"n": 0}

    def stalled(**kwargs):
        calls["n"] += 1
        time.sleep(0.05)  # 専用クライアントが read_timeout で打ち切った状況を模す
        raise ReadTimeoutError(endpoint_url="https://bedrock-runtime.example")

    monkeypatch.setattr(rag.bedrock_runtime_title, "invoke_model", stalled)

    deadline = time.monotonic() + rag.RESPONSE_TIME_BUDGET_SECONDS
    started = time.monotonic()
    title = rag.generate_session_title("溶接の脚長は？", deadline=deadline)
    elapsed = time.monotonic() - started

    assert title == "溶接の脚長は？"
    assert calls["n"] == 1  # 再試行しない
    assert elapsed < rag.SESSION_TITLE_RESERVE_SECONDS
    assert time.monotonic() < deadline


def test_title_skipped_when_response_budget_is_low(rag, monkeypatch):
    """残り予算が読取期限 + 予備時間に満たなければ Bedrock を呼ばずにフォールバックする。"""
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")

    def unexpected(**kwargs):  # pragma: no cover - 呼ばれたら失敗させる
        raise AssertionError("予算不足時は LLM を呼ばない")

    monkeypatch.setattr(rag.bedrock_runtime_title, "invoke_model", unexpected)

    # 検索・生成で時間を使い切り、残り予算が閾値をわずかに下回る
    threshold = rag.SESSION_TITLE_READ_TIMEOUT_SECONDS + rag.SESSION_TITLE_RESERVE_SECONDS
    deadline = time.monotonic() + threshold - 0.5

    assert rag.generate_session_title("溶接の脚長は？", deadline=deadline) == "溶接の脚長は？"


def test_title_generated_when_response_budget_is_enough(rag, monkeypatch):
    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")
    _stub_invoke(rag, monkeypatch, "溶接脚長の判断基準")

    threshold = rag.SESSION_TITLE_READ_TIMEOUT_SECONDS + rag.SESSION_TITLE_RESERVE_SECONDS
    deadline = time.monotonic() + threshold + 1.0

    assert rag.generate_session_title("溶接の脚長は？", deadline=deadline) == "溶接脚長の判断基準"


def test_session_title_budget_allows_boundary(rag):
    threshold = rag.SESSION_TITLE_READ_TIMEOUT_SECONDS + rag.SESSION_TITLE_RESERVE_SECONDS
    now = 1000.0
    assert rag.session_title_budget_allows(None) is True
    assert rag.session_title_budget_allows(now + threshold, now=now) is True
    assert rag.session_title_budget_allows(now + threshold - 0.01, now=now) is False
    assert rag.session_title_budget_allows(now - 1, now=now) is False


def test_handler_enqueues_title_after_saving_user_message(rag):
    """通常・聞き返し・該当なしの全経路で、回答を待たずに非同期化する。"""
    src = inspect.getsource(rag.lambda_handler)
    assert src.count("enqueue_session_title(session_id, user_message_id, user_id, query)") == 3
    assert src.count("session_title=session_title") == 0
    assert src.count("'sessionTitle': session_title") == 3
    assert "generate_session_title(query, deadline=request_deadline)" not in src
    assert "event.get('_internalTask') == 'session-title'" in src


def test_enqueue_title_is_async_and_never_raises(rag, monkeypatch):
    calls = {}

    def invoke(**kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(rag, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag, "SESSION_TITLE_MODEL_ID", "model-x")
    monkeypatch.setattr(rag.lambda_client, "invoke", invoke)
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "rag-dev")
    rag.enqueue_session_title("s", "m", "u", "質問")
    assert calls["InvocationType"] == "Event"
    assert json.loads(calls["Payload"].decode("utf-8"))["_internalTask"] == "session-title"


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


def test_async_title_update_succeeds_when_initial_put_omits_it(rag, monkeypatch):
    """初回 put に sessionTitle が無いとき、非同期更新が条件を満たして書く。"""
    items = {}

    class _Table:
        def put_item(self, Item=None):
            items[Item["messageId"]] = dict(Item)

        def update_item(self, **kwargs):
            assert "attribute_not_exists(sessionTitle)" in kwargs["ConditionExpression"]
            message_id = kwargs["Key"]["messageId"]
            item = items[message_id]
            values = kwargs["ExpressionAttributeValues"]
            if item.get("userId") != values[":uid"] or "sessionTitle" in item:
                raise ClientError(
                    {"Error": {"Code": "ConditionalCheckFailedException", "Message": "no"}},
                    "UpdateItem",
                )
            item["sessionTitle"] = values[":title"]

    monkeypatch.setattr(rag, "chatlogs_table", _Table())
    monkeypatch.setattr(rag, "generate_session_title", lambda query: "溶接脚長の判断基準")

    message_id = rag.save_message_to_dynamodb(
        session_id="s1",
        user_id="u1",
        role="user",
        content="溶接の脚長が基準外となる判断基準は？",
    )
    assert "sessionTitle" not in items[message_id]

    result = rag.handle_session_title_task({
        "sessionId": "s1",
        "messageId": message_id,
        "userId": "u1",
        "query": "溶接の脚長が基準外となる判断基準は？",
    })

    assert result == {"ok": True}
    assert items[message_id]["sessionTitle"] == "溶接脚長の判断基準"


def test_async_title_update_skips_when_session_title_already_exists(rag, monkeypatch):
    """先に sessionTitle があると条件が外れ、一覧用の値は上書きしない。"""
    items = {}

    class _Table:
        def update_item(self, **kwargs):
            message_id = kwargs["Key"]["messageId"]
            item = items[message_id]
            values = kwargs["ExpressionAttributeValues"]
            if "sessionTitle" in item:
                raise ClientError(
                    {"Error": {"Code": "ConditionalCheckFailedException", "Message": "no"}},
                    "UpdateItem",
                )
            item["sessionTitle"] = values[":title"]

    items["m1"] = {"userId": "u1", "sessionTitle": "質問の先頭"}
    monkeypatch.setattr(rag, "chatlogs_table", _Table())
    monkeypatch.setattr(rag, "generate_session_title", lambda query: "溶接脚長の判断基準")

    result = rag.handle_session_title_task({
        "sessionId": "s1",
        "messageId": "m1",
        "userId": "u1",
        "query": "溶接の脚長は？",
    })

    assert result == {"ok": True}
    assert items["m1"]["sessionTitle"] == "質問の先頭"
