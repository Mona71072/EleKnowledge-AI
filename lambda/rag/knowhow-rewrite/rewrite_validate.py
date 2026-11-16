"""Server-side validation of the model output. The model output is never trusted.

The model's JSON is parsed strictly, reduced to the sections the request asked for, and every
changed body is checked against the request before it is returned to the admin.
"""
import json
import re

from rewrite_body_checks import has_new_link_or_html, has_suspicious_chars, link_or_html_items, structure_problems
from rewrite_errors import ApiError
from rewrite_model import TRUNCATED_STOP_REASONS
from rewrite_tokens import Support

BODY_MAX_CHARS = 4000
REASON_MAX_CHARS = 300
SUMMARY_MAX_CHARS = 200
CONFLICTS_MAX = 10
USABLE_STOP_REASONS = frozenset({"", "end_turn", "stop_sequence"})

_LEADING_BLANK_LINES = re.compile(r"\A(?:[ \t]*\r?\n)+")


def _failed(detail: str) -> ApiError:
    return ApiError(502, "RewriteFailed", f"書き換え案を作成できませんでした。再度お試しください（{detail}）")


def _truncated() -> ApiError:
    return ApiError(502, "RewriteTruncated", "書き換え案が長すぎて途中で切れました。対象の節を減らして再度お試しください")


def _extract_json(text: str) -> dict:
    candidate = text.strip()
    outer = candidate[candidate.find("{"):candidate.rfind("}") + 1] if "{" in candidate else ""
    for attempt in (candidate, outer):
        try:
            value = json.loads(attempt) if attempt else None
        except (ValueError, RecursionError):
            continue
        if isinstance(value, dict):
            return value
    raise _failed("形式")


def _evidence_numbers(raw, count: int) -> list:
    if not isinstance(raw, list):
        raise _failed("根拠の番号")
    valid = {n for n in raw if isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= count}
    return sorted(valid)


def _clean_note(text: str, limit: int) -> str:
    """Reason / summary text; empty when it carries a link, HTML or odd characters (it is shown to the admin)."""
    text = text.strip()
    if has_suspicious_chars(text) or link_or_html_items(text):
        return ""
    return text[:limit]


def _parse_section(entry, headings: tuple, count: int):
    """Return (heading, parsed) for a section the request asked for; None for any other section."""
    if not isinstance(entry, dict) or not isinstance(entry.get("heading"), str):
        raise _failed("節")
    status = entry.get("status")
    if status not in ("changed", "unchanged"):
        raise _failed("状態")
    if entry["heading"] not in headings:
        return None
    if status == "unchanged":
        return entry["heading"], {"status": "unchanged"}
    reason = entry.get("reason", "")
    if not isinstance(entry.get("body"), str) or not isinstance(reason, str):
        raise _failed("本文")
    return entry["heading"], {
        "status": "changed",
        "body": _LEADING_BLANK_LINES.sub("", entry["body"]).rstrip(),  # keep indentation of the first line
        "reason": _clean_note(reason, REASON_MAX_CHARS),
        "evidence": _evidence_numbers(entry.get("evidence"), count),
    }


def _parse_sections(parsed: dict, headings: tuple, count: int) -> dict:
    raw = parsed.get("sections")
    if not isinstance(raw, list):
        raise _failed("sections")
    sections = {}
    for entry in raw:
        item = _parse_section(entry, headings, count)
        if item is None:
            continue
        if item[0] in sections:
            raise _failed("節の重複")
        sections[item[0]] = item[1]
    return sections


def _parse_conflicts(parsed: dict, headings: tuple, count: int) -> list:
    raw = parsed.get("conflicts", [])
    if not isinstance(raw, list):
        raise _failed("conflicts")
    conflicts = []
    for entry in raw[:CONFLICTS_MAX]:
        if not isinstance(entry, dict) or not isinstance(entry.get("summary"), str) or not entry["summary"].strip():
            raise _failed("conflicts")
        heading = entry.get("heading")
        if heading is not None and not isinstance(heading, str):
            raise _failed("conflicts")
        summary = _clean_note(entry["summary"], SUMMARY_MAX_CHARS)
        if summary:
            conflicts.append({
                "heading": heading if heading in headings else None,
                "summary": summary,
                "evidence": _evidence_numbers(entry.get("evidence", []), count),
            })
    return conflicts


def _squash(text: str) -> str:
    return " ".join(text.split())


def _support(request: dict) -> Support:
    if request["evidence"][0]["lane"] == "field":
        return Support([item["answer"] for item in request["evidence"]])
    texts = [item["body"] for item in request["targets"]]
    texts += [item["heading"] + "\n" + item["body"] for item in request["context"]]
    for item in request["evidence"]:
        texts += [item["question"], item["answer"], item["checkedOn"]] + [s["title"] for s in item["sources"]]
    return Support(texts)


def _rejected(heading: str, warnings: list) -> dict:
    return {"heading": heading, "status": "rejected", "warnings": warnings}


def _check_body(body: str, original: str, support: Support) -> list:
    if not body:
        return [{"code": "empty_body"}]
    if len(body) > BODY_MAX_CHARS:
        return [{"code": "too_long"}]
    codes = (["suspicious_text"] if has_suspicious_chars(body) else []) + structure_problems(body)
    if has_new_link_or_html(body, original):
        codes.append("link_or_html")
    warnings = [{"code": code} for code in codes]
    unsupported = support.unsupported_values(body)
    if unsupported:
        warnings.append({"code": "unsupported_value", "tokens": unsupported})
    return warnings


def _evaluate(heading: str, parsed: dict, original: str, support: Support, *, strict_numbers: bool = False) -> dict:
    unchanged = {"heading": heading, "status": "unchanged"}
    if parsed["status"] == "unchanged" or _squash(parsed["body"]) == _squash(original):
        return unchanged
    warnings = [] if parsed["evidence"] else [{"code": "missing_evidence"}]
    warnings += _check_body(parsed["body"], original, support)
    unverified = support.unverified_numbers(parsed["body"])
    if strict_numbers and unverified:
        warnings.append({"code": "unverified_number", "tokens": unverified})
    if warnings:
        return _rejected(heading, warnings)
    return {
        "heading": heading,
        "status": "changed",
        "body": parsed["body"],
        "reason": parsed["reason"],
        "evidence": parsed["evidence"],
        "warnings": [{"code": "unverified_number", "tokens": unverified}] if unverified else [],
    }


def build_response(request: dict, text: str, stop_reason: str) -> dict:
    """Validate the model text against the request and return the public response, or raise ApiError."""
    if stop_reason in TRUNCATED_STOP_REASONS:
        raise _truncated()
    if stop_reason not in USABLE_STOP_REASONS:
        raise _failed("応答が完了しませんでした")
    if not (text or "").strip():
        raise _failed("空の応答")
    parsed = _extract_json(text)
    headings = tuple(item["heading"] for item in request["targets"])
    count = len(request["evidence"])
    sections = _parse_sections(parsed, headings, count)
    conflicts = _parse_conflicts(parsed, headings, count)
    support = _support(request)
    strict_numbers = request["evidence"][0]["lane"] == "field"
    result = [
        _evaluate(
            item["heading"], sections.get(item["heading"], {"status": "unchanged"}),
            item["body"], support, strict_numbers=strict_numbers,
        )
        for item in request["targets"]
    ]
    return {
        "knowledgeId": request["knowledgeId"],
        "cardVersion": request["cardVersion"],
        "sections": result,
        "conflicts": conflicts,
    }
