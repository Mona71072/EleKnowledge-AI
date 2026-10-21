"""Private, bounded retrieval of the explicitly approved Senpai Markdown index.

The returned cards are navigation-only material. They are never a source of
technical authority, even when their source record says ``approved``.
"""
from __future__ import annotations

import json
import hashlib
import math
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
# SYNC: must equal SOURCE_REF_KEYS in build-senpai-index.mjs and KNOWHOW_SOURCE_FIELDS in knowledge-research.mjs (tests/unit/test_knowhow_contract_sync.py).
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
# SYNC: must equal MODEL_SCOPE_KEYS in build-senpai-index.mjs and KNOWHOW_SCOPE_FIELDS in knowledge-research.mjs (tests/unit/test_knowhow_contract_sync.py).
MODEL_SCOPE_KEYS = frozenset({
    "control_methods", "door_families", "door_types", "excludes",
    "guide_systems", "lists_model_label", "machine_room", "may_apply_to",
    "model_abbreviations", "observed_on", "product_lines", "scope_note",
    "conditions", "scope_status", "scope_verified_by", "scope_verified_at",
})
# SYNC: must equal SCOPE_VERIFICATION_KEYS in build-senpai-index.mjs (tests/unit/test_knowhow_contract_sync.py).
SCOPE_VERIFICATION_KEYS = frozenset({"scope_status", "scope_verified_by", "scope_verified_at"})
SCOPE_STATUSES = frozenset({"verified", "unverified"})
SCOPE_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Only fields stating where a card DOES apply may influence ranking; excludes,
# may_apply_to and scope_note describe exclusions or unconfirmed scope.
# SYNC: must equal POSITIVE_SCOPE_KEYS in build-senpai-index.mjs (tests/unit/test_knowhow_contract_sync.py).
POSITIVE_SCOPE_KEYS = (
    "control_methods", "door_families", "door_types", "guide_systems",
    "lists_model_label", "machine_room", "model_abbreviations", "observed_on",
    "product_lines", "conditions",
)
MODEL_CLASSIFY_KEYS = ("product_lines", "model_abbreviations", "lists_model_label", "observed_on")
# Keys mirror app.UI_MODEL_FILTERS; values are normalized aliases found in card scopes.
MODEL_ALIASES = {
    "AXIEZ": frozenset({"axiez", "axiez(ke-wf・ke-hf)", "駅舎エレ"}),
    "AXIEZ-LINKs": frozenset({"axiez-links"}),
    "NEXCUBE": frozenset({"nexcube", "nexcube limited", "特注機械室レスエレベーター"}),
    "メルシティ": frozenset({"メルシティ"}),
    "メルワイド": frozenset({"メルワイド"}),
    "エスカレーター": frozenset({"エスカレーター", "escalator"}),
}
# SYNC: must equal KNOWHOW_MODEL_FITS in knowledge-research.mjs (tests/unit/test_knowhow_contract_sync.py).
MODEL_FIT_VALUES = frozenset({"matched", "general", "other_product", "unknown"})
ESCALATOR_KEY = "エスカレーター"
GENERIC_ELEVATOR_LABEL = "全エレ機種"
GENERIC_ESCALATOR_LABEL = "全エス機種"

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
    if not isinstance(source_refs, list) or not 1 <= len(source_refs) <= 30:
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
    _validate_scope_verification(model_scope)


def _validate_scope_verification(model_scope: dict) -> None:
    """Reject malformed verification marks; ``verified`` needs a reviewer and a date."""
    for key in SCOPE_VERIFICATION_KEYS & set(model_scope):
        if not isinstance(model_scope[key], str):
            raise KnowhowIndexError("modelScope verification fields must be strings")
    status = model_scope.get("scope_status", "unverified")
    if status not in SCOPE_STATUSES:
        raise KnowhowIndexError("modelScope scope_status is invalid")
    if status == "verified":
        if not model_scope.get("scope_verified_by", "").strip():
            raise KnowhowIndexError("verified modelScope requires scope_verified_by")
        if not SCOPE_DATE_PATTERN.match(model_scope.get("scope_verified_at", "")):
            raise KnowhowIndexError("verified modelScope requires scope_verified_at as YYYY-MM-DD")


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
    return _remember_validated(index)


