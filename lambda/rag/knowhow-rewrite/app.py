"""POST /rag/knowhow/rewrite-proposal: propose a rewrite of knowhow-card sections from confirmed evidence.

Development-only, admin-only, off by default. Nothing is stored: the proposal goes back to the caller,
who reviews the difference and decides. The model output is validated on the server before it is returned.
"""
import json
import os
import time

import boto3
from botocore.exceptions import ClientError, ReadTimeoutError

import rewrite_input
import rewrite_model
import rewrite_prompt
import rewrite_validate
from rewrite_errors import ApiError

AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
THROTTLING_CODES = frozenset({"ThrottlingException", "TooManyRequestsException"})
TIMEOUT_CODES = frozenset({"ModelTimeoutException"})

bedrock_runtime = boto3.client(
    "bedrock-runtime", region_name=AWS_REGION, config=rewrite_model.client_config()
)

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}


def _log(stage: str, status: str, error: Exception = None, **counts) -> None:
    # SECURITY: only fixed fields, counts and the error class. Never log bodies, questions, answers,
    # identifiers (knowledgeId, sub, tokens) or exception messages.
    record = {"event": "knowhow_rewrite", "stage": stage, "status": status}
    if error is not None:
        record["errorClass"] = type(error).__name__
    record.update(counts)
    print(json.dumps(record, separators=(",", ":")))


def _respond(status: int, payload: dict) -> dict:
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps(payload, ensure_ascii=False)}


def _error(status: int, code: str, message: str) -> dict:
    return _respond(status, {"error": code, "message": message})


def _claims(event: dict) -> dict:
    return ((event.get("requestContext") or {}).get("authorizer") or {}).get("claims") or {}


def _is_admin(claims: dict) -> bool:
    groups = claims.get("cognito:groups", "")
    names = groups if isinstance(groups, list) else [g.strip() for g in str(groups).split(",") if g.strip()]
    return (os.environ.get("ADMIN_GROUP_NAME", "admin").strip() or "admin") in names


def _feature_available(claims: dict) -> bool:
    return (
        os.environ.get("ENVIRONMENT") == "dev"
        and os.environ.get("KNOWHOW_REWRITE_ENABLED") == "true"
        and _is_admin(claims)
    )


def _model_error(error: Exception, counts: dict) -> dict:
    code = error.response.get("Error", {}).get("Code") if isinstance(error, ClientError) else None
    if code in THROTTLING_CODES:
        _log("generate", "throttled", error, **counts)
        return _error(429, "RewriteThrottled", "混み合っています。少し待ってから再度お試しください")
    if isinstance(error, ReadTimeoutError) or code in TIMEOUT_CODES:
        _log("generate", "timeout", error, **counts)
        return _error(504, "RewriteTimeout", "書き換え案の作成が時間内に完了しませんでした。再度お試しください")
    _log("generate", "error", error, **counts)
    return _error(500, "InternalError", "処理中にエラーが発生しました")


def _result_counts(result: dict) -> dict:
    statuses = [section["status"] for section in result["sections"]]
    return {
        "changedCount": statuses.count("changed"),
        "rejectedCount": statuses.count("rejected"),
        "conflictCount": len(result["conflicts"]),
    }


def _handle(event: dict, claims: dict) -> dict:
    started = time.monotonic()
    if not claims.get("sub"):
        return _error(401, "Unauthorized", "ログインが必要です")
    try:
        request = rewrite_input.parse_request(event)
    except ApiError as error:
        _log("input", "rejected", error)
        return _error(error.status, error.code, error.message)
    if request["evidence"][0]["lane"] == rewrite_input.FIELD_LANE and os.environ.get(
        "KNOWHOW_FIELD_MATERIAL_ENABLED"
    ) != "true":
        return _error(403, "FeatureUnavailable", "この資料レーンは利用できません")
    counts = {"targetCount": len(request["targets"]), "evidenceCount": len(request["evidence"])}
    model_id = os.environ.get("BEDROCK_MODEL_ID", "")
    try:
        text, usage, stop_reason = rewrite_model.generate(
            bedrock_runtime, model_id, rewrite_prompt.system_prompt_for(request),
            rewrite_prompt.build_messages(request), rewrite_model.max_tokens_from_env(),
        )
    except Exception as error:  # noqa: BLE001 - mapped to the unified format, class only in logs
        return _model_error(error, counts)
    counts.update(
        modelId=model_id, inputTokens=usage["inputTokens"], outputTokens=usage["outputTokens"],
        durationMs=int((time.monotonic() - started) * 1000),
    )
    try:
        result = rewrite_validate.build_response(request, text, stop_reason)
    except ApiError as error:
        _log("validate", "rejected", error, **counts)
        return _error(error.status, error.code, error.message)
    _log("validate", "ok", **counts, **_result_counts(result))
    return _respond(200, result)


def lambda_handler(event, context):
    method = event.get("httpMethod") or (event.get("requestContext") or {}).get("http", {}).get("method")
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": HEADERS, "body": ""}
    claims = _claims(event)
    if not _feature_available(claims):
        return _error(403, "FeatureUnavailable", "この機能は開発環境の管理者のみ利用できます")
    if method != "POST":
        return _error(405, "MethodNotAllowed", "許可されていないメソッドです")
    try:
        return _handle(event, claims)
    except Exception as error:  # noqa: BLE001 - never leak a stack trace to the client
        _log("handler", "error", error)
        return _error(500, "InternalError", "処理中にエラーが発生しました")
