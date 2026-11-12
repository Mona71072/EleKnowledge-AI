"""検索トレース（docs/design-2026-09-10-retrieval-trace.md 第 1 版）のスキーマ・サイズ制限・保存境界。

純粋関数（retrieval_trace.py）のテストは mona の feature/retrieval-trace（2026-09-25）から引き継ぎ、
app.py への組み込みは develop の現行構成（法令モード・Converse 対応後）に合わせて書き直した。
"""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = ROOT / "lambda" / "rag" / "rag-function"

CANDIDATE_KEYS = {"rank", "sourceUri", "documentName", "pageNumber", "chunkId", "score",
                  "rerankScore", "modelType", "category", "hasImage", "selected", "excludedBy",
                  "dedupeCount", "text", "textTruncated", "originalLength"}
ATTEMPT_KEYS = {"stage", "query", "searchType", "filters", "scope", "requested", "returned",
                "afterPostFilter", "latencyMs"}
TRACE_KEYS = {"schemaVersion", "logicVersion", "promptVersion", "requestId", "kb", "questionRef",
              "searchAttempts", "rewrite", "rerank", "gate", "candidates", "generation",
              "latencyMs", "truncatedTrace", "truncationReason"}


def _load_trace():
    spec = importlib.util.spec_from_file_location("retrieval_trace_under_test", RAG_DIR / "retrieval_trace.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _candidate(text="sent to model", selected=True):
    return {
        "rank": 1, "sourceUri": "s3://kb/C-1.pdf", "documentName": "C-1.pdf",
        "pageNumber": 4, "chunkId": "chunk-1", "score": 0.82, "rerankScore": None,
        "modelType": "AXIEZ", "category": "spec", "hasImage": False,
        "selected": selected, "excludedBy": None, "dedupeCount": 0, "text": text,
    }


def _kb_result(uri="s3://kb/C-1.pdf", score=0.6, text="chunk", chunk_id="c1", **metadata):
    return {"score": score, "content": {"text": text},
            "metadata": {"x-amz-bedrock-kb-source-uri": uri,
                         "x-amz-bedrock-kb-chunk-id": chunk_id, **metadata}}


# --- 純粋関数（retrieval_trace.py） ---

def test_trace_has_only_design_schema_and_all_required_nested_keys():
    trace = _load_trace().build_retrieval_trace(
        logic_version="ecc7d09", prompt_version_value="rag-prompt-v1", request_id="req-1",
        kb_id="kb-1", profile_hash="hash", message_id="msg-1",
        search_attempts=[{"stage": "initial", "query": "q", "searchType": "HYBRID",
                          "filters": {}, "scope": {"profileHash": "hash"}, "requested": 30,
                          "returned": 2, "afterPostFilter": 1, "latencyMs": 10}],
        rewrite={"enabled": False, "status": "skipped", "reason": "disabled",
                 "rewrittenQuery": None, "modelId": None, "callCount": 0, "latencyMs": 0},
        rerank={"enabled": False, "status": "skipped", "reason": "disabled",
                "modelId": None, "callCount": 0, "latencyMs": 0},
        gate={"responseType": "pages", "weak": False, "scores": [0.82],
              "thresholds": [0.22, 0.3], "rankKey": "score", "selectedCount": 1,
              "excludedCounts": {}},
        candidates=[_candidate()], total_ms=100,
    )
    assert set(trace) == TRACE_KEYS
    assert trace["schemaVersion"] == 1
    assert trace["kb"] == {"kbId": "kb-1", "profileHash": "hash", "dataSourceSyncAt": None}
    assert trace["questionRef"] == {"messageId": "msg-1", "composedQuery": None}
    assert set(trace["searchAttempts"][0]) == ATTEMPT_KEYS
    assert set(trace["gate"]) == {
        "responseType", "weak", "scores", "thresholds", "rankKey", "selectedCount", "excludedCounts",
    }
    assert set(trace["gate"]["excludedCounts"]) == {"model_scope", "dedupe", "below_threshold", "limit"}
    assert trace["latencyMs"] == {"total": 100}


def test_candidate_contains_exact_fields_and_only_selected_body():
    trace = _load_trace().build_retrieval_trace(
        candidates=[_candidate(), _candidate("private", selected=False)],
    )
    assert set(trace["candidates"][0]) == CANDIDATE_KEYS
    assert trace["candidates"][0]["text"] == "sent to model"
    assert trace["candidates"][0]["textTruncated"] is False
    assert trace["candidates"][0]["originalLength"] == len("sent to model")
    assert trace["candidates"][1]["text"] is None
    assert trace["candidates"][1]["originalLength"] is None


def test_candidate_text_matches_1200_character_model_input():
    trace = _load_trace().build_retrieval_trace(candidates=[_candidate("x" * 1500)])
    assert trace["candidates"][0]["text"] == "x" * 1200 + "…"
    assert trace["candidates"][0]["textTruncated"] is True
    assert trace["candidates"][0]["originalLength"] == 1500


def test_trace_size_guard_nulls_bodies_and_records_reason():
    trace = _load_trace().build_retrieval_trace(
        candidates=[_candidate("large" * 240)], max_item_bytes=400 * 1024,
        base_item_bytes=398 * 1024,
    )
    assert trace["truncatedTrace"] is True
    assert trace["truncationReason"] == "dynamodb_item_size_limit"
    assert trace["candidates"][0]["text"] is None
    assert trace["candidates"][0]["textTruncated"] is True


def test_trace_size_guard_collapses_to_minimal_trace_when_reduction_is_not_enough():
    trace = _load_trace().build_retrieval_trace(
        candidates=[_candidate("large" * 240)],
        search_attempts=[{"query": "q" * 1000}], max_item_bytes=500,
    )
    assert trace == {
        "schemaVersion": 1, "logicVersion": "unknown", "promptVersion": "unknown",
        "candidateCount": 1, "searchAttemptCount": 1,
        "truncatedTrace": True, "truncationReason": "dynamodb_item_size_limit",
    }


def test_generation_uses_design_generation_thinking_position():
    trace = _load_trace().build_retrieval_trace(
        generation={"inputTokens": 11, "outputTokens": 7, "stopReason": "end_turn", "latencyMs": 45},
        generation_config={"modelId": "model-1", "requestStyle": "converse",
                           "thinking": {"type": "adaptive", "effort": "low"}},
    )
    assert trace["generation"] == {
        "modelId": "model-1", "requestStyle": "converse",
        "thinking": {"type": "adaptive", "effort": "low"},
        "inputTokens": 11, "outputTokens": 7, "stopReason": "end_turn", "latencyMs": 45,
    }


def test_trace_builder_does_not_log_sensitive_values(capsys):
    _load_trace().build_retrieval_trace(
        search_attempts=[{"query": "private search phrase"}], candidates=[_candidate("private body")],
        request_id="req-1", message_id="message-secret",
    )
    assert capsys.readouterr().out == ""


# --- 保存（save_message_to_dynamodb） ---

def test_save_message_persists_trace_with_decimal_scores(monkeypatch, rag_app):
    table = MagicMock()
    monkeypatch.setattr(rag_app, "chatlogs_table", table)
    trace = {"schemaVersion": 1, "requestId": "req-1", "gate": {"scores": [0.5]}}
    rag_app.save_message_to_dynamodb("s1", "u1", "assistant", "answer", retrieval_trace=trace)
    saved = table.put_item.call_args.kwargs["Item"]["retrievalTrace"]
    assert saved["requestId"] == "req-1"
    assert saved["gate"]["scores"] == [rag_app.Decimal("0.5")]


def test_put_item_failure_with_trace_retries_without_trace(monkeypatch, rag_app, capsys):
    table = MagicMock()
    table.put_item.side_effect = [RuntimeError("item too large"), {}]
    monkeypatch.setattr(rag_app, "chatlogs_table", table)
    result = rag_app.save_message_to_dynamodb(
        "s1", "u1", "assistant", "answer", retrieval_trace={"schemaVersion": 1},
    )
    assert result
    assert table.put_item.call_count == 2
    first, second = (call.kwargs["Item"] for call in table.put_item.call_args_list)
    assert second["messageId"] == first["messageId"]
    assert "retrievalTrace" not in second
    assert "retrieval_trace_dropped" in capsys.readouterr().out


def test_put_item_failure_without_trace_still_raises(monkeypatch, rag_app):
    table = MagicMock()
    table.put_item.side_effect = RuntimeError("boom")
    monkeypatch.setattr(rag_app, "chatlogs_table", table)
    with pytest.raises(RuntimeError):
        rag_app.save_message_to_dynamodb("s1", "u1", "user", "question")


# --- 組み立て（build_request_trace） ---

def test_request_trace_text_matches_references_block_after_truncation(rag_app):
    raw = "  " + "x" * 1400 + "  "
    result = _kb_result(text=raw, score=0.9)
    block = rag_app.build_references_block([result])
    trace = rag_app.build_request_trace(event={}, mode="normal", response_type="pages", query="q",
                                        results=[result], selected_results=[result])
    assert trace["candidates"][0]["text"] == block.splitlines()[1]
    assert set(trace["candidates"][0]) == CANDIDATE_KEYS


def test_image_candidate_text_matches_references_block(rag_app):
    result = {"score": 0.9, "content": {"type": "IMAGE", "byteContent": "data:image/png;base64,XYZ"},
              "metadata": {"x-amz-bedrock-kb-source-uri": "s3://kb/diagram.pdf",
                           "x-amz-bedrock-kb-chunk-id": "image-1"}}
    block = rag_app.build_references_block([result])
    trace = rag_app.build_request_trace(event={}, mode="normal", response_type="pages", query="q",
                                        results=[result], selected_results=[result])
    assert trace["candidates"][0]["hasImage"] is True
    assert trace["candidates"][0]["text"] == block.splitlines()[1]


def test_unselected_candidates_record_reason_and_counts(rag_app):
    chosen = _kb_result(uri="s3://kb/a.pdf", score=0.7, model_type=["AXIEZ", "NEXCUBE"])
    capped = _kb_result(uri="s3://kb/a.pdf", score=0.5, text="other", chunk_id="c2")
    low = _kb_result(uri="s3://kb/b.pdf", score=0.25, text="low", chunk_id="c3")
    scoped_out = _kb_result(uri="s3://kb/other-model.pdf", score=0.8, text="x", chunk_id="c4")
    trace = rag_app.build_request_trace(
        event={"requestContext": {"requestId": "api-req"}}, mode="normal", response_type="pages",
        query="q", results=[low, capped, chosen], selected_results=[chosen],
        search_attempts=[{"stage": "initial", "query": "q", "kbId": "KB1",
                          "excludedByModelScope": [scoped_out]}],
        dedupe_counts={id(chosen): 2},
    )
    rows = trace["candidates"]
    assert [(r["documentName"], r["selected"], r["excludedBy"]) for r in rows] == [
        ("a.pdf", True, None), ("a.pdf", False, "limit"), ("b.pdf", False, "below_threshold"),
        ("other-model.pdf", False, "model_scope"),
    ]
    assert rows[0]["modelType"] == "AXIEZ,NEXCUBE"
    assert rows[0]["dedupeCount"] == 2
    assert rows[1]["text"] is None
    assert trace["gate"]["excludedCounts"] == {
        "model_scope": 1, "dedupe": 2, "below_threshold": 1, "limit": 1}
    assert trace["gate"]["thresholds"] == [0.22, 0.3]
    assert trace["gate"]["selectedCount"] == 1
    assert trace["kb"]["kbId"] == "KB1"
    assert trace["requestId"] == "api-req"
    assert set(trace["searchAttempts"][0]) == ATTEMPT_KEYS


def test_request_trace_sums_rerank_over_attempts_and_keeps_rewrite(rag_app):
    attempts = [
        {"query": "q1", "stage": "initial", "rerank": {
            "enabled": True, "status": "fallback", "reason": "error", "callCount": 1, "latencyMs": 12}},
        {"query": "q2", "stage": "abbreviation_expansion", "rerank": {
            "enabled": True, "status": "applied", "reason": None, "callCount": 1, "latencyMs": 31}},
    ]
    rewrite = {"enabled": True, "status": "applied", "reason": None, "rewrittenQuery": "q1",
               "modelId": "rewrite-model", "callCount": 1, "latencyMs": 8}
    trace = rag_app.build_request_trace(event={}, mode="normal", response_type="pages",
                                        query="q", search_attempts=attempts, rewrite=rewrite)
    assert trace["rerank"]["callCount"] == 2
    assert trace["rerank"]["latencyMs"] == 43
    assert trace["rerank"]["status"] == "applied"
    assert trace["rewrite"]["rewrittenQuery"] == "q1"
    assert [a["stage"] for a in trace["searchAttempts"]] == ["initial", "abbreviation_expansion"]
    assert len(trace["kb"]["profileHash"]) == 64


def test_candidate_limit_is_recorded(rag_app):
    results = [_kb_result(text=f"chunk-{i}", chunk_id=f"c{i}", score=0.9 - i * 0.001) for i in range(31)]
    trace = rag_app.build_request_trace(event={}, mode="normal", response_type="pages", query="q",
                                        results=results, selected_results=results[:10])
    assert len(trace["candidates"]) == 30
    assert trace["truncatedTrace"] is True
    assert trace["truncationReason"] == "candidate_limit"


def test_trace_build_failure_returns_none_and_logs_type_only(monkeypatch, rag_app, capsys):
    def boom(**kwargs):
        raise ValueError("private search phrase")
    monkeypatch.setattr(rag_app, "_build_request_trace", boom)
    assert rag_app.build_request_trace(event={}, mode="normal", response_type="pages", query="q") is None
    logged = capsys.readouterr().out
    assert "retrieval_trace_failed" in logged and "ValueError" in logged
    assert "private search phrase" not in logged


# --- 部品の記録（検索・リランク・統合・書き換え・生成） ---

def test_merge_records_dedupe_count_on_surviving_chunk(rag_app):
    low = _kb_result(score=0.3)
    high = _kb_result(score=0.6)
    counts = {}
    merged = rag_app.merge_retrieval_results([low], [high], dedupe_counts=counts)
    assert merged == [high]
    assert counts == {id(high): 1}


def test_disabled_query_rewrite_reports_canonical_fields(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "QUERY_REWRITE_MODEL_ID", "")
    monkeypatch.setattr(rag_app, "_get_query_rewrite_client",
                        lambda: (_ for _ in ()).throw(AssertionError("client accessed")))
    assert rag_app.maybe_rewrite_search_query("original", []) == "original"
    query, info = rag_app.maybe_rewrite_search_query("original", [], return_trace=True)
    assert query == "original"
    assert info == {"enabled": False, "modelId": None, "status": "skipped",
                    "reason": "disabled", "rewrittenQuery": None, "callCount": 0, "latencyMs": 0}


def test_enabled_query_rewrite_reports_applied(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "QUERY_REWRITE_MODEL_ID", "rewrite-model")
    monkeypatch.setattr(rag_app, "_get_query_rewrite_client", lambda: object())
    monkeypatch.setattr(rag_app, "invoke_generation", lambda *args, **kwargs: ("書き換え後", {}, "end_turn"))
    history = [{"role": "user", "content": "前の質問"}, {"role": "assistant", "content": "回答"}]
    query, info = rag_app.maybe_rewrite_search_query("それは？", history, return_trace=True)
    assert query == "書き換え後"
    assert info["status"] == "applied" and info["rewrittenQuery"] == "書き換え後"
    assert info["callCount"] == 1 and info["reason"] is None


def test_rerank_trace_reports_disabled(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "RERANK_MODEL_ARN", "")
    trace = {}
    rows = [_kb_result()]
    assert rag_app.rerank_retrieval_results(rows, "q", trace=trace) is rows
    assert trace["status"] == "skipped" and trace["reason"] == "disabled"
    assert trace["callCount"] == 0


def test_query_knowledge_base_records_search_and_scope_exclusions(rag_app, monkeypatch):
    in_scope = _kb_result(uri="s3://kb/in.pdf")
    out_of_scope = _kb_result(uri="s3://kb/out.pdf", chunk_id="c2")
    agent = MagicMock()
    agent.retrieve.return_value = {"retrievalResults": [in_scope, out_of_scope]}
    monkeypatch.setattr(rag_app, "bedrock_agent", agent)
    monkeypatch.setattr(rag_app, "in_service_scope",
                        lambda metadata: metadata["x-amz-bedrock-kb-source-uri"].endswith("in.pdf"))
    monkeypatch.setattr(rag_app, "RERANK_MODEL_ARN", "")
    response = rag_app.query_knowledge_base("q", {}, number_of_results=30)
    search = response["_traceSearch"]
    assert response["retrievalResults"] == [in_scope]
    assert (search["requested"], search["returned"], search["afterPostFilter"]) == (30, 2, 1)
    assert search["excludedByModelScope"] == [out_of_scope]
    assert search["rerank"]["status"] == "skipped"
    assert isinstance(search["latencyMs"], int)


@pytest.mark.parametrize("api,usage", [
    ("invoke", {"inputTokens": 21, "outputTokens": 13}),
    ("converse", {"inputTokens": 5, "outputTokens": 3}),
])
def test_generation_meta_reports_tokens_and_request_style(rag_app, monkeypatch, api, usage):
    monkeypatch.setattr(rag_app, "invoke_generation",
                        lambda *args, **kwargs: ("answer", usage, "end_turn"))
    monkeypatch.setattr(rag_app, "get_model_profile", lambda model_id: SimpleNamespace(
        api=api, sampling=False, adaptive=False, effort=False, thinking_disable=True,
        image_input=True))
    text, meta = rag_app.generate_response_with_claude(
        "q", {"retrievalResults": [_kb_result(score=0.9)]}, None, "normal", return_meta=True)
    assert text == "answer"
    assert meta["requestStyle"] == api
    assert (meta["inputTokens"], meta["outputTokens"], meta["stopReason"]) == (
        usage["inputTokens"], usage["outputTokens"], "end_turn")
    assert meta["thinking"] == {"type": "disabled", "effort": None}
    assert len(meta["promptVersion"]) == 12
    assert rag_app.generate_response_with_claude(
        "q", {"retrievalResults": [_kb_result(score=0.9)]}, None, "normal") == "answer"


# --- ハンドラの全経路（clarify / not_found / pages / law） ---

@pytest.fixture
def handler_env(monkeypatch, rag_app):
    saved = []
    monkeypatch.setattr(rag_app, "get_caller_id", lambda event: "user-1")
    monkeypatch.setattr(rag_app, "get_chat_history", lambda *args, **kwargs: [])
    monkeypatch.setattr(rag_app, "enqueue_session_title", lambda *args: None)
    monkeypatch.setattr(rag_app.telemetry, "stamp_reformulation", lambda *args, **kwargs: None)
    monkeypatch.setattr(rag_app, "save_message_to_dynamodb",
                        lambda **kwargs: saved.append(kwargs) or f"message-{len(saved)}")
    return saved


def _event(query="振動がする", mode=None):
    body = {"query": query}
    if mode:
        body["mode"] = mode
    return {"body": json.dumps(body, ensure_ascii=False), "httpMethod": "POST",
            "requestContext": {"requestId": "api-req", "authorizer": {"claims": {"sub": "user-1"}}}}


def test_clarify_path_saves_trace_without_search(rag_app, monkeypatch, handler_env):
    monkeypatch.setattr(rag_app, "needs_clarify", lambda *args: (True, ["機種は？"]))
    response = rag_app.handle_rag_request(_event(), None, 1.0)
    assert response["statusCode"] == 200
    assistant = handler_env[-1]
    assert "retrieval_trace" not in handler_env[0]
    trace = assistant["retrieval_trace"]
    assert trace["gate"]["responseType"] == "clarify"
    assert trace["generation"] is None and trace["searchAttempts"] == []
    assert trace["requestId"] == "api-req"
    assert trace["questionRef"]["messageId"] == "message-1"
    assert "retrievalTrace" not in json.loads(response["body"])


def test_not_found_path_saves_attempts_and_no_selected_text(rag_app, monkeypatch, handler_env):
    monkeypatch.setattr(rag_app, "needs_clarify", lambda *args: (False, []))
    weak = _kb_result(score=0.1)
    monkeypatch.setattr(rag_app, "retrieve_for_normal_query", lambda *args, **kwargs: {
        "retrievalResults": [weak],
        "_traceSearch": {"kbId": "KB1", "searchType": "HYBRID", "requested": 30,
                         "returned": 1, "afterPostFilter": 1, "latencyMs": 5}})
    response = rag_app.handle_rag_request(_event(), None, 1.0)
    assert response["statusCode"] == 200
    trace = handler_env[-1]["retrieval_trace"]
    assert trace["gate"]["responseType"] == "not_found" and trace["gate"]["weak"] is True
    assert trace["generation"] is None
    assert trace["searchAttempts"][0]["stage"] == "initial"
    assert trace["searchAttempts"][0]["latencyMs"] == 5
    assert [c["excludedBy"] for c in trace["candidates"]] == ["below_threshold"]
    assert trace["candidates"][0]["text"] is None


def test_pages_path_saves_selected_text_and_generation(rag_app, monkeypatch, handler_env):
    monkeypatch.setattr(rag_app, "needs_clarify", lambda *args: (False, []))
    strong = _kb_result(score=0.8, text="本文")
    monkeypatch.setattr(rag_app, "retrieve_for_normal_query", lambda *args, **kwargs: {
        "retrievalResults": [strong]})
    monkeypatch.setattr(rag_app, "generate_response_with_claude", lambda *args, **kwargs: (
        "回答", {"promptVersion": "p1", "modelId": "m1", "requestStyle": "invoke",
               "thinking": {"type": "disabled", "effort": None},
               "inputTokens": 10, "outputTokens": 2, "stopReason": "end_turn", "latencyMs": 7}))
    response = rag_app.handle_rag_request(_event(), None, 1.0)
    assert response["statusCode"] == 200
    trace = handler_env[-1]["retrieval_trace"]
    assert trace["gate"]["responseType"] == "pages" and trace["gate"]["selectedCount"] == 1
    assert trace["candidates"][0]["selected"] is True and trace["candidates"][0]["text"] == "本文"
    assert trace["generation"]["inputTokens"] == 10 and trace["generation"]["modelId"] == "m1"
    assert trace["promptVersion"] == "p1"
    assert "retrievalTrace" not in json.loads(response["body"])


def test_pages_path_without_generation_meta_still_answers(rag_app, monkeypatch, handler_env):
    monkeypatch.setattr(rag_app, "needs_clarify", lambda *args: (False, []))
    monkeypatch.setattr(rag_app, "retrieve_for_normal_query", lambda *args, **kwargs: {
        "retrievalResults": [_kb_result(score=0.8)]})
    monkeypatch.setattr(rag_app, "generate_response_with_claude", lambda *args, **kwargs: "回答")
    response = rag_app.handle_rag_request(_event(), None, 1.0)
    assert response["statusCode"] == 200
    assert handler_env[-1]["retrieval_trace"]["generation"] is None


def test_law_path_saves_law_kb_and_truncated_full_text(rag_app, monkeypatch, handler_env):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag_app, "LAW_KNOWLEDGE_BASE_ID", "LAWKB12345")
    article = _kb_result(uri="s3://law/kb/egov/123.txt", score=0.9, text="第一条 断片",
                         source_type="law")
    monkeypatch.setattr(rag_app, "query_law_knowledge_base", lambda query: {
        "retrievalResults": [article],
        "_traceSearch": {"kbId": "LAWKB12345", "searchType": "MANAGED", "requested": 30,
                         "returned": 3, "afterPostFilter": 1, "latencyMs": 9}})
    full_text = "法" * 3000
    monkeypatch.setattr(rag_app, "prepare_law_references", lambda selected, **kwargs: [
        {**selected[0], "_lawReferenceText": full_text, "_lawReferenceCoverage": "full",
         "_lawReferenceReason": "complete", "_lawSourceResultIds": [id(selected[0])]}])
    monkeypatch.setattr(rag_app, "generate_response_with_claude", lambda *args, **kwargs: (
        "法令の回答", {"promptVersion": "law-p", "modelId": "m1", "requestStyle": "invoke",
                   "thinking": {}, "inputTokens": 1, "outputTokens": 1,
                   "stopReason": "end_turn", "latencyMs": 1}))
    response = rag_app.handle_rag_request(_event("建築基準法の規定", mode="law"), None, 1.0)
    assert response["statusCode"] == 200
    trace = handler_env[-1]["retrieval_trace"]
    assert trace["kb"]["kbId"] == "LAWKB12345"
    assert trace["searchAttempts"][0]["stage"] == "law"
    assert trace["searchAttempts"][0]["returned"] == 3
    assert trace["rewrite"]["reason"] == "law_mode"
    row = trace["candidates"][0]
    assert row["selected"] is True
    assert row["text"] == "法" * 1200 + "…"
    assert row["textTruncated"] is True and row["originalLength"] == 3000


