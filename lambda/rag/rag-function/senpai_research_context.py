"""調査 1 件ぶんの作業状態（集めた根拠・検索語・道具の記録）。検索は 2 スレッドから書き込む。"""
import hashlib
import json
import threading

import senpai_research_citations as citations
import senpai_research_text as text_util
from senpai_research_sufficiency import SNIPPET_CHARS
from senpai_research_errors import ResearchFailure


LANE_LABELS = {'tech': '技術資料', 'law': '法令'}


class RunContext:
    def __init__(self, job: dict, deps, recorder, budget):
        self.job = job
        self.deps = deps
        self.recorder = recorder
        self.budget = budget
        self.question = job['question']
        self.ui_model = job.get('modelType')
        self.understanding = None
        self.fallback = False
        self.model_type = None
        self.cards = []
        self.hints = []
        self.notes = []
        self.warnings = []
        self._failed_lanes = set()
        self.queries = {'tech': [], 'law': [], 'knowhow': ''}
        self.law_planned = False
        self._lock = threading.RLock()
        self._evidence = {'tech': [], 'law': []}
        self._seen_items = set()
        self._seen_docs = {'tech': set(), 'law': set()}
        self._tried = {}
        self._tools = []
        self._searches_ok = 0
        self._searches_failed = 0
        self.stages = []
        self.progress = []
        self.stop_detail = None
        self.last_judgment = 'unjudged'
        self.coverage = None
        self.grounding = {'mode': 'not_run'}

    @property
    def model_from_ui(self) -> bool:
        return bool(self.ui_model)

    def evidence(self, kind: str) -> list:
        with self._lock:
            return list(self._evidence[kind])

    def add_evidence(self, kind: str, items: list) -> tuple:
        """重複を除いて追加し、(新しい資料の数, 新しい断片の数) を返す。"""
        new_docs, new_items = set(), 0
        with self._lock:
            for item in items:
                key = (kind, *citations.evidence_key(item))
                if key in self._seen_items:
                    continue
                self._seen_items.add(key)
                self._evidence[kind].append(item)
                new_items += 1
                if item['docKey'] not in self._seen_docs[kind]:
                    self._seen_docs[kind].add(item['docKey'])
                    new_docs.add(item['docKey'])
        return len(new_docs), new_items

    def lane_failed(self, tool: str) -> None:
        """検索が全滅した道具を、まとめ（notes）と結果（warnings）に 1 回だけ伝える。"""
        label = LANE_LABELS[tool]
        with self._lock:
            if tool in self._failed_lanes:
                return
            self._failed_lanes.add(tool)
            self.notes.append(f'{label}の検索に失敗したため、{label}は確認できていません。')
            self.warnings.append(f'{label}の検索に失敗したため、{label}の根拠は含まれていません。')

    def has_evidence(self) -> bool:
        with self._lock:
            return bool(self._evidence['tech'] or self._evidence['law'])

    def add_measured_evidence(self, kind: str, items: list) -> tuple:
        """並列検索間で増分を二重帰属しないよう、追加前後の観測を一つのロック内で行う。"""
        with self._lock:
            before = self.exposed_fingerprints()
            docs, fragments = self.add_evidence(kind, items)
            return docs, fragments, len(self.exposed_fingerprints() - before)

    def sources(self) -> dict:
        return citations.build_sources(self.evidence('tech'), self.evidence('law'), self.cards)

    def _query_key(self, tool: str, query: str, scope) -> tuple:
        effective = ((self.model_type or '') if tool == 'tech' else '') if scope is None else scope
        return tool, text_util.normalize_for_match(query), effective

    def is_tried(self, tool: str, query: str, scope=None) -> bool:
        with self._lock:
            return self._query_key(tool, query, scope) in self._tried

    def mark_tried(self, tool: str, query: str, scope=None) -> bool:
        """検索語を試し済みとして記録する。道具ごとに既に試していれば False（重複は拒否）。"""
        key = self._query_key(tool, query, scope)
        with self._lock:
            if key in self._tried:
                return False
            self._tried[key] = query
            return True

    def tried_queries(self) -> list:
        with self._lock:
            return list(dict.fromkeys(self._tried.values()))

    def record_tool(self, entry: dict, *, failed: bool) -> None:
        with self._lock:
            self._tools.append(entry)
            if failed:
                self._searches_failed += 1
            else:
                self._searches_ok += 1

    def all_searches_failed(self) -> bool:
        with self._lock:
            return self._searches_failed > 0 and self._searches_ok == 0

    def add_query(self, tool: str, query: str) -> None:
        with self._lock:
            if query not in self.queries[tool]:
                self.queries[tool].append(query)

    def exposed_fingerprints(self) -> set:
        """次の判定に渡す内容の増分。順位・score・参照番号の変化は進捗としない。"""
        sources = self.sources()
        values = []
        for kind in ('tech', 'law', 'knowhow'):
            for item in sources[kind]:
                identity = (kind, item.get('docKey') or item.get('knowledgeId'), item.get('pageNumber'),
                            item.get('provision'), item.get('effectiveDate'))
                content = (item.get('body') or item.get('text') or '')[:SNIPPET_CHARS]
                values.append(hashlib.sha256(json.dumps((identity, content), ensure_ascii=False).encode()).hexdigest())
        return set(values)

    def call_model(self, purpose: str, system: str, user: str, max_tokens: int) -> str:
        """本文を診断へ複製せず、段階時間とusageだけを保存する。"""
        if not self.budget.input_allows(system, user):
            raise ResearchFailure('BudgetExceeded', 'モデル入力の上限に達しました。')
        started = self.budget.elapsed_ms()
        usage = {}
        completed = False
        try:
            measured = getattr(self.deps, 'call_model_with_usage', None)
            if measured:
                result, usage = measured(purpose, system, user, max_tokens)
            else:
                result = self.deps.call_model(purpose, system, user, max_tokens)
            completed = True
            return result
        finally:
            fields = ('inputTokens', 'outputTokens', 'cacheReadInputTokens', 'cacheWriteInputTokens')
            clean = {k: v for k, v in (usage or {}).items() if k in fields and type(v) is int and v >= 0}
            self.stages.append({'stage': purpose, 'ms': self.budget.elapsed_ms() - started,
                                'modelCalls': 1, 'usage': clean, 'usageMissing': not all(k in clean for k in fields),
                                'completed': completed})

    def debug(self) -> dict:
        """管理者向けの診断（検索語・件数・時間・整理結果）。回答の本文は含めない。

        検索語には利用者の質問そのもの（元の文での検索）と、モデルが整理した言い換えが入る。
        管理者にだけ返し、ジョブ行の TTL（7 日）で消える。CloudWatch には出さない。
        """
        with self._lock:
            tools = [dict(entry) for entry in self._tools]
        return {
            'understandingRaw': {**(self.understanding or {}), 'fallback': self.fallback},
            'queries': {'tech': list(self.queries['tech']), 'law': list(self.queries['law']),
                        'knowhow': self.queries['knowhow']},
            'tools': sorted(tools, key=lambda entry: entry.get('seq') or 0),
            'budget': self.budget.snapshot(),
            'stages': list(self.stages) + [
                {'stage': entry['tool'], **{key: entry[key] for key in (
                    'seq', 'ms', 'searchesCharged', 'selected', 'newCandidateItems',
                    'newExposedEvidence', 'evidenceValidity') if key in entry}}
                for entry in tools],
            'progress': list(self.progress),
            'stopDetail': self.stop_detail,
            'lastJudgment': self.last_judgment,
            'coverage': None if self.coverage is None else {
                'supported': [{k: item[k] for k in ('id', 'kind', 'status', 'ref')}
                              for item in self.coverage['supported']],
                'missing': [item['id'] for item in self.coverage['missing']]},
            'grounding': dict(self.grounding),
        }
