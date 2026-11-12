"""調査ジョブの本体: 整理 → ノウハウ → 技術・法令（同時）→ 十分性 → 再検索 → まとめ → 照合。

骨組みはコードが決め、AI が選ぶのは「足りないときの調べ直し方」だけ（型 B）。
検索とモデル呼び出しは deps（差し替え可能な部品）経由なので、この関数は AWS を直接呼ばない。
契約: docs/features/development/senpai-research-contract.md
"""
import senpai_research_citations as citations
import senpai_research_log as run_log
import senpai_research_search as search
import senpai_research_sufficiency as sufficiency
import senpai_research_synthesize as synthesize
import senpai_research_text as text_util
import senpai_research_understand as understand
import senpai_research_grounding as grounding
from senpai_research_context import RunContext
from senpai_research_errors import KnowhowUnavailable, ResearchFailure, TimeBudgetExceeded  # noqa: F401 (re-export)

MODEL_MAX_TOKENS = {'understand': 900, 'sufficiency': 1200, 'synthesize': 1800, 'grounding': 600}
TIMEOUT_ERROR_CODES = frozenset({'ModelTimeoutException', 'RequestTimeout', 'RequestTimeoutException'})
RAG_QUERY_MAX_LENGTH = 2000
MIN_SYNTH_MS = 8000  # これより残りが少ないときは、まとめを呼ばずに資料の一覧で返す

TIMEOUT_MESSAGE = 'まとめの作成が時間内に完了しませんでした。もう一度お試しください。'
INTERNAL_MESSAGE = '回答を作成できませんでした。時間をおいて再度お試しください。'
BUDGET_MESSAGE = '調査の上限に達したため、回答をまとめられませんでした。'
SEARCH_FAILED_MESSAGE = '資料の検索に失敗しました。時間をおいて再度お試しください。'

BUDGET_NOTE = '調査の上限に達したため、確認できた範囲での回答です。これ以上の検索は行っていません。'
JUDGMENT_NOTE = '根拠の十分性の判定が完了しなかったため、以下は取得候補に基づく暫定回答です。'


def _is_timeout(error: Exception) -> bool:
    code = (getattr(error, 'response', None) or {}).get('Error', {}).get('Code')
    return 'Timeout' in type(error).__name__ or code in TIMEOUT_ERROR_CODES


def _distinct(queries: list) -> list:
    seen, result = set(), []
    for query in queries:
        key = text_util.normalize_for_match(query)
        if query and key not in seen:
            seen.add(key)
            result.append(query)
    return result


# ---------------------------------------------------------------- 段階0: 整理

def _understand_detail(ctx: RunContext) -> str:
    if ctx.fallback:
        return '整理できなかったため元の質問で検索'
    parts = [ctx.model_type, ctx.understanding.get('part'), ctx.understanding.get('symptom'),
             ctx.understanding.get('situation')]
    return ' / '.join(part for part in parts if part) or '質問を整理しました'


def _call_understand(ctx: RunContext):
    if not ctx.budget.try_model_call(reserve=1):
        return None
    try:
        raw = ctx.call_model('understand', understand.SYSTEM_PROMPT,
                                  understand.build_user_text(ctx.question),
                                  MODEL_MAX_TOKENS['understand'])
        return understand.parse_understanding(raw, ctx.question)
    except Exception as error:  # noqa: BLE001 - 整理に失敗しても元の質問で続ける
        run_log.log('understand', 'error', error)
        return None


def _step_understand(ctx: RunContext) -> None:
    handle = ctx.recorder.begin('understand')
    parsed = _call_understand(ctx)
    ctx.fallback = parsed is None
    ctx.understanding = parsed or understand.fallback_understanding()
    if not ctx.understanding.get('aspects'):
        ctx.understanding['aspects'] = understand._aspects(None, ctx.question, ctx.understanding.get('intent'))
    ctx.model_type = understand.effective_model_type(ctx.ui_model, ctx.understanding, ctx.question)
    ctx.recorder.end(handle, 'done', detail=_understand_detail(ctx))


# ---------------------------------------------------------------- 段階1: ノウハウ

