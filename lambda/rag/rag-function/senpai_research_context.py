"""調査 1 件ぶんの作業状態（集めた根拠・検索語・道具の記録）。検索は 2 スレッドから書き込む。"""
import threading

import senpai_research_citations as citations
import senpai_research_text as text_util


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
        self.queries = {'tech': [], 'law': [], 'knowhow': ''}
        self.law_planned = False
        self._lock = threading.Lock()
        self._evidence = {'tech': [], 'law': []}
        self._seen_items = set()
        self._seen_docs = {'tech': set(), 'law': set()}
        self._tried = {}
        self._tools = []
        self._searches_ok = 0
        self._searches_failed = 0

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
                key = (kind, item['docKey'], item.get('pageNumber'), item.get('text'))
                if key in self._seen_items:
                    continue
                self._seen_items.add(key)
                self._evidence[kind].append(item)
                new_items += 1
                if item['docKey'] not in self._seen_docs[kind]:
                    self._seen_docs[kind].add(item['docKey'])
                    new_docs.add(item['docKey'])
        return len(new_docs), new_items

    def has_evidence(self) -> bool:
        with self._lock:
            return bool(self._evidence['tech'] or self._evidence['law'])

    def sources(self) -> dict:
        return citations.build_sources(self.evidence('tech'), self.evidence('law'), self.cards)

    def is_tried(self, tool: str, query: str) -> bool:
        with self._lock:
            return (tool, text_util.normalize_for_match(query)) in self._tried

    def mark_tried(self, tool: str, query: str) -> bool:
        """検索語を試し済みとして記録する。道具ごとに既に試していれば False（重複は拒否）。"""
        key = (tool, text_util.normalize_for_match(query))
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

    def debug(self) -> dict:
        """管理者向けの診断。質問や回答の本文は含めない（検索語・件数・時間のみ）。"""
        with self._lock:
            tools = [dict(entry) for entry in self._tools]
        return {
            'understandingRaw': {**(self.understanding or {}), 'fallback': self.fallback},
            'queries': {'tech': list(self.queries['tech']), 'law': list(self.queries['law']),
                        'knowhow': self.queries['knowhow']},
            'tools': sorted(tools, key=lambda entry: entry.get('seq') or 0),
            'budget': self.budget.snapshot(),
        }
