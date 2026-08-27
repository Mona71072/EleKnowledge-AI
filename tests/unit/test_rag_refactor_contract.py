"""Characterization tests that lock RAG behavior before structural refactoring.

These tests intentionally assert existing public behavior rather than proposing
new retrieval rules.  They provide a safety net while app.py is split into
smaller modules.
"""
import importlib.util
import os
import sys

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")


@pytest.fixture(scope="module")
def rag():
    os.environ.setdefault("CHATLOGS_TABLE", "test-chatlogs")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    path = os.path.normpath(os.path.join(BASE, "lambda/rag/rag-function/app.py"))
    name = "rag_refactor_contract_app"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


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


def test_modeless_filter_contract_is_currently_no_filter(rag):
    # This pins develop behavior only.  PR #57/#58 may deliberately change it;
    # rebase the refactor branch after those decisions are merged.
    assert rag.build_kb_filter({}) is None


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