def _step_knowhow(ctx: RunContext) -> None:
    if not ctx.deps.knowhow_available:
        ctx.recorder.skip('knowhow', 'ノウハウ検索は無効です')
        return
    queries = _distinct([ctx.question, ctx.understanding['queries']['knowhow']])
    ctx.queries['knowhow'] = queries[-1]
    handle = ctx.recorder.begin('knowhow')
    started = ctx.budget.snapshot()
    completed = False
    try:
        if getattr(ctx.deps, 'knowhow_uses_remote', False):
            found = ctx.deps.search_knowhow(queries, ctx.model_type, claim_search=ctx.budget.try_search)
        else:
            found = ctx.deps.search_knowhow(queries, ctx.model_type)
        ctx.cards, ctx.hints = list(found['cards']), list(found['hints'])
        completed = True
    except Exception as error:  # noqa: BLE001 - ノウハウなしで調査を続ける
        run_log.log('knowhow', 'error', error)
        ctx.notes.append('ノウハウの索引を読み込めなかったため、事例は参照していません。')
        ctx.recorder.end(handle, 'failed', detail='ノウハウを読み込めませんでした')
        return
    finally:
        ended = ctx.budget.snapshot()
        ctx.stages.append({'stage': 'knowhow', 'ms': ended['elapsedMs'] - started['elapsedMs'],
                           'searches': ended['searchesUsed'] - started['searchesUsed'],
                           'selected': len(ctx.cards), 'completed': completed,
                           'evidenceValidity': 'unassessed'})
    count = len(ctx.cards)
    ctx.recorder.end(handle, 'done', detail=f'{count}件の事例メモ',
                     counts={'hits': count, 'selected': count, 'documents': count})


# ---------------------------------------------------------------- 段階2: 技術・法令を同時に

def _with_hints(question: str, hints: list) -> str:
    query = question
    for hint in hints:
        if len(query) + len(hint) + 1 <= RAG_QUERY_MAX_LENGTH:
            query = f'{query} {hint}'
    return query


def _law_skip_reason(ctx: RunContext):
    if not ctx.deps.law_available:
        return '法令検索は利用できません', '法令検索は行いませんでした（この環境では利用できません）。'
    if not ctx.understanding['lawRelevant']:
        return '法令に関係しない質問のため省略', '法令検索は行いませんでした（質問が法令に関係しないと判断したため）。'
    return None


def _claim_queries(ctx: RunContext, candidates: list) -> dict:
    """優先順（技術の原文 → 法令の原文 → 技術の整理語 → 法令の整理語）に検索回数を確保する。"""
    plan = {'tech': [], 'law': []}
    for tool, query in candidates:
        if not query or ctx.is_tried(tool, query):
            continue
        if not ctx.budget.try_search():
            break
        ctx.mark_tried(tool, query)
        ctx.add_query(tool, query)
        plan[tool].append(query)
    return plan


def _initial_candidates(ctx: RunContext, law_on: bool) -> list:
    queries = ctx.understanding['queries']
    tech_original = _with_hints(ctx.question, ctx.hints)
    law = [ctx.question, queries['law']] if law_on else [None, None]
    return [('tech', tech_original), ('law', law[0]), ('tech', queries['tech']), ('law', law[1])]


def _search_tasks(ctx: RunContext, plan: dict) -> list:
    tasks = []
    if plan['tech']:
        tasks.append(lambda: search.run_search_step(
            ctx, 'tech_search', 'tech', plan['tech'], detail=search.search_detail(plan['tech']),
            model_type=ctx.model_type))
    if plan['law']:
        tasks.append(lambda: search.run_search_step(
            ctx, 'law_search', 'law', plan['law'], detail=search.search_detail(plan['law'])))
    return tasks


def _step_initial_search(ctx: RunContext) -> None:
    skip = _law_skip_reason(ctx)
    plan = _claim_queries(ctx, _initial_candidates(ctx, law_on=skip is None))
    if skip:
        ctx.recorder.skip('law_search', skip[0])
        ctx.notes.append(skip[1])
    elif not plan['law']:
        ctx.recorder.skip('law_search', '検索回数の上限のため省略')
        ctx.notes.append('法令検索は行いませんでした（検索回数の上限のため）。')
    ctx.law_planned = bool(plan['law'])
    search.run_parallel(_search_tasks(ctx, plan))


# ---------------------------------------------------------------- 段階3: 十分性と調べ直し

def _directive_detail(directive) -> str:
    if directive is None:
        return '判断できなかったため現状の結果でまとめます'
    return {
        'none': '十分な根拠が揃っています' if directive['sufficient'] else '追加で調べる方法がありません',
        'retry_search': '言い換えて再検索します',
        'doc_page': '資料のページを確認します',
        'clarify': '確認が必要な点があります',
    }[directive['action']]


