"""POST /rag/senpai/synthesis: combine the saved technical and law answers of one turn.

Development-only, admin-only prototype. The server reads the answers from the
caller's own saved ChatLogs rows; answer text from the client is never accepted.
"""
import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError, ReadTimeoutError

import synthesis_model
import synthesis_prompt
import synthesis_store
from synthesis_prompt import KNOWHOW_MAX_CARDS, MAX_INPUT_CHARS  # noqa: F401  (re-exported for tests)
from synthesis_store import HISTORY_MAX_PAGES  # noqa: F401

AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
CHATLOGS_TABLE = os.environ.get("CHATLOGS_TABLE", "")
ALLOWED_BODY_KEYS = frozenset({"senpaiConversationId", "senpaiTurnId"})

chatlogs_table = boto3.resource("dynamodb", region_name=AWS_REGION).Table(CHATLOGS_TABLE or "unset")
bedrock_runtime = boto3.client(
    "bedrock-runtime", region_name=AWS_REGION, config=synthesis_model.client_config()
)

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}


def _log(stage: str, status: str, error: Exception = None) -> None:
    # SECURITY: only stage and error class. Never log answers, identifiers or tokens.
    record = {"event": "senpai_synthesis", "stage": stage, "status": status}
    if error is not None:
        record["errorClass"] = type(error).__name__
    print(json.dumps(record, separators=(",", ":")))


def _respond(status: int, payload: dict) -> dict:
    return {
        "statusCode": status,
        "headers": HEADERS,
        "body": json.dumps(payload, ensure_ascii=False, default=str),
    }


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
        and os.environ.get("SENPAI_SYNTHESIS_ENABLED") == "true"
        and _is_admin(claims)
    )


def _canonical_uuid(value) -> bool:
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def _parse_ids(event: dict):
    raw = event.get("body")
    try:
        body = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return None
    if not isinstance(body, dict) or set(body) != ALLOWED_BODY_KEYS:
        return None
    ids = (body["senpaiConversationId"], body["senpaiTurnId"])
    return ids if all(_canonical_uuid(value) for value in ids) else None


def _public_payload(row: dict) -> dict:
    inputs = row.get("synthesisInputs") or {}
    return {
        "senpaiConversationId": row["senpaiConversationId"],
        "senpaiTurnId": row["senpaiTurnId"],
        "messageId": row["messageId"],
        "content": row["content"],
        "inputs": {
            "normal": bool(inputs.get("normal")),
            "law": bool(inputs.get("law")),
            "knowhowCount": int(inputs.get("knowhowCount") or 0),
        },
        "timestamp": row["timestamp"],
    }


def _generate(normal_row, law_row) -> tuple:
    messages, inputs = synthesis_prompt.build_messages(normal_row, law_row)
    text = synthesis_model.generate(
        bedrock_runtime,
        os.environ.get("BEDROCK_MODEL_ID", ""),
        synthesis_prompt.SYSTEM_PROMPT,
        messages,
        synthesis_model.max_tokens_from_env(),
    )
    return text.strip(), inputs


def _save_or_load(user_id: str, conversation_id: str, turn_id: str, content: str, inputs: dict) -> dict:
    item = synthesis_store.build_item(user_id, conversation_id, turn_id, content, inputs)
    if synthesis_store.put_if_absent(chatlogs_table, item):
        return _respond(200, _public_payload(item))
    existing = synthesis_store.get_row(chatlogs_table, turn_id)
    if not synthesis_store.is_visible_saved_row(existing, user_id, conversation_id, turn_id):
        # SECURITY: another owner's row, or a deleted/expired row, is never shown again.
        _log("save", "conflict")
        return _error(409, "SynthesisConflict", "この相談のまとめは保存されていないため表示できません")
    return _respond(200, _public_payload(existing))


def _handle(event: dict, claims: dict) -> dict:
    user_id = claims.get("sub") or ""
    if not user_id:
        return _error(401, "Unauthorized", "ログインが必要です")
    ids = _parse_ids(event)
    if ids is None:
        return _error(400, "ValidationError", "相談の識別情報を確認してください")
    conversation_id, turn_id = ids

    try:
        rows = synthesis_store.query_turn_rows(chatlogs_table, user_id, conversation_id, turn_id)
    except ClientError as error:
        _log("read_turn", "error", error)
        return _error(500, "InternalError", "相談の読み込みに失敗しました")
    if not rows:
        return _error(404, "TurnNotFound", "対象の相談が見つかりません")

    saved = synthesis_store.find_saved_synthesis(rows, turn_id)
    if saved is not None:
        _log("reuse", "ok")
        return _respond(200, _public_payload(saved))

    normal_row, law_row = synthesis_store.select_lane_answers(rows)
    if normal_row is None and law_row is None:
        return _error(422, "NothingToSynthesize", "まとめられる回答がありません")

    try:
        content, inputs = _generate(normal_row, law_row)
    except ReadTimeoutError as error:
        _log("generate", "timeout", error)
        return _error(504, "SynthesisTimeout", "まとめの作成が時間内に完了しませんでした。再度お試しください")
    except Exception as error:  # noqa: BLE001 - unified error format, class only in logs
        _log("generate", "error", error)
        return _error(502, "SynthesisFailed", "まとめを作成できませんでした。時間をおいて再度お試しください")
    if not content:
        _log("generate", "empty")
        return _error(502, "SynthesisFailed", "まとめを作成できませんでした。時間をおいて再度お試しください")

    try:
        response = _save_or_load(user_id, conversation_id, turn_id, content, inputs)
    except ClientError as error:
        _log("save", "error", error)
        return _error(500, "InternalError", "まとめの保存に失敗しました")
    _log("save", "ok")
    return response


def lambda_handler(event, context):
    method = event.get("httpMethod") or (event.get("requestContext") or {}).get("http", {}).get("method")
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": HEADERS, "body": ""}
    claims = _claims(event)
    if not _feature_available(claims):
        return _error(403, "FeatureUnavailable", "先輩チャットは開発環境の管理者のみ利用できます")
    if method != "POST":
        return _error(405, "MethodNotAllowed", "許可されていないメソッドです")
    try:
        return _handle(event, claims)
    except Exception as error:  # noqa: BLE001 - never leak a stack trace to the client
        _log("handler", "error", error)
        return _error(500, "InternalError", "処理中にエラーが発生しました")
