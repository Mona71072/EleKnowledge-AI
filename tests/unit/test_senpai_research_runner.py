"""調査の流れ（整理 → ノウハウ → 技術・法令 → 十分性 → 再検索 → まとめ → 照合）の契約テスト。

検索・モデル呼び出しは差し替え可能な部品（deps）に分かれているので、ここでは台本どおりに
動く偽物で、段階イベントの順序・予算・停止理由・照合を確認する。
"""
import json
import threading

import pytest

import test_senpai_research_support as support

QUESTION = "LINKsのドアが開閉時に異音。固有質問ZZZQ"


@pytest.fixture(scope="module")
def runner():
    return support.load_module("senpai_research_runner.py")


# ---------------------------------------------------------------- 偽物

def _tech(doc, page, text="技術本文", score=0.7):
    return {"kind": "tech", "docKey": f"s3://kb-docs-bucket/docs/{doc}", "documentName": doc, "title": doc,
            "pageNumber": page, "sourceUri": f"s3://kb-docs-bucket/docs/{doc}", "text": text, "score": score}


def _law(provision="第三十五条", score=0.6):
    return {"kind": "law", "docKey": f"https://laws.e-gov.go.jp/{provision}", "lawTitle": "建築基準法",
            "lawNumber": "法律第二百一号", "provision": provision, "effectiveDate": "2025-04-01",
            "sourceUrl": f"https://laws.e-gov.go.jp/{provision}", "text": "法令本文", "score": score}


def _retrieval(*evidence, hits=None):
    return {"hits": hits if hits is not None else len(evidence), "evidence": list(evidence),
            "topScores": [e["score"] for e in evidence][:3]}


def _card(kid="KH-AX-001", title="ドア異音"):
    return {"knowledgeId": kid, "cardVersion": 2, "title": title, "status": "draft",
            "modelFit": "matched", "body": "## 症状\n異音"}


def _understanding(**overrides):
    base = {"modelType": "AXIEZ-LINKs", "modelEvidence": "LINKs", "controlMethod": None,
            "part": "ドア", "symptom": "異音", "situation": "開閉時", "intent": "cause",
            "lawRelevant": False,
            "queries": {"tech": "AXIEZ-LINKs ドア 開閉 異音", "law": "", "knowhow": "ドア 異音"},
            "missing": []}
    base.update(overrides)
    return json.dumps(base, ensure_ascii=False)


def _directive(**kw):
    return json.dumps(kw, ensure_ascii=False)


SUFFICIENT = _directive(sufficient=True, action="none")
GOOD_ANSWER = "## 結論の候補\nドアの調整を確認します[T1]。\n## 法令から\nなし\n## ノウハウ（未承認・参考）\n類似事例[K1]"


class FakeDeps:
    def __init__(self, *, understand=None, sufficiency=None, synth=GOOD_ANSWER,
                 tech=None, law=None, cards=None, hints=(), law_available=True,
                 knowhow_available=True, knowhow_error=None):
        self.responses = {
            "understand": list(understand) if isinstance(understand, list) else [understand or _understanding()],
            "sufficiency": list(sufficiency) if isinstance(sufficiency, list) else [sufficiency or SUFFICIENT],
            "synthesize": [synth],
        }
        self.tech = tech if tech is not None else (lambda q, m: _retrieval(_tech("TI-1.pdf", 3)))
        self.law = law if law is not None else (lambda q: _retrieval(_law()))
        self.cards = [_card()] if cards is None else cards
        self.hints = list(hints)
        self.law_available = law_available
        self.knowhow_available = knowhow_available
        self.knowhow_error = knowhow_error
        self.model_calls = []
        self.tech_calls = []
        self.law_calls = []
        self.knowhow_calls = []
        self._lock = threading.Lock()

    def call_model(self, purpose, system, user, max_tokens):
        with self._lock:
            self.model_calls.append((purpose, user))
            queue = self.responses[purpose]
            item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        return item

    def search_knowhow(self, queries, model_type):
        self.knowhow_calls.append((list(queries), model_type))
        if self.knowhow_error:
            raise self.knowhow_error
        return {"status": "matched" if self.cards else "not_found", "cards": list(self.cards),
                "hints": list(self.hints)}

    def search_tech(self, query, model_type, claim_search=None):
        with self._lock:
            self.tech_calls.append((query, model_type))
        result = self.tech(query, model_type)
        if isinstance(result, Exception):
            raise result
        return result

    def search_law(self, query, claim_search=None):
        with self._lock:
            self.law_calls.append(query)
        result = self.law(query)
        if isinstance(result, Exception):
            raise result
        return result

    def purposes(self):
        return [purpose for purpose, _ in self.model_calls]