def _ask_sufficiency(ctx: RunContext, retries_left: int):
    handle = ctx.recorder.begin('sufficiency')
    directive = None
    try:
        user_text = sufficiency.build_user_text(
            question=ctx.question, understanding={
                **ctx.understanding, 'modelType': ctx.model_type,
                'extractedModelType': ctx.understanding.get('modelType')}, sources=ctx.sources(),
            tried_queries=ctx.tried_queries(), retries_left=retries_left)
        raw = ctx.call_model('sufficiency', sufficiency.SYSTEM_PROMPT, user_text,
                                  MODEL_MAX_TOKENS['sufficiency'])
        directive = sufficiency.parse_directive(raw)
        if directive is not None:
            ctx.coverage = sufficiency.assess_coverage(directive, ctx.understanding['aspects'], ctx.sources())
            directive['sufficient'] = directive['sufficient'] and ctx.coverage['complete']
    except ResearchFailure:
        ctx.recorder.end(handle, 'failed', detail='モデル入力の上限に達しました')
        raise
    except Exception as error:  # noqa: BLE001 - 判断できなければ現状の結果でまとめる
        run_log.log('sufficiency', 'error', error)
    if directive is None:
        ctx.notes.append('十分性を判断できなかったため、現状の結果でまとめています。')
    ctx.recorder.end(handle, 'done', detail=_directive_detail(directive))
    return directive


def _retry_targets(ctx: RunContext, directive: dict) -> list:
    wanted = {'tech': ['tech'], 'law': ['law'], 'both': ['tech', 'law']}[directive['target']]
    wanted = [tool for tool in wanted if tool == 'tech' or ctx.deps.law_available]
    scope = '' if directive['dropModelFilter'] and not ctx.model_from_ui else None
    return [tool for tool in wanted if not ctx.is_tried(tool, directive['query'], scope if tool == 'tech' else None)]


def _extra_retry_search(ctx: RunContext, directive: dict) -> str:
    targets = _retry_targets(ctx, directive)
    if not targets:
        return 'duplicate'
    query = directive['query']
    scope = '' if directive['dropModelFilter'] and not ctx.model_from_ui else None
    claimed = []
    for tool in targets:
        if not ctx.budget.try_search():
            break
        ctx.mark_tried(tool, query, scope if tool == 'tech' else None)
        ctx.add_query(tool, query)
        claimed.append(tool)
    if not claimed:
        return 'no_budget'
    drop_filter = directive['dropModelFilter'] and not ctx.model_from_ui
    model_type = None if drop_filter else ctx.model_type
    tasks = [
        (lambda tool=tool: search.run_search_step(
            ctx, 'retry_search', tool, [query], detail=search.search_detail([query], 'で再検索'),
            model_type=model_type if tool == 'tech' else None))
        for tool in claimed
    ]
    results = search.run_parallel(tasks)
    if all(result['failed'] for result in results):
        raise ResearchFailure('Internal', SEARCH_FAILED_MESSAGE)
    ctx.last_extra_items = sum(result['new_items'] for result in results)
    if any(result.get('timeSkipped') for result in results):
        return 'no_budget'
    return 'progress' if ctx.last_extra_items > 0 else 'no_new'


def _extra_doc_page(ctx: RunContext, directive: dict) -> str:
    name, page = directive['documentName'], directive['pageNumber']
    query = f'{name} {directive.get("query") or ""}'.strip()
    scope = (ctx.model_type, name, page)
    if ctx.is_tried('tech', query, scope):
        return 'duplicate'
    if not ctx.budget.try_search():
        return 'no_budget'
    ctx.mark_tried('tech', query, scope)
    ctx.add_query('tech', query)
    page_text = f' p.{page}' if page else ''
    result = search.run_search_step(
        ctx, 'doc_page', 'tech', [query], detail=f'『{name[:40]}』{page_text}を確認',
        model_type=ctx.model_type, evidence_filter=search.keep_document(name, page))
    ctx.last_extra_items = result['new_items']
    if result['failed']:
        raise ResearchFailure('Internal', SEARCH_FAILED_MESSAGE)
    if result.get('timeSkipped'):
        return 'no_budget'
    return 'progress' if result['new_items'] > 0 else 'no_new'


STOP_AFTER_EXTRA = {'duplicate': 'no_new_results', 'no_new': 'no_new_results', 'no_budget': 'budget'}


