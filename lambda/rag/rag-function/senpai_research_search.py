"""検索の実行と段階イベント（tech_search / law_search / retry_search / doc_page）の記録。"""
from concurrent.futures import ThreadPoolExecutor

import senpai_research_log as run_log
import senpai_research_text as text_util

DETAIL_QUERY_CHARS = 40


def _quoted(query: str) -> str:
    return f'『{query[:DETAIL_QUERY_CHARS]}』'


def search_detail(queries: list, suffix: str = 'で検索') -> str:
    if len(queries) == 1:
        return f'{_quoted(queries[0])}{suffix}'
    return f'{_quoted(queries[0])}など{len(queries)}件の検索語{suffix}'


def keep_document(document_name: str, page_number):
    """doc_page 用: 指定資料の断片だけを残す（ページが分かれば、そのページを優先）。"""
    wanted = text_util.normalize_for_match(document_name)

    def apply(evidence: list) -> list:
        same_document = [
            item for item in evidence
            if text_util.normalize_for_match(item.get('documentName')) == wanted
        ]
        if page_number is None:
            return same_document
        on_page = [item for item in same_document if item.get('pageNumber') == page_number]
        return on_page or same_document

    return apply


def _call_tool(ctx, tool: str, query: str, model_type):
    if tool == 'tech':
        return ctx.deps.search_tech(query, model_type, claim_search=ctx.budget.try_search)
    return ctx.deps.search_law(query, claim_search=ctx.budget.try_search)


def _search_one(ctx, step_seq, tool: str, query: str, model_type, evidence_filter) -> dict:
    """1 回の検索。失敗しても例外は外へ出さず、結果に failed として載せる。"""
    started = ctx.budget.elapsed_ms()
    failed, retrieval = False, {'hits': 0, 'evidence': [], 'topScores': []}
    try:
        retrieval = _call_tool(ctx, tool, query, model_type)
    except Exception as error:  # noqa: BLE001 - 検索 1 本の失敗で調査全体を止めない
        failed = True
        run_log.log('search', 'error', error, tool=tool)
    evidence = retrieval['evidence']
    if evidence_filter is not None:
        evidence = evidence_filter(evidence)
    new_docs, new_items = ctx.add_evidence(tool, evidence)
    ctx.record_tool({
        'seq': step_seq, 'tool': f'{tool}_search', 'query': query,
        'filters': {'modelType': model_type} if (tool == 'tech' and model_type) else {},
        'hits': retrieval['hits'], 'selected': len(evidence),
        'topScores': list(retrieval['topScores'][:3]),
        'ms': ctx.budget.elapsed_ms() - started,
        **({'error': True} if failed else {}),
    }, failed=failed)
    return {'failed': failed, 'hits': retrieval['hits'], 'evidence': evidence,
            'new_docs': new_docs, 'new_items': new_items}


def run_search_step(ctx, step: str, tool: str, queries: list, *, detail: str,
                    model_type=None, evidence_filter=None) -> dict:
    """検索語を順に実行し、段階イベントの前後を記録する。集計を返す。"""
    handle = ctx.recorder.begin(step, detail)
    results = [
        _search_one(ctx, handle['seq'], tool, query, model_type, evidence_filter)
        for query in queries
    ]
    unique = {(item['docKey'], item.get('pageNumber'), item.get('text'))
              for result in results for item in result['evidence']}
    documents = {key[0] for key in unique}
    summary = {
        'failed': all(result['failed'] for result in results),
        'new_docs': sum(result['new_docs'] for result in results),
        'new_items': sum(result['new_items'] for result in results),
    }
    counts = {'hits': sum(result['hits'] for result in results),
              'selected': len(unique),
              'documents': len(documents)}
    if summary['failed']:
        ctx.recorder.end(handle, 'failed', detail='検索に失敗しました', counts=counts)
    else:
        ctx.recorder.end(handle, 'done', counts=counts)
    return summary


def run_parallel(tasks: list) -> list:
    """技術と法令の検索を同時に実行する（それぞれ内部は順次）。"""
    if len(tasks) <= 1:
        return [task() for task in tasks]
    with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
        futures = [pool.submit(task) for task in tasks]
        return [future.result() for future in futures]
