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

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from timeutil import normalize_utc_iso, now_utc_iso

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
    return now_utc_iso()


def _ts_key(value) -> str:
    """Comparable UTC key; empty/invalid sorts as empty string."""
    try:
        return normalize_utc_iso(value) or ''
    except (TypeError, ValueError):
        return str(value or '')


def _response(status: int, body: dict) -> dict:
    return {
        'statusCode': status,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, ensure_ascii=False, default=str),
    }


def _query_by_status(status: str, now_iso: str, fetch_limit: int) -> list:
    """Page until we collect fetch_limit items or the GSI is exhausted."""
    items = []
    kwargs = {
        'IndexName': 'status-publishAt-index',
        'KeyConditionExpression': Key('status').eq(status) & Key('publishAt').lte(now_iso),
        'ScanIndexForward': False,  # newest first
        'Limit': min(50, max(1, fetch_limit)),
    }
    while len(items) < fetch_limit:
        resp = table.query(**kwargs)
        batch = resp.get('Items') or []
        items.extend(batch)
        lek = resp.get('LastEvaluatedKey')
        if not lek or not batch:
            break
        kwargs['ExclusiveStartKey'] = lek
        kwargs['Limit'] = min(50, fetch_limit - len(items))
    return items[:fetch_limit]


def get_published(limit: int, now_iso: str) -> list:
    """Return currently-visible announcements.

    Includes:
    - status=published with publishAt<=now
    - status=scheduled with publishAt<=now (due; publisher Lambda flips status async)

    Excludes items whose endAt has passed. Pinned first, then publishAt desc.
    Legacy rows with non-canonical timestamps are filtered with normalized compares.
    """
    now_iso = normalize_utc_iso(now_iso) or now_iso
    fetch = max(limit * 5, 50)
    items = _query_by_status('published', now_iso, fetch)
    # Due scheduled items must appear even before the 5-min publisher runs.
    items.extend(_query_by_status('scheduled', now_iso, fetch))

    # Drop items whose display window has ended (endAt < now); dedupe by id.
    # Also drop legacy rows whose publishAt is still in the future after normalize
    # (GSI string compare can disagree with mixed formats).
    by_id = {}
    for it in items:
        pub = _ts_key(it.get('publishAt'))
        if pub and pub > now_iso:
            continue
        end = _ts_key(it.get('endAt')) if it.get('endAt') else ''
        if end and end < now_iso:
            continue
        by_id[it['announcementId']] = it

    visible = list(by_id.values())
    pinned = sorted(
        [x for x in visible if x.get('pinned')],
        key=lambda x: _ts_key(x.get('publishAt')),
        reverse=True,
    )
    rest = sorted(
        [x for x in visible if not x.get('pinned')],
        key=lambda x: _ts_key(x.get('publishAt')),
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
