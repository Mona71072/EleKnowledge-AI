"""
EleKnowledge Chat Management Lambda Function
Session and Message Management
"""
import json
import os
import boto3
import time
from datetime import datetime
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))

# Environment variables
CHATLOGS_TABLE_NAME = os.environ.get('CHATLOGS_TABLE')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
FEEDBACK_METRIC_NAMESPACE = os.environ.get('FEEDBACK_METRIC_NAMESPACE', 'EleKnowledge/Feedback')
ADMIN_GROUP_NAME = os.environ.get('ADMIN_GROUP_NAME', 'admin')

# DynamoDB table
chatlogs_table = dynamodb.Table(CHATLOGS_TABLE_NAME)

# 👎 理由コード（成功＝資料到達＋疑問解決。何がダメかを採取）
# unresolved は「直す場所の入口」であり KB が悪いと決め打ちしない → failures で人手振り分け
FEEDBACK_REASONS = frozenset({
    'wrong_doc',    # 資料が違う → 検索・フィルタ・KB
    'unresolved',   # 疑問が解けない → failures で検索／snippet／作文／聞き返し等に振り分け
    'bad_answer',   # 回答がおかしい → プロンプト・弱ゲート
    'other',        # その他
})
# 旧データに残る値（新規 PUT では FEEDBACK_REASONS 外＝400。一覧表示はそのまま）
# wrong_page: 頁が違う（廃止・頁誘導仕様ではないため）
FEEDBACK_COMMENT_MAX = 200
WISH_TEXT_MAX = 1000
FAILURES_SCAN_MAX_PAGES = 25
FAILURES_DEFAULT_LIMIT = 50
FAILURES_HARD_LIMIT = 100


def emit_feedback_metric(feedback: str) -> None:
    """Emit an Embedded Metric Format (EMF) log so CloudWatch counts feedback in
    real time. Both FeedbackGood and FeedbackBad are always emitted (one 1, one 0)
    so the like-rate metric-math (Good / (Good + Bad)) always has data points and
    no table scan is needed for live dashboards.
    """
    try:
        emf = {
            '_aws': {
                'Timestamp': int(time.time() * 1000),
                'CloudWatchMetrics': [{
                    'Namespace': FEEDBACK_METRIC_NAMESPACE,
                    'Dimensions': [['Environment']],
                    'Metrics': [{'Name': 'FeedbackGood'}, {'Name': 'FeedbackBad'}],
                }],
            },
            'Environment': ENVIRONMENT,
            'FeedbackGood': 1 if feedback == 'good' else 0,
            'FeedbackBad': 1 if feedback == 'bad' else 0,
        }
        print(json.dumps(emf))
    except Exception as e:  # noqa: BLE001 - metrics must never break the request
        print(f"[chat] Failed to emit feedback EMF: {e}")


def get_caller_id(event) -> str:
    """検証済み Cognito クレームから呼び出し元の sub を返す。

    API Gateway の Cognito Authorizer が保証するのは「誰かがログイン済みである」
    ことだけで、「どのユーザーか」はここで確定させる必要がある。
    クエリ文字列やボディの userId はクライアントが自由に詐称できるため使わない。
    """
    claims = (event.get('requestContext', {}) or {}).get('authorizer', {}).get('claims', {}) or {}
    return claims.get('sub') or ''


def is_admin(event) -> bool:
    """Cognito グループに admin が含まれるか（サーバー側必須。UI ガードだけでは不十分）。"""
    claims = (event.get('requestContext', {}) or {}).get('authorizer', {}).get('claims', {}) or {}
    groups = claims.get('cognito:groups', '')
    if isinstance(groups, list):
        group_list = [str(g).strip() for g in groups if str(g).strip()]
    else:
        group_list = [g.strip() for g in str(groups).split(',') if g.strip()]
    return ADMIN_GROUP_NAME in group_list


def owns_session(session_id: str, user_id: str) -> bool:
    """session_id が user_id のものであるかを判定する。

    chatlogs テーブルは PK=sessionId / SK=messageId で、各アイテムが userId を
    持つ。同一セッション内の userId は同じなので先頭 1 件で判定できる。
    存在しないセッションは False（呼び出し側で 404 に丸める）。
    """
    if not session_id or not user_id:
        return False
    try:
        response = chatlogs_table.query(
            KeyConditionExpression='sessionId = :sid',
            ExpressionAttributeValues={':sid': session_id},
            Limit=1
        )
    except ClientError as e:
        print(f"Error verifying session ownership: {e}")
        return False
    items = response.get('Items', [])
    return bool(items) and items[0].get('userId') == user_id


