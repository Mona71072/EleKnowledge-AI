"""Authenticated API boundary. No real storage/auth configuration is inferred."""
import base64
import json
import re
import uuid

from service import Failure, exact, require
from storage import encode


MESSAGES = {400: '入力内容を確認してください。', 401: '認証が必要です。',
            403: 'この操作は許可されていません。', 404: '対象を利用できません。',
            409: '版または状態が変わりました。再確認してください。',
            503: '保存先または公開情報を確認できません。同じ操作で再試行してください。'}
SERVICE = None  # Deployment factory is deliberately absent until real adapters are accepted.


def handle(event, service=None):
    request_id = str(uuid.uuid4())
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store'}
    try:
        require(service is not None, 503, 'StorageNotConfigured')
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        service.principal(claims)
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '').rstrip('/')
        incoming = {k.lower(): v for k, v in event.get('headers', {}).items()}
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
        if path == '/knowledge/contributions' and method == 'POST':
            result = service.contribute(claims, key, data)
            status = 201
        elif path == '/knowledge/contributions' and method == 'GET':
            require(query.keys() <= {'scope', 'state', 'cursor', 'limit'})
            scope, state = query.get('scope', 'mine'), query.get('state', 'unconfirmed')
            offset = 0
            if query.get('cursor'):
                cursor = json.loads(base64.urlsafe_b64decode(query['cursor']).decode())
                exact(cursor, ('offset', 'binding', 'mac'))
                binding = [claims['sub'], scope, state]
                secret = service.policy.get('cursorSecret')
                require(isinstance(secret, str) and len(secret) >= 32, 503, 'CursorNotConfigured')
                import hmac
                check = hmac.new(secret.encode(), encode([binding, cursor['offset']]).encode(), 'sha256').hexdigest()
                require(cursor['binding'] == binding and hmac.compare_digest(cursor['mac'], check))
                offset = cursor['offset']
            result = service.list_candidates(claims, scope, state, offset, int(query.get('limit', 20)))
            offset = result.pop('nextOffset')
            result['cursor'] = None
            if offset is not None:
                import hmac
                secret = service.policy.get('cursorSecret')
                require(isinstance(secret, str) and len(secret) >= 32, 503, 'CursorNotConfigured')
                binding = [claims['sub'], scope, state]
                cursor = {'offset': offset, 'binding': binding, 'mac': hmac.new(secret.encode(),
                          encode([binding, offset]).encode(), 'sha256').hexdigest()}
                result['cursor'] = base64.urlsafe_b64encode(encode(cursor).encode()).decode()
        elif path == '/knowledge/operations' and method == 'GET':
            result = service.pending_operations(claims)
        else:
            route = re.fullmatch(r'/knowledge/(contributions|cards|published|operations)/'
                                 r'([A-Za-z0-9][A-Za-z0-9_-]{0,79})(?:/([a-z-]+))?', path)
            require(route is not None, 404, 'NotFound')
            group, identifier, action = route.groups()
            if group == 'contributions' and action is None:
                if method == 'GET':
                    result = service.detail(claims, identifier)
                else:
                    require(method == 'PATCH', 400, 'MethodNotAllowed')
                    result = service.transition(claims, key, identifier, expected(), data)
            elif group == 'cards':
                if method == 'GET' and action is None:
                    result = service.card_detail(claims, identifier)
                elif method == 'PUT' and action == 'draft':
                    result = service.save_draft(claims, key, identifier, expected(), data)
                elif method == 'POST' and action in {'review-requests', 'decisions', 'publish', 'withdraw'}:
                    methods = {'review-requests': service.review, 'decisions': service.decide,
                               'publish': service.publish}
                    if action == 'withdraw':
                        result = service.publish(claims, key, identifier, expected(), data, withdraw=True)
                    else:
                        result = methods[action](claims, key, identifier, expected(), data)
                else:
                    raise Failure(404, 'NotFound')
            elif group == 'published' and method == 'GET' and action is None:
                result = service.published(claims, identifier)
            elif group == 'operations' and method == 'GET' and action is None:
                result = service.operation(claims, identifier)
            elif group == 'operations' and method == 'POST' and action == 'retry':
                exact(data, ())
                require(isinstance(key, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,80}', key))
                result = service.resume(claims, identifier)
            else:
                raise Failure(404, 'NotFound')
        return {'statusCode': status, 'headers': headers, 'body': encode(result)}
    except Failure as error:
        status, code = error.status, error.code
    except (ValueError, TypeError, KeyError, UnicodeError):
        status, code = 400, 'ValidationError'
    except Exception:  # External adapter errors never expose paths, content or traces.
        status, code = 503, 'DependencyUnavailable'
    return {'statusCode': status, 'headers': headers, 'body': encode({
        'code': code, 'message': MESSAGES.get(status, MESSAGES[503]), 'requestId': request_id})}


def lambda_handler(event, context):
    return handle(event, SERVICE)
