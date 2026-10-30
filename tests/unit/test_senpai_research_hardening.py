"""調査ジョブの堅牢化（監査 F1〜F13）の契約テスト。

時間予算の実効化・リース喪失・日次枠の返却・引用の強制・リンク除去・ログの jobId など。
"""
import json
import time
from types import SimpleNamespace

import pytest

import test_senpai_research_support as support
from test_senpai_research_runner import (
    FakeDeps, GOOD_ANSWER, SUFFICIENT, _directive, _law, _retrieval, _setup, _tech, _understanding,
)
from test_senpai_research_support import (  # noqa: F401
    FakeClock, OTHER_USER_ID, USER_ID, api_event, body_of, research_env, valid_body,
)
from test_senpai_research_worker import JOB_ID, _deps, _process, world  # noqa: F401
from test_senpai_research_api import api  # noqa: F401


def _limits(config, **kw):
    base = dict(max_searches=6, max_model_calls=4, job_ms=60000, synth_reserve_ms=20000)
    base.update(kw)
    return config.BudgetLimits(**base)


class Tick:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def _enqueue(world, *, take_slot=True):
    worker, runtime, store, chatlogs, clock = world
    request = {"question": support.QUESTION, "modelType": None,
               "senpaiConversationId": support.CONVERSATION_ID, "senpaiTurnId": support.TURN_ID,
               "clientRequestId": support.CLIENT_REQUEST_ID}
    item = worker.store.build_job_item(JOB_ID, USER_ID, request, now=clock(), ttl_seconds=300,
                                       daily_day=store.daily_day())
    store.create_job(item)
    assert store.acquire_lock(USER_ID, JOB_ID, 300)
    if take_slot:
        assert store.take_daily_slot(USER_ID, 20)
    return item


def _daily_count(store, day=None):
    item = store._table.get_item(Key={"pk": f"DAILY#{USER_ID}#{day or store.daily_day()}"}).get("Item")
    return int(item["cnt"]) if item else 0


def _lock(store):
    return store._table.get_item(Key={"pk": f"LOCK#{USER_ID}"}).get("Item")


# ================================================================ F1 時間予算

def test_budget_remaining_and_call_timeouts_follow_the_hard_deadline():
    config = support.load_module("senpai_research_config.py")
    budget_mod = support.load_module("senpai_research_budget.py")
    clock = Tick()
    budget = budget_mod.Budget(_limits(config), clock=clock)
    assert budget.remaining_ms() == 80000  # 予算 60 秒 + まとめ用 20 秒
    assert budget.call_timeout_s(final=False) == 40  # 1 呼び出しの上限
    clock.now += 50
    assert budget.call_timeout_s(final=False) == pytest.approx(10)  # まとめ用 20 秒を残す
    assert budget.call_timeout_s(final=True) == pytest.approx(28)
    clock.now += 25  # 残り 5 秒
    assert budget.call_timeout_s(final=False) is None
    assert budget.call_timeout_s(final=True) == pytest.approx(3)


def test_hard_limit_from_lambda_remaining_time_caps_the_budget():
    config = support.load_module("senpai_research_config.py")
    budget_mod = support.load_module("senpai_research_budget.py")
    budget = budget_mod.Budget(_limits(config), clock=Tick(), hard_limit_ms=30000)
    assert budget.remaining_ms() == 30000
    assert budget.call_timeout_s(final=True) == pytest.approx(28)


def test_worker_binds_the_budget_to_lambda_remaining_time(world):
    worker, runtime, store, *_ = world
    _enqueue(world)
    seen = {}

    class Spy(FakeDeps):
        def bind_budget(self, budget):
            seen["budget"] = budget

    worker.process_job(JOB_ID, runtime, Spy(understand=_understanding(), synth=GOOD_ANSWER),
                       remaining_ms=40000)
    # 40 秒 - 安全マージン 10 秒
    assert seen["budget"].remaining_ms() <= 30000


