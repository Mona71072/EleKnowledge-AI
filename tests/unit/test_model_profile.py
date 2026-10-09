"""Model capability profiles and safe JSON overrides."""

import json
import os

import pytest


def _load_profile(load_rag_module, monkeypatch, *, model_profile_json=""):
    monkeypatch.setenv("MODEL_PROFILE_JSON", model_profile_json)
    return load_rag_module(
        "model_profile_test_" + str(abs(hash((model_profile_json, os.environ.get("BEDROCK_REQUEST_STYLE", "auto"))))),
        "model_profile.py",
    )


def test_known_model_capabilities_and_longest_name_match(load_rag_module, monkeypatch):
    profiles = _load_profile(load_rag_module, monkeypatch)

    assert profiles.get_model_profile("global.anthropic.claude-sonnet-5-5") == profiles.ModelProfile(
        sampling=False, thinking_disable=False, adaptive=True, effort=True
    )
    assert profiles.get_model_profile("global.anthropic.claude-sonnet-5") == profiles.ModelProfile(
        sampling=False, thinking_disable=True, adaptive=True, effort=True
    )
    assert profiles.get_model_profile("anthropic.claude-opus-5-5") == profiles.ModelProfile(
        sampling=False, thinking_disable=False, adaptive=True, effort=True
    )
    assert profiles.get_model_profile("anthropic.claude-fable-5-1") == profiles.ModelProfile(
        sampling=False, thinking_disable=False, adaptive=True, effort=True
    )
    assert profiles.get_model_profile("anthropic.claude-opus-5") == profiles.ModelProfile(
        sampling=False, thinking_disable=True, adaptive=True, effort=True
    )
    for name in ("opus-4-7", "opus-4-8"):
        assert profiles.get_model_profile(f"jp.anthropic.claude-{name}") == profiles.ModelProfile(
            sampling=False, thinking_disable=True, adaptive=True, effort=True
        )
    assert profiles.get_model_profile("jp.anthropic.claude-haiku-4-5") == profiles.ModelProfile(
        sampling=True, thinking_disable=False, adaptive=False, effort=False
    )
    assert profiles.get_model_profile("anthropic.claude-sonnet-4-6") == profiles.ModelProfile(
        sampling=True, thinking_disable=False, adaptive=False, effort=False
    )
    assert profiles.get_model_profile(
        "anthropic.claude-sonnet-4-20250514-v1:0"
    ).sampling
    assert profiles.get_model_profile(
        "anthropic.claude-opus-4-6-20250514-v1:0"
    ).sampling
    for name in (
        "claude-3-haiku-20240307-v1:0",
        "claude-3-5-haiku-20241022-v1:0",
        "claude-3-opus-20240229-v1:0",
        "claude-3-5-sonnet-20241022-v2:0",
        "claude-3-7-sonnet-20250219-v1:0",
    ):
        assert profiles.get_model_profile(f"anthropic.{name}").sampling


def test_profile_strips_inference_prefix_and_version_suffix(load_rag_module, monkeypatch):
    profiles = _load_profile(load_rag_module, monkeypatch)

    assert profiles.get_model_profile(
        "apac.anthropic.claude-haiku-4-5-20251001-v1:0"
    ).sampling
    assert profiles.get_model_profile(
        "global.anthropic.claude-sonnet-5-5-20260901-v1:0"
    ).thinking_disable is False


def test_unknown_model_uses_minimal_capabilities_and_logs_only_model_id(
    load_rag_module, monkeypatch, capsys
):
    profiles = _load_profile(load_rag_module, monkeypatch)
    model_id = "global.anthropic.claude-future-6-0"

    assert profiles.get_model_profile(model_id) == profiles.ModelProfile(False, False, False, False)
    assert profiles.get_model_profile(model_id) == profiles.ModelProfile(False, False, False, False)
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event"] == "unknown_model_profile"
    assert event["model_id"] == model_id
    assert set(event) == {"event", "model_id"}


def test_json_override_adds_and_overrides_capabilities(load_rag_module, monkeypatch):
    profiles = _load_profile(
        load_rag_module,
        monkeypatch,
        model_profile_json=json.dumps(
            {
                "sonnet-5-5": {"thinking_disable": True},
                "future-6-0": {
                    "sampling": True,
                    "thinking_disable": False,
                    "adaptive": True,
                    "effort": True,
                },
            }
        ),
    )

    assert profiles.get_model_profile("global.anthropic.claude-sonnet-5-5").thinking_disable
    assert profiles.get_model_profile("global.anthropic.claude-future-6-0") == profiles.ModelProfile(
        True, False, True, True
    )


def test_application_profile_arn_can_be_overridden_by_exact_arn(load_rag_module, monkeypatch):
    arn = "arn:aws:bedrock:ap-northeast-1:123456789012:application-inference-profile/sonnet5"
    profiles = _load_profile(
        load_rag_module,
        monkeypatch,
        model_profile_json=json.dumps(
            {arn: {"sampling": False, "thinking_disable": True, "adaptive": True, "effort": True}}
        ),
    )

    assert profiles.get_model_profile(arn).thinking_disable


@pytest.mark.parametrize("invalid_json", [
    "{",
    '{"sonnet-5-5":{"effort":true,"unknown":false}}',
    '{"sonnet-5-5":{"effort":"high"}}',
])
def test_invalid_profile_json_is_ignored_safely(
    load_rag_module, monkeypatch, capsys, invalid_json
):
    profiles = _load_profile(
        load_rag_module, monkeypatch, model_profile_json=invalid_json
    )

    assert profiles.get_model_profile("global.anthropic.claude-sonnet-5-5") == profiles.ModelProfile(
        sampling=False, thinking_disable=False, adaptive=True, effort=True
    )
    assert '"event":"invalid_model_profile_json"' in capsys.readouterr().out


@pytest.mark.parametrize(("request_style", "expected"), [
    ("auto", (False, False, False, False)),
    ("new", (False, False, False, False)),
    ("legacy", (True, False, False, False)),
])
def test_request_style_only_changes_unknown_model_fallback(
    load_rag_module, monkeypatch, request_style, expected
):
    monkeypatch.setenv("BEDROCK_REQUEST_STYLE", request_style)
    profiles = _load_profile(load_rag_module, monkeypatch)

    assert profiles.get_model_profile("unknown-6-0") == profiles.ModelProfile(*expected)
    assert profiles.get_model_profile("global.anthropic.claude-haiku-4-5").sampling is True


def test_request_style_does_not_override_model_profile_json(
    load_rag_module, monkeypatch
):
    monkeypatch.setenv("BEDROCK_REQUEST_STYLE", "legacy")
    profiles = _load_profile(
        load_rag_module,
        monkeypatch,
        model_profile_json='{"unknown-6-0":{"sampling":false,"thinking_disable":false,"adaptive":true,"effort":true}}',
    )

    assert profiles.get_model_profile("unknown-6-0") == profiles.ModelProfile(
        sampling=False, thinking_disable=False, adaptive=True, effort=True
    )