class Ticker:
    """読むたびに進む単調時計（秒）。モデル呼び出しなどでテストが明示的に進める。"""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def _setup(runner, deps, *, limits=None, model_type=None, question=QUESTION):
    config = support.load_module("senpai_research_config.py")
    budget_mod = support.load_module("senpai_research_budget.py")
    recorder_mod = support.load_module("senpai_research_recorder.py")
    limits = limits or config.BudgetLimits(max_searches=6, max_model_calls=4, job_ms=60000,
                                           synth_reserve_ms=20000)
    clock = Ticker()
    budget = budget_mod.Budget(limits, clock=clock)
    events = []
    recorder = recorder_mod.StepRecorder(lambda event: events.append(event) or True)
    job = {"jobId": "j1", "question": question, "modelType": model_type}
    return job, budget, recorder, events, clock


def _run(runner, deps, **kw):
    job, budget, recorder, events, clock = _setup(runner, deps, **kw)
    outcome = runner.run_research(job, deps, recorder, budget)
    return outcome, events, budget, clock


def _flow(events, exclude=("tech_search", "law_search")):
    return [(e["step"], e["status"]) for e in events if e["step"] not in exclude]


# ---------------------------------------------------------------- 正常系

def test_happy_path_emits_ordered_events_with_monotonic_seq(runner):
    deps = FakeDeps(understand=_understanding(lawRelevant=True))
    outcome, events, _budget, _clock = _run(runner, deps)

    assert [e["seq"] for e in events] == list(range(1, len(events) + 1))
    assert _flow(events) == [
        ("understand", "running"), ("understand", "done"),
        ("knowhow", "running"), ("knowhow", "done"),
        ("sufficiency", "running"), ("sufficiency", "done"),
        ("synthesize", "running"), ("synthesize", "done"),
        ("verify", "running"), ("verify", "done"),
    ]
    # 技術と法令は、整理・ノウハウの後に始まり、十分性の前に終わる
    index = {(e["step"], e["status"]): e["seq"] for e in events}
    assert index[("tech_search", "running")] > index[("knowhow", "done")]
    assert index[("law_search", "running")] > index[("knowhow", "done")]
    assert index[("tech_search", "done")] < index[("sufficiency", "running")]
    assert index[("law_search", "done")] < index[("sufficiency", "running")]
    assert deps.purposes() == ["understand", "sufficiency", "synthesize"]

    result = outcome["result"]
    assert result["kind"] == "answer" and result["stopReason"] == "sufficient"
    assert result["unverifiedRefs"] == [] and result["clarifyQuestions"] == []
    assert result["understanding"]["part"] == "ドア"
    assert [t["ref"] for t in result["sources"]["tech"]] == ["T1"]
    assert [k["ref"] for k in result["sources"]["knowhow"]["used"]] == ["K1"]


def test_each_event_has_label_times_and_counts(runner):
    outcome, events, *_ = _run(runner, FakeDeps(understand=_understanding(lawRelevant=True)))
    by_key = {(e["step"], e["status"]): e for e in events}
    running = by_key[("tech_search", "running")]
    done = by_key[("tech_search", "done")]
    assert running["labelJa"] == "技術資料を検索中"
    assert running["endedAt"] is None and done["endedAt"]
    assert done["startedAt"] == running["startedAt"]
    assert done["counts"] == {"hits": 2, "selected": 1, "documents": 1}  # 2本の検索で同じ断片が1件
    assert by_key[("law_search", "done")]["labelJa"] == "法令を確認中"
    assert by_key[("synthesize", "running")]["labelJa"] == "回答をまとめています"
    assert by_key[("verify", "running")]["labelJa"] == "根拠を照合中"
    assert all(len(e.get("detailJa") or "") <= 120 for e in events)


