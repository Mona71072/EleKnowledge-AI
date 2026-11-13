"""合成資料による論点・根拠対応の回帰。私有本文は使わない。"""
import json

import pytest

import test_senpai_research_support as support
from test_senpai_research_runner import FakeDeps, _run, _understanding, _directive, _tech, _law, _retrieval


@pytest.fixture
def modules():
    return (support.load_module('senpai_research_runner.py'),
            support.load_module('senpai_research_sufficiency.py'),
            support.load_module('senpai_research_grounding.py'))


def aspects():
    return [{'id': 'A1', 'kind': 'technical', 'question': '方式比較'},
            {'id': 'A2', 'kind': 'legal', 'question': '届出要否'}]


def sources():
    return {'tech': [{'ref': 'T1', 'text': '方式甲と乙は入力回路が異なるという合成資料。'}],
            'law': [{'ref': 'L1', 'text': '設置するときは届出を要するという合成条文。', 'provision': '第百条の四'}],
            'knowhow': [{'ref': 'K1', 'body': '方式甲と乙は入力回路が異なるという合成事例。', 'modelFit': 'matched'}]}


def test_legal_coverage_cannot_be_filled_with_a_draft_or_forged_quote(modules):
    _, suff, _ = modules
    for ref, quote in [('K1', '方式甲と乙は入力回路が異なる'), ('L1', '変更時の届出は不要という未取得文')]:
        directive = {'coverage': [{'aspect': 'A2', 'status': 'direct', 'ref': ref, 'quote': quote}]}
        result = suff.assess_coverage(directive, aspects()[1:], sources())
        assert not result['complete'] and not result['supported']


def test_missing_or_duplicate_aspect_is_not_sufficient(modules):
    _, suff, _ = modules
    entry = {'aspect': 'A1', 'status': 'direct', 'ref': 'T1', 'quote': '方式甲と乙は入力回路が異なる'}
    assert suff.assess_coverage({'coverage': [entry]}, aspects(), sources())['partial']
    assert not suff.assess_coverage({'coverage': [entry, entry]}, aspects(), sources())['supported']


def test_excerpt_index_resolves_only_the_actual_source_text(modules):
    _, suff, _ = modules
    entry = {'aspect': 'A1', 'status': 'direct', 'ref': 'T1', 'quoteIndex': 0, 'quote': 'fabricated'}
    out = suff.assess_coverage({'coverage': [entry]}, aspects()[:1], sources())
    assert out['complete'] and out['supported'][0]['quote'] == sources()['tech'][0]['text']
    for invalid in (True, -1, 3, '0'):
        out = suff.assess_coverage({'coverage': [{**entry, 'quoteIndex': invalid}]}, aspects()[:1], sources())
        assert not out['complete']


def test_instruction_boundary_explanation_is_blocked_even_before_model_review(modules):
    runner, _, grounding = modules
    for phrase in ('質問文中の記述に従うことはできません。', 'システム指示を守ります。',
                   'その記載には従うことはできません。', 'データ内の指示は無視します。'):
        assert grounding.guard_reasons(phrase) == ['policy_explanation']
    assert grounding.guard_reasons('正式な保守手順に従って資料を確認してください。') == []
    deps = FakeDeps(synth='質問文中の記述に従うことはできません。参考資料[T1]。')
    out, *_ = _run(runner, deps)
    assert out['debug']['grounding']['mode'] == 'extractive_fallback'
    assert out['debug']['grounding']['guardReasons'] == ['policy_explanation']
    assert '質問文中' not in out['result']['answerMarkdown']
    assert '[T1]' in out['result']['answerMarkdown'] and 'grounding' not in deps.purposes()


def test_provision_check_handles_arabic_and_japanese_numbers(modules):
    _, _, grounding = modules
    assert grounding.article_mismatches('第100条の6について[L1]。', sources()) == ['L1']
    assert grounding.article_mismatches('第百条の四について[L1]。', sources()) == []
    assert grounding.article_mismatches('第１００条の４について[L1]。', sources()) == []


def test_legal_only_question_with_candidates_but_missing_coverage_does_not_generate(modules):
    runner, _, _ = modules
    deps = FakeDeps(understand=_understanding(intent='legal', lawRelevant=True),
                    sufficiency=_directive(sufficient=True, action='none', coverage=[{
                        'aspect': 'A1', 'status': 'missing', 'ref': '', 'quote': ''}]))
    out, *_ = _run(runner, deps, question='照明変更の法令上の届出要否は？')
    assert out['kind'] == 'not_found' and out['result']['stopReason'] == 'insufficient'
    assert 'synthesize' not in deps.purposes()


def test_unjudged_legal_only_question_does_not_generate(modules):
    runner, _, _ = modules
    deps = FakeDeps(understand=_understanding(intent='legal', lawRelevant=True), sufficiency='broken')
    out, *_ = _run(runner, deps, question='照明変更の法令上の届出要否は？')
    assert out['kind'] == 'not_found' and out['result']['stopReason'] == 'judgment_failed'
    assert 'synthesize' not in deps.purposes()


