"""Bedrock InvokeModel payloads follow per-model capabilities."""


def _request(rag_app, model_id, *, apply_generation_settings=True):
    return rag_app.build_generation_request(
        "sys", [{"role": "user", "content": "q"}], model_id,
        apply_generation_settings=apply_generation_settings,
    )


def test_legacy_model_keeps_temperature(rag_app):
    body = rag_app.build_generation_request(
        "sys", [{"role": "user", "content": "q"}],
        "jp.anthropic.claude-haiku-4-5-20251001-v1:0")
    assert body["temperature"] == 0.3
    assert "thinking" not in body and "output_config" not in body
    assert body["max_tokens"] == 4096
    assert body["system"] == "sys"
    assert body["anthropic_version"] == "bedrock-2023-05-31"


def test_sonnet5_disabled_thinking(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "GENERATION_THINKING", "disabled")
    body = _request(rag_app, "global.anthropic.claude-sonnet-5")
    assert "temperature" not in body
    assert body["thinking"] == {"type": "disabled"}
    assert "output_config" not in body


def test_sonnet55_defaults_to_effort_low_without_disabling_thinking(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "GENERATION_THINKING", "disabled")
    body = _request(rag_app, "global.anthropic.claude-sonnet-5-5")
    assert "temperature" not in body
    assert "thinking" not in body
    assert body["output_config"] == {"effort": "low"}


def test_opus55_and_fable51_follow_always_adaptive_rules(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "GENERATION_THINKING", "disabled")
    for model_id in (
        "global.anthropic.claude-opus-5-5",
        "global.anthropic.claude-fable-5-1",
    ):
        body = _request(rag_app, model_id)
        assert "temperature" not in body
        assert "thinking" not in body
        assert body["output_config"] == {"effort": "low"}


def test_adaptive_mode_sends_adaptive_and_effort_only_when_supported(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "GENERATION_THINKING", "adaptive")
    monkeypatch.setattr(rag_app, "GENERATION_EFFORT", "medium")

    for model_id in (
        "global.anthropic.claude-sonnet-5",
        "global.anthropic.claude-sonnet-5-5",
        "global.anthropic.claude-opus-5-5",
        "global.anthropic.claude-fable-5-1",
        "global.anthropic.claude-opus-5",
        "global.anthropic.claude-opus-4-7",
        "global.anthropic.claude-opus-4-8",
    ):
        body = _request(rag_app, model_id)
        assert body["thinking"] == {"type": "adaptive"}
        assert body["output_config"] == {"effort": "medium"}
        assert "temperature" not in body

    legacy = _request(rag_app, "jp.anthropic.claude-haiku-4-5")
    assert "thinking" not in legacy and "output_config" not in legacy
    assert legacy["temperature"] == 0.3


def test_title_and_query_rewrite_use_safe_disabled_mode(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "GENERATION_THINKING", "adaptive")
    monkeypatch.setattr(rag_app, "GENERATION_EFFORT", "high")

    for model_id in (
        "global.anthropic.claude-sonnet-5-5",
        "global.anthropic.claude-opus-5-5",
        "global.anthropic.claude-fable-5-1",
    ):
        body = _request(rag_app, model_id, apply_generation_settings=False)
        assert "thinking" not in body
        assert body["output_config"] == {"effort": "low"}
        assert "temperature" not in body

    disable_capable = _request(
        rag_app, "global.anthropic.claude-sonnet-5", apply_generation_settings=False
    )
    assert disable_capable["thinking"] == {"type": "disabled"}
    assert "output_config" not in disable_capable


def test_unknown_model_uses_minimal_request(rag_app, capsys):
    body = _request(rag_app, "global.anthropic.claude-future-6-0")
    assert "temperature" not in body
    assert "thinking" not in body and "output_config" not in body
    events = capsys.readouterr().out
    assert '"event":"unknown_model_profile"' in events
    assert "claude-future-6-0" in events


def test_title_generation_can_override_budget(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "GENERATION_THINKING", "adaptive")
    body = rag_app.build_generation_request(
        None, [], "global.anthropic.claude-sonnet-5", max_tokens=64,
        temperature=0, apply_generation_settings=False,
    )
    assert body["max_tokens"] == 64
    assert body["thinking"] == {"type": "disabled"}
    assert "system" not in body

    legacy = rag_app.build_generation_request(
        None, [], "jp.anthropic.claude-haiku-4-5-20251001-v1:0",
        max_tokens=64, temperature=0,
    )
    assert legacy["temperature"] == 0 and legacy["max_tokens"] == 64


def test_extract_response_text_skips_thinking_block(rag_app):
    body = {"content": [{"type": "thinking", "thinking": "reason"}, {"type": "text", "text": "回答"}]}
    assert rag_app.extract_response_text(body) == "回答"
    assert rag_app.extract_response_text({"content": []}) == ""
    assert rag_app.extract_response_text({"content": [{"type": "thinking", "thinking": "only"}]}) == ""
