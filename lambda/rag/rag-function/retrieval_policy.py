"""Pure retrieval-result policy for EleKnowledge RAG.

The Bedrock API call belongs elsewhere.  This module only interprets and selects
returned chunks so score thresholds, deduplication, and page metadata can be
unit-tested without AWS.

注意（移行期間中）: app.py と本モジュールは同じ KB プロファイルを参照する。
閾値 0.2/0.22/0.3 を含む選択ロジックを変更する場合は、必ず
tests/unit/test_rag_retrieval_policy.py のパリティテストも同時に更新すること。
"""

from kb_profile import load_kb_profile

KB_PROFILE = load_kb_profile()
PAGE_NUMBER_META_KEYS = KB_PROFILE.page_number_keys


def chunk_text(result: dict) -> str:
    """Extract text from a Bedrock KB result; IMAGE chunks have no text."""
    content = result.get("content", {}) or {}
    if content.get("type") == "IMAGE":
        return ""
    return content.get("text", "") or ""


def chunk_image_b64(result: dict):
    """Return raw base64 payload for an IMAGE chunk, otherwise None."""
    content = result.get("content", {}) or {}
    if content.get("type") != "IMAGE":
        return None
    raw = content.get("byteContent") or ""
    if not raw:
        return None
    return raw.split(",", 1)[1] if "," in raw else raw


def merge_retrieval_results(*result_lists: list) -> list:
    """Merge result lists, keeping the highest score for an identical chunk."""
    best = {}
    for results in result_lists:
        for result in results or []:
            metadata = result.get("metadata", {}) or {}
            source_uri = metadata.get(KB_PROFILE.source_uri_key, "") or ""
            text = chunk_text(result)
            chunk_id = metadata.get(KB_PROFILE.chunk_id_key, "") or ""
            key = (source_uri, text, chunk_id)
            previous = best.get(key)
            if not previous or (result.get("score", 0.0) or 0.0) > (
                previous.get("score", 0.0) or 0.0
            ):
                best[key] = result

    merged = list(best.values())
    merged.sort(key=lambda item: item.get("score", 0.0) or 0.0, reverse=True)
    return merged


def extract_page_number(metadata: dict):
    """Extract a known Bedrock KB page-number metadata value, if present."""
    metadata = metadata or {}
    for key in PAGE_NUMBER_META_KEYS:
        raw = metadata.get(key)
        if raw is None or raw == "":
            continue
        try:
            return int(float(raw))
        except (TypeError, ValueError):
            continue
    return None


def select_retrieval_results(
    retrieval_results: list, mode: str = "normal", rank_key: str = None
) -> list:
    """Apply the current score, per-document, and total-result limits."""
    if not retrieval_results:
        return []

    if mode == "spec":
        min_score = 0.2
        limit = 30
        max_chunks_per_doc = 3
    else:
        min_score = 0.3
        limit = 10
        max_chunks_per_doc = 2

    if rank_key is None:
        sorted_results = sorted(
            retrieval_results,
            key=lambda result: result.get("score", 0.0) or 0.0,
            reverse=True,
        )
    else:
        def sort_key(result):
            rank_value = result.get(rank_key)
            if rank_value is None:
                return (False, result.get("score", 0.0) or 0.0)
            return (True, rank_value)

        sorted_results = sorted(retrieval_results, key=sort_key, reverse=True)

    selected = []
    per_doc_counts = {}
    seen_text = set()

    for result in sorted_results:
        score = result.get("score", 0.0) or 0.0
        if score < min_score:
            continue

        metadata = result.get("metadata", {}) or {}
        source_uri = metadata.get(KB_PROFILE.source_uri_key, "") or ""
        doc_key = source_uri or (metadata.get("title") or "unknown")

        if per_doc_counts.get(doc_key, 0) >= max_chunks_per_doc:
            continue

        text = chunk_text(result)
        chunk_id = metadata.get(KB_PROFILE.chunk_id_key, "") or ""
        text_key = (doc_key, text, chunk_id)
        if text_key in seen_text:
            continue
        seen_text.add(text_key)

        selected.append(result)
        per_doc_counts[doc_key] = per_doc_counts.get(doc_key, 0) + 1

        if len(selected) >= limit:
            break

    return selected


def is_weak_retrieval(retrieval_results: list, mode: str = "normal") -> bool:
    """Return whether the current retrieval evidence is too weak for generation."""
    if not retrieval_results:
        return True
    top_score = max(
        (result.get("score", 0.0) or 0.0) for result in retrieval_results
    )
    if mode != "spec" and top_score < 0.22:
        return True
    if not select_retrieval_results(retrieval_results, mode=mode):
        return True
    return False
