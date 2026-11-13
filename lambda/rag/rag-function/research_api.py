"""Authenticated API for long-running research jobs."""

import json
import os
import time
import uuid
from datetime import datetime, time as datetime_time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

import boto3
from botocore.exceptions import ClientError

import research_job_store
from research_request import normalize_research_request


RESEARCH_MODES = frozenset({"off", "beta", "on"})
DAILY_SUCCESS_LIMIT = research_job_store.SUCCESS_QUOTA_LIMIT
JST = ZoneInfo("Asia/Tokyo")
REGION = os.environ.get("AWS_REGION", "ap-northeast-1")


def _response(status_code: int, payload: dict, headers: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(payload, ensure_ascii=False, default=_json_default),
    }


def _json_default(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def _error(status_code: int, code: str, headers: dict, **extra) -> dict:
    return _response(status_code, {"error": code, **extra}, headers)


def get_daily_quota(table, user_id: str, now: datetime) -> dict:
    jst_now = now.astimezone(JST)
    date_key = jst_now.strftime("%Y-%m-%d")
    response = table.get_item(
        Key={"pk": f"QUOTA#{user_id}#{date_key}"}, ConsistentRead=True
    )
    used = int((response.get("Item") or {}).get("count", 0))
    reset = datetime.combine(
        jst_now.date() + timedelta(days=1), datetime_time.min, tzinfo=JST
    )
    return {
        "limit": DAILY_SUCCESS_LIMIT,
        "used": used,
        "remaining": max(0, DAILY_SUCCESS_LIMIT - used),
        "resetsAt": reset.isoformat(),
    }


def get_daily_attempt_count(table, user_id: str, now: datetime) -> int:
    response = table.get_item(
        Key={"pk": f"ATTEMPT#{user_id}#{research_job_store.day_key(now)}"},
        ConsistentRead=True,
    )
    return int((response.get("Item") or {}).get("count", 0))


def _get_caller_id(event: dict) -> str:
    context = event.get("requestContext") or {}
    authorizer = context.get("authorizer") or {}
    claims = authorizer.get("claims") or {}
    return claims.get("sub") or ""


def _path(event: dict) -> str:
    return event.get("resource") or event.get("rawPath") or event.get("path") or ""


def _parse_body(event: dict) -> dict:
    raw = event.get("body")
    if isinstance(raw, str):
        parsed = json.loads(raw)
    else:
        parsed = raw
    if not isinstance(parsed, dict):
        raise ValueError("Request body must be an object")
    return parsed


def _load_rag_app():
    import app
    return app


def _get_request_record(table, user_id: str, client_request_id: str):
    return table.get_item(
        Key={"pk": f"REQ#{user_id}#{client_request_id}"}, ConsistentRead=True
    ).get("Item")


def _get_job(table, job_id: str):
    return table.get_item(Key={"pk": f"JOB#{job_id}"}, ConsistentRead=True).get("Item")


def _accepted_existing_job(table, job_id: str, user_id: str, headers: dict):
    job = _get_job(table, job_id)
    if not job or job.get("userId") != user_id:
        return _error(404, "NotFound", headers)
    job = _expire_stale_job(table, job)
    quota = get_daily_quota(table, user_id, datetime.now(JST))
    payload = {
        "jobId": job_id, "sessionId": job.get("sessionId"),
        "userMessageId": job.get("userMessageId"),
        "status": job.get("status"), "quota": quota,
    }
    if job.get("status") == "queued":
        payload["pollAfterMs"] = 5000
    elif job.get("status") == "completed":
        payload["pollAfterMs"] = 0
    return _response(202, payload, headers)


def classify_reservation_conflict(table, user_id: str, client_request_id: str, now: datetime, headers: dict):
    """Recover a useful idempotency/quota/concurrency response without cancellation details."""
    existing = _get_request_record(table, user_id, client_request_id)
    if existing:
        return _accepted_existing_job(table, existing["jobId"], user_id, headers)

    active = table.get_item(
        Key={"pk": f"ACTIVE#{user_id}"}, ConsistentRead=True
    ).get("Item")
    if active and int(active.get("expiresAt", 0)) > int(now.timestamp()):
        return _error(409, "ResearchAlreadyRunning", headers)

    quota = get_daily_quota(table, user_id, now)
    if quota["remaining"] <= 0:
        return _error(429, "DailyLimitExceeded", headers, quota=quota)

    if get_daily_attempt_count(table, user_id, now) >= research_job_store.DAILY_ATTEMPT_LIMIT:
        return _error(429, "DailyAttemptLimitExceeded", headers)
    return None


def _log_reservation_failure(error: ClientError) -> None:
    detail = error.response.get("Error", {})
    reason_codes = [
        reason.get("Code", "")
        for reason in error.response.get("CancellationReasons") or []
    ]
    print(json.dumps({
        "event": "research_reservation_failed",
        "errorCode": detail.get("Code", "Unknown"),
        "cancellationReasons": reason_codes,
    }, separators=(",", ":")))


def _job_response(table, job_id: str, headers: dict, expected_user_id: str):
    job = _get_job(table, job_id)
    if not job or job.get("userId") != expected_user_id:
        return _error(404, "NotFound", headers)
    job = _expire_stale_job(table, job)
    payload = {
        "jobId": job_id,
        "sessionId": job.get("sessionId"),
        "status": job.get("status"),
        "stage": job.get("stage"),
        "progress": job.get("progress") or {},
    }
    if job.get("status") == "queued":
        payload["pollAfterMs"] = 5000
    elif job.get("stage") == "checking":
        payload["pollAfterMs"] = 3000
    if job.get("pollAfterMs"):
        payload["pollAfterMs"] = int(job["pollAfterMs"])
    if job.get("errorCode"):
        payload["error"] = {"code": job["errorCode"]}
    if job.get("status") == "completed" and job.get("resultMessageId"):
        chatlogs = boto3.resource("dynamodb", region_name=REGION).Table(
            os.environ["CHATLOGS_TABLE"]
        )
        message = chatlogs.get_item(
            Key={
                "sessionId": job["sessionId"],
                "messageId": job["resultMessageId"],
            },
            ConsistentRead=True,
        ).get("Item")
        if message and message.get("userId") == expected_user_id:
            public_message = {
                key: message[key]
                for key in (
                    "messageId", "role", "content", "timestamp", "citations",
                    "sourceDocuments", "responseType", "research",
                )
                if key in message
            }
            public_message["id"] = message.get("messageId")
            payload["message"] = public_message
    return _response(200, payload, headers)


def _expire_stale_job(table, job: dict):
    now = datetime.now(timezone.utc)
    client = boto3.client("dynamodb", region_name=REGION)
    try:
        if job.get("status") == "queued" and int(job.get("dispatchDeadline", 0)) < int(now.timestamp()):
            research_job_store.fail_queued_research_job(
                client, table_name=table.name, user_id=job["userId"],
                job_id=job["jobId"], now=now, error_code="DispatchTimeout",
                quota_day=job.get("quotaDay"),
            )
        elif job.get("status") == "running" and int(job.get("runningUntil", 0)) < int(now.timestamp()):
            research_job_store.fail_running_research_job(
                client, table_name=table.name, user_id=job["userId"],
                job_id=job["jobId"], lease_token=job.get("leaseToken", ""),
                quota_day=job.get("quotaDay") or research_job_store.day_key(now),
                now=now, error_code="Timeout",
            )
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") != "TransactionCanceledException":
            raise
    return _get_job(table, job["jobId"]) or job


def _handle_post(event, headers, user_id: str, jobs_table, dynamodb_client):
    rag_app = _load_rag_app()
    try:
        body = _parse_body(event)
        request = normalize_research_request(body)
    except (ValueError, json.JSONDecodeError):
        return _error(400, "ValidationError", headers)

    client_request_id = request["clientRequestId"]
    existing = _get_request_record(jobs_table, user_id, client_request_id)
    if existing:
        return _accepted_existing_job(jobs_table, existing["jobId"], user_id, headers)

    session_id = request.get("sessionId") or rag_app.generate_session_id()
    if request.get("sessionId") and not rag_app.owns_session(session_id, user_id):
        return _error(404, "NotFound", headers)

    chat_history = rag_app.get_chat_history(session_id, limit=5) if request.get("sessionId") else []
    should_clarify, questions = rag_app.needs_clarify(
        request["query"], request.get("filters"), chat_history
    )
    if should_clarify:
        content = rag_app.build_clarify_content(questions)
        title = rag_app._fallback_session_title(request["query"]) if not chat_history else None
        user_message_id = rag_app.save_message_to_dynamodb(
            session_id=session_id, user_id=user_id, role="user",
            content=request["query"], session_title=title, query_filters=request.get("filters", {}),
        )
        ai_message_id = rag_app.save_message_to_dynamodb(
            session_id=session_id, user_id=user_id, role="assistant",
            content=content, response_type="clarify", clarify_questions=questions,
            query_filters=request.get("filters", {}),
        )
        return _response(200, {
            "sessionId": session_id, "userMessageId": user_message_id,
            "aiMessageId": ai_message_id, "responseType": "clarify",
            "clarifyQuestions": questions, "content": content,
        }, headers)

    job_id = str(uuid.uuid4())
    user_message_id = rag_app.generate_message_id()
    now = datetime.now(timezone.utc)
    reservation = {
        "table_name": jobs_table.name,
        "user_id": user_id,
        "client_request_id": client_request_id,
        "job_id": job_id,
        "session_id": session_id,
        "user_message_id": user_message_id,
        "filters": request.get("filters", {}),
        "now": now,
    }
    try:
        research_job_store.reserve_research_job(dynamodb_client, **reservation)
    except ClientError as error:
        _log_reservation_failure(error)
        reasons = error.response.get("CancellationReasons") or []
        reason_codes = [item.get("Code") for item in reasons]
        if len(reason_codes) > 3 and reason_codes[3] == "ConditionalCheckFailed":
            duplicate = _get_request_record(jobs_table, user_id, client_request_id)
            if duplicate:
                return _accepted_existing_job(jobs_table, duplicate["jobId"], user_id, headers)
        quota = get_daily_quota(jobs_table, user_id, now)
        if reason_codes and reason_codes[0] == "ConditionalCheckFailed":
            return _error(409, "ResearchAlreadyRunning", headers)
        if len(reason_codes) > 1 and reason_codes[1] == "ConditionalCheckFailed":
            return _error(429, "DailyLimitExceeded", headers, quota=quota)
        if len(reason_codes) > 2 and reason_codes[2] == "ConditionalCheckFailed":
            return _error(429, "DailyAttemptLimitExceeded", headers)
        classified = classify_reservation_conflict(
            jobs_table, user_id, client_request_id, now, headers,
        )
        if classified is not None:
            return classified
        return _error(503, "ResearchUnavailable", headers)

    chatlogs = boto3.resource("dynamodb", region_name=REGION).Table(
        os.environ["CHATLOGS_TABLE"]
    )
    now_epoch = int(now.timestamp())
    message = {
        "sessionId": session_id,
        "messageId": user_message_id,
        "userId": user_id,
        "role": "user",
        "ragMode": "normal",
        "content": request["query"],
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "ttl": now_epoch + 60 * 24 * 60 * 60,
        "researchJobId": job_id,
        "queryFilters": request.get("filters", {}),
    }
    if not chat_history:
        message["sessionTitle"] = rag_app._fallback_session_title(request["query"])
    message.update(rag_app.chatlog_metric_keys.metric_day_keys(now, user_message_id))

    question_saved = False
    try:
        chatlogs.put_item(
            Item=message,
            ConditionExpression="attribute_not_exists(sessionId) AND attribute_not_exists(messageId)",
        )
        question_saved = True
        boto3.client("lambda", region_name=REGION).invoke(
            FunctionName=os.environ["RESEARCH_WORKER_FUNCTION"],
            InvocationType="Event",
            Payload=json.dumps({"jobId": job_id}).encode("utf-8"),
        )
    except Exception as error:
        try:
            research_job_store.fail_queued_research_job(
                dynamodb_client, table_name=jobs_table.name, user_id=user_id,
                job_id=job_id, now=datetime.now(timezone.utc),
                error_code="DispatchFailed", quota_day=research_job_store.day_key(now),
            )
        except ClientError as cleanup_error:
            print(f"[research] reservation_cleanup_failed error_type={type(cleanup_error).__name__}")
        print(f"[research] dispatch_failed error_type={type(error).__name__}")
        if question_saved:
            # 再送で同じ質問が重複しないよう、保存済みの質問行を論理削除する。
            # ChatLogs の削除は deleted=True の更新が流儀（実行ロールも DeleteItem を持たない）。
            try:
                chatlogs.update_item(
                    Key={"sessionId": session_id, "messageId": user_message_id},
                    UpdateExpression="SET #del = :true",
                    ConditionExpression="attribute_exists(messageId)",
                    ExpressionAttributeNames={"#del": "deleted"},
                    ExpressionAttributeValues={":true": True},
                )
            except Exception as cleanup_error:
                print(f"[research] question_cleanup_failed error_type={type(cleanup_error).__name__}")
        return _error(503, "ResearchUnavailable", headers)

    quota = get_daily_quota(jobs_table, user_id, now)
    return _response(202, {
        "jobId": job_id, "sessionId": session_id,
        "userMessageId": user_message_id, "status": "queued", "quota": quota,
        "pollAfterMs": 5000,
    }, headers)


def _dispatch_authenticated_request(event, headers, user_id, table_name):
    table = boto3.resource("dynamodb", region_name=REGION).Table(table_name)
    dynamodb_client = boto3.client("dynamodb", region_name=REGION)
    method = event.get("httpMethod") or (event.get("requestContext") or {}).get("http", {}).get("method")
    path = _path(event)

    if method == "POST" and path.endswith("/rag/research"):
        return _handle_post(event, headers, user_id, table, dynamodb_client)
    if method == "GET" and path.endswith("/rag/research/quota"):
        return _response(200, get_daily_quota(table, user_id, datetime.now(JST)), headers)
    if method == "GET" and path.endswith("/rag/research"):
        params = event.get("queryStringParameters") or {}
        session_id = params.get("sessionId")
        if not session_id:
            return _error(400, "ValidationError", headers)
        rag_app = _load_rag_app()
        if not rag_app.owns_session(session_id, user_id):
            return _error(404, "NotFound", headers)
        result = table.query(
            IndexName="userId-createdAt-index",
            KeyConditionExpression="userId = :user",
            ExpressionAttributeValues={":user": user_id},
            ScanIndexForward=False,
            Limit=20,
        )
        jobs = [
            item for item in result.get("Items", [])
            if item.get("sessionId") == session_id
            and item.get("status") in {"queued", "running"}
        ]
        if not jobs:
            return _response(200, {"job": None}, headers)
        job = max(jobs, key=lambda item: item.get("createdAt", ""))
        response = _job_response(table, job["jobId"], headers, user_id)
        if response["statusCode"] == 200:
            return _response(200, {"job": json.loads(response["body"])}, headers)
        return response
    if method == "GET" and path.endswith("/rag/research/{jobId}"):
        job_id = ((event.get("pathParameters") or {}).get("jobId") or "")
        if not job_id:
            return _error(400, "ValidationError", headers)
        return _job_response(table, job_id, headers, user_id)
    return _error(404, "NotFound", headers)


def lambda_handler(event, context):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }
    method = event.get("httpMethod") or (event.get("requestContext") or {}).get("http", {}).get("method")
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    mode = os.environ.get("RESEARCH_MODE_ENABLED", "off").lower()
    environment = os.environ.get("ENVIRONMENT", "dev").lower()
    if mode not in RESEARCH_MODES or mode == "off" or environment != "dev":
        return _error(404, "NotFound", headers)

    user_id = _get_caller_id(event)
    if not user_id:
        return _error(401, "Unauthorized", headers)

    table_name = os.environ.get("RESEARCH_JOBS_TABLE")
    if not table_name:
        return _error(500, "InternalServerError", headers)
    try:
        return _dispatch_authenticated_request(event, headers, user_id, table_name)
    except Exception as error:
        print(f"[research] request_failed error_type={type(error).__name__}")
        return _error(500, "InternalServerError", headers)