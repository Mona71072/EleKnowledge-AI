"""
EleKnowledge Announcements - Write (admin only)

POST   /admin/announcements          create
PUT    /admin/announcements/{id}      update
DELETE /admin/announcements/{id}      delete

Admin is verified server-side from the Cognito authorizer claims
(cognito:groups must contain ADMIN_GROUP_NAME). Frontend gating is UI-assist only.
Markdown body is sanitized before storage (defense in depth; the frontend renders
Markdown without raw-HTML, so this is a second layer).
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))

ANNOUNCEMENTS_TABLE = os.environ.get('ANNOUNCEMENTS_TABLE')
ADMIN_GROUP_NAME = os.environ.get('ADMIN_GROUP_NAME', 'admin')
table = dynamodb.Table(ANNOUNCEMENTS_TABLE)

VALID_TYPES = {'update', 'maintenance', 'notice'}
VALID_SEVERITY = {'info', 'warning', 'critical'}
VALID_STATUS = {'draft', 'scheduled', 'published'}

TITLE_MAX = 120
BODY_MAX = 20000

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
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


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

    # Maintenance requires a valid time window
    if body.get('type') == 'maintenance':
        start, end = body.get('startAt'), body.get('endAt')
        if not partial and (not start or not end):
            return "maintenance requires startAt and endAt"
        if start and end and start >= end:
            return "startAt must be before endAt"
    return None


def create(body: dict, actor: str) -> dict:
    err = validate(body, partial=False)
    if err:
        return _response(400, {'error': 'ValidationError', 'message': err})

    now = _now_iso()
    status = body['status']
    publish_at = body.get('publishAt') or now
    # A future publishAt with published status is treated as scheduled
    if status == 'published' and publish_at > now:
        status = 'scheduled'

    announcement_id = f"anc_{int(time.time() * 1000)}"
    item = {
        'announcementId': announcement_id,
        'type': body['type'],
        'title': body['title'].strip(),
        'body': sanitize_markdown(body.get('body', '')),
        'severity': body['severity'],
        'status': status,
        'publishAt': publish_at,
        'pinned': bool(body.get('pinned', False)),
        'createdBy': actor,
        'createdAt': now,
        'updatedAt': now,
    }
    if body.get('type') == 'maintenance':
        item['startAt'] = body.get('startAt')
        item['endAt'] = body.get('endAt')
    if body.get('endAt') and 'endAt' not in item:
        item['endAt'] = body['endAt']
    if body.get('ttl'):
        item['ttl'] = int(body['ttl'])

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
    for field in ('type', 'title', 'severity', 'status', 'publishAt', 'pinned', 'startAt', 'endAt'):
        if field in body:
            merged[field] = body[field]
    if 'title' in body:
        merged['title'] = body['title'].strip()
    if 'body' in body:
        merged['body'] = sanitize_markdown(body['body'])
    if 'pinned' in body:
        merged['pinned'] = bool(body['pinned'])

    now = _now_iso()
    if merged.get('status') == 'published' and merged.get('publishAt', now) > now:
        merged['status'] = 'scheduled'
    merged['updatedAt'] = now
    merged['updatedBy'] = actor

    table.put_item(Item=merged)
    return _response(200, {'announcementId': announcement_id, 'status': merged.get('status')})


def delete(announcement_id: str) -> dict:
    table.delete_item(Key={'announcementId': announcement_id})
    return _response(200, {'message': 'deleted', 'announcementId': announcement_id})


def list_all() -> dict:
    """Admin listing across every status (draft/scheduled/published)."""
    items = []
    kwargs = {}
    while True:
        resp = table.scan(**kwargs)
        items.extend(resp.get('Items', []))
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            break
        kwargs['ExclusiveStartKey'] = lek
    items.sort(key=lambda x: x.get('publishAt', x.get('createdAt', '')), reverse=True)
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
            return list_all()
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