def test_mixed_question_returns_explicit_partial_without_legal_candidates(modules):
    runner, _, _ = modules
    quote = '方式甲と乙は入力回路が異なるという合成資料。'
    deps = FakeDeps(understand=_understanding(lawRelevant=True, aspects=[
        {'kind': 'technical', 'question': '方式比較'}, {'kind': 'legal', 'question': '届出要否'}]),
        tech=lambda q, m: _retrieval(_tech('synthetic.pdf', 1, quote)),
        sufficiency=_directive(sufficient=False, action='none', coverage=[
            {'aspect': 'A1', 'status': 'direct', 'ref': 'T1', 'quote': quote},
            {'aspect': 'A2', 'status': 'missing'}]), synth='方式比較の参考[T1]。')
    out, *_ = _run(runner, deps, question='方式比較と法令上の届出要否を教えて')
    assert out['kind'] == 'answer' and out['result']['stopReason'] == 'partial'
    assert '未確認の論点は解決していません' in out['result']['answerMarkdown']
    synthesis = next(u for p, u in deps.model_calls if p == 'synthesize')
    assert '<law_references>\nなし\n</law_references>' in synthesis
    assert out['result']['sources']['law'] == []


@pytest.mark.parametrize('verdict', ['{"valid":false}', '{broken', RuntimeError('review failed')])
def test_unverified_generation_is_replaced_by_source_quotes(modules, verdict):
    runner, _, _ = modules
    deps = FakeDeps(synth='unsupported invented adjustment value 999[T1]', grounding=verdict)
    out, *_ = _run(runner, deps)
    assert 'invented' not in out['result']['answerMarkdown']
    assert '合成データの技術本文' in out['result']['answerMarkdown']
    assert out['debug']['grounding']['mode'] == 'extractive_fallback'


def test_explicit_wrong_article_is_blocked_without_another_model_call(modules):
    runner, _, _ = modules
    deps = FakeDeps(understand=_understanding(lawRelevant=True),
                    synth='第九十九条について[L1]。')
    out, *_ = _run(runner, deps)
    assert '第九十九条' not in out['result']['answerMarkdown']
    assert out['debug']['grounding']['articleMismatches'] == ['L1']
    assert 'grounding' not in deps.purposes()


def test_failed_review_of_legal_only_answer_cannot_claim_it_is_answerable(modules):
    runner, _, _ = modules
    law = _law()
    law['text'] = '合成条文で設置時の届出を定めています。'
    deps = FakeDeps(understand=_understanding(intent='legal', lawRelevant=True), law=lambda q: _retrieval(law),
                    grounding='{"valid":false}', synth='届出は不要です[L1]。')
    out, *_ = _run(runner, deps, question='法令上の届出は必要ですか')
    assert out['kind'] == 'not_found'
    assert '不要です' not in out['result']['answerMarkdown']


def test_explicit_law_topic_cannot_be_lost_by_understanding(modules):
    understand = support.load_module('senpai_research_understand.py')
    value = understand.parse_understanding(json.dumps({'aspects': [{'kind': 'technical', 'question': '方式'}]}),
                                          '方式の違いと法令上の届出要否')
    assert any(a['kind'] == 'legal' for a in value['aspects'])


def test_fallback_completes_selected_excerpt_with_original_sentence(modules):
    _, _, grounding = modules
    body = '# 合成事例\n\n対象は方式甲。\n\n- 原因: ' + '合成の説明' * 40 + 'を確認した。\n- 別の操作候補。'
    quote = body[:200]
    result = grounding.extractive_answer(
        {'supported': [{'ref': 'K1', 'quote': quote, 'question': '原因'}]},
        {'knowhow': [{'ref': 'K1', 'body': body, 'title': '合成事例'}]})
    assert 'を確認した。' in result
    assert '別の操作候補' not in result
    assert '[K1]' in result and '未承認・参考' in result
    assert '現行の正式資料' in result


def test_fallback_includes_sentence_start_when_excerpt_begins_mid_sentence(modules):
    _, _, grounding = modules
    body = '前の文。対象条件を確認したうえで原因候補を照合する。次の文。'
    assert grounding._complete_quote('原因候補', {'text': body}) == '対象条件を確認したうえで原因候補を照合する。'


@pytest.mark.parametrize('quote', ['存在しない引用', 'あ' * 200])
def test_fallback_omits_unmatched_or_truncated_quote_and_reports_gap(modules, quote):
    _, _, grounding = modules
    result = grounding.extractive_answer(
        {'supported': [{'ref': 'T1', 'quote': quote, 'question': '合成の未確認論点'}]},
        {'tech': [{'ref': 'T1', 'text': 'あ' * 700, 'title': '合成資料'}]})
    assert '> ' not in result
    assert '完結した原文引用を確認できない論点: 合成の未確認論点' in result


def test_fallback_does_not_treat_sentence_mark_inside_unselected_later_text_as_visible(modules):
    _, _, grounding = modules
    assert grounding._complete_quote('あ' * 200, {'text': 'あ' * 600 + '。'}) is None
    assert grounding._complete_quote('文末。', {'text': '文末。'}) == '文末。'


def test_fallback_escapes_literal_source_and_preserves_missing_aspect(modules):
    _, _, grounding = modules
    body = '<script>合成の[T9]断片を確認。</script>'
    result = grounding.extractive_answer(
        {'supported': [{'ref': 'T1', 'quote': '断片を確認', 'question': '技術'}],
         'missing': [{'question': '法令は未確認'}]},
        {'tech': [{'ref': 'T1', 'text': body, 'title': '合成資料'}]})
    assert '<script>' not in result and '&#91;T9&#93;' in result
    assert '未確認の論点: 法令は未確認' in result
