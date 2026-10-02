"""Knowledge Base-specific metadata and retrieval settings."""

from dataclasses import dataclass, fields
import json
import os


@dataclass(frozen=True)
class KbProfile:
    """The metadata contract needed to retrieve and interpret KB chunks."""

    source_uri_key: str = "x-amz-bedrock-kb-source-uri"
    chunk_id_key: str = "x-amz-bedrock-kb-chunk-id"
    page_number_keys: tuple[str, ...] = (
        "x-amz-bedrock-kb-document-page-number",
        "x-amz-bedrock-kb-page-number",
    )
    model_type_key: str = "model_type"
    category_key: str = "category"
    model_type_filter_operator: str = "listContains"
    search_type: str = "HYBRID"

    def __post_init__(self):
        if self.model_type_filter_operator not in {'listContains', 'equals', 'in'}:
            raise ValueError(
                "KB profile model_type_filter_operator must be listContains, equals, or in"
            )


_PROFILE_FIELDS = frozenset(field.name for field in fields(KbProfile))
_STRING_FIELDS = frozenset(
    {
        "source_uri_key",
        "chunk_id_key",
        "model_type_key",
        "category_key",
        "model_type_filter_operator",
    }
)
_MODEL_TYPE_FILTER_OPERATORS = frozenset({'listContains', 'equals', 'in'})


def _validate_override(overrides: dict) -> dict:
    unknown = set(overrides) - _PROFILE_FIELDS
    if unknown:
        raise ValueError(f"Unknown KB profile keys: {sorted(unknown)}")

    validated = {}
    for key, value in overrides.items():
        if key == "model_type_filter_operator":
            if value not in _MODEL_TYPE_FILTER_OPERATORS:
                raise ValueError(
                    "KB profile model_type_filter_operator must be listContains, equals, or in"
                )
            validated[key] = value
            continue
        if key in _STRING_FIELDS:
            if not isinstance(value, str) or not value:
                raise TypeError(f"KB profile field {key} must be a non-empty string")
            validated[key] = value
        elif key == "page_number_keys":
            if (
                not isinstance(value, list)
                or not value
                or any(not isinstance(item, str) or not item for item in value)
            ):
                raise TypeError("KB profile field page_number_keys must be a non-empty string array")
            validated[key] = tuple(value)
        elif key == "search_type":
            if value not in ("HYBRID", "SEMANTIC"):
                raise ValueError("KB profile search_type must be HYBRID or SEMANTIC")
            validated[key] = value
    return validated


def load_kb_profile() -> KbProfile:
    """Load the immutable KB profile, optionally applying strict JSON overrides."""

    profile = KbProfile(search_type=os.environ.get("RAG_SEARCH_TYPE", "HYBRID"))
    if profile.search_type not in ("HYBRID", "SEMANTIC"):
        profile = KbProfile()

    raw = os.environ.get("KB_PROFILE_JSON", "")
    if not raw:
        return profile

    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("KB_PROFILE_JSON must be valid JSON") from exc
    if not isinstance(decoded, dict):
        raise TypeError("KB_PROFILE_JSON must be a JSON object")

    overrides = _validate_override(decoded)
    overridden_key_names = [
        key for key in ("model_type_key", "category_key") if key in overrides
    ]
    if overridden_key_names:
        print(
            "[rag] kb_profile warning overridden_keys="
            + ",".join(overridden_key_names)
        )
    return KbProfile(**{**profile.__dict__, **overrides})
