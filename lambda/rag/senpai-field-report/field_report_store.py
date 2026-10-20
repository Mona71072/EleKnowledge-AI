"""DynamoDB access for field reports: bounded ChatLogs reads and idempotent report writes."""
import os
import time
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from field_report_vocab import INITIAL_REVIEW_STATE

HISTORY_PAGE_SIZE = 200
HISTORY_MAX_PAGES = 10
REPORT_PAGE_SIZE = 100
REPORT_MAX_PAGES = 5
DEFAULT_TTL_DAYS = 180
MAX_TTL_DAYS = 3650
# Same product keys the model filter classifies (knowhow_retrieval.MODEL_CLASSIFY_KEYS).
PRODUCT_SCOPE_KEYS = ("product_lines", "model_abbreviations", "lists_model_label", "observed_on")


def ttl_days_from_env() -> int:
    try:
        days = int(os.environ.get("FIELD_REPORT_TTL_DAYS", ""))
    except ValueError:
        return DEFAULT_TTL_DAYS
    return days if 1 <= days <= MAX_TTL_DAYS else DEFAULT_TTL_DAYS


def report_id(turn_id: str) -> str:
    return f"field-report-{turn_id}"


def _live(row: dict, now: int) -> bool:
    if row.get("deleted") is True:
        return False
    ttl = row.get("ttl")
    if ttl is None:
        return True
    try:
        return int(ttl) > now
    except (TypeError, ValueError):
        return False


def query_turn_rows(table, user_id: str, conversation_id: str, turn_id: str) -> list:
    """Read this user's live ChatLogs rows of one Senpai turn through the user GSI (never Scan)."""
    now = int(time.time())
    rows = []
    start_key = None
    for _page in range(HISTORY_MAX_PAGES):
        query = {
            "IndexName": "userId-timestamp-index",
            "KeyConditionExpression": "userId = :uid",
            "FilterExpression": "senpaiConversationId = :cid AND senpaiTurnId = :tid",
            "ExpressionAttributeValues": {":uid": user_id, ":cid": conversation_id, ":tid": turn_id},
            "ScanIndexForward": False,
            "Limit": HISTORY_PAGE_SIZE,
        }
        if start_key:
            query["ExclusiveStartKey"] = start_key
        response = table.query(**query)
        rows.extend(
            row for row in response.get("Items") or []
            if row.get("userId") == user_id
            and row.get("senpaiConversationId") == conversation_id
            and row.get("senpaiTurnId") == turn_id
            and _live(row, now)
        )
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            break
    return rows


def _values(value) -> list:
    items = value if isinstance(value, list) else [value]
    return [str(item) for item in items if isinstance(item, str) and item.strip()]


def _product_scope(scope: dict) -> list:
    seen = []
    for key in PRODUCT_SCOPE_KEYS:
        for value in _values(scope.get(key)):
            if value not in seen:
                seen.append(value)
    return seen


def referenced_cards(rows: list) -> dict:
    """Map (knowledgeId, cardVersion) to the card scope saved with this turn's technical answers."""
    cards = {}
    for row in rows:
        if row.get("role") != "assistant" or (row.get("ragMode") or "normal") != "normal":
            continue
        knowhow = row.get("knowhow")
        matches = knowhow.get("matches") if isinstance(knowhow, dict) else None
        for match in matches or []:
            if not isinstance(match, dict):
                continue
            try:
                key = (str(match["knowledgeId"]), int(match["cardVersion"]))
            except (KeyError, TypeError, ValueError):
                continue
            scope = match.get("modelScope") if isinstance(match.get("modelScope"), dict) else {}
            cards[key] = {
                "cardScopeStatus": "verified" if scope.get("scope_status") == "verified" else "unverified",
                "cardProductScope": _product_scope(scope),
            }
    return cards


def turn_model_type(rows: list):
    for row in rows:
        filters = row.get("queryFilters")
        if row.get("role") == "assistant" and isinstance(filters, dict) and isinstance(filters.get("modelType"), str):
            return filters["modelType"]
    return None


def build_item(user_id: str, fields: dict, reactions: list, turn_model) -> dict:
    created = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    item = {
        "reportId": report_id(fields["senpaiTurnId"]),
        "userId": user_id,
        "senpaiConversationId": fields["senpaiConversationId"],
        "senpaiTurnId": fields["senpaiTurnId"],
        "createdAt": created,
        "finding": fields["finding"],
        "cardReactions": reactions,
        "reviewState": INITIAL_REVIEW_STATE,
        "ttl": int(time.time()) + ttl_days_from_env() * 86400,
    }
    if fields["condition"]:
        item["condition"] = fields["condition"]
    if fields["modelType"]:
        item["modelType"] = fields["modelType"]
    if turn_model:
        item["turnModelType"] = turn_model
    return item


def put_if_absent(table, item: dict) -> bool:
    """Conditional put. Returns False when the deterministic report already exists."""
    try:
        table.put_item(Item=item, ConditionExpression="attribute_not_exists(reportId)")
        return True
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return False
        raise


def get_report(table, turn_id: str):
    return table.get_item(Key={"reportId": report_id(turn_id)}, ConsistentRead=True).get("Item")


def list_conversation_reports(table, user_id: str, conversation_id: str) -> list:
    """The caller's live reports of one conversation, newest first (user GSI, never Scan)."""
    now = int(time.time())
    reports = []
    start_key = None
    for _page in range(REPORT_MAX_PAGES):
        query = {
            "IndexName": "userId-createdAt-index",
            "KeyConditionExpression": Key("userId").eq(user_id),
            "ScanIndexForward": False,
            "Limit": REPORT_PAGE_SIZE,
        }
        if start_key:
            query["ExclusiveStartKey"] = start_key
        response = table.query(**query)
        reports.extend(
            item for item in response.get("Items") or []
            if item.get("userId") == user_id
            and item.get("senpaiConversationId") == conversation_id
            and _live(item, now)
        )
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            break
    return reports