def test_synthesis_is_replaced_by_a_source_list_when_time_is_nearly_gone():
    runner = support.load_module("senpai_research_runner.py")
    holder = {}

    def slow_tech(query, model):
        holder["clock"].now += 74  # 残り 6 秒
        return _retrieval(_tech("TI-1.pdf", 3))

    deps = FakeDeps(tech=slow_tech)
    job, budget, recorder, events, clock = _setup(runner, deps)
    holder["clock"] = clock
    outcome = runner.run_research(job, deps, recorder, budget)
    result = outcome["result"]
    assert "synthesize" not in deps.purposes()
    assert result["kind"] == "answer" and result["stopReason"] == "budget"
    assert "[T1]" in result["answerMarkdown"] and result["sources"]["tech"][0]["ref"] == "T1"
    assert ("synthesize", "skipped") in [(e["step"], e["status"]) for e in events]


@pytest.fixture
def rag_ctx(rag_app, monkeypatch):
    module = support.load_module("senpai_research_rag.py")
    module.set_app(rag_app)
    return module, rag_app


def test_model_call_timeout_is_derived_from_the_remaining_budget(rag_ctx, monkeypatch):
    module, app = rag_ctx
    config = support.load_module("senpai_research_config.py")
    budget_mod = support.load_module("senpai_research_budget.py")
    clock = Tick()
    budget = budget_mod.Budget(_limits(config), clock=clock)
    deps = module.RagDeps()
    deps.bind_budget(budget)
    captured = {}
    monkeypatch.setattr(deps, "_bedrock_client", lambda app_, timeout_s, attempts: captured.update(t=timeout_s) or "client")
    monkeypatch.setattr(app, "invoke_generation", lambda client, *a, **k: ("text", {}, None))
    clock.now += 60
    assert deps.call_model("synthesize", "s", "u", 100) == "text"
    assert captured["t"] == pytest.approx(18)
    clock.now += 15
    with pytest.raises(module.TimeBudgetExceeded):
        deps.call_model("understand", "s", "u", 100)


def test_search_is_refused_when_no_time_is_left(rag_ctx, monkeypatch):
    module, app = rag_ctx
    config = support.load_module("senpai_research_config.py")
    budget_mod = support.load_module("senpai_research_budget.py")
    clock = Tick()
    budget = budget_mod.Budget(_limits(config), clock=clock)
    agent = SimpleNamespace(calls=0)
    monkeypatch.setattr(app, "bedrock_agent", SimpleNamespace(
        retrieve=lambda **k: agent.__setattr__("calls", agent.calls + 1) or {"retrievalResults": []}))
    deps = module.RagDeps()
    deps.bind_budget(budget)
    clock.now += 79
    with pytest.raises(module.TimeBudgetExceeded):
        deps.search_tech("ドア異音", None)
    assert agent.calls == 0


# ================================================================ F2 / F3 リース

def test_complete_job_failure_fails_the_job_and_saves_no_history(world):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    store.complete_job = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("ValidationException"))
    _process(world, _deps())
    job = store.get_job(JOB_ID)
    assert job["status"] == "failed" and job["error"]["code"] == "Internal"
    assert chatlogs.scan()["Items"] == []
    assert _lock(store) is None


def test_history_is_saved_only_after_complete_job_succeeds(world):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    order = []
    original = store.complete_job
    store.complete_job = lambda *a, **k: order.append("complete") or original(*a, **k)
    original_save = worker.chatlog.save_rows
    worker.chatlog.save_rows = lambda *a, **k: order.append("history") or original_save(*a, **k)
    try:
        _process(world, _deps())
    finally:
        worker.chatlog.save_rows = original_save
    assert order == ["complete", "history"]


def test_lost_lease_stops_without_history_and_logs_it(world, capsys):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    deps = _deps()
    original = deps.call_model

    def expire_then_answer(purpose, system, user, max_tokens):
        if purpose == "synthesize":
            clock.advance(10000)
            assert store.expire_job(JOB_ID)
        return original(purpose, system, user, max_tokens)

    deps.call_model = expire_then_answer
    _process(world, deps)
    assert store.get_job(JOB_ID)["status"] == "failed"
    assert chatlogs.scan()["Items"] == []
    records = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
    finished = [r for r in records if r.get("stage") == "job_finished"]
    assert finished and finished[-1]["status"] == "lost_lease"


def test_start_job_refuses_an_expired_queued_job(world):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    clock.advance(301)
    deps = _deps()
    _process(world, deps)
    assert deps.model_calls == []
    assert store.get_job(JOB_ID)["status"] == "queued"