_validated: dict[str, Any] = {"index": None, "fingerprint": None}


def _validation_fingerprint(index: dict) -> int:
    """Hash of every validated field of the index (body by string hash, which Python caches).

    Cheap compared with ``validate_index``; any edit to a validated field changes it."""
    return hash((
        index["schemaVersion"], index["indexVersion"], index["generatedAt"],
        tuple(
            (card["knowledgeId"], card["cardVersion"], card["sha256"], card["title"], card["status"],
             card["usage"], card["body"], tuple(card["searchTerms"]), repr(card["sourceRefs"]),
             repr(card["modelScope"]))
            for card in index["cards"]
        ),
    ))


def _remember_validated(index: dict) -> dict:
    _validated.update(index=index, fingerprint=_validation_fingerprint(index))
    return index


def _ensure_valid(index: Any) -> dict:
    """Validate ``index`` unless this very object was already validated and is unchanged."""
    if _validated["index"] is index and isinstance(index, dict):
        try:
            if _validated["fingerprint"] == _validation_fingerprint(index):
                return index
        except (KeyError, TypeError):
            pass  # shape was changed: fall through to the strict check, which raises
    return validate_index(index)


def clear_cache() -> None:
    """Clear process-local cache; exposed for deterministic unit tests."""
    _cache.update(identity=None, expires=0.0, index=None, version_id=None, etag=None)
    _feature_cache.update(signature=None, value=None)
    _validated.update(index=None, fingerprint=None)