def test_law_trace_marks_only_selected_source_chunks(rag_app):
    uri = "s3://law/kb/egov/123.txt"
    selected = _kb_result(uri=uri, score=0.9, text="採用する断片")
    below_threshold = _kb_result(uri=uri, score=0.01, text="採用しない断片")
    reference = {
        **selected,
        "_lawReferenceText": "採用する断片",
        "_lawSourceResultIds": [id(selected)],
    }

    rows, counts = rag_app._trace_candidates(
        [selected, below_threshold], [reference], [], {}, "law",
    )

    assert rows[0]["sourceUri"] == uri
    assert rows[0]["selected"] is True
    assert rows[0]["modelInputText"] == "採用する断片"
    assert rows[1]["selected"] is False
    assert rows[1]["excludedBy"] == "below_threshold"
    assert "modelInputText" not in rows[1]
    assert counts["below_threshold"] == 1


def test_law_trace_marks_all_contributing_chunks_once_per_reference(rag_app):
    uri = "s3://law/kb/egov/123.txt"
    selected = [
        _kb_result(uri=uri, score=0.9, text="第一の断片"),
        _kb_result(uri=uri, score=0.8, text="第二の断片"),
    ]
    reference = {
        **selected[0],
        "_lawReferenceText": "第一の断片\n第二の断片",
        "_lawSourceResultIds": [id(result) for result in selected],
    }

    rows, counts = rag_app._trace_candidates(selected, [reference], [], {}, "law")

    assert [row["selected"] for row in rows] == [True, True]
    assert rows[0]["modelInputText"] == "第一の断片\n第二の断片"
    assert "modelInputText" not in rows[1]
    assert counts["below_threshold"] == 0
    assert counts["limit"] == 0

    trace = rag_app._build_request_trace(
        event={}, mode="law", response_type="pages", query="法令の質問",
        composed_query=None, message_id="message-1", search_attempts=[], rewrite={},
        results=selected, selected_results=[reference], dedupe_counts={}, weak=False,
        generation_meta=None, started_at=None, rank_key=None,
    )

    assert trace["gate"]["selectedCount"] == 2
    assert sum(row.get("text") is not None for row in trace["candidates"]) == 1