def test_complete_job_is_refused_after_the_lease_expired(world):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    assert store.start_job(JOB_ID)
    clock.advance(301)
    assert store.complete_job(JOB_ID, {"kind": "answer"}, {}) is False


def test_job_ttl_default_covers_async_event_age_plus_worker_timeout():
    config = support.load_module("senpai_research_config.py")
    assert config.job_ttl_seconds() >= 120 + 120


# ================================================================ F5 seq の再同期

def test_recorder_resyncs_seq_after_a_lost_append_response(world):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    assert store.start_job(JOB_ID)
    recorder_mod = support.load_module("senpai_research_recorder.py")
    calls = {"n": 0}

    def append(event):
        calls["n"] += 1
        stored = store.append_step(JOB_ID, event)
        if calls["n"] == 1:
            raise TimeoutError("response lost after the write succeeded")
        return stored

    recorder = recorder_mod.StepRecorder(append, resync=lambda: store.next_seq(JOB_ID))
    recorder.begin("understand")
    recorder.begin("knowhow")
    recorder.begin("tech_search")
    seqs = [int(step["seq"]) for step in store.get_job(JOB_ID)["steps"]]
    assert seqs == [1, 2, 3]


# ================================================================ F6 日次枠の返却

def test_worker_failure_refunds_the_daily_slot_once(world, monkeypatch):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    assert _daily_count(store) == 1
    monkeypatch.setattr(worker.runner, "run_research",
                        lambda *a, **k: (_ for _ in ()).throw(ValueError("x")))
    _process(world, _deps())
    assert _daily_count(store) == 0
    _process(world, _deps())  # 二重起動されても戻しすぎない
    assert _daily_count(store) == 0


def test_successful_job_keeps_the_daily_slot(world):
    _enqueue(world)
    _process(world, _deps())
    assert _daily_count(world[2]) == 1


def test_refund_goes_to_the_day_the_slot_was_taken(world, monkeypatch):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    taken_day = store.daily_day()
    clock.advance(24 * 3600)  # 日付を跨ぐ
    store.take_daily_slot(USER_ID, 20)  # 翌日の枠 1 件
    monkeypatch.setattr(worker.runner, "run_research",
                        lambda *a, **k: (_ for _ in ()).throw(ValueError("x")))
    job = store.get_job(JOB_ID)
    store._table.update_item(Key={"pk": job["pk"]}, UpdateExpression="SET expiresAt = :e",
                             ExpressionAttributeValues={":e": int(clock()) + 1000})
    _process(world, _deps())
    assert _daily_count(store, taken_day) == 0
    assert _daily_count(store) == 1


def test_poller_expiry_refunds_once(api):
    ctx = api.test_ctx
    response = api.lambda_handler(api_event(valid_body()), None)
    job_id = body_of(response)["jobId"]
    assert _daily_count(ctx.store) == 1
    ctx.clock.advance(400)
    for _ in range(2):
        got = api.lambda_handler(api_event(method="GET", job_id=job_id), None)
        assert body_of(got)["error"]["code"] == "Timeout"
    assert _daily_count(ctx.store) == 0


def test_invoke_failure_refunds_the_slot(api, monkeypatch):
    monkeypatch.setattr(api, "invoke_worker", lambda job_id: (_ for _ in ()).throw(RuntimeError("x")))
    response = api.lambda_handler(api_event(valid_body()), None)
    assert response["statusCode"] == 502
    assert _daily_count(api.test_ctx.store) == 0


# ================================================================ F7 受付の取り消し

def test_create_job_failure_undoes_every_reservation(api, monkeypatch):
    ctx = api.test_ctx
    original = ctx.store.create_job
    monkeypatch.setattr(ctx.store, "create_job",
                        lambda item: (_ for _ in ()).throw(RuntimeError("ddb down")))
    response = api.lambda_handler(api_event(valid_body()), None)
    assert response["statusCode"] == 500
    assert _lock(ctx.store) is None and _daily_count(ctx.store) == 0
    monkeypatch.setattr(ctx.store, "create_job", original)
    again = api.lambda_handler(api_event(valid_body()), None)
    assert again["statusCode"] == 202


