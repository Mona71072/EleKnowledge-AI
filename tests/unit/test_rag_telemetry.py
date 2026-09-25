"""rag の運用テレメトリ: 構造化ログ・500 経路の一般化・資料クリックの加算・言い換えの印。"""
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = ROOT / "lambda" / "rag" / "rag-function"

os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
os.environ.setdefault("KB_SOURCE_BUCKET", "kb-source-bucket")
os.environ.setdefault("KB_SOURCE_PREFIX", "docs/")
os.environ.setdefault("DOCUMENTS_BUCKET", "documents-test")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, RAG_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


telemetry = _load("rag_telemetry_mod", "telemetry.py")
with patch("boto3.client"), patch("boto3.resource"):
    rag = _load("rag_app_telemetry", "app.py")


def _client_error(op, code="ThrottlingException", msg="Rate exceeded"):
    return ClientError({"Error": {"Code": code, "Message": msg}}, op)


# ------------------------------------------------------------------ stage / error response
def test_stage_of_maps_botocore_operations():
    assert telemetry.stage_of(_client_error("Retrieve")) == "retrieve"
    assert telemetry.stage_of(_client_error("InvokeModel")) == "generate"
    assert telemetry.stage_of(_client_error("PutItem")) == "save"
    assert telemetry.stage_of(_client_error("Query")) == "history"
    assert telemetry.stage_of(ValueError("x")) == "unknown"


def test_error_response_hides_aws_message_and_logs_structured_line(capsys):
    event = {"requestContext": {"requestId": "req-123"}}
    resp = telemetry.error_response({"h": "1"}, _client_error("InvokeModel"), time.perf_counter(), event)
    assert resp["statusCode"] == 500
    body = json.loads(resp["body"])
    assert body == {"error": "InternalServerError", "message": telemetry.GENERIC_500_MESSAGE, "requestId": "req-123"}
    assert "Rate exceeded" not in resp["body"]
    line = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert line["event"] == "rag_error" and line["stage"] == "generate"
    assert line["errorCode"] == "ThrottlingException" and line["apiRequestId"] == "req-123"
    assert line["exceptionClass"] == "ClientError"
    assert "errorMessage" not in line and "Rate exceeded" not in json.dumps(line)
    assert "latencyMs" in line


def test_error_response_omits_non_client_exception_text(capsys):
    event = {"requestContext": {"requestId": "req-456"}}
    secret = "引用チャンクの本文"
    resp = telemetry.error_response({"h": "1"}, ValueError(secret), time.perf_counter(), event)
    body = json.loads(resp["body"])
    assert body["error"] == "InternalServerError" and secret not in resp["body"]
    logged = capsys.readouterr().out
    assert secret not in logged
    line = json.loads(logged.strip().splitlines()[-1])
    assert line["errorCode"] == "ValueError" and line["exceptionClass"] == "ValueError"
    assert "errorMessage" not in line


def test_log_request_emits_counts_not_bodies(capsys):
    event = {"httpMethod": "POST", "requestContext": {"requestId": "req-9"}}
    body = {"sessionId": "s1", "aiMessageId": "m2", "responseType": "pages", "content": "秘密の本文",
            "pageCandidates": [{}, {}, {}], "sourceDocuments": [{}], "priorityExpanded": True}
    telemetry.log_request(event, {"statusCode": 200, "body": json.dumps(body)}, time.perf_counter())
    out = capsys.readouterr().out
    line = json.loads(out.strip().splitlines()[-1])
    assert line["event"] == "rag_request" and line["apiRequestId"] == "req-9"
    assert "sessionId" not in line and "messageId" not in line
    assert line["responseType"] == "pages"
    assert line["pageCandidates"] == 3 and line["sourceDocuments"] == 1
    assert "秘密の本文" not in out and "content" not in line


def test_log_request_skips_document_get(capsys):
    telemetry.log_request({"httpMethod": "GET"}, {"statusCode": 200, "body": "{}"}, time.perf_counter())
    assert capsys.readouterr().out == ""


# ------------------------------------------------------------------ document open
def test_record_document_open_updates_owned_assistant_message(capsys):
    table = MagicMock()
    ok = telemetry.record_document_open(table, "s1", "m1", "u1", lambda s, u: True, "s3://b/docs/C-591124.pdf",
                                        {"requestContext": {"requestId": "r1"}})
    assert ok is True
    kw = table.update_item.call_args.kwargs
    assert kw["Key"] == {"sessionId": "s1", "messageId": "m1"}
    assert "ADD documentOpens :one" in kw["UpdateExpression"] and "lastOpenedAt" in kw["UpdateExpression"]
    assert "#role = :assistant" in kw["ConditionExpression"]
    line = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert line["event"] == "document_open" and line["documentName"] == "C-591124.pdf"
    assert "sessionId" not in line and "messageId" not in line


def test_record_document_open_refuses_foreign_session_and_missing_ids():
    table = MagicMock()
    assert telemetry.record_document_open(table, "s1", "m1", "u1", lambda s, u: False, "s3://x") is False
    assert telemetry.record_document_open(table, "", "m1", "u1", lambda s, u: True, "s3://x") is False
    table.update_item.assert_not_called()