# Custom JSON encoder for Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def calculate_days_until_deletion(ttl: int) -> int:
    """Calculate days remaining until TTL deletion"""
    current_time = int(time.time())
    seconds_remaining = ttl - current_time
    days_remaining = max(0, seconds_remaining // (24 * 60 * 60))
    return days_remaining


SESSION_TITLE_MAX_LENGTH = 50


def build_session_title(content) -> str:
    """セッション一覧のタイトルをメッセージ本文から作る。

    機種未指定時に RAG が回答の先頭へ付ける注意書き（「※機種未指定のため…」）や
    Markdown の見出し記号をそのままタイトルにすると、どのセッションも同じ文字列になり
    履歴を判別できなくなるため取り除く。
    """
    text = (content or '').strip()

    # 先頭の注意書き段落（※ で始まる）は定型文なので落とす
    while text.startswith('※'):
        _, sep, rest = text.partition('\n\n')
        if not sep:
            _, sep, rest = text.partition('\n')
        if not sep:
            return 'Untitled'
        text = rest.strip()

    # Markdown の見出し・引用記号を落として素の文にする
    text = text.lstrip('#>*- \t')
    text = text.replace('**', '').strip()
    if not text:
        return 'Untitled'
    return text[:SESSION_TITLE_MAX_LENGTH]


def get_sessions_by_user(user_id: str, limit: int = 50, mode: str = None) -> list:
    """Get all sessions for a user"""
    try:
        messages = []
        matching_session_ids = set()
        exclusive_start_key = None
        while True:
            query = {
                'IndexName': 'userId-timestamp-index',
                'KeyConditionExpression': 'userId = :uid',
                # Hide logically-deleted messages (deleted flag null/false only)
                'FilterExpression': 'attribute_not_exists(#del) OR #del = :false',
                'ExpressionAttributeNames': {'#del': 'deleted'},
                'ExpressionAttributeValues': {':uid': user_id, ':false': False},
                'ScanIndexForward': False,
                'Limit': limit * 10,
            }
            if exclusive_start_key:
                query['ExclusiveStartKey'] = exclusive_start_key
            response = chatlogs_table.query(**query)
            page = response.get('Items', [])
            messages.extend(page)
            for message in page:
                session_id = message.get('sessionId')
                message_mode = message.get('ragMode') or 'normal'
                if (
                    session_id
                    and not str(session_id).startswith('wish-')
                    and (mode is None or message_mode == mode)
                ):
                    matching_session_ids.add(session_id)
            exclusive_start_key = response.get('LastEvaluatedKey')
            if not exclusive_start_key or len(matching_session_ids) >= limit:
                break
        
        # Group by sessionId and get session metadata
        sessions_dict = {}
        # タイトル採用済みメッセージの優先度（小さいほど優先）
        title_rank = {}
        for msg in messages:
            session_id = msg['sessionId']
            message_mode = msg.get('ragMode') or 'normal'
            if mode and message_mode != mode:
                continue
            # 改善要望（product_wish）はチャット履歴一覧に出さない
            if str(session_id).startswith('wish-'):
                continue
            timestamp = msg['timestamp']
            session = sessions_dict.get(session_id)
            if session is None:
                session = {
                    'sessionId': session_id,
                    'createdAt': timestamp,
                    'lastMessageTime': timestamp,
                    'messageCount': 0,
                    'title': 'Untitled',
                    'ttl': msg.get('ttl', 0),
                    'ragMode': message_mode,
                }
                sessions_dict[session_id] = session
                title_rank[session_id] = None

            session['messageCount'] += 1
            if timestamp > session['lastMessageTime']:
                session['lastMessageTime'] = timestamp
            if timestamp < session['createdAt']:
                session['createdAt'] = timestamp
            # 残り日数は最後のメッセージが消えるまで（= 最大 TTL）で示す
            if msg.get('ttl', 0) > session['ttl']:
                session['ttl'] = msg.get('ttl', 0)

            # タイトルは RAG が最初のやりとりで生成した sessionTitle を最優先で使う。
            # 無い場合（生成前の既存セッション・生成失敗時）はそのセッションの
            # 「最初のユーザー質問」を使う。直近メッセージ（多くは AI 回答）を使うと、
            # 機種未指定の注意書きで一覧が埋まる。
            stored_title = str(msg.get('sessionTitle') or '').strip()
            # rank: 0=生成済み見出し / 1=ユーザー発言 / 2=それ以外、同順位なら古い方
            if stored_title:
                rank = (0, timestamp)
            else:
                rank = (1 if msg.get('role') == 'user' else 2, timestamp)
            if title_rank[session_id] is None or rank < title_rank[session_id]:
                title_rank[session_id] = rank
                session['title'] = (
                    stored_title[:SESSION_TITLE_MAX_LENGTH]
                    if stored_title
                    else build_session_title(msg.get('content'))
                )
        
        # Convert to list and calculate days until deletion
        sessions = list(sessions_dict.values())
        for session in sessions:
            session['daysUntilDeletion'] = calculate_days_until_deletion(session['ttl'])
        
        # Sort by last message time (newest first)
        sessions.sort(key=lambda x: x['lastMessageTime'], reverse=True)
        
        return sessions[:limit]
        
    except ClientError as e:
        print(f"Error getting sessions: {e}")
        raise


def get_session_messages(session_id: str, limit: int = 100, fetch_all: bool = False) -> list:
    """Get messages in a session (excludes logically deleted).

    DynamoDB Limit applies before FilterExpression, so we page until we have
    enough visible rows (or the query is exhausted when fetch_all=True).
    """
    try:
        collected = []
        exclusive_start = None
        target = None if fetch_all else max(1, int(limit))

        while True:
            page_limit = 100
            if target is not None:
                page_limit = min(100, max(20, (target - len(collected)) * 2))
            kwargs = {
                'KeyConditionExpression': 'sessionId = :sid',
                'FilterExpression': (
                    '(attribute_not_exists(#del) OR #del = :false) '
                    'AND (attribute_not_exists(#role) OR #role <> :wish)'
                ),
                'ExpressionAttributeNames': {'#del': 'deleted', '#role': 'role'},
                'ExpressionAttributeValues': {
                    ':sid': session_id,
                    ':false': False,
                    ':wish': 'product_wish',
                },
                'ScanIndexForward': True,
                'Limit': page_limit,
            }
            if exclusive_start:
                kwargs['ExclusiveStartKey'] = exclusive_start

            response = chatlogs_table.query(**kwargs)
            collected.extend(response.get('Items') or [])
            exclusive_start = response.get('LastEvaluatedKey')

            if not exclusive_start:
                break
            if target is not None and len(collected) >= target:
                break

        messages = collected if fetch_all else collected[:target]

        for msg in messages:
            if 'ttl' in msg:
                msg['daysUntilDeletion'] = calculate_days_until_deletion(msg['ttl'])

        return messages

    except ClientError as e:
        print(f"Error getting messages: {e}")
        raise



def delete_session(session_id: str) -> int:
    """Logically delete all messages in a session (soft delete).

    Sets a `deleted` flag instead of removing the item, so the conversation is
    hidden from the user (and cannot be restored via the UI) while the data is
    retained for internal analysis. Physical removal is handled by TTL, and the
    DynamoDB stream archives every change (including this flag) to S3.
    """
    try:
        # Only the currently-visible (not-yet-deleted) messages
        messages = get_session_messages(session_id, fetch_all=True)

        now_iso = datetime.utcnow().isoformat() + 'Z'
        deleted_count = 0
        for msg in messages:
            chatlogs_table.update_item(
                Key={
                    'sessionId': session_id,
                    'messageId': msg['messageId']
                },
                UpdateExpression='SET #del = :true, deletedAt = :ts',
                ExpressionAttributeNames={'#del': 'deleted'},
                ExpressionAttributeValues={':true': True, ':ts': now_iso}
            )
            deleted_count += 1

        return deleted_count

    except ClientError as e:
        print(f"Error deleting session: {e}")
        raise


def update_message_feedback(
    session_id: str,
    message_id: str,
    feedback: str,
    reason: str = None,
    comment: str = None,
) -> bool:
    """Update message feedback (thumbs up/down).

    bad のとき任意で reason / comment を付ける（ワンタップ分類用）。
    good のときは理由フィールドを消して残滓を残さない。
    存在しない / assistant 以外の messageId は ConditionalCheckFailed → False。
    """
    try:
        names = {'#role': 'role'}
        values = {
            ':feedback': feedback,
            ':assistant': 'assistant',
        }
        parts = ['feedback = :feedback', 'feedbackAt = :at']
        values[':at'] = datetime.utcnow().isoformat() + 'Z'
        condition = (
            'attribute_exists(sessionId) AND attribute_exists(messageId) '
            'AND #role = :assistant'
        )

        if feedback == 'bad':
            if reason:
                parts.append('feedbackReason = :reason')
                values[':reason'] = reason
            if comment:
                parts.append('feedbackComment = :comment')
                values[':comment'] = comment[:FEEDBACK_COMMENT_MAX]
            kwargs = {
                'Key': {'sessionId': session_id, 'messageId': message_id},
                'UpdateExpression': 'SET ' + ', '.join(parts),
                'ConditionExpression': condition,
                'ExpressionAttributeValues': values,
                'ExpressionAttributeNames': names,
            }
        else:
            names['#fr'] = 'feedbackReason'
            names['#fc'] = 'feedbackComment'
            expr = 'SET ' + ', '.join(parts) + ' REMOVE #fr, #fc'
            kwargs = {
                'Key': {'sessionId': session_id, 'messageId': message_id},
                'UpdateExpression': expr,
                'ConditionExpression': condition,
                'ExpressionAttributeValues': values,
                'ExpressionAttributeNames': names,
            }

        chatlogs_table.update_item(**kwargs)
        return True

    except ClientError as e:
        if e.response.get('Error', {}).get('Code') == 'ConditionalCheckFailedException':
            return False
        print(f"Error updating feedback: {e}")
        raise


def _session_user_query_before(session_id: str, assistant_ts: str, cache: dict) -> str:
    """同一セッションで、assistant の直前 user 文を返す（失敗一覧用）。"""
    if session_id not in cache:
        try:
            msgs = get_session_messages(session_id, limit=200)
        except ClientError:
            msgs = []
        cache[session_id] = msgs
    prev = ''
    for msg in cache[session_id]:
        ts = msg.get('timestamp') or ''
        if ts >= assistant_ts:
            break
        if msg.get('role') == 'user':
            prev = (msg.get('content') or '').strip()
    return prev


def list_failure_messages(kind: str = 'all', limit: int = FAILURES_DEFAULT_LIMIT) -> dict:
    """admin 用: bad フィードバックと not_found を新しい順に返す。

    chatlogs は GSI が失敗専用ではないため Scan + Filter。
    試用初期のホットウィンドウ（TTL 約60日）向け。大規模化したら Athena へ移す。
    """
    limit = max(1, min(int(limit or FAILURES_DEFAULT_LIMIT), FAILURES_HARD_LIMIT))
    kind = (kind or 'all').lower()
    if kind not in ('all', 'bad', 'not_found'):
        kind = 'all'

    # role=assistant かつ (feedback=bad OR responseType=not_found)、未削除
    filter_parts = [
        '#role = :assistant',
        '(attribute_not_exists(#del) OR #del = :false)',
    ]
    values = {
        ':assistant': 'assistant',
        ':false': False,
        ':bad': 'bad',
        ':not_found': 'not_found',
    }
    names = {'#role': 'role', '#del': 'deleted', '#rt': 'responseType'}

    if kind == 'bad':
        filter_parts.append('feedback = :bad')
    elif kind == 'not_found':
        filter_parts.append('#rt = :not_found')
    else:
        filter_parts.append('(feedback = :bad OR #rt = :not_found)')

    collected = []
    exclusive_start = None
    pages = 0
    scanned_count = 0

    while pages < FAILURES_SCAN_MAX_PAGES:
        kwargs = {
            'FilterExpression': ' AND '.join(filter_parts),
            'ExpressionAttributeNames': names,
            'ExpressionAttributeValues': values,
            'Limit': 100,
        }
        if exclusive_start:
            kwargs['ExclusiveStartKey'] = exclusive_start
        resp = chatlogs_table.scan(**kwargs)
        pages += 1
        scanned_count += int(resp.get('ScannedCount') or 0)
        collected.extend(resp.get('Items') or [])
        exclusive_start = resp.get('LastEvaluatedKey')
        if not exclusive_start:
            break

    incomplete = bool(exclusive_start)
    collected.sort(key=lambda x: x.get('timestamp') or '', reverse=True)
    collected = collected[:limit]

    session_cache = {}
    failures = []
    for item in collected:
        ts = item.get('timestamp') or ''
        session_id = item.get('sessionId') or ''
        user_query = _session_user_query_before(session_id, ts, session_cache)
        candidates = item.get('pageCandidates') or []
        top_docs = []
        for c in candidates[:5]:
            name = c.get('documentName') or c.get('name') or ''
            if name:
                top_docs.append(name)
        if not top_docs:
            for d in (item.get('sourceDocuments') or [])[:5]:
                name = d.get('documentName') or ''
                if name:
                    top_docs.append(name)

        signal = []
        if item.get('feedback') == 'bad':
            signal.append('bad')
        if item.get('responseType') == 'not_found':
            signal.append('not_found')

        failures.append({
            'sessionId': session_id,
            'messageId': item.get('messageId'),
            'timestamp': ts,
            'signals': signal,
            'ragMode': item.get('ragMode') or 'normal',
            'responseType': item.get('responseType'),
            'feedback': item.get('feedback'),
            'feedbackReason': item.get('feedbackReason'),
            'feedbackComment': item.get('feedbackComment'),
            'userQuery': user_query,
            'queryFilters': item.get('queryFilters') or {},
            'topDocuments': top_docs,
            'assistantPreview': ((item.get('content') or '')[:120]),
        })

    return {
        'failures': failures,
        'count': len(failures),
        'scannedCount': scanned_count,
        'incomplete': incomplete,
        'kind': kind,
        'note': (
            'hot window (TTL〜60日)。Scan ベースのため件数増で遅くなる場合は Athena へ移行。'
            + ((' Scan 打ち切りのため一部が欠けています（Scan はハッシュ順のため'
                '欠けるのは最新分とは限りません）。') if incomplete else '')
        ),
    }


def save_product_wish(user_id: str, text: str, context_session_id: str = None) -> dict:
    """利用者の「こうなってほしい」自由記述を chatlogs に保存（role=product_wish）。"""
    text = (text or '').strip()
    if not text:
        raise ValueError('text is required')
    if len(text) > WISH_TEXT_MAX:
        raise ValueError(f'text must be at most {WISH_TEXT_MAX} characters')

    now = datetime.utcnow().isoformat() + 'Z'
    ttl = int(time.time()) + (60 * 24 * 60 * 60)
    message_id = f'wish-{int(time.time() * 1000)}'
    session_id = f'wish-{user_id}'

    item = {
        'sessionId': session_id,
        'messageId': message_id,
        'userId': user_id,
        'role': 'product_wish',
        'content': text,
        'timestamp': now,
        'ttl': ttl,
    }
    if context_session_id:
        item['contextSessionId'] = context_session_id

    chatlogs_table.put_item(Item=item)
    return {'messageId': message_id, 'timestamp': now}


def list_product_wishes(limit: int = FAILURES_DEFAULT_LIMIT) -> dict:
    """admin 用: product_wish を新しい順に返す（Scan + Filter）。"""
    limit = max(1, min(int(limit or FAILURES_DEFAULT_LIMIT), FAILURES_HARD_LIMIT))
    filter_expr = '#role = :wish AND (attribute_not_exists(#del) OR #del = :false)'
    names = {'#role': 'role', '#del': 'deleted'}
    values = {':wish': 'product_wish', ':false': False}

    collected = []
    exclusive_start = None
    pages = 0
    scanned_count = 0

    while pages < FAILURES_SCAN_MAX_PAGES:
        kwargs = {
            'FilterExpression': filter_expr,
            'ExpressionAttributeNames': names,
            'ExpressionAttributeValues': values,
            'Limit': 100,
        }
        if exclusive_start:
            kwargs['ExclusiveStartKey'] = exclusive_start
        resp = chatlogs_table.scan(**kwargs)
        pages += 1
        scanned_count += int(resp.get('ScannedCount') or 0)
        collected.extend(resp.get('Items') or [])
        exclusive_start = resp.get('LastEvaluatedKey')
        if not exclusive_start:
            break

    incomplete = bool(exclusive_start)
    collected.sort(key=lambda x: x.get('timestamp') or '', reverse=True)
    collected = collected[:limit]

    wishes = []
    for item in collected:
        wishes.append({
            'messageId': item.get('messageId'),
            'userId': item.get('userId'),
            'text': item.get('content') or '',
            'timestamp': item.get('timestamp'),
            'contextSessionId': item.get('contextSessionId'),
        })

    return {
        'wishes': wishes,
        'count': len(wishes),
        'scannedCount': scanned_count,
        'incomplete': incomplete,
        'note': 'hot window (TTL〜60日)。Scan ベース。',
    }


def lambda_handler(event, context):
    """
    Handle chat management operations
    
    Routes:
    - GET /chat/sessions - List user sessions
    - GET /chat/sessions/{sessionId} - Get session details
    - DELETE /chat/sessions/{sessionId} - Delete session
    - GET /chat/sessions/{sessionId}/messages - Get session messages
    - PUT /chat/messages/{messageId}/feedback - Update message feedback
    - GET /chat/admin/failures - List bad / not_found (admin only)
    - POST /chat/suggestions - Submit product wish (authenticated user)
    - GET /chat/admin/suggestions - List product wishes (admin only)
    """
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Get route info
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method'))
        path = event.get('path', event.get('rawPath', ''))
        path_parameters = event.get('pathParameters', {})
        query_parameters = event.get('queryStringParameters', {}) or {}
        
        # Parse body if present
        body = {}
        if event.get('body'):
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']

        # 呼び出し元は必ず検証済みクレームから決める（クライアント申告値は使わない）
        caller_id = get_caller_id(event)
        if not caller_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Unauthorized',
                    'message': 'Authentication required'
                })
            }

        # 他人のセッションを指す要求は、存在有無を漏らさないよう一律 404 に丸める
        not_found = {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({
                'error': 'NotFound',
                'message': 'Session not found'
            })
        }

        # Route: GET /chat/sessions - List user sessions
        if http_method == 'GET' and path == '/chat/sessions':
            # userId クエリパラメータは廃止。自分のセッションのみ返す。
            requested_mode = query_parameters.get('mode')
            if requested_mode not in (None, 'normal', 'law'):
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'ValidationError',
                        'message': 'Unsupported session mode',
                    }),
                }
            sessions = get_sessions_by_user(caller_id, mode=requested_mode)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'sessions': sessions}, cls=DecimalEncoder, ensure_ascii=False)
            }
        
        # Route: GET /chat/sessions/{sessionId}/messages - Get session messages
        elif http_method == 'GET' and '/messages' in path:
            session_id = path_parameters.get('sessionId')
            
            if not session_id:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'ValidationError',
                        'message': 'sessionId is required'
                    })
                }

            # admin は PDCA（失敗一覧からの照合）のため他ユーザーのセッションも
            # 「読み取りのみ」許可する。書き込み系（RAG 送信・削除・feedback）は
            # 従来どおり所有者限定のまま。
            is_owner = owns_session(session_id, caller_id)
            if not is_owner and not is_admin(event):
                return not_found

            messages = get_session_messages(session_id)
            requested_mode = query_parameters.get('mode')
            if requested_mode not in (None, 'normal', 'law'):
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'ValidationError',
                        'message': 'Unsupported session mode',
                    }),
                }
            session_modes = {
                message.get('ragMode') or 'normal'
                for message in messages
                if message.get('role') in ('user', 'assistant')
            }
            if requested_mode and session_modes and session_modes != {requested_mode}:
                return {
                    'statusCode': 409,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'SessionModeMismatch',
                        'message': 'このチャットモードでは既存セッションを開けません',
                    }, ensure_ascii=False),
                }

            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(
                    {'messages': messages, 'readOnly': not is_owner},
                    cls=DecimalEncoder, ensure_ascii=False)
            }
        
        # Route: DELETE /chat/sessions/{sessionId} - Delete session
        elif http_method == 'DELETE' and path_parameters.get('sessionId'):
            session_id = path_parameters.get('sessionId')

            if not owns_session(session_id, caller_id):
                return not_found

            deleted_count = delete_session(session_id)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': f'Session deleted successfully',
                    'deletedCount': deleted_count
                })
            }
        
        # Route: PUT /chat/messages/{messageId}/feedback - Update feedback
        elif http_method == 'PUT' and '/feedback' in path:
            message_id = path_parameters.get('messageId')
            session_id = body.get('sessionId')
            feedback = body.get('feedback')
            reason = body.get('reason') or body.get('feedbackReason')
            comment = body.get('comment') or body.get('feedbackComment')
            
            if not all([message_id, session_id, feedback]):
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'ValidationError',
                        'message': 'messageId, sessionId, and feedback are required'
                    })
                }
            
            if feedback not in ['good', 'bad']:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'ValidationError',
                        'message': 'feedback must be "good" or "bad"'
                    })
                }

            if reason is not None and reason != '':
                if feedback != 'bad':
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'error': 'ValidationError',
                            'message': 'reason is only allowed with feedback=bad'
                        })
                    }
                if reason not in FEEDBACK_REASONS:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'error': 'ValidationError',
                            'message': f'reason must be one of: {", ".join(sorted(FEEDBACK_REASONS))}'
                        })
                    }
            else:
                reason = None

            if comment is not None and not isinstance(comment, str):
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'ValidationError',
                        'message': 'comment must be a string'
                    })
                }
            if isinstance(comment, str):
                comment = comment.strip() or None

            if not owns_session(session_id, caller_id):
                return not_found

            updated = update_message_feedback(
                session_id, message_id, feedback, reason=reason, comment=comment
            )
            if not updated:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'NotFound',
                        'message': 'Message not found'
                    })
                }
            emit_feedback_metric(feedback)

            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Feedback updated successfully'
                })
            }

        # Route: GET /chat/admin/failures - bad / not_found 一覧（admin のみ）
        elif http_method == 'GET' and path.rstrip('/').endswith('/chat/admin/failures'):
            if not is_admin(event):
                return {
                    'statusCode': 403,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Forbidden',
                        'message': 'Admin privileges required'
                    })
                }
            kind = query_parameters.get('kind') or 'all'
            try:
                limit = int(query_parameters.get('limit') or FAILURES_DEFAULT_LIMIT)
            except (TypeError, ValueError):
                limit = FAILURES_DEFAULT_LIMIT
            payload = list_failure_messages(kind=kind, limit=limit)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(payload, cls=DecimalEncoder, ensure_ascii=False)
            }

        # Route: POST /chat/suggestions - 利用者の「こうなってほしい」
        elif http_method == 'POST' and path.rstrip('/').endswith('/chat/suggestions'):
            text = (body.get('text') or body.get('content') or '').strip()
            context_session_id = body.get('sessionId') or body.get('contextSessionId')
            if context_session_id and not owns_session(context_session_id, caller_id):
                context_session_id = None
            try:
                saved = save_product_wish(caller_id, text, context_session_id)
            except ValueError as ve:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'ValidationError',
                        'message': str(ve),
                    }),
                }
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Suggestion received',
                    **saved,
                }, ensure_ascii=False),
            }

        # Route: GET /chat/admin/suggestions - admin の改善要望一覧
        elif http_method == 'GET' and path.rstrip('/').endswith('/chat/admin/suggestions'):
            if not is_admin(event):
                return {
                    'statusCode': 403,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Forbidden',
                        'message': 'Admin privileges required',
                    }),
                }
            try:
                limit = int(query_parameters.get('limit') or FAILURES_DEFAULT_LIMIT)
            except (TypeError, ValueError):
                limit = FAILURES_DEFAULT_LIMIT
            payload = list_product_wishes(limit=limit)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(payload, cls=DecimalEncoder, ensure_ascii=False),
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    'error': 'NotFound',
                    'message': 'Route not found'
                })
            }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': error_code,
                'message': error_message
            })
        }
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'InternalServerError',
                'message': 'An unexpected error occurred'
            })
        }