def canonical_index_version(index: dict) -> str:
    """Recompute the builder's content hash, including bodies, scope and sources."""
    serialized = json.dumps(index["cards"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()


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
        if not index["cards"]:
            raise KnowhowIndexError("index has no selected cards")
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
    """NFKC + casefold. Used for model labels, which are compared verbatim."""
    return unicodedata.normalize("NFKC", value).casefold()


# --- Search-side text normalisation -------------------------------------------------
# Applied identically to card text and queries so that katakana/hiragana, half/full
# width and long-vowel spelling variants (ヘルスエアー / ヘルスエア, タイマー / タイマ)
# share the same n-grams. Model labels keep using ``_normalize`` (verbatim compare).
_KATAKANA_TO_HIRAGANA = {code: code - 0x60 for code in range(0x30A1, 0x30F7)}
_KANA_LONG_VOWEL = re.compile("(?<=[\u3041-\u3096])ー")
_ORTHOGRAPHIC_VARIANTS = {ord("廻"): "回"}
_WORD_PATTERN = re.compile(r"[a-z0-9][a-z0-9._:-]{1,63}")
_CJK_RUN_PATTERN = re.compile(r"[\u3040-\u30ff\u3400-\u9fffー]+")
_DIGIT_PATTERN = re.compile(r"\d")


def _fold(text: str) -> str:
    folded = text.translate(_KATAKANA_TO_HIRAGANA).translate(_ORTHOGRAPHIC_VARIANTS)
    return _KANA_LONG_VOWEL.sub("", folded)


def _search_normalize(value: str) -> str:
    return _fold(_normalize(value))


# Conservative, purely conversational hiragana phrases removed from queries only
# (before kana folding, so katakana words are never cut). Short function words such as
# ない / して / から are deliberately NOT listed: IDF weighting already downweights them.
QUERY_STOPWORDS = tuple(sorted((
    "できない", "出来ない", "できません", "ください", "下さい", "教えて", "教えてください",
    "について", "に関して", "どうすれば", "どうしたら", "ですか", "でしょうか", "ありますか",
    "なんですけど", "なんだけど", "したい", "知りたい",
), key=len, reverse=True))

# Explicit spelling / abbreviation aliases appended to the query (never to cards).
# Each alias is a notation the cards demonstrably use for the same product or object;
# no technical synonyms are inferred beyond this list.
_QUERY_ALIAS_SOURCE = (
    ("リンクス", "links"),
    ("ネクスキューブ", "nexcube"),
    ("ネックスキューブ", "nexcube"),
    ("アクシーズ", "axiez"),
    ("エスカレータ", "escalator"),
    ("エスカ", "escalator エスカレーター"),
    ("メガー", "絶縁抵抗"),
)
QUERY_ALIASES = tuple((_search_normalize(k), _search_normalize(v)) for k, v in _QUERY_ALIAS_SOURCE)

# Scoring constants. Chosen on 85 real-card-derived queries + 16 unrelated ones (see
# docs): field weights are the best of the tested sets, WORD_WEIGHT=4 beat 1 and 2,
# MIN_MATCH_SCORE sits in the 0.18-0.22 plateau of the hit@3 / false-positive trade-off.
FIELD_WEIGHTS = {"title": 1.0, "terms": 1.0, "scope": 0.8, "body": 0.6}
WORD_WEIGHT = 4.0
CODE_MATCH_BONUS = 0.3
MIN_MATCH_SCORE = 0.2
RELATIVE_SCORE_GATE = 0.7
# Matched IDF mass at which the length-independent evidence score reaches 0.5.
EVIDENCE_HALF_MASS = 100.0


def _prepare_query(query: str) -> str:
    text = _normalize(query)
    for stopword in QUERY_STOPWORDS:
        text = text.replace(stopword, " ")
    text = _fold(text)
    extras = [value for key, value in QUERY_ALIASES if key in text]
    return " ".join([text, *extras]) if extras else text


def _extract_features(normalized: str) -> tuple[set[str], set[str]]:
    words = set(_WORD_PATTERN.findall(normalized))
    grams: set[str] = set()
    for run in _CJK_RUN_PATTERN.findall(normalized):
        if len(run) < 2:
            continue
        for size in (2, 3):
            grams.update(run[index:index + size] for index in range(len(run) - size + 1))
    return grams, words


def _query_features(query: str) -> tuple[set[str], set[str]]:
    return _extract_features(_prepare_query(query))


def _scope_values(card: dict, keys) -> list[str]:
    values = []
    for key in keys:
        raw = card["modelScope"].get(key, [])
        values.extend(str(item) for item in (raw if isinstance(raw, list) else [raw]))
    return values


def _build_card_features(card: dict) -> dict:
    """Per-card feature -> best field weight, plus the card's alphanumeric words."""
    fields = {
        "title": card["title"],
        "terms": " ".join(card["searchTerms"]),
        # Only positive scope keys; excludes / may_apply_to / scope_note never score.
        "scope": " ".join(_scope_values(card, POSITIVE_SCOPE_KEYS)),
        "body": card["body"],
    }
    weights: dict[str, float] = {}
    words: set[str] = set()
    for name, text in fields.items():
        grams, field_words = _extract_features(_search_normalize(text))
        words |= field_words
        weight = FIELD_WEIGHTS[name]
        for feature in grams | field_words:
            if weights.get(feature, 0.0) < weight:
                weights[feature] = weight
    return {"weights": weights, "words": frozenset(words)}


class _IndexFeatures:
    """Immutable per-index search data: card features and document frequencies."""

    def __init__(self, cards: list[dict]):
        self.features = [_build_card_features(card) for card in cards]
        self.count = len(cards)
        document_frequency: dict[str, int] = {}
        for item in self.features:
            for feature in item["weights"]:
                document_frequency[feature] = document_frequency.get(feature, 0) + 1
        self.document_frequency = document_frequency

    def idf(self, feature: str) -> float:
        frequency = self.document_frequency.get(feature, 0)
        return math.log((self.count + 1) / (frequency + 0.5))


_feature_cache: dict[str, Any] = {"signature": None, "value": None}


def _index_signature(cards: list[dict]) -> int:
    return hash(tuple(
        (card["knowledgeId"], card["sha256"], card["title"], tuple(card["searchTerms"]),
         repr(card["modelScope"]), len(card["body"]))
        for card in cards
    ))


def _index_features(index: dict) -> _IndexFeatures:
    """Return features for ``index``, rebuilt only when the searchable content changes.

    Keyed by a content signature (not object identity) so the 60 s S3 refresh of an
    unchanged index does not recompute every card."""
    signature = _index_signature(index["cards"])
    if _feature_cache["signature"] == signature:
        return _feature_cache["value"]
    value = _IndexFeatures(index["cards"])
    _feature_cache.update(signature=signature, value=value)
    return value


def _score_features(item: dict, store: _IndexFeatures, grams: list[str], words: list[str],
                    idf: dict[str, float]) -> float:
    """Score in [0, 1]: IDF-weighted query coverage or saturating matched mass, plus code bonus."""
    weights = item["weights"]
    numerator = denominator = 0.0
    for feature in grams:
        weight = idf[feature]
        denominator += weight
        numerator += weight * weights.get(feature, 0.0)
    for feature in words:
        weight = idf[feature] * WORD_WEIGHT
        denominator += weight
        numerator += weight * weights.get(feature, 0.0)
    if denominator <= 0.0:
        return 0.0
    # Coverage favours short, precise queries. A long natural sentence has many filler
    # n-grams no card contains, which caps its coverage; its few informative matches
    # still add up to a large absolute matched mass, so the saturating evidence term
    # (mass / (mass + half-mass)) keeps long questions findable. The better one wins.
    score = max(numerator / denominator, numerator / (numerator + EVIDENCE_HALF_MASS))
    codes = [word for word in words if _DIGIT_PATTERN.search(word)]
    if codes:
        matched = sum(1 for code in codes if code in item["words"])
        score += CODE_MATCH_BONUS * matched / len(codes)
    return min(1.0, score)


def _rank(index: dict, query: str, model_type: str | None) -> list[tuple[float, dict]]:
    query_grams, query_words = _query_features(query)
    if not query_grams and not query_words:
        return []
    store = _index_features(index)
    grams, words = sorted(query_grams), sorted(query_words)
    idf = {feature: store.idf(feature) for feature in (*grams, *words)}
    ranked = []
    for card, item in zip(index["cards"], store.features):
        if model_type in MODEL_ALIASES and _conflicts_with_model(card, model_type):
            continue
        ranked.append((_score_features(item, store, grams, words, idf), card))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["knowledgeId"]))
    return ranked


