"""
EleKnowledge Announcements - Read (public to authenticated users)

GET /announcements?limit=10
Returns currently-visible announcements:
  - status=published with publishAt<=now
  - status=scheduled with publishAt<=now (due; publisher promotes async)
Pinned first then publishAt descending. Expired items (endAt < now) are excluded.
"""
import json
import os
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


def _query_by_status(status: str, now_iso: str, fetch_limit: int) -> list:
    resp = table.query(
        IndexName='status-publishAt-index',
        KeyConditionExpression=Key('status').eq(status) & Key('publishAt').lte(now_iso),
        ScanIndexForward=False,  # newest first
        Limit=fetch_limit,
    )
    return resp.get('Items', [])


def get_published(limit: int, now_iso: str) -> list:
    """Return currently-visible announcements.

    Includes:
    - status=published with publishAt<=now
    - status=scheduled with publishAt<=now (due; publisher Lambda flips status async)

    Excludes items whose endAt has passed. Pinned first, then publishAt desc.
    """
    fetch = max(limit * 3, 30)
    items = _query_by_status('published', now_iso, fetch)
    # Due scheduled items must appear even before the 5-min publisher runs.
    items.extend(_query_by_status('scheduled', now_iso, fetch))

    # Drop items whose display window has ended (endAt < now); dedupe by id
    by_id = {}
    for it in items:
        if it.get('endAt') and it['endAt'] < now_iso:
            continue
        by_id[it['announcementId']] = it

    visible = list(by_id.values())
    pinned = sorted(
        [x for x in visible if x.get('pinned')],
        key=lambda x: x.get('publishAt', ''),
        reverse=True,
    )
    rest = sorted(
        [x for x in visible if not x.get('pinned')],
        key=lambda x: x.get('publishAt', ''),
        reverse=True,
    )
    return (pinned + rest)[:limit]


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