def _sufficiency_loop(ctx: RunContext) -> tuple:
    """進捗停止を優先し、回数・時間は有限の非常停止枠として残す。"""
    stagnant = 0
    while True:
        if not ctx.budget.time_allows_more():
            ctx.stop_detail = 'time_limit'
            return 'budget', None
        if not ctx.budget.try_model_call(reserve=1):
            ctx.stop_detail = ctx.budget.blocked_by
            return 'budget', None
        try:
            directive = _ask_sufficiency(ctx, ctx.budget.searches_left())
        except ResearchFailure:
            ctx.stop_detail = ctx.budget.blocked_by
            return 'budget', None
        if directive is None:
            ctx.last_judgment = 'unjudged'
            return 'judgment_failed', None
        ctx.last_judgment = 'sufficient' if directive['sufficient'] else 'insufficient'
        if directive['sufficient']:
            return 'sufficient', None
        if directive['action'] == 'clarify':
            return 'clarify', directive['clarifyQuestions']
        if directive['action'] == 'none':
            return 'partial' if ctx.coverage and ctx.coverage['partial'] else 'insufficient', None
        extra = _extra_retry_search if directive['action'] == 'retry_search' else _extra_doc_page
        before = ctx.exposed_fingerprints()
        started = ctx.budget.snapshot()
        ctx.last_extra_items = 0
        outcome = extra(ctx, directive)
        after = ctx.exposed_fingerprints()
        ended = ctx.budget.snapshot()
        gained = len(after - before)
        stagnant = stagnant + 1 if gained == 0 else 0
        ctx.progress.append({'round': len(ctx.progress) + 1, 'action': directive['action'],
                             'ms': ended['elapsedMs'] - started['elapsedMs'],
                             'searches': ended['searchesUsed'] - started['searchesUsed'],
                             'newCandidateItems': ctx.last_extra_items, 'newExposedEvidence': gained,
                             'evidenceValidity': 'unassessed', 'outcome': outcome})
        if outcome != 'progress':
            ctx.stop_detail = {'duplicate': 'repeated_query', 'no_new': 'repeated_results',
                               'no_budget': ctx.budget.blocked_by}[outcome]
            return STOP_AFTER_EXTRA[outcome], None
        if stagnant >= ctx.budget.no_progress_limit:
            ctx.stop_detail = 'no_exposed_progress'
            return 'no_new_results', None


# ---------------------------------------------------------------- 結果の組み立て

def _result(ctx: RunContext, *, kind: str, markdown: str, public_sources: dict,
            stop_reason: str, clarify_questions=(), unverified=()) -> dict:
    result = {
        'kind': kind,
        'answerMarkdown': markdown,
        'clarifyQuestions': list(clarify_questions),
        'sources': public_sources,
        'understanding': understand.public_understanding(ctx.understanding, model_type=ctx.model_type),
        'unverifiedRefs': list(unverified),
        'stopReason': stop_reason,
    }
    if ctx.warnings:  # 任意項目: 検索に失敗した道具があるときだけ
        result['warnings'] = list(ctx.warnings)
    return result


def _outcome(ctx: RunContext, result: dict) -> dict:
    return {'kind': result['kind'], 'result': result, 'debug': ctx.debug()}


def _clarify_outcome(ctx: RunContext, questions: list) -> dict:
    handle = ctx.recorder.begin('clarify')
    ctx.recorder.end(handle, 'done', detail=f'{len(questions)}件の確認事項')
    result = _result(
        ctx, kind='clarify', markdown=synthesize.clarify_markdown(questions),
        public_sources=citations.public_sources(ctx.sources(), cited=set()),
        stop_reason='clarify', clarify_questions=questions)
    return _outcome(ctx, result)


def _not_found_outcome(ctx: RunContext, stop_reason: str) -> dict:
    ctx.recorder.skip('synthesize', '根拠が見つからないため省略')
    ctx.recorder.skip('verify', '根拠が見つからないため省略')
    result = _result(
        ctx, kind='not_found', markdown=((BUDGET_NOTE + '\n\n') if stop_reason == 'budget' else '') +
        synthesize.not_found_markdown(),
        public_sources=citations.public_sources(ctx.sources(), cited=set()),
        stop_reason=stop_reason)
    return _outcome(ctx, result)


def _failure_from(error: Exception) -> ResearchFailure:
    if _is_timeout(error):
        return ResearchFailure('Timeout', TIMEOUT_MESSAGE)
    return ResearchFailure('Internal', INTERNAL_MESSAGE)