def test_debug_payload_has_queries_tools_and_budget(runner):
    outcome, events, budget, _clock = _run(runner, FakeDeps(understand=_understanding(lawRelevant=True)))
    debug = outcome["debug"]
    assert debug["understandingRaw"]["part"] == "ドア"
    assert QUESTION in debug["queries"]["tech"]
    assert "AXIEZ-LINKs ドア 開閉 異音" in debug["queries"]["tech"]
    assert debug["queries"]["law"] == [QUESTION]
    assert debug["queries"]["knowhow"] == "ドア 異音" or QUESTION in debug["queries"]["knowhow"]
    tools = {t["tool"]: t for t in debug["tools"]}
    assert set(tools) == {"tech_search"} | ({"law_search"} if "law_search" in tools else set())
    first = debug["tools"][0]
    assert {"seq", "tool", "query", "filters", "hits", "selected", "topScores", "ms"} <= set(first)
    assert first["filters"] == {"modelType": "AXIEZ-LINKs"}
    assert debug["budget"]["searchesMax"] == 6 and debug["budget"]["modelCallsMax"] == 4
    assert debug["budget"]["modelCallsUsed"] == 3 and debug["budget"]["searchesUsed"] >= 2


# ---------------------------------------------------------------- 質問の整理

def test_original_question_and_rewritten_queries_are_both_searched(runner):
    deps = FakeDeps()
    _run(runner, deps)
    queries = [q for q, _ in deps.tech_calls]
    assert QUESTION in queries and "AXIEZ-LINKs ドア 開閉 異音" in queries
    assert len(queries) == len(set(queries))


def test_identical_rewrite_is_not_searched_twice(runner):
    same = _understanding(queries={"tech": QUESTION, "law": "", "knowhow": QUESTION})
    deps = FakeDeps(understand=same)
    _run(runner, deps)
    assert [q for q, _ in deps.tech_calls] == [QUESTION]


def test_unparseable_understanding_falls_back_to_original_question(runner):
    deps = FakeDeps(understand="すみません、整理できません")
    outcome, events, *_ = _run(runner, deps)
    done = next(e for e in events if e["step"] == "understand" and e["status"] == "done")
    assert done["detailJa"] == "整理できなかったため元の質問で検索"
    assert [q for q, _ in deps.tech_calls] == [QUESTION]
    assert deps.law_calls == [QUESTION]  # 整理できないときは法令を省略しない
    assert outcome["result"]["understanding"]["modelType"] is None
    assert outcome["debug"]["understandingRaw"]["fallback"] is True


def test_understand_model_error_falls_back_gracefully(runner):
    deps = FakeDeps(understand=TimeoutError("read timeout"))
    outcome, events, *_ = _run(runner, deps)
    assert outcome["result"]["kind"] == "answer"
    assert ("understand", "done") in _flow(events)


def test_ui_model_type_wins_over_understanding(runner):
    deps = FakeDeps()
    _run(runner, deps, model_type="NEXCUBE")
    assert {m for _, m in deps.tech_calls} == {"NEXCUBE"}
    assert deps.knowhow_calls[0][1] == "NEXCUBE"


def test_model_type_without_evidence_is_not_invented(runner):
    invented = _understanding(modelType="NEXCUBE", modelEvidence="ネクスキューブ")
    deps = FakeDeps(understand=invented)
    outcome, *_ = _run(runner, deps)
    assert {m for _, m in deps.tech_calls} == {None}
    assert outcome["result"]["understanding"]["modelType"] is None


# ---------------------------------------------------------------- ノウハウ

def test_knowhow_hints_are_appended_to_the_original_query(runner):
    deps = FakeDeps(hints=["TI-2024-017"])
    _run(runner, deps)
    original = next(q for q, _ in deps.tech_calls if q.startswith(QUESTION))
    assert original == f"{QUESTION} TI-2024-017"


