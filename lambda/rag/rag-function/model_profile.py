"""Bedrock 対応モデルの生成 API と能力プロファイル。"""

from dataclasses import dataclass, fields
import json
import os
import re


@dataclass(frozen=True)
class ModelProfile:
    """モデルが受け付ける生成 API とリクエスト設定。"""

    sampling: bool
    thinking_disable: bool
    adaptive: bool
    effort: bool
    api: str = "invoke"
    image_input: bool = False


_PROFILE_FIELDS = frozenset(field.name for field in fields(ModelProfile))
_SAFE_MINIMAL_PROFILE = ModelProfile(False, False, False, False)
_LEGACY_UNKNOWN_PROFILE = ModelProfile(True, False, False, False)
_REQUEST_STYLE = os.environ.get("BEDROCK_REQUEST_STYLE", "auto").strip().lower()
if _REQUEST_STYLE not in {"auto", "new", "legacy"}:
    print(json.dumps({"event": "invalid_bedrock_request_style"}, separators=(",", ":")))
    _REQUEST_STYLE = "auto"

# Keys are normalized model names. Prefix matches ending in '-' cover a model
# family such as Sonnet 4.x. Matching always checks longer keys first.
MODEL_PROFILES = {
    "gpt-6-luna": ModelProfile(False, False, False, False, "converse", True),
    "sonnet-5-5": ModelProfile(False, False, True, True),
    "opus-5-5": ModelProfile(False, False, True, True),
    "fable-5-1": ModelProfile(False, False, True, True),
    "sonnet-5": ModelProfile(False, True, True, True),
    "opus-5": ModelProfile(False, True, True, True),
    "opus-4-7": ModelProfile(False, True, True, True),
    "opus-4-8": ModelProfile(False, True, True, True),
    "haiku-4-5": ModelProfile(True, False, False, False),
    "haiku-3-": ModelProfile(True, False, False, False),
    "sonnet-3-": ModelProfile(True, False, False, False),
    "opus-3-": ModelProfile(True, False, False, False),
    "opus-4-": ModelProfile(True, False, False, False),
    "3-5-haiku": ModelProfile(True, False, False, False),
    "3-haiku": ModelProfile(True, False, False, False),
    "3-7-sonnet": ModelProfile(True, False, False, False),
    "3-5-sonnet": ModelProfile(True, False, False, False),
    "3-sonnet": ModelProfile(True, False, False, False),
    "3-opus": ModelProfile(True, False, False, False),
    "sonnet-4": ModelProfile(True, False, False, False),
    "sonnet-4-": ModelProfile(True, False, False, False),
}


def _normalize_model_name(model_id: str) -> str:
    """Remove inference-profile prefixes, provider namespace, and dated suffix."""
    value = (model_id or "").strip().lower()
    if not value:
        return ""
    if value.startswith("arn:"):
        # Application inference profile ARNs do not expose the model name.
        # Keep an exact key available for MODEL_PROFILE_JSON overrides.
        return value

    # System inference profile IDs are of the form global.anthropic.claude-...
    parts = value.split(".")
    if parts and parts[0] in {"global", "jp", "us", "apac", "eu", "au", "ca", "in"}:
        parts = parts[1:]
    if parts and parts[0] in {"anthropic", "openai"}:
        parts = parts[1:]
    name = ".".join(parts)
    if name.startswith("claude-"):
        name = name[len("claude-"):]
    name = re.sub(r"-\d{8}-v\d+:\d+$", "", name)
    return name


def _load_overrides() -> dict[str, ModelProfile]:
    raw = os.environ.get("MODEL_PROFILE_JSON", "").strip()
    if not raw:
        return {}

    try:
        decoded = json.loads(raw)
        if not isinstance(decoded, dict):
            raise TypeError("root must be an object")
        overrides = {}
        for name, values in decoded.items():
            normalized_name = _normalize_model_name(name)
            if not normalized_name or not isinstance(values, dict):
                raise TypeError("each model profile must be an object")
            unknown = set(values) - _PROFILE_FIELDS
            if unknown:
                raise TypeError("profile capabilities have invalid values")
            api = values.get("api", "invoke")
            if type(api) is not str or api not in ("invoke", "converse"):
                print(json.dumps(
                    {"event": "invalid_model_profile_api"},
                    separators=(",", ":"),
                ))
                values = {**values, "api": "invoke"}
            invalid_capability = any(
                key != "api" and type(value) is not bool
                for key, value in values.items()
            )
            if invalid_capability:
                raise TypeError("profile capabilities have invalid values")
            base = _profile_for_normalized_name(normalized_name) or _SAFE_MINIMAL_PROFILE
            overrides[normalized_name] = ModelProfile(
                **{**base.__dict__, **values}
            )
        return overrides
    except (json.JSONDecodeError, TypeError, ValueError):
        print(json.dumps({"event": "invalid_model_profile_json"}, separators=(",", ":")))
        return {}


def _profile_for_normalized_name(name: str) -> ModelProfile | None:
    for model_name in sorted(MODEL_PROFILES, key=len, reverse=True):
        if name == model_name or (model_name.endswith("-") and name.startswith(model_name)):
            return MODEL_PROFILES[model_name]
    return None


def _log_unknown_model(model_id: str) -> None:
    if model_id and model_id not in _logged_unknown_models:
        _logged_unknown_models.add(model_id)
        print(json.dumps(
            {"event": "unknown_model_profile", "model_id": model_id},
            separators=(",", ":"),
        ))


_OVERRIDES = _load_overrides()
_logged_unknown_models: set[str] = set()


def get_model_profile(model_id: str) -> ModelProfile:
    """Return known capabilities or the configured fallback for unknown models."""
    normalized_name = _normalize_model_name(model_id)
    if normalized_name in _OVERRIDES:
        return _OVERRIDES[normalized_name]
    profile = _profile_for_normalized_name(normalized_name)
    if profile is None:
        _log_unknown_model(model_id)
        return _LEGACY_UNKNOWN_PROFILE if _REQUEST_STYLE == "legacy" else _SAFE_MINIMAL_PROFILE
    return profile


def log_unknown_model_once(model_id: str) -> None:
    """Emit the startup warning for an unrecognized configured model ID."""
    if _normalize_model_name(model_id) not in _OVERRIDES:
        profile = _profile_for_normalized_name(_normalize_model_name(model_id))
        if profile is None:
            _log_unknown_model(model_id)