def test_resend_with_a_missing_job_creates_it(api):
    ctx = api.test_ctx
    ctx.store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, support.UNKNOWN_JOB_ID)  # job 行なし
    ctx.clock.advance(api.store.REQUEST_CLAIM_LEASE_SECONDS + 1)
    response = api.lambda_handler(api_event(valid_body()), None)
    assert response["statusCode"] == 202
    job_id = body_of(response)["jobId"]
    assert job_id != support.UNKNOWN_JOB_ID and ctx.store.get_job(job_id) is not None


def test_api_create_log_has_job_id_and_missing_env_is_a_500(api, capsys, monkeypatch):
    response = api.lambda_handler(api_event(valid_body()), None)
    job_id = body_of(response)["jobId"]
    records = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
    assert any(r.get("stage") == "create" and r.get("jobId") == job_id for r in records)
    monkeypatch.delenv("SENPAI_RESEARCH_TABLE")
    broken = api.lambda_handler(api_event(valid_body(clientRequestId=support.SECOND_CLIENT_REQUEST_ID)), None)
    assert broken["statusCode"] == 500 and body_of(broken)["error"] == "InternalError"


# ================================================================ F4 引用の検証

def _sources():
    citations = support.load_module("senpai_research_citations.py")
    return citations, citations.build_sources([_tech("a.pdf", 1), _tech("b.pdf", 2, score=0.5)], [], [])


def test_comma_separated_and_variant_refs_are_verified_individually():
    citations, sources = _sources()
    out = citations.verify_refs("x [T1, T9] y【Ｔ２】 z［t 1］", sources)
    assert out["text"] == "x [T1] y[T2] z[T1]"
    assert out["cited"] == {"T1", "T2"} and out["unverifiedRefs"] == ["T9"]


def test_unknown_prefix_and_leading_zero_refs_are_unverified():
    citations, sources = _sources()
    out = citations.verify_refs("[X1] [T01] [1] [T1](#a)", sources)
    assert out["unverifiedRefs"] == ["T01"]
    assert out["text"] == "[X1]  [1] [T1](#a)"  # 参照でない括弧は触らない


def test_answer_without_any_verified_ref_becomes_not_found():
    runner = support.load_module("senpai_research_runner.py")
    deps = FakeDeps(synth="## 結論\n根拠のない断定。")
    job, budget, recorder, events, clock = _setup(runner, deps)
    result = runner.run_research(job, deps, recorder, budget)["result"]
    assert result["kind"] == "not_found"
    assert "参照" in result["answerMarkdown"]
    assert result["sources"]["tech"] == [] and result["sources"]["law"] == []


def test_answer_with_only_hallucinated_refs_becomes_not_found():
    runner = support.load_module("senpai_research_runner.py")
    deps = FakeDeps(synth="断定[T9]。")
    job, budget, recorder, events, clock = _setup(runner, deps)
    result = runner.run_research(job, deps, recorder, budget)["result"]
    assert result["kind"] == "not_found" and result["unverifiedRefs"] == ["T9"]


# ================================================================ F10 リンクの除去

def test_strip_links_keeps_text_and_source_refs():
    citations = support.load_module("senpai_research_citations.py")
    text = ("見る ![x](https://evil.example/i.png?q=1) と [ここ](https://evil.example/a) と "
            "https://evil.example/raw と www.evil.example と <https://evil.example/b> と [T1](http://e/x)")
    out = citations.strip_links(text)
    assert "http" not in out and "evil" not in out and "![" not in out
    assert "ここ" in out and "[T1]" in out


def test_runner_answer_has_no_urls():
    runner = support.load_module("senpai_research_runner.py")
    deps = FakeDeps(synth="手順[T1] 参照 https://evil.example/x ![i](https://evil.example/i.png)")
    job, budget, recorder, events, clock = _setup(runner, deps)
    result = runner.run_research(job, deps, recorder, budget)["result"]
    assert "http" not in result["answerMarkdown"] and "[T1]" in result["answerMarkdown"]


# ================================================================ F8 検索失敗の通知