def test_knowhow_unavailable_is_reported_and_search_continues(runner):
    support_mod = support.load_module("senpai_research_runner.py")
    deps = FakeDeps(knowhow_error=support_mod.KnowhowUnavailable("index"), synth="## 結論の候補\n資料[T1]")
    outcome, events, *_ = _run(runner, deps)
    failed = next(e for e in events if e["step"] == "knowhow" and e["status"] == "failed")
    assert "ノウハウ" in failed["detailJa"]
    assert outcome["result"]["kind"] == "answer"
    assert outcome["result"]["sources"]["knowhow"] == {"used": [], "candidates": []}


def test_knowhow_disabled_is_skipped(runner):
    deps = FakeDeps(knowhow_available=False, cards=[], synth="## 結論の候補\n資料[T1]")
    _outcome, events, *_ = _run(runner, deps)
    assert ("knowhow", "skipped") in _flow(events)
    assert deps.knowhow_calls == []


def test_knowhow_used_and_candidates_follow_citations(runner):
    deps = FakeDeps(cards=[_card("KH-1", "引用される"), _card("KH-2", "引用されない")],
                    synth="結論[T1] 事例[K1]")
    outcome, *_ = _run(runner, deps)
    knowhow = outcome["result"]["sources"]["knowhow"]
    assert [c["knowledgeId"] for c in knowhow["used"]] == ["KH-1"]
    assert [c["knowledgeId"] for c in knowhow["candidates"]] == ["KH-2"]


def test_no_knowhow_cited_leaves_used_empty(runner):
    deps = FakeDeps(synth="結論[T1]")
    outcome, *_ = _run(runner, deps)
    assert outcome["result"]["sources"]["knowhow"]["used"] == []
    assert len(outcome["result"]["sources"]["knowhow"]["candidates"]) == 1


# ---------------------------------------------------------------- 法令

def test_law_search_is_skipped_when_understanding_says_irrelevant(runner):
    deps = FakeDeps()  # lawRelevant False
    outcome, events, *_ = _run(runner, deps)
    skipped = next(e for e in events if e["step"] == "law_search")
    assert skipped["status"] == "skipped" and "法令" in skipped["detailJa"]
    assert deps.law_calls == []
    synth_user = next(u for p, u in deps.model_calls if p == "synthesize")
    assert "法令検索は行いませんでした" in synth_user
    assert outcome["result"]["sources"]["law"] == []


def test_law_search_is_skipped_when_not_configured(runner):
    deps = FakeDeps(understand=_understanding(lawRelevant=True), law_available=False)
    _outcome, events, *_ = _run(runner, deps)
    assert next(e for e in events if e["step"] == "law_search")["status"] == "skipped"
    assert deps.law_calls == []


def test_law_results_are_cited_with_l_refs(runner):
    deps = FakeDeps(understand=_understanding(lawRelevant=True, queries={"tech": "", "law": "昇降機 構造", "knowhow": ""}),
                    synth="技術[T1]。法令は第三十五条[L1]。")
    outcome, *_ = _run(runner, deps)
    assert sorted(deps.law_calls) == sorted([QUESTION, "昇降機 構造"])
    assert outcome["result"]["sources"]["law"][0]["provision"] == "第三十五条"


# ---------------------------------------------------------------- 十分性と再検索

def _retry(query, target="tech"):
    return _directive(sufficient=False, action="retry_search", query=query, target=target)


def test_retry_search_adds_new_documents_then_finishes(runner):
    calls = {"n": 0}

    def tech(query, model):
        calls["n"] += 1
        return _retrieval(_tech("TI-1.pdf", 3)) if "調整" not in query else _retrieval(_tech("TI-9.pdf", 1))

    deps = FakeDeps(tech=tech, sufficiency=[_retry("ドア 調整"), SUFFICIENT],
                    synth="結論[T1][T2]")
    outcome, events, *_ = _run(runner, deps)
    assert _flow(events).count(("retry_search", "running")) == 1
    assert _flow(events).count(("sufficiency", "done")) == 2
    assert deps.purposes() == ["understand", "sufficiency", "sufficiency", "synthesize"]
    assert outcome["result"]["stopReason"] == "sufficient"
    assert {s["documentName"] for s in outcome["result"]["sources"]["tech"]} == {"TI-1.pdf", "TI-9.pdf"}
    retry_event = next(e for e in events if e["step"] == "retry_search" and e["status"] == "done")
    assert "ドア 調整" in retry_event["detailJa"] and retry_event["counts"]["documents"] == 1


