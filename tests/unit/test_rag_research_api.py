import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError


ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = ROOT / "lambda" / "rag" / "rag-function"
sys.path.insert(0, str(RAG_DIR))


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, RAG_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


research_api = _load_module("research_api_test", "research_api.py")
research_job_store = _load_module("research_job_store_test", "research_job_store.py")
research_request = _load_module("research_request_test", "research_request.py")
_deserializer = TypeDeserializer()


def _unpack(item):
    return {key: _deserializer.deserialize(value) for key, value in item.items()}


def _event(method="GET", path="/dev/rag/research/quota", user_id="user-1", body=None):
    return {
        "httpMethod": method,
        "path": path,
        "body": json.dumps(body) if body is not None else None,
        "requestContext": {"authorizer": {"claims": {"sub": user_id}}},
    }


def test_normalize_research_request_discards_client_user_id():
    result = research_request.normalize_research_request({
        "query": "  compare models ",
        "clientRequestId": "550E8400-E29B-41D4-A716-446655440000",
        "filters": {"category": [" spec ", "drawing"], "modelType": " AXIEZ "},
        "userId": "untrusted",
    })

    assert result == {
        "query": "compare models",
        "clientRequestId": "550e8400-e29b-41d4-a716-446655440000",
        "filters": {"category": ["spec", "drawing"], "modelType": "AXIEZ"},
    }


@pytest.mark.parametrize("body", [
    None,
    {"query": " ", "clientRequestId": "550e8400-e29b-41d4-a716-446655440000"},
    {"query": "x" * 2001, "clientRequestId": "550e8400-e29b-41d4-a716-446655440000"},
    {"query": "question", "clientRequestId": "invalid"},
    {"query": "question", "clientRequestId": "550e8400-e29b-41d4-a716-446655440000", "filters": {"bad": 1}},
])
def test_rejects_invalid_research_requests(body):
    with pytest.raises(ValueError):
        research_request.normalize_research_request(body)


def test_reservation_is_atomic_and_uses_jst_calendar_day():
    now = datetime(2026, 11, 2, 15, 30, tzinfo=timezone.utc)
    items = research_job_store.build_reservation_transaction(
        table_name="research-jobs",
        user_id="user-1",
        client_request_id="request-1",
        job_id="job-1",
        session_id="session-1",
        user_message_id="message-1",
        filters={},
        now=now,
    )

    assert len(items) == 5
    assert items[0]["Put"]["ConditionExpression"] == "attribute_not_exists(pk) OR expiresAt <= :now"
    assert "#count < :limit" in items[1]["Update"]["ConditionExpression"]
    assert "#count < :limit" in items[2]["Update"]["ConditionExpression"]
    assert items[3]["Put"]["ConditionExpression"] == "attribute_not_exists(pk)"
    assert items[4]["Put"]["ConditionExpression"] == "attribute_not_exists(pk)"
    assert items[1]["Update"]["Key"]["pk"]["S"] == "QUOTA#user-1#2026-11-03"
    assert items[4]["Put"]["Item"]["status"]["S"] == "queued"
    assert "createdAt" in items[4]["Put"]["Item"]
    assert "query" not in items[4]["Put"]["Item"]


def test_queued_failure_compensates_quota_and_owns_lock_conditionally():
    items = research_job_store.build_queued_failure_transaction(
        table_name="research-jobs", user_id="user-1", job_id="job-1",
        now=datetime(2026, 11, 2, 15, 30, tzinfo=timezone.utc),
        error_code="DispatchFailed",
    )

    assert len(items) == 3
    assert "#status = :queued AND #refunded = :false" in items[0]["Update"]["ConditionExpression"]
    assert items[1]["Update"]["UpdateExpression"] == "ADD #count :minus"
    assert items[2]["Delete"]["ConditionExpression"] == "jobId = :job"


def test_worker_claim_is_guarded_by_queued_state_dispatch_time_and_active_lock():
    items = research_job_store.build_claim_transaction(
        table_name="research-jobs", user_id="user-1", job_id="job-1",
        lease_token="lease-1", now=datetime(2026, 11, 2, 15, 30, tzinfo=timezone.utc),
    )

    assert len(items) == 2
    assert "#status = :queued AND dispatchDeadline >= :now" in items[0]["Update"]["ConditionExpression"]
    assert items[1]["ConditionCheck"]["ConditionExpression"] == "jobId = :job"
    values = _unpack(items[0]["Update"]["ExpressionAttributeValues"])
    assert values[":running"] == "running"
    assert values[":lease"] == "lease-1"