def test_record_document_open_swallows_conditional_failure():
    table = MagicMock()
    table.update_item.side_effect = _client_error("UpdateItem", code="ConditionalCheckFailedException")
    assert telemetry.record_document_open(table, "s1", "user-msg", "u1", lambda s, u: True, "s3://x") is False


# ------------------------------------------------------------------ reformulation
def _history(answered_at, **kw):
    row = {"role": "assistant", "sessionId": "s1", "messageId": "a1", "responseType": "pages", "timestamp": answered_at}
    row.update(kw)
    return [{"role": "user", "sessionId": "s1", "messageId": "u1"}, row]


def test_stamp_reformulation_marks_recent_unrated_pages_answer(capsys):
    table = MagicMock()
    now = datetime(2026, 9, 23, 1, 3, tzinfo=timezone.utc)
    assert telemetry.stamp_reformulation(table, _history("2026-09-23T01:00:00Z"), now) is True
    kw = table.update_item.call_args.kwargs
    assert kw["Key"] == {"sessionId": "s1", "messageId": "a1"}
    assert "attribute_not_exists(reformulatedAt)" in kw["ConditionExpression"]
    assert kw["ExpressionAttributeValues"][":now"] == "2026-09-23T01:03:00Z"
    line = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert line == {"event": "reformulation"}


@pytest.mark.parametrize("history", [
    [],
    _history("2026-09-23T01:00:00Z", feedback="good"),                # 評価済み
    _history("2026-09-23T01:00:00Z", responseType="not_found"),        # 候補なし
    _history("2026-09-23T00:40:00Z"),                                  # 10 分超
    _history("2026-09-23T01:00:00Z", reformulatedAt="x"),              # 印済み
    [{"role": "user", "sessionId": "s1", "messageId": "u1"}],           # 直前が回答ではない
])
def test_stamp_reformulation_skips(history):
    table = MagicMock()
    now = datetime(2026, 9, 23, 1, 3, tzinfo=timezone.utc)
    assert telemetry.stamp_reformulation(table, history, now) is False
    table.update_item.assert_not_called()


# ------------------------------------------------------------------ app wiring
def test_document_endpoint_passes_session_and_message_to_telemetry(monkeypatch):
    calls = []
    monkeypatch.setattr(rag.telemetry, "record_document_open", lambda *a, **k: calls.append(a) or True)
    monkeypatch.setattr(rag, "presign_source_uri", lambda client, uri: "https://signed.example/x")
    with patch.object(rag.boto3, "client"):
        event = {"httpMethod": "GET", "requestContext": {"authorizer": {"claims": {"sub": "user-1"}}, "requestId": "r1"},
                 "queryStringParameters": {"uri": "s3://kb-source-bucket/docs/manual.pdf", "s": "sess-1", "m": "msg-1"}}
        resp = rag.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    assert calls and calls[0][1:4] == ("sess-1", "msg-1", "user-1")


def test_handler_500_returns_generic_body_with_request_id(monkeypatch, capsys):
    monkeypatch.setattr(rag, "get_caller_id", lambda event: "user-1")
    monkeypatch.setattr(rag, "owns_session", lambda s, u: (_ for _ in ()).throw(_client_error("Query", code="ProvisionedThroughputExceededException", msg="internal detail")))
    event = {"httpMethod": "POST", "requestContext": {"requestId": "req-500"},
             "body": json.dumps({"sessionId": "s1", "query": "x"})}
    resp = rag.lambda_handler(event, None)
    assert resp["statusCode"] == 500
    body = json.loads(resp["body"])
    assert body["requestId"] == "req-500" and "internal detail" not in resp["body"]
    lines = [json.loads(l) for l in capsys.readouterr().out.strip().splitlines() if l.startswith("{")]
    kinds = [l["event"] for l in lines]
    assert "rag_error" in kinds and "rag_request" in kinds
    err = next(l for l in lines if l["event"] == "rag_error")
    assert err["stage"] == "history" and err["errorCode"] == "ProvisionedThroughputExceededException"
    req = next(l for l in lines if l["event"] == "rag_request")
    assert req["statusCode"] == 500 and req["apiRequestId"] == "req-500"


@pytest.mark.parametrize("template_name, expected_count", [
    ("phase1-template.yaml", 1),
    ("phase2-template.yaml", 2),
    ("announcements-monitoring-template.yaml", 1),
])
def test_api_gateway_access_logs_omit_user_and_device_identifiers(template_name, expected_count):
    template = (ROOT / "infrastructure" / "sam" / template_name).read_text()
    lines = template.splitlines()
    format_lines = []
    for index, line in enumerate(lines):
        if line.strip() != "AccessLogSetting:":
            continue
        format_line = next((candidate for candidate in lines[index:index + 5] if "Format:" in candidate), None)
        assert format_line is not None
        format_lines.append(format_line)

    assert len(format_lines) == expected_count
    for format_line in format_lines:
        assert "$context.identity.sourceIp" not in format_line
        assert "$context.identity.userAgent" not in format_line
        assert "$context.authorizer.claims.sub" not in format_line