# --- 露出制御・ログ ---

def test_telemetry_does_not_log_trace_payload(capsys, rag_app):
    with_trace = {
        "sessionId": "session-secret", "aiMessageId": "message-secret",
        "content": "private body", "query": "private search phrase",
        "retrievalTrace": {"searchAttempts": [{"query": "private search phrase"}]},
        "responseType": "pages", "pageCandidates": [], "sourceDocuments": [],
    }
    rag_app.telemetry.log_request({"httpMethod": "POST"},
                                  {"statusCode": 200, "body": json.dumps(with_trace)}, 0)
    logged = capsys.readouterr().out
    for secret in ("private search phrase", "private body", "session-secret", "message-secret"):
        assert secret not in logged


def _load_chat_management(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "lambda" / "chat" / "chat-management" / "app.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_history_message_reader_removes_trace():
    module = _load_chat_management("chat_mgmt_trace_test")
    table = MagicMock()
    module.chatlogs_table = table
    table.query.return_value = {"Items": [{"messageId": "m1", "ttl": 1,
                                          "retrievalTrace": {"questionRef": {"composedQuery": "secret"}}}]}
    messages = module.get_session_messages("s1")
    assert len(messages) == 1
    assert "retrievalTrace" not in messages[0]


def test_session_list_reads_only_listing_attributes():
    module = _load_chat_management("chat_mgmt_trace_list_test")
    table = MagicMock()
    module.chatlogs_table = table
    table.query.return_value = {"Items": [
        {"sessionId": "s1", "messageId": "m1", "role": "user", "timestamp": "2026-11-12T00:00:00Z",
         "content": "質問", "ttl": 1}]}
    sessions = module.get_sessions_by_user("user-1")
    kwargs = table.query.call_args.kwargs
    names = kwargs["ExpressionAttributeNames"]
    projected = {names[token.strip()] for token in kwargs["ProjectionExpression"].split(",")}
    assert "retrievalTrace" not in projected and "sourceDocuments" not in projected
    assert {"sessionId", "timestamp", "content", "sessionTitle", "role", "ttl", "ragMode"} <= projected
    assert sessions[0]["title"] == "質問"