def test_progress_update_requires_own_running_lease():
    update = research_job_store.build_progress_update(
        table_name="research-jobs", job_id="job-1", lease_token="lease-1",
        stage="searching", progress={"step": 2, "searchesDone": 1, "searchesTotal": 3},
        now=datetime(2026, 11, 2, 15, 30, tzinfo=timezone.utc), poll_after_ms=5000,
    )

    assert update["ConditionExpression"] == "#status = :running AND #lease = :lease"
    values = _unpack(update["ExpressionAttributeValues"])
    assert values[":stage"] == "searching"
    assert values[":poll"] == 5000


def test_completion_saves_answer_and_releases_lock_in_one_transaction():
    items = research_job_store.build_completion_transaction(
        table_name="research-jobs", chatlogs_table_name="chatlogs",
        user_id="user-1", job_id="job-1", lease_token="lease-1",
        message={"sessionId": "session-1", "messageId": "research-job-1", "userId": "user-1"},
        now=datetime(2026, 11, 2, 15, 30, tzinfo=timezone.utc),
        progress={"step": 6, "totalSteps": 6},
        research={"claims": [], "searchCount": 3, "evidence": [{"score": 0.81}]},
    )

    assert len(items) == 3
    assert items[0]["Put"]["TableName"] == "chatlogs"
    assert items[1]["Update"]["ConditionExpression"] == "#status = :running AND #lease = :lease"
    assert items[2]["Delete"]["ConditionExpression"] == "jobId = :job"
    values = _unpack(items[1]["Update"]["ExpressionAttributeValues"])
    assert values[":completed"] == "completed"
    assert values[":result"]["searchCount"] == 3
    assert values[":result"]["evidence"][0]["score"] == _deserializer.deserialize(
        items[1]["Update"]["ExpressionAttributeValues"][":result"]["M"]["evidence"]["L"][0]["M"]["score"]
    )


def test_running_failure_refunds_reservation_day_not_current_day():
    items = research_job_store.build_running_failure_transaction(
        table_name="research-jobs", user_id="user-1", job_id="job-1",
        lease_token="lease-1", quota_day="2026-11-03",
        now=datetime(2026, 11, 4, 1, 0, tzinfo=timezone.utc), error_code="Timeout",
    )

    assert items[1]["Update"]["Key"]["pk"]["S"] == "QUOTA#user-1#2026-11-03"
    assert items[0]["Update"]["ConditionExpression"] == "#status = :running AND #lease = :lease AND #refunded = :false"


def test_stale_queued_job_is_failed_and_refunded_to_reserved_day():
    table = Mock()
    table.name = "research-jobs"
    job = {
        "jobId": "job-1", "userId": "user-1", "status": "queued",
        "dispatchDeadline": 1, "quotaDay": "2026-11-02",
    }
    table.get_item.side_effect = [{"Item": job}, {"Item": {**job, "status": "failed"}}]

    with (
        patch.object(research_api.boto3, "client", return_value=Mock()),
        patch.object(research_api.research_job_store, "fail_queued_research_job") as fail,
    ):
        result = research_api._job_response(table, "job-1", {}, "user-1")

    fail.assert_called_once()
    assert fail.call_args.kwargs["quota_day"] == "2026-11-02"
    assert result["statusCode"] == 200
    assert json.loads(result["body"])["status"] == "failed"


@patch.dict("os.environ", {"RESEARCH_MODE_ENABLED": "off"}, clear=False)
def test_feature_flag_off_hides_research_endpoints():
    result = research_api.lambda_handler(_event(), None)

    assert result["statusCode"] == 404


@patch.dict("os.environ", {"RESEARCH_MODE_ENABLED": "beta", "ENVIRONMENT": "prd"}, clear=False)
def test_non_dev_environment_cannot_enable_research_api():
    result = research_api.lambda_handler(_event(), None)

    assert result["statusCode"] == 404


@patch.dict("os.environ", {"RESEARCH_MODE_ENABLED": "beta"}, clear=False)
def test_research_api_requires_cognito_sub():
    result = research_api.lambda_handler(_event(user_id=""), None)

    assert result["statusCode"] == 401


