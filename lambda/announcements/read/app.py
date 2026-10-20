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
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from timeutil import normalize_utc_iso, now_utc_iso

ANNOUNCEMENT_QUERY_PAGE_SIZE = 50
MAX_ANNOUNCEMENT_QUERY_PAGES = 5

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
    """期限切れを除外し、必要件数まで最大ページ数の範囲で取得する。"""
    items = []
    kwargs = {
        'IndexName': 'status-publishAt-index',
        'KeyConditionExpression': Key('status').eq(status) & Key('publishAt').lte(now_iso),
        'FilterExpression': (
            Attr('endAt').not_exists()
            | Attr('endAt').eq(None)
            | Attr('endAt').eq('')
            | Attr('endAt').gte(now_iso)
        ),
        'ScanIndexForward': False,  # newest first
        'Limit': ANNOUNCEMENT_QUERY_PAGE_SIZE,
    }
    page_count = 0
    while len(items) < fetch_limit and page_count < MAX_ANNOUNCEMENT_QUERY_PAGES:
        resp = table.query(**kwargs)
        page_count += 1
        batch = resp.get('Items') or []
        for item in batch:
            pub = _ts_key(item.get('publishAt'))
            end = _ts_key(item.get('endAt')) if item.get('endAt') else ''
            if pub and pub > now_iso:
                continue
            if end and end < now_iso:
                continue
            items.append(item)
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            break
        kwargs['ExclusiveStartKey'] = lek
        # Limit はフィルター前に評価される件数なので、空ページでも次ページへ進む。
        kwargs['Limit'] = ANNOUNCEMENT_QUERY_PAGE_SIZE
    return items[:fetch_limit]


def get_active_maintenance(now_iso: str) -> list:
    """現在有効なメンテナンス告知を、通常一覧の件数に依存せず全件返す（issue #94 B1）。

    published と期限到来の scheduled を publishAt <= now で全ページ走査し、
    type=maintenance かつ startAt <= now <= endAt のものだけを返す。
    メンテ告知は少数のため FilterExpression 付きの全走査で足りる。
    """
    now_iso = normalize_utc_iso(now_iso) or now_iso
    found = {}
    for status in ('published', 'scheduled'):
        kwargs = {
            'IndexName': 'status-publishAt-index',
            'KeyConditionExpression': Key('status').eq(status) & Key('publishAt').lte(now_iso),
            'FilterExpression': Attr('type').eq('maintenance'),
        }
        while True:
            resp = table.query(**kwargs)
            for it in resp.get('Items') or []:
                start = _ts_key(it.get('startAt')) if it.get('startAt') else ''
                end = _ts_key(it.get('endAt')) if it.get('endAt') else ''
                if start and end and start <= now_iso <= end:
                    found[it['announcementId']] = it
            lek = resp.get('LastEvaluatedKey')
            if not lek:
                break
            kwargs['ExclusiveStartKey'] = lek
    return sorted(found.values(), key=lambda x: _ts_key(x.get('startAt')), reverse=True)


def get_published(limit: int, now_iso: str) -> list:
    """Return currently-visible announcements.

    Includes:
    - status=published with publishAt<=now
    - status=scheduled with publishAt<=now (due; publisher Lambda flips status async)

    Excludes items whose endAt has passed. Pinned first, then publishAt desc.
    Legacy rows with non-canonical timestamps are filtered with normalized compares.
    """
    now_iso = normalize_utc_iso(now_iso) or now_iso
    fetch_limit = max(limit * 5, 50)
    items = _query_by_status('published', now_iso, fetch_limit)
    # Due scheduled items must appear even before the 5-min publisher runs.
    items.extend(_query_by_status('scheduled', now_iso, fetch_limit))

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
        active_maintenance = get_active_maintenance(now_iso)

        return _response(200, {
            'announcements': announcements,
            'activeMaintenance': active_maintenance,
            'serverTime': now_iso,
        })

    except ClientError as e:
        print(f"[announcements-read] ClientError: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'Failed to load announcements'})
    except Exception as e:  # noqa: BLE001
        print(f"[announcements-read] Unexpected error: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'An unexpected error occurred'})
