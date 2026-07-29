"""Unit tests for clarify / weak / page helpers (2026-07-29 Phase1)."""
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
    name = "rag_clarify_app"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_needs_clarify_symptom_without_model(rag):
    ok, qs = rag.needs_clarify("振動がする", {})
    assert ok is True
    assert len(qs) >= 2


def test_no_clarify_when_model_selected(rag):
    ok, _ = rag.needs_clarify("振動がする", {"modelType": "AXIEZ"})
    assert ok is False


def test_no_clarify_for_spec_style_question(rag):
    ok, _ = rag.needs_clarify("火災管制の動作は？", {})
    assert ok is False


def test_followup_after_clarify_skips(rag):
    hist = [{"role": "assistant", "content": rag.CLARIFY_MARKER + "\n1. 機種"}]
    ok, _ = rag.needs_clarify("かご、走行中です", {}, hist)
    assert ok is False


def test_compose_search_query_joins_prior_symptom(rag):
    hist = [
        {"role": "user", "content": "エレベーターから異音がする"},
        {"role": "assistant", "content": rag.CLARIFY_MARKER + "\n1. 機種"},
    ]
    combined = rag.compose_search_query("かご、走行中です", hist)
    assert "異音" in combined
    assert "かご" in combined


def test_compose_search_query_no_join_without_clarify(rag):
    hist = [{"role": "user", "content": "火災管制の動作は？"}]
    assert rag.compose_search_query("追記だけ", hist) == "追記だけ"


def test_compose_search_query_avoids_duplicate_prior(rag):
    hist = [
        {"role": "user", "content": "振動がする"},
        {"role": "assistant", "content": rag.CLARIFY_MARKER + "\n1. 機種"},
    ]
    full = "振動がする。かご、走行中"
    assert rag.compose_search_query(full, hist) == full


def test_is_weak_uses_max_score(rag):
    assert rag.is_weak_retrieval([]) is True
    weak = [{"score": 0.1, "metadata": {}, "content": {"text": "a"}}]
    assert rag.is_weak_retrieval(weak) is True
    strong = [{
        "score": 0.55,
        "metadata": {"x-amz-bedrock-kb-source-uri": "s3://b/doc.pdf"},
        "content": {"text": "火災管制"},
    }]
    assert rag.is_weak_retrieval(strong) is False


def test_extract_page_number(rag):
    assert rag.extract_page_number({"x-amz-bedrock-kb-document-page-number": "3"}) == 3
    assert rag.extract_page_number({}) is None


def test_priority_categories_match_spec(rag):
    assert rag.PRIORITY_CATEGORIES == rag.SPEC_CATEGORIES
