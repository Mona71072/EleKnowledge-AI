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


def test_no_clarify_when_model_part_and_situation(rag):
    ok, _ = rag.needs_clarify(
        "かごが走行中に振動がする",
        {"modelType": "AXIEZ"},
    )
    assert ok is False


def test_clarify_when_model_but_missing_part_or_situation(rag):
    ok, qs = rag.needs_clarify("振動がする", {"modelType": "AXIEZ"})
    assert ok is True
    assert any('部位' in q for q in qs)
    assert any('いつ' in q or '発生' in q for q in qs)
    assert not any('機種' in q for q in qs)


def test_clarify_for_error_symptom_without_model(rag):
    ok, qs = rag.needs_clarify("エラーが出る", {})
    assert ok is True
    assert len(qs) >= 2


def test_no_clarify_for_spec_style_question(rag):
    ok, _ = rag.needs_clarify("火災管制の動作は？", {})
    assert ok is False


def test_no_clarify_for_spec_condition_question(rag):
    # SYMPTOM_RE の「停止」が誤発火しても仕様質問は聞き返さない（Major 5）
    ok, _ = rag.needs_clarify("地震管制で最寄階に停止する条件は？", {})
    assert ok is False


def test_no_clarify_for_error_code_meaning_question(rag):
    # 「エラー」を含んでも定義質問は聞き返さない
    ok, _ = rag.needs_clarify("エラーコードE21の意味は？", {})
    assert ok is False


def test_no_clarify_when_model_and_part_present(rag):
    # 機種あり＋部位ありなら状況が欠けていても検索へ進む（両方欠けたときだけ聞く）
    ok, _ = rag.needs_clarify("かごが振動する", {"modelType": "AXIEZ"})
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


def test_build_claude_messages_alternating_on_first_turn(rag):
    msgs = rag.build_claude_messages('振動がする', [], chat_history=None)
    roles = [m['role'] for m in msgs]
    assert roles == ['user']
    assert all(roles[i] != roles[i + 1] for i in range(len(roles) - 1))


def test_build_claude_messages_alternating_after_clarify(rag):
    hist = [
        {'role': 'user', 'content': 'エレベーターから異音がする'},
        {'role': 'assistant', 'content': rag.CLARIFY_MARKER + '\n1. 機種'},
    ]
    msgs = rag.build_claude_messages(
        'かご、走行中です',
        [],
        chat_history=hist,
        search_query='エレベーターから異音がする\nかご、走行中です',
    )
    roles = [m['role'] for m in msgs]
    assert roles[0] == 'user'
    assert all(roles[i] != roles[i + 1] for i in range(len(roles) - 1))
    # final user content includes references + composed question
    final = msgs[-1]['content']
    assert isinstance(final, list)
    texts = ' '.join(b.get('text', '') for b in final if isinstance(b, dict))
    assert '異音' in texts and 'かご' in texts


def test_build_claude_messages_drops_leading_assistant_history(rag):
    # get_chat_history(limit=5) は奇数件を返すため、4問目以降は履歴が
    # assistant 始まりになる（Bedrock は assistant 先頭を拒否する）
    hist = [
        {'role': 'assistant', 'content': '1問目の回答です'},
        {'role': 'user', 'content': '2問目の質問'},
        {'role': 'assistant', 'content': '2問目の回答です'},
        {'role': 'user', 'content': '3問目の質問'},
        {'role': 'assistant', 'content': '3問目の回答です'},
    ]
    msgs = rag.build_claude_messages('4問目の質問', [], chat_history=hist)
    roles = [m['role'] for m in msgs]
    assert roles[0] == 'user'
    assert roles[-1] == 'user'
    assert all(roles[i] != roles[i + 1] for i in range(len(roles) - 1))


def test_build_question_text_includes_composed_search(rag):
    text = rag.build_question_text_for_claude('かご', '異音がする\nかご')
    assert '【検索クエリ】' in text
    assert '異音' in text


def test_build_not_found_mentions_category(rag):
    plain = rag.build_not_found_content({})
    assert '絞り込み' not in plain
    with_cat = rag.build_not_found_content({'category': 'drawing'})
    assert '資料カテゴリ' in with_cat


def test_expand_abbrev_includes_domain_terms(rag):
    assert '火災管制' in rag.expand_query_abbreviations('火管の動作')
    assert '地震管制' in rag.expand_query_abbreviations('震管')


def test_normalize_mode_spec_forces_priority_categories(rag):
    mode, filters = rag.normalize_mode_and_filters('spec', {})
    assert mode == 'normal'
    assert filters['category'] == ['spec', 'tech_info', 'std']
    mode2, filters2 = rag.normalize_mode_and_filters('spec', {'category': 'drawing'})
    assert mode2 == 'normal'
    assert filters2['category'] == 'drawing'


def test_ui_category_keys_exclude_unreachable(rag):
    assert 'site_agent' not in rag.UI_CATEGORY_KEYS
    assert 'quality_mgmt' not in rag.UI_CATEGORY_KEYS
    assert 'site_agent' in rag.CATEGORY_MAP
