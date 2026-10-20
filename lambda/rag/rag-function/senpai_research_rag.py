"""既存の RAG（app.py）の検索・選別・生成・ノウハウを、調査ジョブの部品（deps）につなぐ。

app.py は編集せず import して再利用する（import 時に boto3 クライアントを作る副作用があるため、
最初に使うときまで読み込まない）。ここで KB の生の結果を、出典に使える最小の根拠データへ変換する。
"""
import os

import senpai_research_errors as errors
from senpai_research_errors import KnowhowUnavailable  # noqa: F401 (re-export)

CHUNK_TEXT_MAX_CHARS = 1200
KNOWHOW_MAX_CARDS = 3
SMALL_MODEL_PURPOSES = frozenset({'understand', 'sufficiency'})
_state = {'app': None}


def set_app(module) -> None:
    """テスト用: app.py の代わりに読み込み済みのモジュールを使う。"""
    _state['app'] = module


def get_app():
    if _state['app'] is None:
        import app  # noqa: PLC0415 - 副作用が大きいので遅延 import
        _state['app'] = app
    return _state['app']


def _tech_evidence(app, result: dict):
    metadata = result.get('metadata') or {}
    uri = metadata.get(app.KB_PROFILE.source_uri_key) or ''
    name = uri.split('/')[-1]
    # RAG と同じ規則: .md は参考資料として見せない。開けない出典（許可外）は引用に使わない。
    if not uri or name.lower().endswith('.md') or not app.is_allowed_document_uri(uri):
        return None
    return {
        'kind': 'tech', 'docKey': uri, 'documentName': name,
        'title': metadata.get('title') or name,
        'pageNumber': app.extract_page_number(metadata), 'sourceUri': uri,
        'text': app.chunk_text(result).strip()[:CHUNK_TEXT_MAX_CHARS],
        'score': float(result.get('score') or 0.0),
    }


def _law_evidence(app, result: dict):
    _citations, documents = app.extract_law_citations([result])
    if not documents:  # e-Gov の出典 URL が確認できない条文は引用しない
        return None
    law = documents[0]['lawCitation']
    return {
        'kind': 'law', 'docKey': law['sourceUrl'], 'lawTitle': law.get('lawTitle'),
        'lawNumber': law.get('lawNumber'),
        'provision': law.get('provisionReference') or law.get('provisionType'),
        'effectiveDate': law.get('effectiveDate'), 'sourceUrl': law['sourceUrl'],
        'text': (result.get('_lawReferenceText') or app.chunk_text(result)).strip(),
        'score': float(result.get('score') or 0.0),
    }


def _retrieval(hits: int, selected: list, evidence: list) -> dict:
    return {'hits': hits, 'evidence': evidence,
            'topScores': [float(r.get('score') or 0.0) for r in selected[:3]]}


class RagDeps:
    """runner が使う部品の本番実装。"""

    @property
    def law_available(self) -> bool:
        app = get_app()
        return app.law_rag_is_enabled(app.ENVIRONMENT, app.LAW_RAG_ENABLED, app.LAW_KNOWLEDGE_BASE_ID)

    @property
    def knowhow_available(self) -> bool:
        app = get_app()
        return bool(
            app.KNOWHOW_ENABLED and app.KNOWHOW_INDEX_BUCKET and app.KNOWHOW_INDEX_KEY
            and app.KNOWHOW_INDEX_BUCKET not in (app.DOCUMENTS_BUCKET, app.KB_SOURCE_BUCKET)
        )

    def call_model(self, purpose: str, system_prompt: str, user_text: str, max_tokens: int) -> str:
        app = get_app()
        small = os.environ.get('SENPAI_UNDERSTAND_MODEL_ID', '').strip() or app.BEDROCK_MODEL_ID
        model_id = small if purpose in SMALL_MODEL_PURPOSES else app.BEDROCK_MODEL_ID
        text, _usage, _stop = app.invoke_generation(
            app.bedrock_runtime, model_id, system_prompt,
            [{'role': 'user', 'content': user_text}],
            max_tokens=max_tokens, apply_generation_settings=purpose == 'synthesize',
            ensure_ascii=False, call_name=purpose,
        )
        return text

    def search_knowhow(self, queries: list, model_type) -> dict:
        app = get_app()
        try:
            index = app.load_index(bucket=app.KNOWHOW_INDEX_BUCKET, key=app.KNOWHOW_INDEX_KEY)
            matches = {}
            for query in queries:
                for card in app.search_index(index, query, model_type=model_type)['matches']:
                    matches.setdefault(card['knowledgeId'], card)
        except app.KnowhowIndexError as error:
            raise errors.KnowhowUnavailable('knowhow index unavailable') from error
        cards = list(matches.values())[:KNOWHOW_MAX_CARDS]
        return {
            'status': 'matched' if cards else 'not_found',
            'cards': [
                {'knowledgeId': c['knowledgeId'], 'cardVersion': c['cardVersion'], 'title': c['title'],
                 'status': c['status'], 'modelFit': c.get('modelFit') or 'unknown', 'body': c['body']}
                for c in cards
            ],
            'hints': app.derive_kb_hints(cards),
        }

    def _retrieve_tech(self, app, query: str, filters: dict) -> list:
        response = app.retrieve_for_normal_query(query, filters, number_of_results=30)
        return response.get('retrievalResults', []) or []

    def search_tech(self, query: str, model_type, claim_search=None) -> dict:
        app = get_app()
        filters = {'modelType': model_type} if model_type else {}
        normalized = app.normalize_query_text(query) or query
        results = self._retrieve_tech(app, normalized, filters)
        selected = app.select_retrieval_results(results, mode='normal', rank_key=app.RERANK_RANK_KEY)
        expanded = app.expand_query_abbreviations(normalized)
        # RAG と同じ規則: 何も選ばれなかったときだけ略語を展開して再検索（予算を確保できたときのみ）
        if not selected and expanded and expanded != normalized and claim_search and claim_search():
            results = app.merge_retrieval_results(results, self._retrieve_tech(app, expanded, filters))
            selected = app.select_retrieval_results(results, mode='normal', rank_key=app.RERANK_RANK_KEY)
        evidence = [e for e in (_tech_evidence(app, r) for r in selected) if e]
        return _retrieval(len(results), selected, evidence)

    def search_law(self, query: str, claim_search=None) -> dict:
        app = get_app()
        normalized = app.normalize_query_text(query) or query
        results = app.query_law_knowledge_base(normalized).get('retrievalResults', []) or []
        selected = app.select_retrieval_results(results, mode='law', rank_key=app.RERANK_RANK_KEY)
        prepared = app.prepare_law_references(selected)
        evidence = [e for e in (_law_evidence(app, r) for r in prepared) if e]
        return _retrieval(len(results), selected, evidence)
