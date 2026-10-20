"""Private, bounded retrieval of the explicitly approved Senpai Markdown index.

The returned cards are navigation-only material. They are never a source of
technical authority, even when their source record says ``approved``.
"""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from datetime import datetime
from typing import Any


MAX_INDEX_BYTES = 8 * 1024 * 1024
MAX_CARD_BODY_CHARS = 16000
MAX_RESPONSE_BODY_CHARS = 16000
MAX_MATCHES = 3
CACHE_TTL_SECONDS = 60
INDEX_KEY_PATTERN = re.compile(r"^[A-Za-z0-9._/-]{1,512}$")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
BODY_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")

SOURCE_TYPES = frozenset({"lists_item", "onenote_page", "kb_document", "law_rag"})
SOURCE_REF_KEYS = frozenset({
    "ref_type", "source_id", "list_item_id", "onenote_id", "document_number",
    "kb_filename", "kb_verify_status", "page_role", "law_id", "law_title",
    "locator",
})
SOURCE_ID_KEYS = {
    "lists_item": "list_item_id",
    "onenote_page": "onenote_id",
    "kb_document": "document_number",
    "law_rag": "law_id",
}
MODEL_SCOPE_KEYS = frozenset({
    "control_methods", "door_families", "door_types", "excludes",
    "guide_systems", "lists_model_label", "machine_room", "may_apply_to",
    "model_abbreviations", "observed_on", "product_lines", "scope_note",
    "conditions",
})

_cache: dict[str, Any] = {"identity": None, "expires": 0.0, "index": None,
                         "version_id": None, "etag": None}


class KnowhowIndexError(ValueError):
    """Index is missing, malformed, or unavailable to the RAG function."""


def _no_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise KnowhowIndexError("duplicate index key")
        result[key] = value
    return result


def parse_index(raw: bytes | str) -> dict:
    """Decode and fully validate an index without accepting duplicate JSON keys."""
    if isinstance(raw, str):
        encoded = raw.encode("utf-8")
    elif isinstance(raw, bytes):
        encoded = raw
    else:
        raise KnowhowIndexError("invalid index bytes")
    if not encoded or len(encoded) > MAX_INDEX_BYTES:
        raise KnowhowIndexError("index size is invalid")
    try:
        decoded = json.loads(encoded.decode("utf-8"), object_pairs_hook=_no_duplicate_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise KnowhowIndexError("index JSON is invalid") from exc
    return validate_index(decoded)


def _safe_text(value: Any, limit: int, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, str)
        and len(value) <= limit
        and (allow_empty or bool(value.strip()))
        and not any(ord(char) < 32 and char not in "\n\r\t" for char in value)
    )


def _validate_source_refs(source_refs: Any) -> None:
    if not isinstance(source_refs, list) or len(source_refs) > 30:
        raise KnowhowIndexError("sourceRefs is invalid")
    for ref in source_refs:
        if not isinstance(ref, dict) or set(ref) - SOURCE_REF_KEYS:
            raise KnowhowIndexError("source reference fields are invalid")
        ref_type = ref.get("ref_type")
        identity_key = SOURCE_ID_KEYS.get(ref_type)
        identity_value = ref.get(identity_key) if identity_key else None
        if ref_type not in SOURCE_TYPES or not _safe_text(identity_value, 200):
            raise KnowhowIndexError("source reference identity is invalid")
        if any(field in ref for field in SOURCE_ID_KEYS.values() if field != identity_key):
            raise KnowhowIndexError("source reference identity type is invalid")
        for key, value in ref.items():
            if not isinstance(value, str) or not _safe_text(value, 500):
                raise KnowhowIndexError("source reference value is invalid")
            if re.search(r"(?i)(https?://|s3://|javascript:|file://|\\|(?:^|/)\.\.(?:/|$))", value):
                raise KnowhowIndexError("source reference must not contain a URL or path")


def _validate_model_scope(model_scope: Any) -> None:
    if not isinstance(model_scope, dict) or set(model_scope) - MODEL_SCOPE_KEYS:
        raise KnowhowIndexError("modelScope fields are invalid")
    for value in model_scope.values():
        values = value if isinstance(value, list) else [value]
        if len(values) > 20:
            raise KnowhowIndexError("modelScope value count is invalid")
        if any(not _safe_text(item, 200) for item in values):
            raise KnowhowIndexError("modelScope value is invalid")


