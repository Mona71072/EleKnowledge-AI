"""Pure helpers for constructing the persisted RAG retrieval trace."""
import hashlib
import json
import os


MAX_CANDIDATES = 30
MAX_CHUNK_TEXT_CHARS = 1200
DYNAMODB_ITEM_LIMIT_BYTES = 400 * 1024
# Leave room for DynamoDB attribute-name/serializer overhead and unrelated fields.
RETRIEVAL_TRACE_ITEM_BUDGET_BYTES = 380 * 1024


def prompt_version(system_prompt: str) -> str:
    """Return a stable short fingerprint for the exact generation prompt."""
    return hashlib.sha256((system_prompt or "").encode("utf-8")).hexdigest()[:12]


def model_input_text(text: str):
    """Match build_references_block's strip and truncation behavior."""
    original = (text or "").strip()
    truncated = len(original) > MAX_CHUNK_TEXT_CHARS
    supplied = original[:MAX_CHUNK_TEXT_CHARS].rstrip() + "…" if truncated else original
    return supplied, truncated, len(original)


def _json_bytes(value) -> int:
    return len(json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":")).encode("utf-8"))


def json_bytes(value) -> int:
    """Return a compact UTF-8 JSON size estimate for DynamoDB item guarding."""
    return _json_bytes(value)


def enforce_trace_size(trace: dict, base_item_bytes: int = 0,
                       max_item_bytes: int = RETRIEVAL_TRACE_ITEM_BUDGET_BYTES) -> dict:
    """Reduce oversized traces until they fit the reserved item-size budget."""
    result = json.loads(json.dumps(trace, ensure_ascii=False, default=str))
    if base_item_bytes + _json_bytes(result) > max_item_bytes:
        removed_text = False
        for row in result.get("candidates", []):
            if row.get("selected") and row.get("text") is not None:
                row["text"] = None
                row["textTruncated"] = True
                removed_text = True
        if removed_text:
            result["truncatedTrace"] = True
            result["truncationReason"] = "dynamodb_item_size_limit"
    if base_item_bytes + _json_bytes(result) > max_item_bytes:
        candidate_count = result.get("candidateCount", len(result.get("candidates", [])))
        attempt_count = result.get("searchAttemptCount", len(result.get("searchAttempts", [])))
        result = {
            "schemaVersion": result.get("schemaVersion", 1),
            "logicVersion": result.get("logicVersion", "unknown"),
            "promptVersion": result.get("promptVersion", "unknown"),
            "candidateCount": candidate_count,
            "searchAttemptCount": attempt_count,
            "truncatedTrace": True,
            "truncationReason": "dynamodb_item_size_limit",
        }
    return result


def _attempt(source: dict) -> dict:
    return {
        "stage": source.get("stage", "unknown"),
        "query": source.get("query"),
        "searchType": source.get("searchType"),
        "filters": source.get("filters") or {},
        "scope": source.get("scope") or {},
        "requested": source.get("requested"),
        "returned": source.get("returned"),
        "afterPostFilter": source.get("afterPostFilter"),
        "latencyMs": source.get("latencyMs"),
    }


def _feature(source: dict, *, rewrite=False) -> dict:
    source = source or {}
    return {
        "enabled": bool(source.get("enabled", False)),
        "status": source.get("status", "skipped"),
        "reason": source.get("reason"),
        **({"rewrittenQuery": source.get("rewrittenQuery")} if rewrite else {}),
        "modelId": source.get("modelId"),
        "callCount": int(source.get("callCount", 0) or 0),
        "latencyMs": source.get("latencyMs", 0),
    }


def _candidate(source: dict, rank: int) -> dict:
    selected = bool(source.get("selected", False))
    text = None
    text_truncated = False
    original_length = None
    if selected:
        if "modelInputText" in source:
            text = source.get("modelInputText")
            text_truncated = bool(source.get("textTruncated", False))
            original_length = source.get("originalLength")
        elif source.get("text") is not None:
            text, text_truncated, original_length = model_input_text(source.get("text"))
    return {
        "rank": source.get("rank", rank),
        "sourceUri": source.get("sourceUri"),
        "documentName": source.get("documentName"),
        "pageNumber": source.get("pageNumber"),
        "chunkId": source.get("chunkId"),
        "score": source.get("score"),
        "rerankScore": source.get("rerankScore"),
        "modelType": source.get("modelType"),
        "category": source.get("category"),
        "hasImage": source.get("hasImage"),
        "selected": selected,
        "excludedBy": source.get("excludedBy"),
        "dedupeCount": int(source.get("dedupeCount", 0) or 0),
        "text": text,
        "textTruncated": text_truncated,
        "originalLength": original_length,
    }


def build_retrieval_trace(*, logic_version=None, prompt_version_value=None,
                          request_id=None, kb_id=None, profile_hash=None,
                          data_source_sync_at=None, message_id=None,
                          composed_query=None, search_attempts=None, rewrite=None,
                          rerank=None, gate=None, candidates=None,
                          generation=None, generation_config=None,
                          total_ms=None, max_item_bytes=DYNAMODB_ITEM_LIMIT_BYTES,
                          base_item_bytes=0):
    """Build a JSON/DynamoDB-safe trace containing only the design's schema."""
    gate = gate or {}
    config = generation_config or {}
    thinking = config.get("thinking") or {}
    generation_value = None
    if generation is not None:
        generation_value = {
            "modelId": config.get("modelId"),
            "requestStyle": config.get("requestStyle"),
            "thinking": {"type": thinking.get("type"), "effort": thinking.get("effort")},
            "inputTokens": generation.get("inputTokens"),
            "outputTokens": generation.get("outputTokens"),
            "stopReason": generation.get("stopReason"),
            "latencyMs": generation.get("latencyMs"),
        }
    excluded = gate.get("excludedCounts") or {}
    candidate_rows = list(candidates or [])
    candidates_truncated = len(candidate_rows) > MAX_CANDIDATES
    trace = {
        "schemaVersion": 1,
        "logicVersion": logic_version or os.environ.get("RAG_LOGIC_VERSION", "unknown"),
        "promptVersion": prompt_version_value or "unknown",
        "requestId": request_id,
        "kb": {
            "kbId": kb_id,
            "profileHash": profile_hash,
            "dataSourceSyncAt": data_source_sync_at,
        },
        "questionRef": {"messageId": message_id, "composedQuery": composed_query},
        "searchAttempts": [_attempt(row) for row in (search_attempts or [])],
        "rewrite": _feature(rewrite, rewrite=True),
        "rerank": _feature(rerank),
        "gate": {
            "responseType": gate.get("responseType", "pages"),
            "weak": bool(gate.get("weak", False)),
            "scores": gate.get("scores") or [],
            "thresholds": gate.get("thresholds") or [],
            "rankKey": gate.get("rankKey"),
            "selectedCount": int(gate.get("selectedCount", 0) or 0),
            "excludedCounts": {
                "model_scope": int(excluded.get("model_scope", 0) or 0),
                "dedupe": int(excluded.get("dedupe", 0) or 0),
                "below_threshold": int(excluded.get("below_threshold", 0) or 0),
                "limit": int(excluded.get("limit", 0) or 0),
            },
        },
        "candidates": [_candidate(row, index) for index, row in
                       enumerate(candidate_rows[:MAX_CANDIDATES], start=1)],
        "generation": generation_value,
        "latencyMs": {"total": total_ms},
        "truncatedTrace": candidates_truncated,
        "truncationReason": "candidate_limit" if candidates_truncated else None,
    }
    return enforce_trace_size(trace, base_item_bytes=base_item_bytes,
                              max_item_bytes=max_item_bytes)
