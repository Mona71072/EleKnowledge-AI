"""Authenticated API boundary. No real storage/auth configuration is inferred."""
import base64
import hmac
import json
import os
import re
import uuid

from service import Failure, exact, require
from storage import Contention, encode


MESSAGES = {400: '入力内容を確認してください。', 401: '認証が必要です。',
            403: 'この操作は許可されていません。', 404: '対象を利用できません。',
            409: '版または状態が変わりました。再確認してください。',
            503: '保存先または公開情報を確認できません。同じ操作で再試行してください。'}
# Each deployed function serves only its own routes, as a second guard behind API Gateway wiring.
RESPONSIBILITIES = {
    'intake': {'contribute', 'list', 'detail', 'transition', 'pending', 'operation', 'me'},
    'editorial': {'card', 'draft', 'review-requests', 'decisions'},
    'publication': {'publish', 'withdraw'},
    'reader': {'published'},
    'recovery': {'retry'},
}
_DEPLOYED = None


def route(method, path):
    if path == '/knowledge/contributions':
        return {'POST': 'contribute', 'GET': 'list'}.get(method), None
    if path == '/knowledge/operations' and method == 'GET':
        return 'pending', None
    if path == '/knowledge/me' and method == 'GET':
        return 'me', None
    match = re.fullmatch(r'/knowledge/(contributions|cards|published|operations)/'
                         r'([A-Za-z0-9][A-Za-z0-9_-]{0,79})(?:/([a-z-]+))?', path)
    if match is None:
        return None, None
    group, identifier, action = match.groups()
    name = {('contributions', 'GET', None): 'detail', ('contributions', 'PATCH', None): 'transition',
            ('cards', 'GET', None): 'card', ('cards', 'PUT', 'draft'): 'draft',
            ('cards', 'POST', 'review-requests'): 'review-requests',
            ('cards', 'POST', 'decisions'): 'decisions', ('cards', 'POST', 'publish'): 'publish',
            ('cards', 'POST', 'withdraw'): 'withdraw', ('published', 'GET', None): 'published',
            ('operations', 'GET', None): 'operation',
            ('operations', 'POST', 'retry'): 'retry'}.get((group, method, action))
    return name, identifier


def sign(secret, binding, position):
    return hmac.new(secret.encode(), encode([binding, position]).encode(), 'sha256').hexdigest()


def handle(event, service=None, responsibility=None, allowed_origin=None):
    request_id = str(uuid.uuid4())
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store'}
    if allowed_origin:
        headers.update({'Access-Control-Allow-Origin': allowed_origin, 'Vary': 'Origin'})
    try:
        require(service is not None, 503, 'StorageNotConfigured')
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        service.principal(claims)
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '').rstrip('/')
        name, identifier = route(method, path)
        require(name is not None and (responsibility is None
                                      or name in RESPONSIBILITIES[responsibility]), 404, 'NotFound')
        service.begin_request()
        incoming = {k.lower(): v for k, v in (event.get('headers') or {}).items()}
        raw = event.get('body') or '{}'
        if event.get('isBase64Encoded'):
            raw = base64.b64decode(raw, validate=True).decode('utf-8')
        require(isinstance(raw, str) and len(raw.encode('utf-8')) <= (
            300 * 1024 if path.endswith('/draft') else 32 * 1024))
        def unique(pairs):
            obj = {}
            for key, value in pairs:
                require(key not in obj)
                obj[key] = value
            return obj
        data = json.loads(raw, object_pairs_hook=unique)
        require(isinstance(data, dict))
        query = event.get('queryStringParameters') or {}
        key = incoming.get('idempotency-key')
        revision = incoming.get('if-match', '').strip('"')
        def expected():
            require(re.fullmatch(r'0|[1-9][0-9]{0,8}', revision) is not None)
            return int(revision)
        status = 200
        if name == 'contribute':
            result = service.contribute(claims, key, data)
            status = 201
        elif name == 'list':
            require(query.keys() <= {'scope', 'state', 'cursor', 'limit'})
            scope, state = query.get('scope', 'mine'), query.get('state', 'unconfirmed')
            binding = [claims['sub'], scope, state]
            secret = service.policy.get('cursorSecret')
            after = None
            if query.get('cursor'):
                cursor = json.loads(base64.urlsafe_b64decode(query['cursor']).decode())
                exact(cursor, ('position', 'binding', 'mac'))
                require(isinstance(secret, str) and len(secret) >= 32, 503, 'CursorNotConfigured')
                require(cursor['binding'] == binding and isinstance(cursor['mac'], str)
                        and hmac.compare_digest(cursor['mac'], sign(secret, binding, cursor['position'])))
                after = cursor['position']
            result = service.list_candidates(claims, scope, state, after, int(query.get('limit', 20)))
            following = result.pop('next')
            result['cursor'] = None
            if following is not None:
                require(isinstance(secret, str) and len(secret) >= 32, 503, 'CursorNotConfigured')
                cursor = {'position': following, 'binding': binding,
                          'mac': sign(secret, binding, following)}
                result['cursor'] = base64.urlsafe_b64encode(encode(cursor).encode()).decode()
        elif name == 'pending':
            result = service.pending_operations(claims)
        elif name == 'me':
            result = service.me(claims)
        elif name == 'detail':
            result = service.detail(claims, identifier)
        elif name == 'transition':
            result = service.transition(claims, key, identifier, expected(), data)
        elif name == 'card':
            result = service.card_detail(claims, identifier)
        elif name == 'draft':
            result = service.save_draft(claims, key, identifier, expected(), data)
        elif name in {'review-requests', 'decisions', 'publish'}:
            action = {'review-requests': service.review, 'decisions': service.decide,
                      'publish': service.publish}[name]
            result = action(claims, key, identifier, expected(), data)
        elif name == 'withdraw':
            result = service.publish(claims, key, identifier, expected(), data, withdraw=True)
        elif name == 'published':
            result = service.published(claims, identifier)
        elif name == 'operation':
            result = service.operation(claims, identifier)
        else:
            exact(data, ())
            require(isinstance(key, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,80}', key))
            result = service.resume(claims, identifier)
        return {'statusCode': status, 'headers': headers, 'body': encode(result)}
    except Failure as error:
        status, code = error.status, error.code
    except Contention:
        status, code = 503, 'ConcurrentUpdate'
    except (ValueError, TypeError, KeyError, UnicodeError):
        status, code = 400, 'ValidationError'
    except Exception:  # External adapter errors never expose paths, content or traces.
        status, code = 503, 'DependencyUnavailable'
    return {'statusCode': status, 'headers': headers, 'body': encode({
        'code': code, 'message': MESSAGES.get(status, MESSAGES[503]), 'requestId': request_id})}


def deployed():
    """Build once per container from validated configuration; any gap stays fail-closed (503)."""
    global _DEPLOYED
    if _DEPLOYED is None:
        try:
            from factory import build
            _DEPLOYED = build(os.environ)
        except Exception:  # Missing/invalid configuration is reported only as StorageNotConfigured.
            return None, None, None
    return _DEPLOYED


def lambda_handler(event, context):
    service, responsibility, origin = deployed()
    return handle(event, service, responsibility or 'reader', origin)