def _generate_answer(ctx: RunContext, sources: dict, stop_reason: str):
    """まとめの本文。残り時間が足りずモデルを呼べないときは None（資料の一覧で返す）。"""
    notes = list(ctx.notes) + ([BUDGET_NOTE] if stop_reason == 'budget' else [])
    if ctx.coverage and ctx.coverage['missing']:
        notes.append('次の論点は未確認。解決したと書かず、根拠を推論で補わない: ' +
                     ' / '.join(i['question'] for i in ctx.coverage['missing']))
    handle = ctx.recorder.begin('synthesize')
    if not ctx.budget.try_model_call():
        ctx.stop_detail = ctx.budget.blocked_by
        ctx.recorder.end(handle, 'failed', detail='モデル呼び出しの上限に達しました')
        return None
    try:
        text = ctx.call_model(
            'synthesize', synthesize.SYSTEM_PROMPT,
            synthesize.build_user_text(ctx.question, {'modelType': ctx.model_type}, sources, notes),
            MODEL_MAX_TOKENS['synthesize'])
    except TimeBudgetExceeded:
        run_log.log('synthesize', 'no_time')
        ctx.recorder.end(handle, 'failed', detail='時間が足りず、まとめを作れませんでした')
        return None
    except ResearchFailure:
        ctx.stop_detail = ctx.budget.blocked_by
        ctx.recorder.end(handle, 'failed', detail='モデル入力の上限に達しました')
        raise
    except Exception as error:  # noqa: BLE001 - 利用者には一般化した失敗として返す
        run_log.log('synthesize', 'error', error)
        ctx.recorder.end(handle, 'failed', detail='回答をまとめられませんでした')
        raise _failure_from(error) from error
    if not isinstance(text, str) or not text.strip():
        run_log.log('synthesize', 'empty')
        ctx.recorder.end(handle, 'failed', detail='回答が空でした')
        raise ResearchFailure('Internal', INTERNAL_MESSAGE)
    ctx.recorder.end(handle, 'done')
    return text.strip()


def _verify_answer(ctx: RunContext, text: str, sources: dict) -> dict:
    handle = ctx.recorder.begin('verify')
    verified = citations.verify_refs(text, sources)
    if not verified['cited']:
        ctx.grounding = {'mode': 'rejected', 'articleMismatches': []}
        ctx.recorder.end(handle, 'done', detail='根拠の参照を確認できませんでした')
        return verified
    mismatch = grounding.article_mismatches(verified['text'], sources)
    guard_reasons = grounding.guard_reasons(verified['text'])
    valid, mode = False, 'extractive_fallback'
    if ctx.coverage is None and not mismatch and not guard_reasons and not ctx.budget.time_allows_more():
        fallback = citations.verify_refs(synthesize.source_list_markdown(sources), sources)
        ctx.grounding = {'mode': 'source_list_only', 'articleMismatches': []}
        ctx.recorder.end(handle, 'done', detail='時間上限のため資料一覧のみ')
        return fallback
    if not mismatch and not guard_reasons and not verified['unverifiedRefs'] and ctx.budget.try_model_call():
        try:
            raw = ctx.call_model('grounding', grounding.SYSTEM_PROMPT,
                                 grounding.build_user_text(ctx.question, verified['text'], sources, ctx.coverage or {}),
                                 MODEL_MAX_TOKENS['grounding'])
            verdict = grounding.parse_verdict(raw)
            valid = verdict is not None and verdict['valid']
        except Exception as error:  # noqa: BLE001 - 未検証の生成文は返さない
            run_log.log('grounding', 'error', error)
    if valid:
        mode = 'model_verified'
    else:
        if ctx.coverage is None and not mismatch and not guard_reasons:
            fallback = citations.verify_refs(synthesize.source_list_markdown(sources), sources)
            ctx.grounding = {'mode': 'source_list_only', 'articleMismatches': []}
            ctx.recorder.end(handle, 'done', detail='根拠対応を検証できないため資料一覧のみ')
            return fallback
        if all(a['kind'] == 'legal' for a in ctx.understanding['aspects']):
            ctx.coverage = {'supported': [], 'missing': ctx.understanding['aspects'], 'complete': False, 'partial': False}
            mode = 'rejected'
        fallback = grounding.extractive_answer(ctx.coverage or {}, sources)
        fallback_verified = citations.verify_refs(fallback, sources)
        verified.update(text=fallback_verified['text'], cited=fallback_verified['cited'])
    ctx.grounding = {'mode': mode, 'articleMismatches': mismatch,
                     **({'guardReasons': guard_reasons} if guard_reasons else {})}
    removed = len(verified['unverifiedRefs'])
    if removed:
        detail = f'実在しない参照 {removed} 件を除去'
    elif verified['cited']:
        detail = f'{len(verified["cited"])}件の参照を確認'
    else:
        detail = '根拠の参照を確認できませんでした'
    ctx.recorder.end(handle, 'done', detail=detail)
    return verified


