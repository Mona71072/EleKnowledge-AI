"""generate 用リクエスト本文のモデル世代別組み立て（Sonnet 5 切替の互換対応）。

経緯: docs/eval-2026-09-09-model-bakeoff.md。Sonnet 5 / Opus 4.7 以降は temperature 等の
サンプリング指定を 400 で拒否し、既定で適応思考が動くため、旧モデルと本文を分ける。
"""


def test_legacy_model_keeps_temperature(rag_app):
    body = rag_app.build_generation_request(
        "sys", [{"role": "user", "content": "q"}],
        "jp.anthropic.claude-haiku-4-5-20251001-v1:0")
    assert body["temperature"] == 0.3
    assert "thinking" not in body
    assert body["max_tokens"] == 4096
    assert body["system"] == "sys"
    assert body["anthropic_version"] == "bedrock-2023-05-31"


def test_sonnet5_drops_sampling_and_disables_thinking(rag_app):
    body = rag_app.build_generation_request("sys", [], "global.anthropic.claude-sonnet-5")
    assert "temperature" not in body
    assert body["thinking"] == {"type": "disabled"}


def test_application_profile_arn_needs_explicit_style(rag_app):
    # ARN には元モデル名が含まれないため auto では判定できず legacy 扱いになる。
    arn = "arn:aws:bedrock:ap-northeast-1:123456789012:application-inference-profile/abc"
    assert not rag_app.is_new_api_model(arn, "auto")
    assert rag_app.is_new_api_model(arn, "new")
    assert not rag_app.is_new_api_model("global.anthropic.claude-sonnet-5", "legacy")


def test_new_api_markers(rag_app):
    assert rag_app.is_new_api_model("global.anthropic.claude-opus-4-8", "auto")
    assert rag_app.is_new_api_model("jp.anthropic.claude-opus-4-7", "auto")
    assert rag_app.is_new_api_model("anthropic.claude-fable-5-1", "auto")
    assert not rag_app.is_new_api_model("jp.anthropic.claude-sonnet-4-6", "auto")
    assert not rag_app.is_new_api_model(None, "auto")