def test_failed_law_lane_holds_answer_and_is_warned_in_result():
    runner = support.load_module("senpai_research_runner.py")
    deps = FakeDeps(understand=_understanding(lawRelevant=True,
                                              queries={"tech": "t", "law": "l", "knowhow": "k"}),
                    law=lambda q: RuntimeError("kb down"))
    job, budget, recorder, events, clock = _setup(runner, deps)
    result = runner.run_research(job, deps, recorder, budget)["result"]
    assert result["kind"] == "not_found"
    assert not any(purpose == "synthesize" for purpose, _ in deps.model_calls)
    assert any("法令" in w for w in result["warnings"])


def test_no_warnings_key_when_every_lane_succeeds():
    runner = support.load_module("senpai_research_runner.py")
    deps = FakeDeps()
    job, budget, recorder, events, clock = _setup(runner, deps)
    assert "warnings" not in runner.run_research(job, deps, recorder, budget)["result"]


# ================================================================ F9 ハンドラ全体の保険

def test_handler_fails_the_job_when_runtime_cannot_be_built(world, monkeypatch):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)
    monkeypatch.setattr(worker, "build_runtime", lambda: (_ for _ in ()).throw(KeyError("CHATLOGS_TABLE")))
    worker.lambda_handler({"jobId": JOB_ID}, None)
    job = store.get_job(JOB_ID)
    assert job["status"] == "failed" and job["error"]["code"] == "Internal"
    assert _lock(store) is None and _daily_count(store) == 0


def test_missing_required_env_is_reported_by_name(monkeypatch):
    config = support.load_module("senpai_research_config.py")
    monkeypatch.delenv("CHATLOGS_TABLE", raising=False)
    monkeypatch.setenv("SENPAI_RESEARCH_TABLE", "t")
    assert config.missing_worker_env() == ["CHATLOGS_TABLE"]
    monkeypatch.delenv("SENPAI_RESEARCH_TABLE")
    monkeypatch.delenv("SENPAI_RESEARCH_WORKER_NAME", raising=False)
    assert config.missing_api_env() == ["SENPAI_RESEARCH_TABLE", "SENPAI_RESEARCH_WORKER_NAME"]


# ================================================================ F11 / F13 ログ

def test_every_log_record_has_the_job_id_and_start_finish_pair(world, capsys):
    _enqueue(world)
    _process(world, _deps())
    output = capsys.readouterr().out
    records = [json.loads(line) for line in output.splitlines()
               if line.startswith("{") and '"senpai_research"' in line]
    assert records and all(r.get("jobId") == JOB_ID for r in records)
    stages = [r["stage"] for r in records]
    assert stages[0] == "job_started" and stages[-1] == "job_finished"
    assert records[-1]["status"] == "completed"


def test_cold_start_warns_when_understand_model_is_unset(monkeypatch, capsys):
    worker = support.load_module("senpai_research_worker.py")
    monkeypatch.delenv("SENPAI_UNDERSTAND_MODEL_ID", raising=False)
    worker.warn_if_unconfigured()
    assert "understand_model_unset" in capsys.readouterr().out
    monkeypatch.setenv("SENPAI_UNDERSTAND_MODEL_ID", "some-model")
    worker.warn_if_unconfigured()
    assert capsys.readouterr().out == ""


# ================================================================ 回答形式（結論先行）

def test_budget_fallback_uses_the_same_headings():
    synth = support.load_module("senpai_research_synthesize.py")
    citations = support.load_module("senpai_research_citations.py")
    sources = citations.build_sources([_tech("a.pdf", 3)], [_law()], [])
    text = synth.source_list_markdown(sources)
    assert text.startswith("## 結論\n時間の上限に達したため、確認できた資料を示します")
    assert "## 根拠と手順\n- " in text and "[T1]" in text and "[L1]" in text
    assert "技術資料から" not in text and "## 確認が必要な点" not in text


def test_runner_passes_the_understanding_to_synthesis():
    runner = support.load_module("senpai_research_runner.py")
    deps = FakeDeps(understand=_understanding(modelType="AXIEZ-LINKs", modelEvidence="LINKs", part="ドア"))
    job, budget, recorder, events, clock = _setup(runner, deps, model_type="NEXCUBE")
    runner.run_research(job, deps, recorder, budget)
    user = [u for p, u in deps.model_calls if p == "synthesize"][0]
    block = user.split("<understanding>")[1].split("</understanding>")[0]
    assert "NEXCUBE" in block and "AXIEZ-LINKs" in block and "ドア" in block and "cause" in block
