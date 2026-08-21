"""Unit tests for RAG build_kb_filter (category + model_type OR)."""
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
    spec = importlib.util.spec_from_file_location("rag_filter_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rag_filter_app"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_model_filter_includes_star_general_and_empty(rag):
    f = rag.build_kb_filter({"modelType": "AXIEZ"}, categories=["C資料"])
    assert f["andAll"]
    model_clause = next(c for c in f["andAll"] if "orAll" in c)
    values = model_clause["orAll"]
    assert {"stringContains": {"key": "model_type", "value": "AXIEZ"}} in values
    assert {"equals": {"key": "model_type", "value": "*"}} in values
    assert {"equals": {"key": "model_type", "value": "general"}} in values
    assert {"equals": {"key": "model_type", "value": ""}} in values


def test_no_category_filter_when_omitted(rag):
    """カテゴリ未指定は全資料（カテゴリフィルタなし）。"""
    f = rag.build_kb_filter({})
    assert f is None


def test_model_only_filter_when_no_category(rag):
    f = rag.build_kb_filter({"modelType": "NEXCUBE"})
    assert "orAll" in f
    assert "andAll" not in f


def test_explicit_category_stable_keys(rag):
    f = rag.build_kb_filter({"category": ["spec", "std"]})
    assert f == {
        "in": {"key": "category", "value": ["C資料", "据付基準"]}
    }


def test_spec_categories_include_installation_std(rag):
    assert rag.SPEC_CATEGORIES == ['C資料', 'テクニカルインフォメーション', '据付基準']
