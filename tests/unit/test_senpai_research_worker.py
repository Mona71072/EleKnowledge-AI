"""ワーカー Lambda（非同期起動）の契約テスト: ジョブの状態遷移・保存・ロック解放・ログ。"""
import json
import time
from types import SimpleNamespace

import pytest

import test_senpai_research_support as support
from test_senpai_research_runner import (
    FakeDeps, GOOD_ANSWER, QUESTION, SUFFICIENT, _directive, _retrieval, _tech, _understanding,
)
from test_senpai_research_support import FakeClock, USER_ID, research_env  # noqa: F401

JOB_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
SECRET_ANSWER = "回答の固有本文ZZZANS"
SECRET_QUERY = "整理語ZZZQRY"


@pytest.fixture
def world(research_env):
    import boto3
    from moto import mock_aws
    worker = support.load_module("senpai_research_worker.py")
    with mock_aws():
        table = support.make_jobs_table(boto3)
        chatlogs = support.make_chatlogs_table(boto3)
        clock = FakeClock(time.time())
        store = worker.store.JobStore(table, clock=clock)
        limits = worker.config.load_limits()
        runtime = SimpleNamespace(store=store, chatlogs_table=chatlogs, limits=limits)
        yield worker, runtime, store, chatlogs, clock


def _enqueue(world, **extra):
    worker, runtime, store, chatlogs, clock = world
    request = {"question": QUESTION, "modelType": None,
               "senpaiConversationId": support.CONVERSATION_ID, "senpaiTurnId": support.TURN_ID,
               "clientRequestId": support.CLIENT_REQUEST_ID}
    request.update(extra)
    item = worker.store.build_job_item(JOB_ID, USER_ID, request, now=clock(), ttl_seconds=150)
    store.create_job(item)
    assert store.acquire_lock(USER_ID, JOB_ID, 150)
    return item


def _deps(**kw):
    kw.setdefault("understand", _understanding(lawRelevant=True,
                                               queries={"tech": SECRET_QUERY, "law": "", "knowhow": ""}))
    kw.setdefault("synth", GOOD_ANSWER.replace("類似事例", SECRET_ANSWER))
    return FakeDeps(**kw)


def _process(world, deps):
    worker, runtime, *_ = world
    worker.process_job(JOB_ID, runtime, deps)


def _chat_rows(chatlogs):
    return sorted(chatlogs.scan()["Items"], key=lambda row: row["messageId"])


# ---------------------------------------------------------------- 正常系

def test_happy_path_completes_job_with_steps_result_and_debug(world):
    _enqueue(world)
    _process(world, _deps())
    store = world[2]
    job = store.get_job(JOB_ID)
    assert job["status"] == "completed"
    assert job["result"]["kind"] == "answer" and job["result"]["stopReason"] == "sufficient"
    seqs = [int(step["seq"]) for step in job["steps"]]
    assert seqs == list(range(1, len(seqs) + 1))
    assert [s["step"] for s in job["steps"]][:2] == ["understand", "understand"]
    assert job["steps"][-1]["step"] == "verify" and job["steps"][-1]["status"] == "done"
    assert job["debug"]["budget"]["modelCallsUsed"] == 4
    assert job["debug"]["queries"]["tech"]


def test_lock_is_released_after_the_job(world):
    _enqueue(world)
    _process(world, _deps())
    assert world[2].acquire_lock(USER_ID, "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", 150) is True


def test_answer_is_saved_to_chatlogs_with_senpai_tags(world):
    _enqueue(world, modelType="AXIEZ-LINKs")
    _process(world, _deps())
    rows = _chat_rows(world[3])
    assert [r["role"] for r in rows] == ["assistant", "user"] or [r["role"] for r in rows] == ["user", "assistant"]
    by_role = {r["role"]: r for r in rows}
    for row in rows:
        assert row["ragMode"] == "senpai_research"
        assert row["userId"] == USER_ID
        assert row["senpaiConversationId"] == support.CONVERSATION_ID
        assert row["senpaiTurnId"] == support.TURN_ID
        assert 59 * 24 * 3600 < int(row["ttl"]) - int(time.time()) <= 60 * 24 * 3600 + 5
        # 回答の集計（日別 GSI）に混ぜない
        assert "metricDay" not in row and "metricDayShard" not in row
    assert by_role["user"]["content"] == QUESTION
    assert by_role["assistant"]["content"].startswith("## 結論")
    assert by_role["assistant"]["timestamp"] >= by_role["user"]["timestamp"]
    saved = by_role["assistant"]["researchResult"]
    assert saved["kind"] == "answer" and saved["sources"]["tech"][0]["ref"] == "T1"
    assert by_role["assistant"]["queryFilters"] == {"modelType": "AXIEZ-LINKs"}
    assert by_role["assistant"]["responseType"] == "pages"


def test_clarify_and_not_found_results_are_saved_too(world):
    _enqueue(world)
    clarify = _directive(sufficient=False, action="clarify", clarifyQuestions=["機種は？"])
    _process(world, _deps(sufficiency=clarify))
    assistant = next(r for r in _chat_rows(world[3]) if r["role"] == "assistant")
    assert assistant["responseType"] == "clarify"
    assert assistant["clarifyQuestions"] == ["機種は？"]


