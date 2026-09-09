"""Parity tests for the extracted pure query policy module.

移行期間限定のテスト: app.py が query_policy を import するよう配線された時点で
new == legacy は恒真（自明に成立）になるため、配線 PR で本ファイルを
モジュール単体の振る舞いテストへ書き換える（または削除する）こと。
"""
import pytest


@pytest.fixture(scope="module")
def modules(rag_app, load_rag_module):
    return rag_app, load_rag_module("rag_query_policy_new", "query_policy.py")


def test_policy_constants_match_existing_behavior(modules):
    # 固定入力のサンプルでは拾えない定数ドリフト（app.py 側だけの hotfix 等)を
    # 丸ごと比較で検出する。ABBREV_MAP は置換順序も挙動に影響するため順序も見る
    legacy, new = modules
    assert new.ABBREV_MAP == legacy.ABBREV_MAP
    assert list(new.ABBREV_MAP) == list(legacy.ABBREV_MAP)
    assert new.CLARIFY_MARKER == legacy.CLARIFY_MARKER
    for attr in ("SYMPTOM_RE", "PART_RE", "SITUATION_RE", "SPEC_QUESTION_RE"):
        assert getattr(new, attr).pattern == getattr(legacy, attr).pattern


@pytest.mark.parametrize(
    "text",
    [
        "  ＡＸＩＥＺ　 火管  ",
        "現調で寸法が合わない",
        "地震管制の条件は？",
        "",
    ],
)
def test_normalize_query_text_matches_existing_behavior(modules, text):
    legacy, new = modules
    assert new.normalize_query_text(text) == legacy.normalize_query_text(text)


@pytest.mark.parametrize(
    "text",
    ["火管の動作", "震管", "現調で確認", "未知語", ""],
)
def test_abbreviation_expansion_matches_existing_behavior(modules, text):
    legacy, new = modules
    assert new.expand_query_abbreviations(text) == legacy.expand_query_abbreviations(text)


@pytest.mark.parametrize(
    "query,filters,history",
    [
        ("振動がする", {}, []),
        ("振動がする", {"modelType": "AXIEZ"}, []),
        ("かごが振動する", {"modelType": "AXIEZ"}, []),
        ("地震管制で最寄階に停止する条件は？", {}, []),
        (
            "かご、走行中です",
            {},
            [
                {"role": "user", "content": "異音がする"},
                {"role": "assistant", "content": "該当ページを探すために教えてください\n1. 機種"},
            ],
        ),
    ],
)
def test_clarification_decision_matches_existing_behavior(modules, query, filters, history):
    legacy, new = modules
    assert new.needs_clarify(query, filters, history) == legacy.needs_clarify(query, filters, history)


def test_followup_composition_matches_existing_behavior(modules):
    legacy, new = modules
    history = [
        {"role": "user", "content": "エレベーターから異音がする"},
        {"role": "assistant", "content": legacy.CLARIFY_MARKER + "\n1. 機種"},
    ]
    assert new.compose_search_query("かご、走行中です", history) == legacy.compose_search_query(
        "かご、走行中です", history
    )


@pytest.mark.parametrize(
    "mode,filters",
    [
        ("normal", {}),
        ("spec", {}),
        ("spec", {"category": "drawing", "modelType": "AXIEZ"}),
        ("unknown", {"category": []}),
    ],
)
def test_mode_normalization_matches_existing_behavior(modules, mode, filters):
    legacy, new = modules
    assert new.normalize_mode_and_filters(mode, filters) == legacy.normalize_mode_and_filters(mode, filters)


@pytest.mark.parametrize(
    "filters",
    [{}, {"category": "drawing"}, {"category": ["spec", "std"]}],
)
def test_not_found_copy_matches_existing_behavior(modules, filters):
    legacy, new = modules
    assert new.build_not_found_content(filters) == legacy.build_not_found_content(filters)
