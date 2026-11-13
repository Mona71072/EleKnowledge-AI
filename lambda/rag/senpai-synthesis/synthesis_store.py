"""ChatLogs access for the Senpai synthesis: bounded read and idempotent write."""
import time
from datetime import datetime, timezone

from botocore.exceptions import ClientError

HISTORY_PAGE_SIZE = 500
HISTORY_MAX_PAGES = 25
TTL_SECONDS = 60 * 24 * 60 * 60
SYNTHESIS_MODE = "senpai_synthesis"
UNUSABLE_RESPONSE_TYPES = frozenset({"not_found", "clarify"})


def synthesis_message_id(turn_id: str) -> str:
    return f"senpai-synthesis-{turn_id}"


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
    """Read this user's live rows of one Senpai turn through the user GSI (never Scan)."""
    now = int(time.time())
    rows = []
    start_key = None
    for _page in range(HISTORY_MAX_PAGES):
        query = {
            "IndexName": "userId-timestamp-index",
            "KeyConditionExpression": "userId = :uid",
            "FilterExpression": "senpaiConversationId = :cid AND senpaiTurnId = :tid",
            "ExpressionAttributeValues": {
                ":uid": user_id, ":cid": conversation_id, ":tid": turn_id,
            },
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


def find_saved_synthesis(rows: list, turn_id: str):
    wanted = synthesis_message_id(turn_id)
    for row in rows:
        if row.get("ragMode") == SYNTHESIS_MODE and row.get("messageId") == wanted:
            return row
    return None


def _usable_answer(row: dict) -> bool:
    content = row.get("content")
    return (
        row.get("role") == "assistant"
        and isinstance(content, str) and bool(content.strip())
        and row.get("responseType") not in UNUSABLE_RESPONSE_TYPES
    )


def select_lane_answers(rows: list) -> tuple:
    """Return (normal_row, law_row): the latest usable assistant row per lane, or None."""
    latest = {"normal": None, "law": None}
    for row in rows:
        mode = row.get("ragMode") or "normal"
        if mode not in latest or not _usable_answer(row):
            continue
        current = latest[mode]
        key = (row.get("timestamp") or "", row.get("messageId") or "")
        if current is None or key > (current.get("timestamp") or "", current.get("messageId") or ""):
            latest[mode] = row
    return latest["normal"], latest["law"]


def build_item(user_id: str, conversation_id: str, turn_id: str, content: str, inputs: dict) -> dict:
    message_id = synthesis_message_id(turn_id)
    # No metricDay keys on purpose: the synthesis must not enter answer metrics.
    return {
        "sessionId": message_id,
        "messageId": message_id,
        "userId": user_id,
        "role": "assistant",
        "ragMode": SYNTHESIS_MODE,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ttl": int(time.time()) + TTL_SECONDS,
        "senpaiConversationId": conversation_id,
        "senpaiTurnId": turn_id,
        "synthesisInputs": inputs,
    }


def put_if_absent(table, item: dict) -> bool:
    """Conditional put. Returns False when the deterministic row already exists."""
    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(messageId)",
        )
        return True
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return False
        raise


def is_visible_saved_row(row, user_id: str, conversation_id: str, turn_id: str) -> bool:
    """SECURITY: a re-read after a conflict is shown only when it is this user's live row of this turn."""
    if not isinstance(row, dict):
        return False
    return (
        row.get("userId") == user_id
        and row.get("senpaiConversationId") == conversation_id
        and row.get("senpaiTurnId") == turn_id
        and row.get("ragMode") == SYNTHESIS_MODE
        and row.get("messageId") == synthesis_message_id(turn_id)
        and _live(row, int(time.time()))
    )


def get_row(table, turn_id: str):
    key = synthesis_message_id(turn_id)
    return table.get_item(Key={"sessionId": key, "messageId": key}, ConsistentRead=True).get("Item")