def validate_index(index: Any) -> dict:
    """Validate the complete snapshot; a single malformed card rejects the index."""
    if not isinstance(index, dict) or set(index) != {
        "schemaVersion", "indexVersion", "generatedAt", "cards"
    }:
        raise KnowhowIndexError("index fields are invalid")
    if type(index.get("schemaVersion")) is not int or index["schemaVersion"] != 1:
        raise KnowhowIndexError("index schema version is invalid")
    if not isinstance(index.get("indexVersion"), str) or not SHA256_PATTERN.fullmatch(index["indexVersion"]):
        raise KnowhowIndexError("index version is invalid")
    generated_at = index.get("generatedAt")
    if not _safe_text(generated_at, 40):
        raise KnowhowIndexError("generatedAt is invalid")
    try:
        datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise KnowhowIndexError("generatedAt is invalid") from exc
    cards = index.get("cards")
    if not isinstance(cards, list) or len(cards) > 5000:
        raise KnowhowIndexError("cards is invalid")
    seen_ids = set()
    total_chars = 0
    for card in cards:
        if not isinstance(card, dict) or set(card) != {
            "knowledgeId", "cardVersion", "sha256", "title", "status", "usage",
            "body", "searchTerms", "sourceRefs", "modelScope",
        }:
            raise KnowhowIndexError("card fields are invalid")
        knowledge_id = card.get("knowledgeId")
        version = card.get("cardVersion")
        body = card.get("body")
        if not isinstance(knowledge_id, str) or not ID_PATTERN.fullmatch(knowledge_id):
            raise KnowhowIndexError("knowledgeId is invalid")
        if knowledge_id in seen_ids:
            raise KnowhowIndexError("knowledgeId is duplicated")
        seen_ids.add(knowledge_id)
        if type(version) is not int or version < 1:
            raise KnowhowIndexError("cardVersion is invalid")
        if not _safe_text(card.get("title"), 400):
            raise KnowhowIndexError("title is invalid")
        if card.get("status") not in ("draft", "approved"):
            raise KnowhowIndexError("status is invalid")
        if card.get("usage") != "navigation_only":
            raise KnowhowIndexError("usage is invalid")
        if not _safe_text(body, MAX_CARD_BODY_CHARS):
            raise KnowhowIndexError("body is invalid")
        body_hash = card.get("sha256")
        if not isinstance(body_hash, str) or not BODY_HASH_PATTERN.fullmatch(body_hash):
            raise KnowhowIndexError("card hash is invalid")
        terms = card.get("searchTerms")
        if not isinstance(terms, list) or len(terms) > 100 or any(
            not _safe_text(term, 200) for term in terms
        ):
            raise KnowhowIndexError("searchTerms are invalid")
        _validate_source_refs(card.get("sourceRefs"))
        _validate_model_scope(card.get("modelScope"))
        total_chars += len(body)
        if total_chars > MAX_INDEX_BYTES:
            raise KnowhowIndexError("index text size is invalid")
    return index


def clear_cache() -> None:
    """Clear process-local cache; exposed for deterministic unit tests."""
    _cache.update(identity=None, expires=0.0, index=None, version_id=None, etag=None)


def load_index(s3_client=None, *, bucket: str | None = None, key: str | None = None,
               now: float | None = None) -> dict:
    """Load one configured private S3 object, validating and caching it for at most 60s."""
    bucket = bucket if bucket is not None else os.environ.get("KNOWHOW_INDEX_BUCKET", "").strip()
    key = key if key is not None else os.environ.get("KNOWHOW_INDEX_KEY", "").strip()
    if not bucket or not key or len(bucket) > 255 or not INDEX_KEY_PATTERN.fullmatch(key):
        raise KnowhowIndexError("index source is not configured")
    identity = (bucket, key)
    current = time.monotonic() if now is None else now
    if _cache["identity"] == identity and current < _cache["expires"] and _cache["index"]:
        return _cache["index"]
    if s3_client is None:
        import boto3
        s3_client = boto3.client("s3")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        body_stream = response.get("Body")
        raw = body_stream.read(MAX_INDEX_BYTES + 1) if body_stream else b""
        if not raw or len(raw) > MAX_INDEX_BYTES:
            raise KnowhowIndexError("index size is invalid")
        index = parse_index(raw)
        _cache.update(
            identity=identity,
            expires=current + CACHE_TTL_SECONDS,
            index=index,
            version_id=response.get("VersionId"),
            etag=response.get("ETag"),
        )
        return index
    except KnowhowIndexError:
        clear_cache()
        raise
    except Exception as exc:  # S3 errors must not disclose storage details to clients.
        clear_cache()
        raise KnowhowIndexError("index is unavailable") from exc


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()


