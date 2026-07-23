"""
EleKnowledge Announcements - Read (public to authenticated users)

GET /announcements?limit=10
Returns currently-published announcements (status=published, publishAt<=now),
pinned first then publishAt descending. Expired items (endAt < now) are excluded.
"""
import json
import os
import time
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))

ANNOUNCEMENTS_TABLE = os.environ.get('ANNOUNCEMENTS_TABLE')
table = dynamodb.Table(ANNOUNCEMENTS_TABLE)

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,OPTIONS',
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _response(status: int, body: dict) -> dict:
    return {
        'statusCode': status,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, ensure_ascii=False, default=str),
    }


def get_published(limit: int, now_iso: str) -> list:
    """Query published announcements via GSI, newest first, then filter/sort."""
    resp = table.query(
        IndexName='status-publishAt-index',
        KeyConditionExpression=Key('status').eq('published') & Key('publishAt').lte(now_iso),
        ScanIndexForward=False,   # newest first
        Limit=max(limit * 3, 30),  # over-fetch to allow expiry filtering
    )
    items = resp.get('Items', [])

    # Drop items whose display window has ended (endAt < now)
    visible = [it for it in items if not it.get('endAt') or it['endAt'] >= now_iso]

    # pinned first, then publishAt desc (query already desc; stable sort keeps it)
    visible.sort(key=lambda x: (0 if x.get('pinned') else 1))
    return visible[:limit]


def lambda_handler(event, context):
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    if method == 'OPTIONS':
        return _response(200, {})

    try:
        qs = event.get('queryStringParameters') or {}
        try:
            limit = int(qs.get('limit', 10))
        except (TypeError, ValueError):
            limit = 10
        limit = max(1, min(limit, 50))

        now_iso = _now_iso()
        announcements = get_published(limit, now_iso)

        return _response(200, {
            'announcements': announcements,
            'serverTime': now_iso,
        })

    except ClientError as e:
        print(f"[announcements-read] ClientError: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'Failed to load announcements'})
    except Exception as e:  # noqa: BLE001
        print(f"[announcements-read] Unexpected error: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'An unexpected error occurred'})
