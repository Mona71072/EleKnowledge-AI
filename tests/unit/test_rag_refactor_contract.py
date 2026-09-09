"""Characterization tests that lock RAG behavior before structural refactoring.

These tests intentionally assert existing public behavior rather than proposing
new retrieval rules.  They provide a safety net while app.py is split into
smaller modules.
"""
import pytest


@pytest.fixture(scope="module")
def rag(rag_app):
    return rag_app


def _result(uri: str, score: float, text: str, *, chunk_id: str = "", category: str = "C資料"):
    metadata = {
        "x-amz-bedrock-kb-source-uri": uri,
        "category": category,
        "model_type": "AXIEZ",
    }
    if chunk_id:
        metadata["x-amz-bedrock-kb-chunk-id"] = chunk_id
    return {
        "score": score,
        "metadata": metadata,
        "content": {"text": text},
    }


def test_query_normalization_is_nfkc_and_space_collapsed(rag):
    assert rag.normalize_query_text("  ＡＸＩＥＺ　 火管  ") == "AXIEZ 火管"


def test_abbreviation_expansion_preserves_unknown_text(rag):
    assert rag.expand_query_abbreviations("火管の解除条件") == "火災管制の解除条件"
    assert rag.expand_query_abbreviations("未知語") == "未知語"


def test_merge_retrieval_results_keeps_best_duplicate_chunk(rag):
    low = _result("s3://bucket/a.pdf", 0.41, "same", chunk_id="c1")
    high = _result("s3://bucket/a.pdf", 0.82, "same", chunk_id="c1")
    other = _result("s3://bucket/b.pdf", 0.65, "other", chunk_id="c2")

    merged = rag.merge_retrieval_results([low, other], [high])

    assert len(merged) == 2
    assert merged[0]["score"] == 0.82
    assert merged[1]["score"] == 0.65


def test_merge_retrieval_results_keeps_distinct_image_chunks(rag):
    first = {
        "score": 0.7,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://bucket/drawing.pdf",
            "x-amz-bedrock-kb-chunk-id": "image-1",
        },
        "content": {"type": "IMAGE", "byteContent": "abc"},
    }
    second = {
        "score": 0.6,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://bucket/drawing.pdf",
            "x-amz-bedrock-kb-chunk-id": "image-2",
        },
        "content": {"type": "IMAGE", "byteContent": "def"},
    }

    merged = rag.merge_retrieval_results([first, second])

    assert len(merged) == 2


def test_selection_limits_chunks_per_document(rag):
    results = [
        _result("s3://bucket/a.pdf", 0.91, "a1", chunk_id="1"),
        _result("s3://bucket/a.pdf", 0.90, "a2", chunk_id="2"),
        _result("s3://bucket/a.pdf", 0.89, "a3", chunk_id="3"),
        _result("s3://bucket/b.pdf", 0.88, "b1", chunk_id="4"),
    ]

    selected = rag.select_retrieval_results(results, mode="normal")

    a_results = [
        r for r in selected
        if r["metadata"]["x-amz-bedrock-kb-source-uri"] == "s3://bucket/a.pdf"
    ]
    assert len(a_results) == 2
    assert any(
        r["metadata"]["x-amz-bedrock-kb-source-uri"] == "s3://bucket/b.pdf"
        for r in selected
    )


def test_selection_rejects_results_below_current_normal_threshold(rag):
    results = [
        _result("s3://bucket/a.pdf", 0.299, "below"),
        _result("s3://bucket/b.pdf", 0.300, "edge"),
    ]

    selected = rag.select_retrieval_results(results, mode="normal")

    assert [r["content"]["text"] for r in selected] == ["edge"]


def test_modeless_filter_applies_category_allowlist(rag):
    # PR #55/#57/#58 マージ後の develop 挙動: フィルタ未指定でもカテゴリ許可リストを
    # 常時適用し、web-crawler / TEST 由来のノイズ文書を検索母集団から遮断する
    # （None は返らない）。根拠: docs/verification-2026-08-26-kb-vqv-metadata.md
    assert rag.build_kb_filter({}) == {
        "in": {"key": "category", "value": list(rag.ALLOWED_CATEGORY_VALUES)}
    }


def test_normalize_mode_keeps_explicit_category(rag):
    mode, filters = rag.normalize_mode_and_filters(
        "spec", {"category": "drawing", "modelType": "AXIEZ"}
    )

    assert mode == "normal"
    assert filters == {"category": "drawing", "modelType": "AXIEZ"}


def test_caller_identity_comes_only_from_verified_claims(rag):
    event = {
        "requestContext": {"authorizer": {"claims": {"sub": "verified-user"}}},
        "body": '{"userId":"spoofed-user"}',
    }

    assert rag.get_caller_id(event) == "verified-user"