def rank_cards(index: dict, query: str, model_type: str | None = None) -> list[tuple[float, dict]]:
    """All cards with their score in [0, 1], best first (no threshold); for evaluation."""
    index = _ensure_valid(index)
    if not isinstance(query, str) or len(query) > 12000:
        raise KnowhowIndexError("query is invalid")
    return _rank(index, query, model_type)


def normalize_model_label(value: str) -> str:
    return _normalize(value).strip()


def _classify_model_value(value: str, model_type: str) -> str:
    label = normalize_model_label(value)
    if label in MODEL_ALIASES[model_type]:
        return "matched"
    is_escalator = model_type == ESCALATOR_KEY
    if label == normalize_model_label(GENERIC_ELEVATOR_LABEL):
        return "conflicting" if is_escalator else "general"
    if label == normalize_model_label(GENERIC_ESCALATOR_LABEL):
        return "general" if is_escalator else "conflicting"
    if any(label in aliases for aliases in MODEL_ALIASES.values()):
        return "conflicting"
    return "unknown"


def _conflicts_with_model(card: dict, model_type: str) -> bool:
    """True when a person-verified card's recognized product scope names only other products.

    Only cards with ``scope_status == "verified"`` can be dropped: list model labels
    are unreliable, so unverified scope never excludes a card. Unrecognized values
    (control codes, sub-attributes) are ignored; a card with no recognized product
    value, or any matched/general one, is never dropped.
    """
    if card["modelScope"].get("scope_status") != "verified":
        return False
    kinds = {
        _classify_model_value(value, model_type)
        for value in _scope_values(card, MODEL_CLASSIFY_KEYS)
    } - {"unknown"}
    return kinds == {"conflicting"}


