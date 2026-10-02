"""Bedrock Converse 形式への変換と API 選択を検証する。"""

import base64
import json


class _Body:
    def __init__(self, value):
        self.value = value

    def read(self):
        return json.dumps(self.value).encode("utf-8")


def test_converse_request_converts_text_images_and_system(rag_app):
    messages, system = rag_app.build_converse_messages(
        [
            {"role": "user", "content": "説明して"},
            {"role": "assistant", "content": [{"type": "text", "text": "了解"}]},
            {"role": "user", "content": [
                {"type": "text", "text": "図を確認"},
                {"type": "image", "source": {
                    "type": "base64", "media_type": "image/jpeg",
                    "data": base64.b64encode(b"img").decode("ascii"),
                }},
            ]},
        ],
        "system instruction",
        supports_images=True,
    )
    assert system == [{"text": "system instruction"}]
    assert messages == [
        {"role": "user", "content": [{"text": "説明して"}]},
        {"role": "assistant", "content": [{"text": "了解"}]},
        {"role": "user", "content": [
            {"text": "図を確認"},
            {"image": {"format": "jpeg", "source": {"bytes": b"img"}}},
        ]},
    ]


def test_converse_response_excludes_reasoning_and_returns_usage(rag_app, monkeypatch):
    class Client:
        def converse(self, **kwargs):
            self.kwargs = kwargs
            return {
                "output": {"message": {"content": [
                    {"reasoningContent": {"reasoningText": {"text": "hidden"}}},
                    {"text": "回答"},
                ]}},
                "usage": {
                    "inputTokens": 10,
                    "outputTokens": 5,
                    "cacheReadInputTokens": 120,
                    "cacheWriteInputTokens": 30,
                },
                "stopReason": "end_turn",
            }

    client = Client()
    text, usage, stop_reason = rag_app.invoke_generation(
        client, "global.openai.gpt-6-luna", "sys",
        [{"role": "user", "content": "q"}], 80,
    )
    assert text == "回答"
    assert usage == {
        "inputTokens": 10,
        "outputTokens": 5,
        "cacheReadInputTokens": 120,
        "cacheWriteInputTokens": 30,
    }
    assert stop_reason == "end_turn"
    assert client.kwargs["inferenceConfig"] == {"maxTokens": 80}
    assert client.kwargs["system"] == [{"text": "sys"}]
    assert "additionalModelRequestFields" not in client.kwargs


def test_invoke_generation_preserves_anthropic_body_exactly(rag_app):
    class Client:
        def invoke_model(self, **kwargs):
            self.kwargs = kwargs
            return {"body": _Body({"content": [{"type": "text", "text": "ok"}],
                                   "usage": {"input_tokens": 2, "output_tokens": 3},
                                   "stop_reason": "end_turn"})}

    client = Client()
    messages = [{"role": "user", "content": "q"}]
    text, usage, stop_reason = rag_app.invoke_generation(
        client, "global.anthropic.claude-sonnet-5", "sys", messages, 42,
    )
    assert text == "ok"
    assert usage == {"inputTokens": 2, "outputTokens": 3}
    assert stop_reason == "end_turn"
    assert json.loads(client.kwargs["body"]) == rag_app.build_generation_request(
        "sys", messages, "global.anthropic.claude-sonnet-5", max_tokens=42,
    )


def test_max_tokens_is_logged_for_converse_without_changing_text(rag_app, capsys):
    class Client:
        def converse(self, **kwargs):
            return {
                "output": {"message": {"content": [{"text": "途中までの回答"}]}},
                "usage": {"inputTokens": 12, "outputTokens": 80},
                "stopReason": "max_tokens",
            }

    text, usage, stop_reason = rag_app.invoke_generation(
        Client(), "global.openai.gpt-6-luna", "sys",
        [{"role": "user", "content": "秘密の質問"}], 80,
    )
    assert text == "途中までの回答"
    assert usage == {
        "inputTokens": 12,
        "outputTokens": 80,
        "cacheReadInputTokens": 0,
        "cacheWriteInputTokens": 0,
    }
    assert stop_reason == "max_tokens"
    event = json.loads(capsys.readouterr().out.strip())
    assert event == {
        "event": "generation_truncated", "api": "converse", "call": "answer",
    }


def test_max_tokens_is_logged_for_invoke_without_changing_text(rag_app, capsys):
    class Client:
        def invoke_model(self, **kwargs):
            return {"body": _Body({
                "content": [{"type": "text", "text": "途中までの回答"}],
                "usage": {"input_tokens": 12, "output_tokens": 80},
                "stop_reason": "max_tokens",
            })}

    text, usage, stop_reason = rag_app.invoke_generation(
        Client(), "global.anthropic.claude-sonnet-5", "sys",
        [{"role": "user", "content": "秘密の質問"}], 80,
    )
    assert text == "途中までの回答"
    assert usage == {"inputTokens": 12, "outputTokens": 80}
    assert stop_reason == "max_tokens"
    event = json.loads(capsys.readouterr().out.strip())
    assert event == {
        "event": "generation_truncated", "api": "invoke", "call": "answer",
    }


def test_unsupported_images_are_omitted_with_structured_log(rag_app, capsys):
    messages, _ = rag_app.build_converse_messages(
        [{"role": "user", "content": [
            {"type": "text", "text": "caption"},
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "aQ=="}},
        ]}], None, supports_images=False,
    )
    assert messages == [{"role": "user", "content": [{"text": "caption"}]}]
    event = json.loads(capsys.readouterr().out.strip())
    assert event["event"] == "model_image_input_omitted"
    assert "caption" not in json.dumps(event)


def test_title_generation_uses_converse_profile(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "SESSION_TITLE_LLM_ENABLED", True)
    monkeypatch.setattr(rag_app, "SESSION_TITLE_MODEL_ID", "global.openai.gpt-6-luna")

    class Client:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "見出し"}]}}}

    monkeypatch.setattr(rag_app, "bedrock_runtime_title", Client())
    assert rag_app.generate_session_title("質問") == "見出し"


def test_main_response_generation_uses_converse_profile(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "BEDROCK_MODEL_ID", "global.openai.gpt-6-luna")
    monkeypatch.setattr(rag_app, "select_retrieval_results", lambda *args, **kwargs: [])
    monkeypatch.setattr(rag_app, "build_claude_messages", lambda *args, **kwargs: [
        {"role": "user", "content": "q"},
    ])

    class Client:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "本文"}]}}}

    monkeypatch.setattr(rag_app, "bedrock_runtime", Client())
    assert rag_app.generate_response_with_claude(
        "質問", {"retrievalResults": []}, search_query="質問",
    ) == "本文"


def test_query_rewrite_uses_converse_profile(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "QUERY_REWRITE_MODEL_ID", "global.openai.gpt-6-luna")

    class Client:
        def converse(self, **kwargs):
            return {"output": {"message": {"content": [{"text": "書き換え後"}]}}}

    monkeypatch.setattr(rag_app, "_get_query_rewrite_client", lambda: Client())
    assert rag_app.maybe_rewrite_search_query(
        "元の質問", [{"role": "user", "content": "前の質問"}],
    ) == "書き換え後"