def test_daily_quota_uses_jst_and_returns_next_midnight():
    table = Mock()
    table.get_item.return_value = {"Item": {"count": 4}}
    quota = research_api.get_daily_quota(
        table, "user-1", datetime(2026, 11, 2, 15, 30, tzinfo=timezone.utc)
    )

    table.get_item.assert_called_once_with(
        Key={"pk": "QUOTA#user-1#2026-11-03"}, ConsistentRead=True
    )
    assert quota == {
        "limit": 10,
        "used": 4,
        "remaining": 6,
        "resetsAt": "2026-11-04T00:00:00+09:00",
    }


def test_reservation_fallback_classifies_live_lock_when_cancellation_reasons_missing():
    now = datetime.now(timezone.utc)
    table = Mock()
    table.get_item.side_effect = [
        {},
        {"Item": {"jobId": "other-job", "expiresAt": int(now.timestamp()) + 60}},
    ]

    response = research_api.classify_reservation_conflict(
        table, "user-1", "550e8400-e29b-41d4-a716-446655440000", now, {},
    )

    assert response["statusCode"] == 409
    assert json.loads(response["body"])["error"] == "ResearchAlreadyRunning"


def test_reservation_fallback_classifies_daily_attempt_limit():
    now = datetime.now(timezone.utc)
    table = Mock()
    table.get_item.side_effect = [
        {}, {}, {"Item": {"count": 2}},
        {"Item": {"count": research_job_store.DAILY_ATTEMPT_LIMIT}},
    ]

    response = research_api.classify_reservation_conflict(
        table, "user-1", "550e8400-e29b-41d4-a716-446655440000", now, {},
    )

    assert response["statusCode"] == 429
    assert json.loads(response["body"])["error"] == "DailyAttemptLimitExceeded"


def test_reservation_failure_log_records_codes_but_not_identifiers(capsys):
    error = ClientError({
        "Error": {"Code": "TransactionCanceledException", "Message": "private detail"},
        "CancellationReasons": [{"Code": "ConditionalCheckFailed"}, {"Code": "None"}],
    }, "TransactWriteItems")

    research_api._log_reservation_failure(error)

    event = json.loads(capsys.readouterr().out)
    assert event == {
        "event": "research_reservation_failed",
        "errorCode": "TransactionCanceledException",
        "cancellationReasons": ["ConditionalCheckFailed", "None"],
    }
    assert "private detail" not in json.dumps(event)


@patch.dict("os.environ", {
    "RESEARCH_MODE_ENABLED": "beta",
    "RESEARCH_JOBS_TABLE": "research-jobs-test",
    "CHATLOGS_TABLE": "chatlogs-test",
    "RESEARCH_WORKER_FUNCTION": "rag-research-worker-dev",
}, clear=False)
def test_post_reserves_job_saves_question_and_dispatches_job_id_only():
    jobs_table = Mock(name="research-jobs-test")
    jobs_table.name = "research-jobs-test"
    chatlogs_table = Mock()
    dynamodb_resource = Mock()
    dynamodb_resource.Table.return_value = chatlogs_table
    dynamodb_client = Mock()
    lambda_client = Mock()
    fake_app = SimpleNamespace(
        generate_session_id=lambda: "session-1",
        generate_message_id=lambda: "message-1",
        get_chat_history=lambda *args, **kwargs: [],
        needs_clarify=lambda *args, **kwargs: (False, []),
        owns_session=lambda *args, **kwargs: True,
        _fallback_session_title=lambda query: query[:50],
        chatlog_metric_keys=SimpleNamespace(metric_day_keys=lambda *args: {}),
    )
    body = {
        "query": "compare these models",
        "clientRequestId": "550e8400-e29b-41d4-a716-446655440000",
    }

    with (
        patch.object(research_api, "_load_rag_app", return_value=fake_app),
        patch.object(research_api, "_get_request_record", return_value=None),
        patch.object(research_api.boto3, "resource", return_value=dynamodb_resource),
        patch.object(research_api.boto3, "client", return_value=lambda_client),
        patch.object(research_api.research_job_store, "reserve_research_job") as api_reserve,
        patch.object(research_api, "get_daily_quota", return_value={"limit": 10, "used": 1, "remaining": 9, "resetsAt": "later"}),
    ):
        result = research_api._handle_post(
            _event("POST", "/dev/rag/research", body=body),
            {}, "user-1", jobs_table, dynamodb_client,
        )

    payload = json.loads(result["body"])
    assert result["statusCode"] == 202
    assert payload["status"] == "queued"
    assert payload["quota"]["remaining"] == 9
    saved = chatlogs_table.put_item.call_args.kwargs["Item"]
    assert saved["content"] == "compare these models"
    assert saved["researchJobId"] == payload["jobId"]
    lambda_client.invoke.assert_called_once()
    assert json.loads(lambda_client.invoke.call_args.kwargs["Payload"]) == {"jobId": payload["jobId"]}
    api_reserve.assert_called_once()