def test_chatlog_failure_does_not_fail_the_job(world):
    worker, runtime, store, chatlogs, clock = world
    _enqueue(world)

    class Broken:
        def put_item(self, **kw):
            raise RuntimeError("chatlogs down")

    broken = SimpleNamespace(store=store, chatlogs_table=Broken(), limits=runtime.limits)
    worker.process_job(JOB_ID, broken, _deps())
    assert store.get_job(JOB_ID)["status"] == "completed"


# ---------------------------------------------------------------- 失敗系

def test_synthesis_timeout_fails_job_with_timeout_code_and_frees_lock(world):
    class ReadTimeoutError(Exception):
        pass
    _enqueue(world)
    _process(world, _deps(synth=ReadTimeoutError("took too long")))
    job = world[2].get_job(JOB_ID)
    assert job["status"] == "failed"
    assert job["error"]["code"] == "Timeout"
    assert "Traceback" not in json.dumps(job["error"], default=str)
    assert job["debug"]["budget"]["modelCallsUsed"] >= 1  # 診断は残る
    assert _chat_rows(world[3]) == []
    assert world[2].acquire_lock(USER_ID, "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", 150) is True


def test_unexpected_error_becomes_generic_internal_failure(world, monkeypatch):
    worker = world[0]
    _enqueue(world)
    monkeypatch.setattr(worker.runner, "run_research",
                        lambda *a, **k: (_ for _ in ()).throw(ValueError("内部詳細ZZZSECRET")))
    _process(world, _deps())
    job = world[2].get_job(JOB_ID)
    assert job["status"] == "failed" and job["error"]["code"] == "Internal"
    assert "ZZZSECRET" not in json.dumps(job["error"], ensure_ascii=False)
    assert world[2].acquire_lock(USER_ID, "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", 150) is True


def test_job_that_cannot_start_is_not_run_twice(world):
    _enqueue(world)
    world[2].start_job(JOB_ID)  # すでに別のワーカーが実行中
    deps = _deps()
    _process(world, deps)
    assert deps.model_calls == []
    assert world[2].get_job(JOB_ID)["status"] == "running"


def test_missing_job_is_ignored(world):
    deps = _deps()
    _process(world, deps)  # ジョブ行が無い
    assert deps.model_calls == []


def test_job_without_question_fails_with_question_unavailable(world):
    item = _enqueue(world)
    world[2]._table.update_item(Key={"pk": item["pk"]}, UpdateExpression="REMOVE question")
    _process(world, _deps())
    job = world[2].get_job(JOB_ID)
    assert job["status"] == "failed" and job["error"]["code"] == "QuestionUnavailable"


# ---------------------------------------------------------------- ログ

def test_logs_contain_stage_metrics_but_never_question_queries_or_answer(world, capsys):
    _enqueue(world)
    _process(world, _deps())
    captured = capsys.readouterr()
    output = captured.out + captured.err
    for secret in ("固有質問ZZZQ", SECRET_QUERY, SECRET_ANSWER, "ドア", "異音", "LINKs"):
        assert secret not in output, secret
    records = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    summary = [r for r in records if r.get("event") == "senpai_research" and r.get("stage") == "job_finished"]
    assert summary and summary[-1]["status"] == "completed"
    assert summary[-1]["stopReason"] == "sufficient" and summary[-1]["kind"] == "answer"
    assert "elapsedMs" in summary[-1] and "modelCalls" in summary[-1] and "searches" in summary[-1]


def test_failure_logs_have_error_class_only(world, capsys, monkeypatch):
    worker = world[0]
    _enqueue(world)
    monkeypatch.setattr(worker.runner, "run_research",
                        lambda *a, **k: (_ for _ in ()).throw(ValueError("固有質問ZZZQ が漏れる")))
    _process(world, _deps())
    output = capsys.readouterr().out
    assert "固有質問ZZZQ" not in output
    assert '"errorClass":"ValueError"' in output


# ---------------------------------------------------------------- エントリーポイント

def test_lambda_handler_ignores_malformed_payloads_without_touching_aws(world, monkeypatch):
    worker = world[0]
    monkeypatch.setattr(worker, "build_runtime", lambda: pytest.fail("must not build runtime"))
    for event in ({}, {"jobId": "x"}, {"jobId": 5}, None):
        assert worker.lambda_handler(event, None) is None


def test_lambda_handler_runs_the_job_it_is_given(world, monkeypatch):
    worker, runtime, *_ = world
    seen = []
    monkeypatch.setattr(worker, "build_runtime", lambda: runtime)
    monkeypatch.setattr(worker, "build_deps", lambda: "deps")
    monkeypatch.setattr(worker, "process_job", lambda job_id, rt, deps, **kw: seen.append((job_id, rt, deps)))
    worker.lambda_handler({"jobId": JOB_ID}, None)
    assert seen == [(JOB_ID, runtime, "deps")]
