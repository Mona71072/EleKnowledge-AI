"""/rag/senpai/field-reports: save and list the caller's 「結果を残す」 field reports.

Development-only, admin-only. A report is an unverified observation candidate, never
verified knowledge. The server checks the turn and the referenced cards against the
caller's own saved ChatLogs rows; the conversation itself is never copied.
"""
import json
import os

import boto3
from botocore.exceptions import ClientError

import field_report_store
from field_report_input import InputError, canonical_uuid, parse_body

AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
CHATLOGS_TABLE = os.environ.get("CHATLOGS_TABLE", "")
FIELD_REPORTS_TABLE = os.environ.get("FIELD_REPORTS_TABLE", "")

_dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
chatlogs_table = _dynamodb.Table(CHATLOGS_TABLE or "unset")
reports_table = _dynamodb.Table(FIELD_REPORTS_TABLE or "unset")

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}
PUBLIC_FIELDS = (
    "reportId", "senpaiConversationId", "senpaiTurnId", "createdAt", "finding", "condition",
    "modelType", "turnModelType", "reviewState",
)


def _log(stage: str, status: str, error: Exception = None) -> None:
    # SECURITY: only stage and error class. Never log report text, identifiers or tokens.
    record = {"event": "senpai_field_report", "stage": stage, "status": status}
    if error is not None:
        record["errorClass"] = type(error).__name__
    print(json.dumps(record, separators=(",", ":")))


def _respond(status: int, payload) -> dict:
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps(payload, ensure_ascii=False, default=str)}


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
        and os.environ.get("SENPAI_FIELD_REPORTS_ENABLED") == "true"
        and _is_admin(claims)
    )


def _public(item: dict) -> dict:
    payload = {key: item[key] for key in PUBLIC_FIELDS if key in item}
    payload["cardReactions"] = [
        {
            "knowledgeId": str(r.get("knowledgeId")),
            "cardVersion": int(r.get("cardVersion") or 0),
            "reaction": r.get("reaction"),
        }
        for r in item.get("cardReactions") or []
    ]
    return payload


def _verified_reactions(fields: dict, rows: list):
    cards = field_report_store.referenced_cards(rows)
    reactions = []
    for entry in fields["cardReactions"]:
        card = cards.get((entry["knowledgeId"], entry["cardVersion"]))
        if card is None:
            return None
        reactions.append({**entry, **card})
    return reactions


def _create(event: dict, user_id: str) -> dict:
    raw = event.get("body")
    try:
        fields = parse_body(json.loads(raw) if isinstance(raw, str) else raw)
    except (InputError, json.JSONDecodeError, TypeError):
        return _error(400, "ValidationError", "入力内容を確認してください")

    try:
        rows = field_report_store.query_turn_rows(
            chatlogs_table, user_id, fields["senpaiConversationId"], fields["senpaiTurnId"]
        )
    except ClientError as error:
        _log("read_turn", "error", error)
        return _error(500, "InternalError", "相談の読み込みに失敗しました")
    if not rows:
        return _error(404, "TurnNotFound", "対象の相談が見つかりません。保存期間を過ぎた可能性があります")

    reactions = _verified_reactions(fields, rows)
    if reactions is None:
        _log("verify_cards", "unknown_card")
        return _error(400, "UnknownCard", "この相談で参照していないノウハウは選べません")

    item = field_report_store.build_item(user_id, fields, reactions, field_report_store.turn_model_type(rows))
    try:
        if field_report_store.put_if_absent(reports_table, item):
            _log("save", "ok")
            return _respond(200, _public(item))
        existing = field_report_store.get_report(reports_table, fields["senpaiTurnId"])
    except ClientError as error:
        _log("save", "error", error)
        return _error(500, "InternalError", "結果の保存に失敗しました")
    if existing is None or existing.get("userId") != user_id:
        # SECURITY: the deterministic key collided with another owner's row; reveal nothing.
        _log("save", "conflict")
        return _error(409, "ReportConflict", "この相談の結果を保存できませんでした")
    _log("save", "reuse")
    return _respond(200, _public(existing))


def _list(event: dict, user_id: str) -> dict:
    conversation_id = (event.get("queryStringParameters") or {}).get("senpaiConversationId")
    if not canonical_uuid(conversation_id):
        return _error(400, "ValidationError", "相談の識別情報を確認してください")
    try:
        items = field_report_store.list_conversation_reports(reports_table, user_id, conversation_id)
    except ClientError as error:
        _log("list", "error", error)
        return _error(500, "InternalError", "結果の読み込みに失敗しました")
    return _respond(200, {"reports": [_public(item) for item in items]})


def lambda_handler(event, context):
    method = event.get("httpMethod") or (event.get("requestContext") or {}).get("http", {}).get("method")
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": HEADERS, "body": ""}
    claims = _claims(event)
    if not _feature_available(claims):
        return _error(403, "FeatureUnavailable", "先輩チャットは開発環境の管理者のみ利用できます")
    user_id = claims.get("sub") or ""
    if not user_id:
        return _error(401, "Unauthorized", "ログインが必要です")
    try:
        if method == "POST":
            return _create(event, user_id)
        if method == "GET":
            return _list(event, user_id)
        return _error(405, "MethodNotAllowed", "許可されていないメソッドです")
    except Exception as error:  # noqa: BLE001 - never leak a stack trace to the client
        _log("handler", "error", error)
        return _error(500, "InternalError", "処理中にエラーが発生しました")
