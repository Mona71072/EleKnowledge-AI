"""
EleKnowledge Announcements - Write (admin only)

GET    /admin/announcements          paginated listing
GET    /admin/announcements/active   all currently visible announcements
POST   /admin/announcements          create
PUT    /admin/announcements/{id}      update
DELETE /admin/announcements/{id}      delete

Admin is verified server-side from the Cognito authorizer claims
(cognito:groups must contain ADMIN_GROUP_NAME). Frontend gating is UI-assist only.
Markdown body is sanitized before storage (defense in depth; the frontend renders
Markdown without raw-HTML, so this is a second layer).
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import re
import secrets
import time
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from timeutil import normalize_utc_iso, now_utc_iso

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))

ANNOUNCEMENTS_TABLE = os.environ.get('ANNOUNCEMENTS_TABLE')
ADMIN_GROUP_NAME = os.environ.get('ADMIN_GROUP_NAME', 'admin')
table = dynamodb.Table(ANNOUNCEMENTS_TABLE)

VALID_TYPES = {'update', 'maintenance', 'notice'}
VALID_SEVERITY = {'info', 'warning', 'critical'}
VALID_STATUS = {'draft', 'scheduled', 'published'}

TITLE_MAX = 120
BODY_MAX = 20000

# 管理一覧のページング（issue #94 R9）。全件 Scan をやめ、status-publishAt-index を状態ごとに Query して併合する
ADMIN_LIST_STATUSES = ('draft', 'scheduled', 'published')
ADMIN_LIST_INDEX = 'status-publishAt-index'
ADMIN_LIST_DEFAULT_LIMIT = 50
ADMIN_LIST_MAX_LIMIT = 100
# 「いま表示中」（公開中かつ未終了）は件数で切らず、Query の全ページを読む（issue #94 R9 の追補）
ACTIVE_LIST_ROUTE = '/admin/announcements/active'
ACTIVE_LIST_PAGE_SIZE = 100

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

# Dangerous HTML/JS patterns to strip from Markdown before storage
_SCRIPT_RE = re.compile(r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r'<\s*/?\s*(script|iframe|object|embed|style|link|meta|form|input|svg)[^>]*>', re.IGNORECASE)
_EVENT_ATTR_RE = re.compile(r'\son\w+\s*=\s*(".*?"|\'.*?\'|[^\s>]+)', re.IGNORECASE)
_JS_URI_RE = re.compile(r'javascript\s*:', re.IGNORECASE)


def _now_iso() -> str:
    return now_utc_iso()


def _norm_ts(value) -> Optional[str]:
    """Normalize a client/server timestamp; raise ValueError on bad input."""
    if value is None or value == '':
        return None
    try:
        return normalize_utc_iso(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f'invalid timestamp: {value!r}') from e


def _response(status: int, body: dict) -> dict:
    return {
        'statusCode': status,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, ensure_ascii=False, default=str),
    }


def is_admin(event) -> bool:
    claims = (event.get('requestContext', {}) or {}).get('authorizer', {}).get('claims', {}) or {}
    groups = claims.get('cognito:groups', '')
    if isinstance(groups, list):
        group_list = groups
    else:
        group_list = [g.strip() for g in str(groups).split(',') if g.strip()]
    return ADMIN_GROUP_NAME in group_list


def get_actor(event) -> str:
    claims = (event.get('requestContext', {}) or {}).get('authorizer', {}).get('claims', {}) or {}
    return claims.get('email') or claims.get('cognito:username') or claims.get('sub') or 'unknown'


def sanitize_markdown(text: str) -> str:
    if not text:
        return ''
    text = _SCRIPT_RE.sub('', text)
    text = _TAG_RE.sub('', text)
    text = _EVENT_ATTR_RE.sub('', text)
    text = _JS_URI_RE.sub('', text)
    return text


def validate(body: dict, partial: bool = False) -> Optional[str]:
    """Return an error message, or None if valid."""
    def required(field):
        return field in body and body[field] not in (None, '')

    if not partial or 'type' in body:
        if body.get('type') not in VALID_TYPES:
            return f"type must be one of {sorted(VALID_TYPES)}"
    if not partial or 'severity' in body:
        if body.get('severity') not in VALID_SEVERITY:
            return f"severity must be one of {sorted(VALID_SEVERITY)}"
    if not partial or 'status' in body:
        if body.get('status') not in VALID_STATUS:
            return f"status must be one of {sorted(VALID_STATUS)}"
    if not partial or 'title' in body:
        title = body.get('title', '')
        if not isinstance(title, str) or not title.strip():
            return "title is required"
        if len(title) > TITLE_MAX:
            return f"title must be <= {TITLE_MAX} chars"
    if body.get('body') and len(body['body']) > BODY_MAX:
        return f"body must be <= {BODY_MAX} chars"

    # scheduled は未来の publishAt 必須（空欄で即時公開に落ちない）
    if (not partial or 'status' in body) and body.get('status') == 'scheduled':
        try:
            pub = _norm_ts(body.get('publishAt'))
        except ValueError:
            return "publishAt must be a valid ISO-8601 timestamp"
        if not pub:
            return "scheduled status requires publishAt"
        if pub <= now_utc_iso():
            return "scheduled publishAt must be in the future"

    # Maintenance requires a valid time window
    if body.get('type') == 'maintenance':
        start, end = body.get('startAt'), body.get('endAt')
        if not partial and (not start or not end):
            return "maintenance requires startAt and endAt"
        try:
            start_n = _norm_ts(start) if start else None
            end_n = _norm_ts(end) if end else None
        except ValueError:
            return "startAt/endAt must be valid ISO-8601 timestamps"
        if start_n and end_n and start_n >= end_n:
            return "startAt must be before endAt"
    return None


def create(body: dict, actor: str) -> dict:
    err = validate(body, partial=False)
    if err:
        return _response(400, {'error': 'ValidationError', 'message': err})

    now = _now_iso()
    status = body['status']
    try:
        publish_at = _norm_ts(body.get('publishAt')) or now
        start_at = _norm_ts(body.get('startAt'))
        end_at = _norm_ts(body.get('endAt'))
    except ValueError as e:
        return _response(400, {'error': 'ValidationError', 'message': str(e)})

    # A future publishAt with published status is treated as scheduled
    if status == 'published' and publish_at > now:
        status = 'scheduled'

    # 同一ミリ秒の衝突で上書きしないよう乱数を付与（issue #94 R5）
    announcement_id = f"anc_{int(time.time() * 1000)}_{secrets.token_hex(2)}"
    item = {
        'announcementId': announcement_id,
        'type': body['type'],
        'title': body['title'].strip(),
        'body': sanitize_markdown(body.get('body', '')),
        'severity': body['severity'],
        'status': status,
        'publishAt': publish_at,
        'pinned': bool(body.get('pinned', False)),
        # チャット画面の帯にも出す（既定: critical なら真。設計 2026-09-10 dashboard v2 §10.4）
        'showInChat': bool(body.get('showInChat', body.get('severity') == 'critical')),
        'createdBy': actor,
        'createdAt': now,
        'updatedAt': now,
    }
    if body.get('type') == 'maintenance':
        item['startAt'] = start_at
        item['endAt'] = end_at
    elif end_at:
        item['endAt'] = end_at
    # ttl はクライアントから受け取らない（テーブルの TTL が有効なため、過去 epoch を渡すと公開中の告知が消える。issue #94 B2）

    table.put_item(Item=item)
    return _response(201, {'announcementId': announcement_id, 'status': status})


def update(announcement_id: str, body: dict, actor: str) -> dict:
    existing = table.get_item(Key={'announcementId': announcement_id}).get('Item')
    if not existing:
        return _response(404, {'error': 'NotFound', 'message': 'Announcement not found'})

    err = validate(body, partial=True)
    if err:
        return _response(400, {'error': 'ValidationError', 'message': err})

    merged = dict(existing)
    try:
        for field in ('type', 'title', 'severity', 'status', 'pinned'):
            if field in body:
                merged[field] = body[field]
        if 'title' in body:
            merged['title'] = body['title'].strip()
        if 'body' in body:
            merged['body'] = sanitize_markdown(body['body'])
        if 'pinned' in body:
            merged['pinned'] = bool(body['pinned'])
        if 'showInChat' in body:
            merged['showInChat'] = bool(body['showInChat'])
        if 'publishAt' in body:
            merged['publishAt'] = _norm_ts(body['publishAt']) or merged.get('publishAt')
        # 空文字は「属性を消す」扱い（None を書くと DynamoDB に NULL 属性が残る。issue #94 R7）
        for field in ('startAt', 'endAt'):
            if field in body:
                value = _norm_ts(body[field])
                if value:
                    merged[field] = value
                else:
                    merged.pop(field, None)
        # Re-normalize existing timestamps so legacy rows become comparable
        if merged.get('publishAt'):
            merged['publishAt'] = _norm_ts(merged['publishAt']) or merged['publishAt']
        if merged.get('startAt'):
            merged['startAt'] = _norm_ts(merged['startAt'])
        if merged.get('endAt'):
            merged['endAt'] = _norm_ts(merged['endAt'])
    except ValueError as e:
        return _response(400, {'error': 'ValidationError', 'message': str(e)})

    # type を maintenance 以外へ変えたとき、明示指定が無ければ旧メンテ期間を引き継がない
    # （endAt が残ると read 側の期限切れフィルタで告知が黙って消える。issue #94 B4）
    if existing.get('type') == 'maintenance' and merged.get('type') != 'maintenance':
        if 'startAt' not in body:
            merged.pop('startAt', None)
        if 'endAt' not in body:
            merged.pop('endAt', None)

    # maintenance の期間チェックはマージ後の項目に対して行う（部分更新で素通りしない。issue #94 B3）
    if merged.get('type') == 'maintenance':
        if not merged.get('startAt') or not merged.get('endAt'):
            return _response(400, {'error': 'ValidationError', 'message': 'maintenance requires startAt and endAt'})
        if merged['startAt'] >= merged['endAt']:
            return _response(400, {'error': 'ValidationError', 'message': 'startAt must be before endAt'})

    now = _now_iso()
    if merged.get('status') == 'published' and merged.get('publishAt', now) > now:
        merged['status'] = 'scheduled'
    merged['updatedAt'] = now
    merged['updatedBy'] = actor

    table.put_item(Item=merged)
    return _response(200, {'announcementId': announcement_id, 'status': merged.get('status')})


def delete(announcement_id: str) -> dict:
    # 存在しない id は 404（無条件削除で 200 を返さない。issue #94 R8）
    try:
        table.delete_item(
            Key={'announcementId': announcement_id},
            ConditionExpression='attribute_exists(announcementId)',
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return _response(404, {'error': 'NotFound', 'message': 'Announcement not found'})
        raise
    return _response(200, {'message': 'deleted', 'announcementId': announcement_id})


def _parse_list_limit(raw) -> int:
    """limit は 1〜ADMIN_LIST_MAX_LIMIT の整数。省略時は既定値。"""
    if raw is None:
        return ADMIN_LIST_DEFAULT_LIMIT
    if not isinstance(raw, str) or not re.fullmatch(r'[0-9]{1,3}', raw):
        raise ValueError('limit must be an integer between 1 and %d' % ADMIN_LIST_MAX_LIMIT)
    value = int(raw)
    if not 1 <= value <= ADMIN_LIST_MAX_LIMIT:
        raise ValueError('limit must be an integer between 1 and %d' % ADMIN_LIST_MAX_LIMIT)
    return value


def _encode_cursor(cursor: dict) -> str:
    raw = json.dumps(cursor, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def _decode_cursor(token: str) -> dict:
    """nextToken を検証して {'p': {status: GSI キー}, 'd': [終了した状態]} を返す。壊れた値は ValueError。"""
    if not isinstance(token, str) or not token or len(token) > 4096:
        raise ValueError('nextToken is invalid')
    try:
        raw = base64.urlsafe_b64decode(token + '=' * (-len(token) % 4))
        cursor = json.loads(raw.decode('utf-8'))
    except (binascii.Error, UnicodeError, json.JSONDecodeError, ValueError) as e:
        raise ValueError('nextToken is invalid') from e
    if not isinstance(cursor, dict) or set(cursor) - {'p', 'd'}:
        raise ValueError('nextToken is invalid')
    positions = cursor.get('p', {})
    done = cursor.get('d', [])
    if not isinstance(positions, dict) or not isinstance(done, list):
        raise ValueError('nextToken is invalid')
    for status, key in positions.items():
        if status not in ADMIN_LIST_STATUSES or not isinstance(key, dict):
            raise ValueError('nextToken is invalid')
        if set(key) != {'status', 'publishAt', 'announcementId'} or key['status'] != status:
            raise ValueError('nextToken is invalid')
        if not all(isinstance(key[k], str) and key[k] for k in ('publishAt', 'announcementId')):
            raise ValueError('nextToken is invalid')
    if not all(isinstance(s, str) and s in ADMIN_LIST_STATUSES for s in done):
        raise ValueError('nextToken is invalid')
    return {'p': positions, 'd': sorted(set(done))}


def _gsi_key(item: dict) -> dict:
    return {k: item[k] for k in ('status', 'publishAt', 'announcementId')}


def list_all(query: Optional[dict] = None) -> dict:
    """Admin listing across every status (draft/scheduled/published), newest publishAt first.

    状態ごとに status-publishAt-index を降順に Query し、先頭 limit 件を併合する。
    次ページは状態ごとに「最後に返した項目」の GSI キーを nextToken（base64url の JSON）に入れて返す。
    """
    query = query or {}
    try:
        limit = _parse_list_limit(query.get('limit'))
        cursor = _decode_cursor(query['nextToken']) if query.get('nextToken') is not None else {'p': {}, 'd': []}
    except ValueError as e:
        return _response(400, {'error': 'ValidationError', 'message': str(e)})

    done = set(cursor['d'])
    fetched = {}  # status -> (items in DynamoDB order, LastEvaluatedKey があるか)
    for status in ADMIN_LIST_STATUSES:
        if status in done:
            continue
        kwargs = {
            'IndexName': ADMIN_LIST_INDEX,
            'KeyConditionExpression': Key('status').eq(status),
            'ScanIndexForward': False,
            'Limit': limit,
        }
        if status in cursor['p']:
            kwargs['ExclusiveStartKey'] = cursor['p'][status]
        resp = table.query(**kwargs)
        fetched[status] = (resp.get('Items', []), bool(resp.get('LastEvaluatedKey')))

    # 併合は安定ソート。各状態の内部順（DynamoDB の順）が崩れないので、選んだ件数はその状態の先頭からの接頭辞になる
    candidates = [(status, item) for status in fetched for item in fetched[status][0]]
    candidates.sort(key=lambda pair: pair[1].get('publishAt') or '', reverse=True)
    chosen = candidates[:limit]

    taken = {status: 0 for status in fetched}
    for status, _ in chosen:
        taken[status] += 1

    positions = dict(cursor['p'])
    next_done = set(done)
    for status, (items, has_more) in fetched.items():
        k = taken[status]
        if k:
            positions[status] = _gsi_key(items[k - 1])
        if not has_more and k == len(items):
            next_done.add(status)

    response = {'announcements': [item for _, item in chosen]}
    if len(next_done) < len(ADMIN_LIST_STATUSES):
        response['nextToken'] = _encode_cursor({
            'p': {s: positions[s] for s in ADMIN_LIST_STATUSES if s in positions and s not in next_done},
            'd': sorted(next_done),
        })
    else:
        response['nextToken'] = None
    return _response(200, response)


def _is_ended(item: dict, now_iso: str) -> bool:
    try:
        end = normalize_utc_iso(item.get('endAt'))
    except (TypeError, ValueError):
        return False  # 壊れた endAt は終了扱いにしない（画面で見えるように残す）
    return end is not None and end < now_iso


def _is_started(item: dict, now_iso: str) -> bool:
    try:
        pub = normalize_utc_iso(item.get('publishAt'))
    except (TypeError, ValueError):
        return False
    return pub is not None and pub <= now_iso


def list_active(now_iso: Optional[str] = None) -> dict:
    """いま表示中（status が published / scheduled で、公開日時を過ぎ、表示終了していない）を全件返す。

    公開一覧 API と同じ条件（isVisibleNow）。status-publishAt-index を状態ごとに Query し、
    LastEvaluatedKey が無くなるまで読む。件数では切らないので「戻し忘れ」の警告が 51 件目以降も出る。
    """
    now = normalize_utc_iso(now_iso or _now_iso())
    found = {}
    for status in ('published', 'scheduled'):
        kwargs = {
            'IndexName': ADMIN_LIST_INDEX,
            'KeyConditionExpression': Key('status').eq(status) & Key('publishAt').lte(now),
            'ScanIndexForward': False,
            'Limit': ACTIVE_LIST_PAGE_SIZE,
        }
        while True:
            resp = table.query(**kwargs)
            for item in resp.get('Items', []):
                # GSI の文字列比較と正規化後の比較がずれる旧形式の行は、ここで正しく判定し直す
                if _is_started(item, now) and not _is_ended(item, now):
                    found[item['announcementId']] = item
            lek = resp.get('LastEvaluatedKey')
            if not lek:
                break
            kwargs['ExclusiveStartKey'] = lek
    items = sorted(found.values(), key=lambda it: it.get('publishAt') or '', reverse=True)
    return _response(200, {'announcements': items})


def lambda_handler(event, context):
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    if method == 'OPTIONS':
        return _response(200, {})

    if not is_admin(event):
        return _response(403, {'error': 'Forbidden', 'message': 'Admin privilege required'})

    try:
        path_params = event.get('pathParameters') or {}
        announcement_id = path_params.get('id')

        body = {}
        if event.get('body'):
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']

        actor = get_actor(event)

        if method == 'GET':
            if event.get('resource') == ACTIVE_LIST_ROUTE or (event.get('path') or '').endswith(ACTIVE_LIST_ROUTE):
                return list_active()
            return list_all(event.get('queryStringParameters') or {})
        if method == 'POST':
            return create(body, actor)
        if method == 'PUT':
            if not announcement_id:
                return _response(400, {'error': 'ValidationError', 'message': 'id is required'})
            return update(announcement_id, body, actor)
        if method == 'DELETE':
            if not announcement_id:
                return _response(400, {'error': 'ValidationError', 'message': 'id is required'})
            return delete(announcement_id)

        return _response(404, {'error': 'NotFound', 'message': 'Route not found'})

    except json.JSONDecodeError:
        return _response(400, {'error': 'ValidationError', 'message': 'Invalid JSON body'})
    except ClientError as e:
        print(f"[announcements-write] ClientError: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'Operation failed'})
    except Exception as e:  # noqa: BLE001
        print(f"[announcements-write] Unexpected error: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'An unexpected error occurred'})