def test_duplicate_retry_query_is_rejected_without_searching(runner):
    deps = FakeDeps(sufficiency=[_retry("AXIEZ-LINKs ドア 開閉 異音")])
    outcome, events, *_ = _run(runner, deps)
    assert outcome["result"]["stopReason"] == "no_new_results"
    assert ("retry_search", "running") not in _flow(events)
    assert len(deps.tech_calls) == 2  # 初回の2本だけ（原文 + 整理語）
    assert deps.purposes() == ["understand", "sufficiency", "synthesize"]


def test_retry_with_no_new_documents_stops(runner):
    deps = FakeDeps(sufficiency=[_retry("まったく別の言い方")])  # 検索結果は同じ資料
    outcome, events, *_ = _run(runner, deps)
    assert outcome["result"]["stopReason"] == "no_new_results"
    assert ("retry_search", "done") in _flow(events)
    assert deps.purposes() == ["understand", "sufficiency", "synthesize"]  # 2回目の十分性は聞かない


def test_at_most_two_extra_searches_then_budget_stop(runner):
    counter = {"n": 0}

    def tech(query, model):
        counter["n"] += 1
        return _retrieval(_tech(f"D{counter['n']}.pdf", 1))

    deps = FakeDeps(tech=tech, sufficiency=[_retry("言い換え1"), _retry("言い換え2"), _retry("言い換え3")])
    limits = support.load_module("senpai_research_config.py").BudgetLimits(
        max_searches=20, max_model_calls=10, job_ms=60000, synth_reserve_ms=20000)
    outcome, events, *_ = _run(runner, deps, limits=limits)
    assert _flow(events).count(("retry_search", "running")) == 2
    assert outcome["result"]["stopReason"] == "budget"
    assert deps.purposes().count("synthesize") == 1


def test_search_budget_blocks_extra_searches_and_still_answers(runner):
    config = support.load_module("senpai_research_config.py")
    limits = config.BudgetLimits(max_searches=2, max_model_calls=4, job_ms=60000, synth_reserve_ms=20000)
    deps = FakeDeps(understand=_understanding(lawRelevant=True), sufficiency=[_retry("追加の検索")])
    outcome, events, budget, _clock = _run(runner, deps, limits=limits)
    assert outcome["result"]["stopReason"] == "budget"
    assert outcome["result"]["kind"] == "answer"
    assert ("retry_search", "running") not in _flow(events)
    assert budget.snapshot()["searchesUsed"] <= 2


def test_time_budget_skips_sufficiency_and_synthesizes_what_it_has(runner):
    clock_box = {}

    def slow_tech(query, model):
        clock_box["clock"].advance(30)  # 技術の2検索で計60秒（予算を使い切るが、まとめ用の20秒は残る）
        return _retrieval(_tech("TI-1.pdf", 3))

    deps = FakeDeps(tech=slow_tech)
    job, budget, recorder, events, clock = _setup(runner, deps)
    clock_box["clock"] = clock
    outcome = runner.run_research(job, deps, recorder, budget)
    assert outcome["result"]["stopReason"] == "budget"
    assert "sufficiency" not in deps.purposes()
    assert deps.purposes()[-1] == "synthesize"
    assert outcome["result"]["kind"] == "answer"


def test_model_call_budget_of_one_uses_it_for_synthesis_only(runner):
    config = support.load_module("senpai_research_config.py")
    limits = config.BudgetLimits(max_searches=6, max_model_calls=1, job_ms=60000, synth_reserve_ms=20000)
    deps = FakeDeps()
    outcome, *_ = _run(runner, deps, limits=limits)
    assert deps.purposes() == ["synthesize"]
    assert outcome["result"]["stopReason"] == "budget"
    assert outcome["result"]["kind"] == "answer"


def test_sufficiency_model_failure_proceeds_with_current_results(runner):
    deps = FakeDeps(sufficiency=[RuntimeError("bedrock down")])
    outcome, events, *_ = _run(runner, deps)
    assert outcome["result"]["kind"] == "answer"
    assert ("sufficiency", "done") in _flow(events)