def _no_citation_outcome(ctx: RunContext, sources: dict, stop_reason: str, unverified: list) -> dict:
    """検証できた参照が 1 つもない回答は出さない（根拠なしの断定を画面に出さない）。"""
    result = _result(
        ctx, kind='not_found', markdown=synthesize.no_citation_markdown(),
        public_sources=citations.public_sources(sources, cited=set()),
        stop_reason=stop_reason, unverified=unverified)
    return _outcome(ctx, result)


def _answer_outcome(ctx: RunContext, stop_reason: str) -> dict:
    sources = ctx.sources()
    if ctx.coverage is None and all(a['kind'] == 'legal' for a in ctx.understanding['aspects']):
        return _not_found_outcome(ctx, stop_reason)
    if ctx.coverage is not None:
        if not ctx.coverage['supported']:
            return _not_found_outcome(ctx, stop_reason)
        if ctx.coverage['partial']:
            stop_reason = 'partial'
            if any(item['kind'] == 'legal' for item in ctx.coverage['missing']):
                sources = {**sources, 'law': []}
    if stop_reason in ('insufficient', 'no_new_results') or not (
            sources['tech'] or sources['law'] or sources['knowhow']):
        return _not_found_outcome(ctx, stop_reason)
    text = None
    if ctx.budget.remaining_ms() >= MIN_SYNTH_MS:
        text = _generate_answer(ctx, sources, stop_reason)
    else:
        ctx.recorder.skip('synthesize', '時間が足りないため省略')
    source_list_only = text is None
    if source_list_only:
        # 時間切れ: 見つかった資料の一覧（参照つき）を返す。推測は書かない。
        text, stop_reason = synthesize.source_list_markdown(sources), 'budget'
    if stop_reason == 'judgment_failed':
        text = f'{JUDGMENT_NOTE}\n\n{text}'
    if stop_reason == 'budget':
        text = f'{BUDGET_NOTE}\n\n{text}'
    text = citations.strip_links(text)
    if source_list_only:
        verified = citations.verify_refs(text, sources)
        ctx.grounding = {'mode': 'source_list_only', 'articleMismatches': []}
        ctx.recorder.skip('verify', '資料の一覧のみ。技術的な回答は生成していません')
    else:
        verified = _verify_answer(ctx, text, sources)
    if not verified['cited']:
        return _no_citation_outcome(ctx, sources, stop_reason, verified['unverifiedRefs'])
    if ctx.coverage is not None and not ctx.coverage['supported']:
        result = _result(ctx, kind='not_found', markdown=synthesize.not_found_markdown(),
                         public_sources=citations.public_sources(ctx.sources(), cited=set()), stop_reason='insufficient')
        ctx.last_judgment = 'insufficient'
        return _outcome(ctx, result)
    if stop_reason == 'partial':
        verified['text'] = '一部の論点についての参考回答です。未確認の論点は解決していません。\n\n' + verified['text']
    result = _result(
        ctx, kind='answer', markdown=verified['text'].strip(),
        public_sources=citations.public_sources(sources, cited=verified['cited']),
        stop_reason=stop_reason, unverified=verified['unverifiedRefs'])
    return _outcome(ctx, result)


def run_research(job: dict, deps, recorder, budget) -> dict:
    """調査を実行して {'kind', 'result', 'debug'} を返す。失敗は ResearchFailure（debug 付き）。"""
    ctx = RunContext(job, deps, recorder, budget)
    try:
        _step_understand(ctx)
        _step_knowhow(ctx)
        _step_initial_search(ctx)
        if ctx.all_searches_failed():
            raise ResearchFailure('Internal', SEARCH_FAILED_MESSAGE)
        stop_reason, questions = _sufficiency_loop(ctx)
        if questions:
            return _clarify_outcome(ctx, questions)
        return _answer_outcome(ctx, stop_reason)
    except ResearchFailure as failure:
        failure.debug = ctx.debug()
        raise
