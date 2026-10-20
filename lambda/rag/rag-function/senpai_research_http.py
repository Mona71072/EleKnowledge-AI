"""調査ジョブ API の HTTP 部品（応答・エラー形式・Cognito クレーム）。"""
import json
from decimal import Decimal

HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
}


def json_default(value):
    """DynamoDB の Decimal を JSON 数値にする。"""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return str(value)


def respond(status: int, payload: dict) -> dict:
    return {
        'statusCode': status,
        'headers': HEADERS,
        'body': json.dumps(payload, ensure_ascii=False, default=json_default),
    }


def error(status: int, code: str, message: str) -> dict:
    """統一エラー形式。スタックトレースや内部情報は載せない。"""
    return respond(status, {'error': code, 'message': message})


def claims_of(event: dict) -> dict:
    return ((event.get('requestContext') or {}).get('authorizer') or {}).get('claims') or {}


def method_of(event: dict) -> str:
    return (
        event.get('httpMethod')
        or (event.get('requestContext') or {}).get('http', {}).get('method')
        or ''
    )
