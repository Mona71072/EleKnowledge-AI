"""
トラブルシューティング履歴取得 Lambda
GET /history            → ユーザー別セッション一覧（最新50件）
GET /history?sessionId= → 特定セッションの詳細
"""
import json
import logging
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SESSIONS_TABLE = os.environ.get("SESSIONS_TABLE", "troubleshooting-sessions")
dynamodb_resource = boto3.resource("dynamodb")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False, cls=DecimalEncoder),
    }


def lambda_handler(event, context):
    user_id = (
        event.get("requestContext", {}).get("authorizer", {}).get("userId", "")
    )
    if not user_id:
        return _response(401, {"error": "認証情報が不正です"})

    params = event.get("queryStringParameters") or {}
    session_id = params.get("sessionId")
    table = dynamodb_resource.Table(SESSIONS_TABLE)

    if session_id:
        resp = table.get_item(Key={"session_id": session_id})
        item = resp.get("Item")
        if not item or item.get("userId") != user_id:
            return _response(404, {"error": "セッションが見つかりません"})
        return _response(200, item)

    # ユーザー別一覧（userId-timestamp-index GSI、新しい順）
    resp = table.query(
        IndexName="userId-timestamp-index",
        KeyConditionExpression=Key("userId").eq(user_id),
        ScanIndexForward=False,
        Limit=50,
    )
    sessions = [
        {
            "sessionId": s["session_id"],
            "timestamp": s.get("timestamp"),
            "input": s.get("input", {}),
            "preview": (s.get("result") or "")[:100],
        }
        for s in resp.get("Items", [])
    ]
    logger.info(f"History query: userId={user_id}, count={len(sessions)}")
    return _response(200, {"sessions": sessions})
