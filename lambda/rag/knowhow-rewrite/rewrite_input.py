"""Request validation for POST /rag/knowhow/rewrite-proposal.

Every limit comes from the contract (docs/features/development/knowhow-rewrite-proposal-contract.md).
Unknown keys are rejected so that nothing outside the contract can reach the prompt.
"""
import base64
import binascii
import json
import re
from datetime import date

from rewrite_errors import ApiError

MAX_BODY_BYTES = 262_144
KNOWLEDGE_ID = re.compile(r"KH-[A-Z0-9-]{1,80}")
CHECKED_ON = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
CARD_VERSION_RANGE = (1, 9999)
TARGET_HEADINGS = ("統合した回答・ノウハウ", "調査・確認手順", "未確認事項")
LANES = ("technical", "law")
TARGETS_MAX, TARGET_BODY_MAX, TARGETS_TOTAL_MAX = 3, 2000, 4000
CONTEXT_MAX, CONTEXT_BODY_MAX, CONTEXT_TOTAL_MAX, CONTEXT_HEADING_MAX = 8, 4000, 16000, 200
EVIDENCE_MAX, QUESTION_MAX, ANSWER_MAX = 12, 2000, 2000
SOURCES_MAX, SOURCE_TITLE_MAX, PAGE_RANGE = 8, 200, (1, 9999)

_TOP_REQUIRED = frozenset({"knowledgeId", "cardVersion", "targets", "evidence"})
_TOP_KEYS = _TOP_REQUIRED | {"context"}
_BAD = "リクエストの内容を確認してください"
# Lone surrogates cannot be encoded as UTF-8; control characters other than newline, carriage return and tab are never valid text.
_UNUSABLE_CHARS = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\ud800-\udfff]")


def _invalid(detail: str) -> ApiError:
    return ApiError(400, "ValidationError", f"{_BAD}（{detail}）")


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _keys(item, required: set, optional: set, name: str) -> dict:
    if not isinstance(item, dict):
        raise _invalid(name)
    keys = set(item)
    if not required <= keys or not keys <= (required | optional):
        raise _invalid(name)
    return item


def _text(value, name: str, limit: int, *, allow_empty: bool = True) -> str:
    if not isinstance(value, str) or len(value) > limit or (not allow_empty and not value.strip()):
        raise _invalid(name)
    if _UNUSABLE_CHARS.search(value):
        raise _invalid(name)
    return value


def _array(value, name: str, low: int, high: int) -> list:
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise _invalid(name)
    return value


def _targets(raw) -> list:
    items = []
    for item in _array(raw, "targets", 1, TARGETS_MAX):
        _keys(item, {"heading", "body"}, set(), "targets")
        if item["heading"] not in TARGET_HEADINGS:
            raise _invalid("targets.heading")
        items.append({"heading": item["heading"], "body": _text(item["body"], "targets.body", TARGET_BODY_MAX)})
    if len({item["heading"] for item in items}) != len(items):
        raise _invalid("targets.heading")
    if sum(len(item["body"]) for item in items) > TARGETS_TOTAL_MAX:
        raise _invalid("targets.total")
    return items


def _context(raw) -> list:
    items = []
    for item in _array(raw, "context", 0, CONTEXT_MAX):
        _keys(item, {"heading", "body"}, set(), "context")
        items.append({
            "heading": _text(item["heading"], "context.heading", CONTEXT_HEADING_MAX, allow_empty=False),
            "body": _text(item["body"], "context.body", CONTEXT_BODY_MAX),
        })
    if sum(len(item["body"]) for item in items) > CONTEXT_TOTAL_MAX:
        raise _invalid("context.total")
    return items


def _checked_on(value) -> str:
    try:
        if isinstance(value, str) and CHECKED_ON.fullmatch(value):
            date.fromisoformat(value)
            return value
    except ValueError:
        pass
    raise _invalid("evidence.checkedOn")


def _sources(raw) -> list:
    items = []
    for item in _array(raw, "sources", 0, SOURCES_MAX):
        _keys(item, {"title"}, {"page"}, "sources")
        source = {"title": _text(item["title"], "sources.title", SOURCE_TITLE_MAX)}
        if "page" in item:
            if not _is_int(item["page"]) or not PAGE_RANGE[0] <= item["page"] <= PAGE_RANGE[1]:
                raise _invalid("sources.page")
            source["page"] = item["page"]
        items.append(source)
    return items


def _evidence(raw) -> list:
    items = []
    for item in _array(raw, "evidence", 1, EVIDENCE_MAX):
        _keys(item, {"question", "lane", "checkedOn", "answer"}, {"sources"}, "evidence")
        if item["lane"] not in LANES:
            raise _invalid("evidence.lane")
        items.append({
            "question": _text(item["question"], "evidence.question", QUESTION_MAX, allow_empty=False),
            "lane": item["lane"],
            "checkedOn": _checked_on(item["checkedOn"]),
            "answer": _text(item["answer"], "evidence.answer", ANSWER_MAX, allow_empty=False),
            "sources": _sources(item.get("sources", [])),
        })
    return items


def _decode(event: dict) -> str:
    raw = event.get("body")
    if isinstance(raw, str) and event.get("isBase64Encoded"):
        try:
            raw = base64.b64decode(raw, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as error:
            raise _invalid("body") from error
    if not isinstance(raw, str):
        raise _invalid("body")
    try:
        size = len(raw.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise _invalid("body") from error
    if size > MAX_BODY_BYTES:
        raise ApiError(413, "PayloadTooLarge", "リクエストが大きすぎます")
    return raw


def parse_request(event: dict) -> dict:
    """Return the validated request as plain dicts, or raise ApiError (400 / 413)."""
    try:
        body = json.loads(_decode(event))
    except (json.JSONDecodeError, RecursionError) as error:
        raise _invalid("JSON") from error
    _keys(body, set(_TOP_REQUIRED), {"context"}, "body")
    if not isinstance(body["knowledgeId"], str) or not KNOWLEDGE_ID.fullmatch(body["knowledgeId"]):
        raise _invalid("knowledgeId")
    low, high = CARD_VERSION_RANGE
    if not _is_int(body["cardVersion"]) or not low <= body["cardVersion"] <= high:
        raise _invalid("cardVersion")
    return {
        "knowledgeId": body["knowledgeId"],
        "cardVersion": body["cardVersion"],
        "targets": _targets(body["targets"]),
        "context": _context(body.get("context", [])),
        "evidence": _evidence(body["evidence"]),
    }