def _recognized_product_keys(card: dict) -> list[str]:
    labels = {normalize_model_label(value) for value in _scope_values(card, MODEL_CLASSIFY_KEYS)}
    return [key for key, aliases in MODEL_ALIASES.items() if labels & aliases]


def model_fit(card: dict, model_type: str) -> dict:
    """Response-only fit of a card to the selected UI model (never an index field).

    ``modelFit`` is ``matched`` / ``general`` (generic label) / ``other_product``
    (recognized scope names only other products) / ``unknown`` (no recognized product).
    ``modelFitProducts`` lists the recognized UI product keys, for ``other_product`` only.
    Unlike the exclusion filter this ignores ``scope_status``: it explains, not filters.
    """
    kinds = {
        _classify_model_value(value, model_type)
        for value in _scope_values(card, MODEL_CLASSIFY_KEYS)
    } - {"unknown"}
    if "matched" in kinds:
        return {"modelFit": "matched"}
    if "general" in kinds:
        return {"modelFit": "general"}
    if kinds == {"conflicting"}:
        return {"modelFit": "other_product", "modelFitProducts": _recognized_product_keys(card)}
    return {"modelFit": "unknown"}


def search_index(index: dict, query: str, model_type: str | None = None, *, max_matches: int = MAX_MATCHES) -> dict:
    """Return up to three whole relevant cards under one combined body-size budget.

    ``model_type`` (a UI model key) drops only person-verified cards
    (``scope_status == "verified"``) whose recognized product scope names only other
    products; unverified cards, unknown keys and unrecognized codes never filter.
    With a known ``model_type`` each returned card is a copy that also carries the
    response-only ``modelFit`` fields (see ``model_fit``).
    """
    index = _ensure_valid(index)
    if type(max_matches) is not int or not 1 <= max_matches <= 12:
        raise KnowhowIndexError("invalid candidate limit")
    if not isinstance(query, str) or len(query) > 12000:
        raise KnowhowIndexError("query is invalid")
    ranked = _rank(index, query, model_type)
    top_score = ranked[0][0] if ranked else 0.0
    matches = []
    total_body_chars = 0
    for score, card in ranked:
        if (score < MIN_MATCH_SCORE or score < RELATIVE_SCORE_GATE * top_score
                or len(matches) >= max_matches):
            break
        if total_body_chars + len(card["body"]) > MAX_RESPONSE_BODY_CHARS:
            continue
        matches.append({**card, **model_fit(card, model_type)} if model_type in MODEL_ALIASES else card)
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
                pattern = (r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}" if key == "document_number"
                           else r"[\w .()（）-]+\.pdf")
                if not re.fullmatch(pattern, value, flags=re.IGNORECASE):
                    continue
                normalized = _normalize(value)
                if normalized not in seen:
                    seen.add(normalized)
                    hints.append(value)
                    if len(hints) >= max_hints:
                        return hints
    return hints


