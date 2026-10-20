"""受付 → ワーカー → 進捗取得 → 履歴復元を、本物のアダプターと moto で通しで確認する。

Bedrock と Knowledge Base だけを偽物にする。app.py の検索・選別・生成の関数は本物を使う。
"""
import json
import time
from types import SimpleNamespace

import pytest

import test_senpai_research_support as support
from test_senpai_research_adapter import FakeAgent, _chunk
from test_senpai_research_support import (
    FakeClock, USER_ID, api_event, body_of, research_env, valid_body,  # noqa: F401
)

QUESTION = "LINKsのドアが開閉時に異音。固有質問ZZZQ"
UNDERSTANDING = json.dumps({
    "modelType": "AXIEZ-LINKs", "modelEvidence": "LINKs", "controlMethod": None,
    "part": "ドア", "symptom": "異音", "situation": "開閉時", "intent": "cause",
    "lawRelevant": False,
    "queries": {"tech": "整理語ZZZQRY ドア 異音", "law": "", "knowhow": ""}, "missing": [],
}, ensure_ascii=False)
ANSWER = "## 結論\nドアの調整を確認します[T1]。根拠のない主張[T9]\n## 根拠と手順\n- 調整手順[T1]"


@pytest.fixture
def flow(research_env, rag_app, monkeypatch):
    import boto3
    from moto import mock_aws
    api = support.load_module("senpai_research_api.py")
    worker = support.load_module("senpai_research_worker.py")
    adapter = support.load_module("senpai_research_rag.py")
    adapter.set_app(rag_app)
    with mock_aws():
        jobs = support.make_jobs_table(boto3)
        chatlogs = support.make_chatlogs_table(boto3)
        clock = FakeClock(time.time())
        store = api.store.JobStore(jobs, clock=clock)
        runtime = SimpleNamespace(store=store, chatlogs_table=chatlogs, limits=worker.config.load_limits())
        agent = FakeAgent()
        agent.default = [_chunk(), _chunk("TI-2.pdf", 5, "別の資料の本文", 0.5)]
        calls = []

        def fake_invoke(client, model_id, system_prompt, messages, **kwargs):
            calls.append((kwargs.get("call_name"), model_id))
            text = {"understand": UNDERSTANDING,
                    "sufficiency": json.dumps({"sufficient": True, "action": "none"}),
                    "synthesize": ANSWER}[kwargs["call_name"]]
            return text, {}, "end_turn"

        monkeypatch.setattr(rag_app, "bedrock_agent", agent)
        monkeypatch.setattr(rag_app, "invoke_generation", fake_invoke)
        monkeypatch.setattr(rag_app, "KB_SOURCE_BUCKET", "kbbucket")
        monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", False)
        monkeypatch.setattr(rag_app, "LAW_RAG_ENABLED", "false")
        monkeypatch.setattr(rag_app, "RERANK_MODEL_ARN", "")
        monkeypatch.setattr(api, "get_store", lambda: store)
        monkeypatch.setattr(api, "now", clock)
        monkeypatch.setattr(
            api, "invoke_worker", lambda job_id: worker.process_job(job_id, runtime, adapter.RagDeps()))
        yield SimpleNamespace(api=api, worker=worker, store=store, chatlogs=chatlogs, agent=agent,
                              calls=calls, clock=clock)


def _post(flow, **overrides):
    return flow.api.lambda_handler(api_event(valid_body(question=QUESTION, **overrides)), None)


def _get(flow, job_id, **query):
    return flow.api.lambda_handler(
        api_event(method="GET", job_id=job_id, query=query or None), None)


