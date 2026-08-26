"""Unit tests for RAG build_kb_filter (category + model_type listContains) and
model_type post-filters (element exact match / handled-model scope).

fixture は実データ型8種（2026-08-26 全数実測 PR #55）:
  "AXIEZ" / ["AXIEZ"] / 多値list / "*" / ["*"] / "general" / ["general"] / カンマ連結文字列
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
    spec = importlib.util.spec_from_file_location("rag_filter_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rag_filter_app"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_model_filter_expands_ui_group_to_listcontains(rag):
    """UI項目は展開機種ごとの listContains ＋ 共通(*/general) の orAll になる。

    stringContains（部分一致・誤マッチ752件）と equals ""（空欄は実データ0件）は
    もう使わない（verification-2026-08-26 §5.4）。
    """
    f = rag.build_kb_filter({"modelType": "AXIEZ"}, categories=["C資料"])
    assert f["andAll"]
    model_clause = next(c for c in f["andAll"] if "orAll" in c)
    values = model_clause["orAll"]
    assert values == [
        {"listContains": {"key": "model_type", "value": "AXIEZ"}},
        {"listContains": {"key": "model_type", "value": "AXIEZ(KE-WF・KE-HF)"}},
        {"listContains": {"key": "model_type", "value": "駅舎エレ"}},
        {"listContains": {"key": "model_type", "value": "*"}},
        {"listContains": {"key": "model_type", "value": "general"}},
    ]


def test_model_filter_has_no_stringcontains_or_empty_equals(rag):
    """全 UI 項目で stringContains / equals "" 句が生成されないこと。"""
    for ui_key in rag.UI_MODEL_FILTERS:
        f = rag.build_kb_filter({"modelType": ui_key})
        model_clause = next(c for c in f["andAll"] if "orAll" in c)
        for cond in model_clause["orAll"]:
            assert set(cond) == {"listContains"}
            assert cond["listContains"]["value"] != ""


def test_model_filter_single_target_ui_items(rag):
    """単一機種の UI 項目（例 AXIEZ-LINKs）は自身 + 共通の3句。"""
    f = rag.build_kb_filter({"modelType": "AXIEZ-LINKs"})
    model_clause = next(c for c in f["andAll"] if "orAll" in c)
    assert model_clause["orAll"] == [
        {"listContains": {"key": "model_type", "value": "AXIEZ-LINKs"}},
        {"listContains": {"key": "model_type", "value": "*"}},
        {"listContains": {"key": "model_type", "value": "general"}},
    ]


def test_model_filter_unknown_value_falls_back_to_itself(rag):
    """UI_MODEL_FILTERS に無い値はその値1つの listContains にフォールバック。"""
    f = rag.build_kb_filter({"modelType": "NEXIEZ-MR"})
    model_clause = next(c for c in f["andAll"] if "orAll" in c)
    assert model_clause["orAll"][0] == {
        "listContains": {"key": "model_type", "value": "NEXIEZ-MR"}
    }
    assert len(model_clause["orAll"]) == 3


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


# --- post-filter（安全弁）: 実データ型8種 fixture ---

COMMON_FIXTURES = ["*", ["*"], "general", ["general"]]
SPECIFIC_FIXTURES = ["AXIEZ", ["AXIEZ"], ["メルワイド", "メルシティ"]]
COMMA_JOINED = "機械室レス荷物用(中抵製),機械室レス荷物用(モダニ)"


def test_is_common_model_type_element_based(rag):
    """`["*"]` / `["general"]` も共通と判定する（旧判定の495件誤除外バグの根治）。"""
    for raw in COMMON_FIXTURES:
        assert rag._is_common_model_type(raw), raw
    for raw in SPECIFIC_FIXTURES + [COMMA_JOINED]:
        assert not rag._is_common_model_type(raw), raw
    # 実データ0件だがキー欠落・空値は共通扱い（除外より安全側）
    assert rag._is_common_model_type(None)
    assert rag._is_common_model_type("")
    assert rag._is_common_model_type([])


def test_model_type_elements_normalizes_all_shapes(rag):
    assert rag._model_type_elements("AXIEZ") == ["AXIEZ"]
    assert rag._model_type_elements(["AXIEZ"]) == ["AXIEZ"]
    assert rag._model_type_elements(["メルワイド", "メルシティ"]) == ["メルワイド", "メルシティ"]
    assert rag._model_type_elements(COMMA_JOINED) == [
        "機械室レス荷物用(中抵製)", "機械室レス荷物用(モダニ)"
    ]
    assert rag._model_type_elements(None) == []


def test_model_type_matches_exact_element_only(rag):
    """要素完全一致のみ。stringContains 時代の部分一致（AXIEZ⊂AXIEZ-LINKs）は不一致。"""
    assert rag.model_type_matches({"model_type": "AXIEZ"}, "AXIEZ")
    assert rag.model_type_matches({"model_type": ["AXIEZ"]}, "AXIEZ")
    # 部分一致誤マッチは通さない（str / list 両型）
    assert not rag.model_type_matches({"model_type": "AXIEZ-LINKs"}, "AXIEZ")
    assert not rag.model_type_matches({"model_type": ["AXIEZ-LINKs"]}, "AXIEZ")
    assert not rag.model_type_matches({"model_type": ["MAXIEZ CZ"]}, "AXIEZ")
    # UI グループ展開（AXIEZ → AXIEZ / AXIEZ(KE-WF・KE-HF) / 駅舎エレ）
    assert rag.model_type_matches({"model_type": ["駅舎エレ"]}, "AXIEZ")
    assert rag.model_type_matches({"model_type": "AXIEZ(KE-WF・KE-HF)"}, "AXIEZ")
    assert rag.model_type_matches({"model_type": ["NEXCUBE Limited"]}, "NEXCUBE")
    # 多値 list はいずれかの要素が一致すればよい
    assert rag.model_type_matches({"model_type": ["メルワイド", "メルシティ"]}, "メルシティ")
    # 共通資料は全 fixture 型で常に一致
    for raw in COMMON_FIXTURES:
        assert rag.model_type_matches({"model_type": raw}, "AXIEZ"), raw


def test_in_service_scope_element_based(rag):
    # 共通資料は全 fixture 型で常にスコープ内（["*"] / ["general"] の495件回復）
    for raw in COMMON_FIXTURES:
        assert rag.in_service_scope({"model_type": raw}), raw
    # 取扱機種（str / list / 多値 list）
    for raw in SPECIFIC_FIXTURES:
        assert rag.in_service_scope({"model_type": raw}), raw
    # カンマ連結60件は要素分解で判定（機械室レス荷物用(中抵製) は取扱機種）
    assert rag.in_service_scope({"model_type": COMMA_JOINED})
    # 取扱外機種のみの資料は除外
    assert not rag.in_service_scope({"model_type": "NEXIEZ-MRL Version 2"})
    assert not rag.in_service_scope({"model_type": ["NEXIEZ-MRL Version 2"]})


def test_handled_model_types_are_the_27_measured_values(rag):
    assert len(rag.HANDLED_MODEL_TYPES) == 27
    assert "NEXIEZ-MRL Version 2" not in rag.HANDLED_MODEL_TYPES


def test_query_knowledge_base_applies_post_filters(rag, monkeypatch):
    """retrieve 結果にスコープ＋機種完全一致の post-filter が掛かる。"""

    def _r(model_type):
        return {"score": 0.5, "metadata": {"model_type": model_type},
                "content": {"text": "x"}}

    fake_results = [
        _r("AXIEZ"),                    # 一致
        _r(["*"]),                      # 共通 (list型)
        _r("general"),                  # 共通 (str型)
        _r(["AXIEZ-LINKs"]),            # 機種指定 AXIEZ には不一致
        _r("NEXIEZ-MRL Version 2"),     # スコープ外
    ]

    class FakeAgent:
        def retrieve(self, **kwargs):
            return {"retrievalResults": [dict(r) for r in fake_results]}

    monkeypatch.setattr(rag, "bedrock_agent", FakeAgent())

    # 機種指定あり: スコープ + 要素完全一致
    res = rag.query_knowledge_base("q", {"modelType": "AXIEZ"})
    kept = [r["metadata"]["model_type"] for r in res["retrievalResults"]]
    assert kept == ["AXIEZ", ["*"], "general"]

    # 機種未指定: スコープのみ（AXIEZ-LINKs は残る）
    res = rag.query_knowledge_base("q", {})
    kept = [r["metadata"]["model_type"] for r in res["retrievalResults"]]
    assert kept == ["AXIEZ", ["*"], "general", ["AXIEZ-LINKs"]]