def retrieve_cards(index: dict, query: str, model_type: str | None = None,
                   *, client=None, claim_search=None, max_matches: int = MAX_MATCHES) -> dict:
    """Retrieve release-bound candidates, returning only canonical card content.

    The default remains the local index. Managed retrieval never treats a KB
    chunk as an authoritative card and never falls back on remote failure.
    """
    if type(max_matches) is not int or not 1 <= max_matches <= 12:
        raise KnowhowIndexError("invalid candidate limit")
    backend = os.environ.get("KNOWHOW_BACKEND", "local").strip()
    if backend == "local":
        return search_index(index, query, model_type=model_type, max_matches=max_matches)
    if backend != "managed" or os.environ.get("ENVIRONMENT") != "dev":
        raise KnowhowIndexError("invalid knowhow backend environment")
    index = validate_index(index)
    release = os.environ.get("KNOWHOW_RELEASE_ID", "").strip()
    kb_id = os.environ.get("KNOWHOW_MANAGED_KB_ID", "").strip()
    bucket = os.environ.get("KNOWHOW_INDEX_BUCKET", "").strip()
    if (not re.fullmatch(r"[a-f0-9]{64}", release) or index["indexVersion"] != f"sha256:{release}"
            or canonical_index_version(index) != index["indexVersion"]
            or not re.fullmatch(r"[A-Z0-9]{10}", kb_id) or not bucket):
        raise KnowhowIndexError("managed release is not configured")
    if not isinstance(query, str) or not query.strip() or len(query) > 12000:
        raise KnowhowIndexError("query is invalid")
    if claim_search is not None and not claim_search():
        raise KnowhowIndexError("managed search budget exhausted")
    if client is None:
        import boto3
        from botocore.config import Config
        client = boto3.client("bedrock-agent-runtime", config=Config(
            connect_timeout=3, read_timeout=20, retries={"total_max_attempts": 1},
        ))
    try:
        response = client.retrieve(
            knowledgeBaseId=kb_id, retrievalQuery={"text": query},
            retrievalConfiguration={"managedSearchConfiguration": {
                "numberOfResults": 12,
                "filter": {"equals": {"key": "release_id", "value": release}},
            }},
        )
    except Exception as error:
        raise KnowhowIndexError("managed retrieval unavailable") from error
    by_id = {card["knowledgeId"]: card for card in index["cards"]}
    selected, seen, total_chars = [], set(), 0
    if not isinstance(response, dict):
        raise KnowhowIndexError("invalid managed response")
    results = response.get("retrievalResults")
    if not isinstance(results, list) or len(results) > 12 or response.get("nextToken"):
        raise KnowhowIndexError("invalid managed response")
    for hit in results:
        if not isinstance(hit, dict) or not isinstance(hit.get("metadata"), dict):
            raise KnowhowIndexError("managed card metadata missing")
        meta = hit["metadata"]
        identity = meta.get("knowledge_id")
        if not isinstance(identity, str):
            raise KnowhowIndexError("invalid managed card ID")
        card = by_id.get(identity)
        if card is None:
            raise KnowhowIndexError("unknown managed card")
        location = hit.get("location")
        if (not isinstance(location, dict) or location.get("type") != "S3"
                or not isinstance(location.get("s3Location"), dict)):
            raise KnowhowIndexError("invalid managed card location")
        uri = location["s3Location"].get("uri")
        expected_uri = f"s3://{bucket}/releases/{release}/documents/{card['knowledgeId']}.md"
        region = os.environ.get("AWS_REGION", "").strip()
        expected_https_uri = (f"https://{bucket}.s3.{region}.amazonaws.com/"
                              f"releases/{release}/documents/{card['knowledgeId']}.md") if region else None
        if (meta.get("release_id") != release or meta.get("card_version") != str(card["cardVersion"])
                or meta.get("card_sha256") != card["sha256"]
                or not isinstance(uri, str) or uri not in {expected_uri, expected_https_uri}):
            raise KnowhowIndexError("managed card identity mismatch")
        score = hit.get("score", 0)
        if type(score) not in (int, float) or not math.isfinite(score):
            raise KnowhowIndexError("invalid managed score")
        if card["knowledgeId"] in seen:
            continue
        seen.add(card["knowledgeId"])
        if model_type in MODEL_ALIASES and _conflicts_with_model(card, model_type):
            continue
        if len(selected) >= max_matches or total_chars + len(card["body"]) > MAX_RESPONSE_BODY_CHARS:
            continue
        selected.append({**card, **model_fit(card, model_type)} if model_type in MODEL_ALIASES else card)
        total_chars += len(card["body"])
    return {"status": "matched" if selected else "not_found",
            "indexVersion": index["indexVersion"], "matches": selected}