def _post_with_failing_dispatch(chatlogs_table, lambda_client):
    jobs_table = Mock(name="research-jobs-test")
    jobs_table.name = "research-jobs-test"
    dynamodb_resource = Mock()
    dynamodb_resource.Table.return_value = chatlogs_table
    fake_app = SimpleNamespace(
        generate_session_id=lambda: "session-1",
        generate_message_id=lambda: "message-1",
        get_chat_history=lambda *args, **kwargs: [],
        needs_clarify=lambda *args, **kwargs: (False, []),
        owns_session=lambda *args, **kwargs: True,
        _fallback_session_title=lambda query: query[:50],
        chatlog_metric_keys=SimpleNamespace(metric_day_keys=lambda *args: {}),
    )
    body = {
        "query": "compare these models",
        "clientRequestId": "550e8400-e29b-41d4-a716-446655440000",
    }
    with (
        patch.object(research_api, "_load_rag_app", return_value=fake_app),
        patch.object(research_api, "_get_request_record", return_value=None),
        patch.object(research_api.boto3, "resource", return_value=dynamodb_resource),
        patch.object(research_api.boto3, "client", return_value=lambda_client),
        patch.object(research_api.research_job_store, "reserve_research_job"),
        patch.object(research_api.research_job_store, "fail_queued_research_job"),
    ):
        return research_api._handle_post(
            _event("POST", "/dev/rag/research", body=body),
            {}, "user-1", jobs_table, Mock(),
        )


@patch.dict("os.environ", {
    "RESEARCH_MODE_ENABLED": "beta",
    "CHATLOGS_TABLE": "chatlogs-test",
    "RESEARCH_WORKER_FUNCTION": "rag-research-worker-dev",
}, clear=False)
def test_post_dispatch_failure_marks_saved_question_deleted():
    chatlogs_table = Mock()
    lambda_client = Mock()
    lambda_client.invoke.side_effect = RuntimeError("boom")

    result = _post_with_failing_dispatch(chatlogs_table, lambda_client)

    assert result["statusCode"] == 503
    kwargs = chatlogs_table.update_item.call_args.kwargs
    assert kwargs["Key"] == {"sessionId": "session-1", "messageId": "message-1"}
    assert kwargs["ExpressionAttributeValues"][":true"] is True
    assert "deleted" in kwargs["ExpressionAttributeNames"].values()


@patch.dict("os.environ", {
    "RESEARCH_MODE_ENABLED": "beta",
    "CHATLOGS_TABLE": "chatlogs-test",
    "RESEARCH_WORKER_FUNCTION": "rag-research-worker-dev",
}, clear=False)
def test_post_dispatch_failure_still_503_when_question_cleanup_fails(capsys):
    chatlogs_table = Mock()
    chatlogs_table.update_item.side_effect = RuntimeError("secret-detail")
    lambda_client = Mock()
    lambda_client.invoke.side_effect = RuntimeError("boom")

    result = _post_with_failing_dispatch(chatlogs_table, lambda_client)

    assert result["statusCode"] == 503
    out = capsys.readouterr().out
    assert "question_cleanup_failed error_type=RuntimeError" in out
    assert "secret-detail" not in out


@patch.dict("os.environ", {
    "RESEARCH_MODE_ENABLED": "beta",
    "CHATLOGS_TABLE": "chatlogs-test",
    "RESEARCH_WORKER_FUNCTION": "rag-research-worker-dev",
}, clear=False)
def test_post_question_save_failure_does_not_touch_chatlogs_again():
    chatlogs_table = Mock()
    chatlogs_table.put_item.side_effect = RuntimeError("put failed")
    lambda_client = Mock()

    result = _post_with_failing_dispatch(chatlogs_table, lambda_client)

    assert result["statusCode"] == 503
    chatlogs_table.update_item.assert_not_called()
    lambda_client.invoke.assert_not_called()