def test_post_then_poll_returns_completed_job_with_ordered_steps_and_verified_result(flow):
    created = body_of(_post(flow, modelType="AXIEZ-LINKs"))
    assert created["status"] == "queued"
    status = body_of(_get(flow, created["jobId"]))

    assert status["status"] == "completed"
    seqs = [s["seq"] for s in status["steps"]]
    assert seqs == list(range(1, len(seqs) + 1))
    names = [s["step"] for s in status["steps"]]
    assert names[0] == "understand" and names[-1] == "verify"
    assert "tech_search" in names and "sufficiency" in names and "synthesize" in names
    assert any(s["step"] == "law_search" and s["status"] == "skipped" for s in status["steps"])

    result = status["result"]
    assert result["kind"] == "answer" and result["unverifiedRefs"] == ["T9"]
    assert "[T9]" not in result["answerMarkdown"] and "[T1]" in result["answerMarkdown"]
    assert result["sources"]["tech"][0]["documentName"] == "TI-1.pdf"
    assert result["sources"]["tech"][0]["pageNumber"] == 3
    assert result["understanding"]["modelType"] == "AXIEZ-LINKs"
    assert status["debug"]["budget"]["modelCallsUsed"] == 3
    # 原文と整理語の両方で技術資料を検索している
    queries = [c["retrievalQuery"]["text"] for c in flow.agent.calls]
    assert any("固有質問ZZZQ" in q for q in queries) and any("整理語ZZZQRY" in q for q in queries)


def test_polling_with_after_seq_returns_only_new_events(flow):
    job_id = body_of(_post(flow))["jobId"]
    everything = body_of(_get(flow, job_id))["steps"]
    later = body_of(_get(flow, job_id, afterSeq=str(everything[2]["seq"])))["steps"]
    assert [s["seq"] for s in later] == [s["seq"] for s in everything[3:]]
    assert body_of(_get(flow, job_id, afterSeq=str(everything[-1]["seq"])))["steps"] == []


def test_lock_is_free_after_completion_and_retry_is_idempotent(flow):
    first = body_of(_post(flow))
    again = body_of(_post(flow))  # 同じ clientRequestId
    assert again["jobId"] == first["jobId"]
    second = _post(flow, clientRequestId=support.SECOND_CLIENT_REQUEST_ID)
    assert second["statusCode"] == 202  # 完了後はロックが残らない


def test_history_restores_the_research_answer_and_stays_out_of_ordinary_chat(flow):
    job_id = body_of(_post(flow, modelType="AXIEZ-LINKs"))["jobId"]
    assert body_of(_get(flow, job_id))["status"] == "completed"

    from test_senpai_history import _chat_event, _load_chat_app
    chat, _table = _load_chat_app()
    chat.chatlogs_table = flow.chatlogs

    detail = chat.lambda_handler(_chat_event(
        f"/chat/sessions/{support.CONVERSATION_ID}/messages", qs={"context": "senpai"}, sub=USER_ID,
        path_params={"sessionId": support.CONVERSATION_ID}), None)
    body = json.loads(detail["body"])
    assert detail["statusCode"] == 200 and body["complete"] is True
    assert [(m["role"], m["ragMode"]) for m in body["messages"]] == [
        ("user", "senpai_research"), ("assistant", "senpai_research")]
    assert body["messages"][0]["content"] == QUESTION
    answer = body["messages"][1]
    assert answer["researchResult"]["sources"]["tech"][0]["documentName"] == "TI-1.pdf"
    assert answer["modelType"] == "AXIEZ-LINKs"
    assert "steps" not in answer and "debug" not in answer

    listing = chat.lambda_handler(_chat_event("/chat/sessions", sub=USER_ID), None)
    assert json.loads(listing["body"])["sessions"] == []  # 通常の /chat 履歴には出ない
    senpai_list = chat.lambda_handler(
        _chat_event("/chat/sessions", qs={"context": "senpai"}, sub=USER_ID), None)
    assert json.loads(senpai_list["body"])["sessions"][0]["title"].startswith("LINKsのドア")


def test_no_log_line_in_the_whole_flow_contains_question_queries_or_answer(flow, capsys):
    job_id = body_of(_post(flow, modelType="AXIEZ-LINKs"))["jobId"]
    _get(flow, job_id)
    captured = capsys.readouterr()
    output = captured.out + captured.err
    for secret in ("固有質問ZZZQ", "整理語ZZZQRY", "ドアの調整を確認", "ドア調整の本文", "別の資料の本文"):
        assert secret not in output, secret
    records = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    assert any(r.get("event") == "senpai_research" and r.get("stage") == "job_finished" for r in records)