def test_doc_page_fetches_the_named_document_only(runner):
    def tech(query, model):
        if "TI-1.pdf" in query:
            return _retrieval(_tech("TI-1.pdf", 7, "7ページの本文"), _tech("OTHER.pdf", 1, "無関係"))
        return _retrieval(_tech("TI-1.pdf", 3))

    directive = _directive(sufficient=False, action="doc_page",
                           target={"documentName": "TI-1.pdf", "pageNumber": 7}, query="ドア調整")
    deps = FakeDeps(tech=tech, sufficiency=[directive, SUFFICIENT], synth="結論[T1][T2]")
    outcome, events, *_ = _run(runner, deps)
    assert ("doc_page", "running") in _flow(events) and ("doc_page", "done") in _flow(events)
    docs = [(s["documentName"], s["pageNumber"]) for s in outcome["result"]["sources"]["tech"]]
    assert ("TI-1.pdf", 7) in docs
    assert all(name == "TI-1.pdf" for name, _ in docs)


# ---------------------------------------------------------------- 聞き返し・見つからない

def test_clarify_path_stops_without_synthesis(runner):
    directive = _directive(sufficient=False, action="clarify",
                           clarifyQuestions=["機種は何ですか", "異音はいつ出ますか"])
    deps = FakeDeps(sufficiency=[directive])
    outcome, events, *_ = _run(runner, deps)
    result = outcome["result"]
    assert result["kind"] == "clarify" and result["stopReason"] == "clarify"
    assert result["clarifyQuestions"] == ["機種は何ですか", "異音はいつ出ますか"]
    assert "機種は何ですか" in result["answerMarkdown"]
    assert "synthesize" not in deps.purposes()
    assert ("clarify", "running") in _flow(events) and ("clarify", "done") in _flow(events)


def test_not_found_when_nothing_was_retrieved(runner):
    empty_tech = lambda q, m: _retrieval()
    deps = FakeDeps(tech=empty_tech, cards=[])
    outcome, events, *_ = _run(runner, deps)
    assert outcome["result"]["kind"] == "not_found"
    assert "synthesize" not in deps.purposes()
    assert next(e for e in events if e["step"] == "synthesize")["status"] == "skipped"


# ---------------------------------------------------------------- 照合

def test_fake_refs_are_removed_and_recorded(runner):
    deps = FakeDeps(synth="ドアを調整します[T1][T9]。別の資料[T5]。事例[K1][K7]")
    outcome, events, *_ = _run(runner, deps)
    result = outcome["result"]
    for fake in ("[T9]", "[T5]", "[K7]"):
        assert fake not in result["answerMarkdown"]
    assert set(result["unverifiedRefs"]) == {"T9", "T5", "K7"}
    verify = next(e for e in events if e["step"] == "verify" and e["status"] == "done")
    assert "3" in verify["detailJa"]


# ---------------------------------------------------------------- 失敗

def test_all_searches_failing_is_a_failure_not_a_not_found(runner):
    deps = FakeDeps(tech=lambda q, m: RuntimeError("kb down"), law=lambda q: RuntimeError("kb down"),
                    understand=_understanding(lawRelevant=True))
    with pytest.raises(runner.ResearchFailure) as caught:
        _run(runner, deps)
    assert caught.value.code == "Internal"


def test_one_failed_search_does_not_stop_the_others(runner):
    deps = FakeDeps(law=lambda q: RuntimeError("law kb down"), understand=_understanding(lawRelevant=True))
    outcome, events, *_ = _run(runner, deps)
    assert any(e["step"] == "law_search" and e["status"] == "failed" for e in events)
    assert outcome["result"]["kind"] == "answer"


def test_synthesis_timeout_is_reported_as_timeout(runner):
    class ReadTimeoutError(Exception):
        pass
    deps = FakeDeps(synth=ReadTimeoutError("read timeout"))
    with pytest.raises(runner.ResearchFailure) as caught:
        _run(runner, deps)
    assert caught.value.code == "Timeout"
    assert "Traceback" not in caught.value.message


def test_empty_synthesis_is_internal_failure(runner):
    with pytest.raises(runner.ResearchFailure) as caught:
        _run(runner, FakeDeps(synth="   "))
    assert caught.value.code == "Internal"