def _query_features(query: str) -> tuple[set[str], set[str]]:
    normalized = _normalize(query)
    words = set(re.findall(r"[a-z0-9][a-z0-9._:-]{1,63}", normalized))
    cjk_runs = re.findall(r"[\u3040-\u30ff\u3400-\u9fffー]+", normalized)
    grams = set()
    for run in cjk_runs:
        if len(run) < 2:
            continue
        for size in (2, 3):
            grams.update(run[index:index + size] for index in range(len(run) - size + 1))
    return grams, words


def _feature_text(value: str) -> tuple[set[str], set[str]]:
    return _query_features(value)


def _score_card(card: dict, query_grams: set[str], query_words: set[str]) -> float:
    text = " ".join([
        card["title"], " ".join(card["searchTerms"]),
        " ".join(str(value) for values in card["modelScope"].values()
                 for value in (values if isinstance(values, list) else [values])),
        card["body"],
    ])
    doc_grams, doc_words = _feature_text(text)
    if not query_grams and not query_words:
        return 0.0
    # Weighted feature coverage favors exact technical terms and titles; full-body
    # matching helps discovery but cannot make a one-character query meaningful.
    title_grams, title_words = _feature_text(card["title"])
    term_grams, term_words = _feature_text(" ".join(card["searchTerms"]))
    scope_values = " ".join(str(value) for values in card["modelScope"].values()
                             for value in (values if isinstance(values, list) else [values]))
    scope_grams, scope_words = _feature_text(scope_values)
    weighted_total = len(query_grams) + 2 * len(query_words)
    matched = (
        len(query_grams & doc_grams)
        + 2 * len(query_words & doc_words)
        + 2 * len(query_grams & title_grams)
        + 3 * len(query_words & title_words)
        + 2 * len(query_grams & term_grams)
        + 3 * len(query_words & term_words)
        + len(query_grams & scope_grams)
        + 2 * len(query_words & scope_words)
    )
    return matched / max(weighted_total, 1)


def search_index(index: dict, query: str) -> dict:
    """Return up to three whole relevant cards under one combined body-size budget."""
    index = validate_index(index)
    if not isinstance(query, str) or len(query) > 4000:
        raise KnowhowIndexError("query is invalid")
    query_grams, query_words = _query_features(query)
    if not query_grams and not query_words:
        return {"status": "not_found", "indexVersion": index["indexVersion"], "matches": []}
    ranked = sorted(
        ((_score_card(card, query_grams, query_words), card) for card in index["cards"]),
        key=lambda item: (-item[0], item[1]["knowledgeId"]),
    )
    matches = []
    total_body_chars = 0
    for score, card in ranked:
        if score < 0.16 or len(matches) >= MAX_MATCHES:
            break
        if total_body_chars + len(card["body"]) > MAX_RESPONSE_BODY_CHARS:
            continue
        matches.append(card)
        total_body_chars += len(card["body"])
    return {
        "status": "matched" if matches else "not_found",
        "indexVersion": index["indexVersion"],
        "matches": matches,
    }


def derive_kb_hints(matches: list[dict], *, max_hints: int = 8) -> list[str]:
    """Extract only typed KB document numbers / filenames as query hints."""
    hints = []
    seen = set()
    for card in matches:
        for ref in card.get("sourceRefs", []):
            if ref.get("ref_type") != "kb_document":
                continue
            for key in ("document_number", "kb_filename"):
                value = ref.get(key, "").strip()
                if (not value or len(value) > 100 or "/" in value or "\\" in value
                        or re.search(r"(?i)(https?://|s3://|\.\.)", value)):
                    continue
                normalized = _normalize(value)
                if normalized not in seen:
                    seen.add(normalized)
                    hints.append(value)
                    if len(hints) >= max_hints:
                        return hints
    return hints
