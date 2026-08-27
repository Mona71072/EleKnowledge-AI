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


def test_all_search_applies_allowed_category_filter(rag):
    """カテゴリ未指定（全検索）でも許可リスト（実カテゴリ10種）を常時適用する。

    web-crawler / quick-start / TEST のノイズ文書遮断（2026-08-26 実測 PR #55）。
    """
    f = rag.build_kb_filter({})
    assert f == {
        "in": {"key": "category", "value": list(rag.ALLOWED_CATEGORY_VALUES)}
    }
    assert rag.build_kb_filter(None) == f
    assert rag.build_kb_filter({"category": []}) == f


def test_allowed_categories_are_the_ten_real_values(rag):
    assert set(rag.ALLOWED_CATEGORY_VALUES) == {
        "据付場用図", "C資料", "テクニカルインフォメーション", "災害事例集",
        "Qシート", "据付基準", "据付ノート",
        "現場代理人業務マニュアル", "品質管理業務マニュアル", "W資料",
    }
    assert "TEST" not in rag.ALLOWED_CATEGORY_VALUES


def test_model_only_filter_still_applies_category_allowlist(rag):
    """機種のみ指定でもカテゴリ許可リストと andAll 合成される。"""
    f = rag.build_kb_filter({"modelType": "NEXCUBE"})
    assert set(f) == {"andAll"}
    assert len(f["andAll"]) == 2
    assert f["andAll"][0] == {
        "in": {"key": "category", "value": list(rag.ALLOWED_CATEGORY_VALUES)}
    }
    assert "orAll" in f["andAll"][1]


def test_unknown_category_key_falls_back_to_allowlist(rag):
    """許可リスト外・未知キーは通さず、許可リスト全体へフォールバック。"""
    f = rag.build_kb_filter({"category": ["no_such_key"]})
    assert f == {
        "in": {"key": "category", "value": list(rag.ALLOWED_CATEGORY_VALUES)}
    }


def test_explicit_categories_param_drops_disallowed_values(rag):
    """categories 直接指定（spec モード経路）でも許可リスト外は除外。"""
    f = rag.build_kb_filter({}, categories=["C資料", "TEST"])
    assert f == {"equals": {"key": "category", "value": "C資料"}}


def test_explicit_category_stable_keys(rag):
    f = rag.build_kb_filter({"category": ["spec", "std"]})
    assert f == {
        "in": {"key": "category", "value": ["C資料", "据付基準"]}
    }


def test_spec_categories_include_installation_std(rag):
    assert rag.SPEC_CATEGORIES == ['C資料', 'テクニカルインフォメーション', '据付基準']
