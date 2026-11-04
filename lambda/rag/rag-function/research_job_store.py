"""Atomic persistence operations for long-running research jobs."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from boto3.dynamodb.types import TypeSerializer


SUCCESS_QUOTA_LIMIT = 10
DAILY_ATTEMPT_LIMIT = 20
ACTIVE_LOCK_SECONDS = 360
JOB_TTL_SECONDS = 60 * 24 * 60 * 60
REQUEST_TTL_SECONDS = 24 * 60 * 60
COUNTER_TTL_SECONDS = 3 * 24 * 60 * 60
ACTIVE_TTL_SECONDS = 24 * 60 * 60
DISPATCH_DEADLINE_SECONDS = 120

_serializer = TypeSerializer()
_JST = ZoneInfo("Asia/Tokyo")


def day_key(now: datetime) -> str:
    return now.astimezone(timezone.utc).astimezone(_JST).strftime("%Y-%m-%d")


def _serialize_item(item: dict[str, Any]) -> dict[str, Any]:
    return {key: _serializer.serialize(_dynamodb_value(value)) for key, value in item.items()}


def _dynamodb_value(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: _dynamodb_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_dynamodb_value(item) for item in value]
    return value


def build_reservation_transaction(
    *,
    table_name: str,
    user_id: str,
    client_request_id: str,
    job_id: str,
    session_id: str,
    user_message_id: str,
    filters: dict[str, Any],
    now: datetime,
) -> list[dict[str, Any]]:
    """Reserve quota, concurrency lock, idempotency key and job atomically."""
    now_utc = now.astimezone(timezone.utc)
    now_epoch = int(now_utc.timestamp())
    now_iso = now_utc.isoformat().replace("+00:00", "Z")
    date_key = day_key(now_utc)

    return [
        {
            "Put": {
                "TableName": table_name,
                "Item": _serialize_item({
                    "pk": f"ACTIVE#{user_id}",
                    "jobId": job_id,
                    "expiresAt": now_epoch + ACTIVE_LOCK_SECONDS,
                    "ttl": now_epoch + ACTIVE_TTL_SECONDS,
                }),
                "ConditionExpression": "attribute_not_exists(pk) OR expiresAt <= :now",
                "ExpressionAttributeValues": {":now": _serializer.serialize(now_epoch)},
            }
        },
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"QUOTA#{user_id}#{date_key}"}),
                "UpdateExpression": "SET #ttl = :ttl ADD #count :one",
                "ConditionExpression": "attribute_not_exists(#count) OR #count < :limit",
                "ExpressionAttributeNames": {"#ttl": "ttl", "#count": "count"},
                "ExpressionAttributeValues": {
                    ":ttl": _serializer.serialize(now_epoch + COUNTER_TTL_SECONDS),
                    ":one": _serializer.serialize(1),
                    ":limit": _serializer.serialize(SUCCESS_QUOTA_LIMIT),
                },
            }
        },
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"ATTEMPT#{user_id}#{date_key}"}),
                "UpdateExpression": "SET #ttl = :ttl ADD #count :one",
                "ConditionExpression": "attribute_not_exists(#count) OR #count < :limit",
                "ExpressionAttributeNames": {"#ttl": "ttl", "#count": "count"},
                "ExpressionAttributeValues": {
                    ":ttl": _serializer.serialize(now_epoch + COUNTER_TTL_SECONDS),
                    ":one": _serializer.serialize(1),
                    ":limit": _serializer.serialize(DAILY_ATTEMPT_LIMIT),
                },
            }
        },
        {
            "Put": {
                "TableName": table_name,
                "Item": _serialize_item({
                    "pk": f"REQ#{user_id}#{client_request_id}",
                    "jobId": job_id,
                    "ttl": now_epoch + REQUEST_TTL_SECONDS,
                }),
                "ConditionExpression": "attribute_not_exists(pk)",
            }
        },
        {
            "Put": {
                "TableName": table_name,
                "Item": _serialize_item({
                    "pk": f"JOB#{job_id}",
                    "jobId": job_id,
                    "userId": user_id,
                    "createdAt": now_iso,
                    "sessionId": session_id,
                    "userMessageId": user_message_id,
                    "clientRequestId": client_request_id,
                    "quotaDay": date_key,
                    "filters": filters,
                    "status": "queued",
                    "stage": "queued",
                    "progress": {
                        "step": 0,
                        "totalSteps": 6,
                        "searchesDone": 0,
                        "searchesTotal": 0,
                    },
                    "createdAt": now_iso,
                    "updatedAt": now_iso,
                    "dispatchDeadline": now_epoch + DISPATCH_DEADLINE_SECONDS,
                    "refunded": False,
                    "ttl": now_epoch + JOB_TTL_SECONDS,
                }),
                "ConditionExpression": "attribute_not_exists(pk)",
            }
        },
    ]


def build_queued_failure_transaction(
    *, table_name: str, user_id: str, job_id: str, now: datetime,
    error_code: str, quota_day: str = None
) -> list[dict[str, Any]]:
    """Fail a queued job, refund its daily quota once, and release its lock."""
    now_epoch = int(now.timestamp())
    date_key = quota_day or day_key(now)
    return [
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"JOB#{job_id}"}),
                "UpdateExpression": "SET #status = :failed, #stage = :failed, #error = :error, #refunded = :true, #updated = :updated",
                "ConditionExpression": "#status = :queued AND #refunded = :false",
                "ExpressionAttributeNames": {
                    "#status": "status", "#stage": "stage", "#error": "errorCode",
                    "#refunded": "refunded", "#updated": "updatedAt",
                },
                "ExpressionAttributeValues": _serialize_item({
                    ":failed": "failed", ":error": error_code, ":true": True,
                    ":updated": now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                    ":queued": "queued", ":false": False,
                }),
            }
        },
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"QUOTA#{user_id}#{date_key}"}),
                "UpdateExpression": "ADD #count :minus",
                "ConditionExpression": "#count > :zero",
                "ExpressionAttributeNames": {"#count": "count"},
                "ExpressionAttributeValues": {
                    ":minus": _serializer.serialize(-1),
                    ":zero": _serializer.serialize(0),
                },
            }
        },
        {
            "Delete": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"ACTIVE#{user_id}"}),
                "ConditionExpression": "jobId = :job",
                "ExpressionAttributeValues": {":job": _serializer.serialize(job_id)},
            }
        },
    ]


def build_claim_transaction(
    *, table_name: str, user_id: str, job_id: str, lease_token: str,
    now: datetime, running_seconds: int = 180
) -> list[dict[str, Any]]:
    now_utc = now.astimezone(timezone.utc)
    now_epoch = int(now_utc.timestamp())
    now_iso = now_utc.isoformat().replace("+00:00", "Z")
    return [
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"JOB#{job_id}"}),
                "UpdateExpression": "SET #status = :running, #stage = :planning, #lease = :lease, #runningUntil = :until, #updated = :updated",
                "ConditionExpression": "#status = :queued AND dispatchDeadline >= :now",
                "ExpressionAttributeNames": {
                    "#status": "status", "#stage": "stage", "#lease": "leaseToken",
                    "#runningUntil": "runningUntil", "#updated": "updatedAt",
                },
                "ExpressionAttributeValues": _serialize_item({
                    ":running": "running", ":planning": "planning", ":lease": lease_token,
                    ":until": now_epoch + running_seconds, ":updated": now_iso,
                    ":queued": "queued", ":now": now_epoch,
                }),
            }
        },
        {
            "ConditionCheck": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"ACTIVE#{user_id}"}),
                "ConditionExpression": "jobId = :job",
                "ExpressionAttributeValues": {":job": _serializer.serialize(job_id)},
            }
        },
    ]


def build_progress_update(
    *, table_name: str, job_id: str, lease_token: str, stage: str,
    progress: dict[str, Any], now: datetime, poll_after_ms: int = None
) -> dict[str, Any]:
    now_iso = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    names = {"#status": "status", "#lease": "leaseToken", "#stage": "stage", "#progress": "progress", "#updated": "updatedAt"}
    values = {
        ":running": _serializer.serialize("running"),
        ":lease": _serializer.serialize(lease_token),
        ":stage": _serializer.serialize(stage),
        ":progress": _serializer.serialize(progress),
        ":updated": _serializer.serialize(now_iso),
    }
    update = "SET #stage = :stage, #progress = :progress, #updated = :updated"
    if poll_after_ms is not None:
        names["#poll"] = "pollAfterMs"
        values[":poll"] = _serializer.serialize(poll_after_ms)
        update += ", #poll = :poll"
    return {
        "TableName": table_name,
        "Key": _serialize_item({"pk": f"JOB#{job_id}"}),
        "UpdateExpression": update,
        "ConditionExpression": "#status = :running AND #lease = :lease",
        "ExpressionAttributeNames": names,
        "ExpressionAttributeValues": values,
    }


def build_completion_transaction(
    *, table_name: str, chatlogs_table_name: str, user_id: str,
    job_id: str, lease_token: str, message: dict[str, Any],
    now: datetime, progress: dict[str, Any], research: dict[str, Any]
) -> list[dict[str, Any]]:
    now_iso = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return [
        {
            "Put": {
                "TableName": chatlogs_table_name,
                "Item": _serialize_item(message),
                "ConditionExpression": "attribute_not_exists(sessionId) AND attribute_not_exists(messageId)",
            }
        },
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"JOB#{job_id}"}),
                "UpdateExpression": "SET #status = :completed, #stage = :completed, #progress = :progress, #result = :result, #resultId = :resultId, #updated = :updated",
                "ConditionExpression": "#status = :running AND #lease = :lease",
                "ExpressionAttributeNames": {
                    "#status": "status", "#stage": "stage", "#progress": "progress",
                    "#result": "researchTrace", "#resultId": "resultMessageId", "#updated": "updatedAt",
                    "#lease": "leaseToken",
                },
                "ExpressionAttributeValues": _serialize_item({
                    ":completed": "completed", ":progress": progress,
                    ":result": {
                        "searchCount": research.get("searchCount", 0),
                        "evidenceCount": research.get("evidenceCount", 0),
                        "risk": research.get("risk", "medium"),
                        "evidence": research.get("evidence", []),
                    },
                    ":resultId": message["messageId"],
                    ":updated": now_iso, ":running": "running", ":lease": lease_token,
                }),
            }
        },
        {
            "Delete": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"ACTIVE#{user_id}"}),
                "ConditionExpression": "jobId = :job",
                "ExpressionAttributeValues": {":job": _serializer.serialize(job_id)},
            }
        },
    ]


def build_running_failure_transaction(
    *, table_name: str, user_id: str, job_id: str, lease_token: str,
    quota_day: str, now: datetime, error_code: str
) -> list[dict[str, Any]]:
    now_iso = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return [
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"JOB#{job_id}"}),
                "UpdateExpression": "SET #status = :failed, #stage = :failed, #error = :error, #refunded = :true, #updated = :updated",
                "ConditionExpression": "#status = :running AND #lease = :lease AND #refunded = :false",
                "ExpressionAttributeNames": {
                    "#status": "status", "#stage": "stage", "#error": "errorCode",
                    "#refunded": "refunded", "#updated": "updatedAt", "#lease": "leaseToken",
                },
                "ExpressionAttributeValues": _serialize_item({
                    ":failed": "failed", ":error": error_code, ":true": True,
                    ":updated": now_iso, ":running": "running", ":lease": lease_token,
                    ":false": False,
                }),
            }
        },
        {
            "Update": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"QUOTA#{user_id}#{quota_day}"}),
                "UpdateExpression": "ADD #count :minus",
                "ConditionExpression": "#count > :zero",
                "ExpressionAttributeNames": {"#count": "count"},
                "ExpressionAttributeValues": {
                    ":minus": _serializer.serialize(-1), ":zero": _serializer.serialize(0),
                },
            }
        },
        {
            "Delete": {
                "TableName": table_name,
                "Key": _serialize_item({"pk": f"ACTIVE#{user_id}"}),
                "ConditionExpression": "jobId = :job",
                "ExpressionAttributeValues": {":job": _serializer.serialize(job_id)},
            }
        },
    ]


def reserve_research_job(client, **reservation: Any) -> None:
    client.transact_write_items(
        TransactItems=build_reservation_transaction(**reservation)
    )


def fail_queued_research_job(client, **failure: Any) -> None:
    client.transact_write_items(
        TransactItems=build_queued_failure_transaction(**failure)
    )


def claim_research_job(client, **claim: Any) -> None:
    client.transact_write_items(TransactItems=build_claim_transaction(**claim))


def update_research_progress(client, **progress: Any) -> None:
    client.update_item(**build_progress_update(**progress))


def complete_research_job(client, **completion: Any) -> None:
    client.transact_write_items(
        TransactItems=build_completion_transaction(**completion)
    )


def fail_running_research_job(client, **failure: Any) -> None:
    client.transact_write_items(
        TransactItems=build_running_failure_transaction(**failure)
    )