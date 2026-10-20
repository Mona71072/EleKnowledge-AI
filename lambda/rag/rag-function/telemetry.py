"""rag Lambda の運用テレメトリ（設計: docs/design-2026-09-10-dashboard-v2.md §4.3 I2 / I3、別立て B2）。

- 1 リクエスト 1 行の構造化ログ（本文・質問文は出さない。AGENTS.md「ログと秘匿」）
- 500 経路の構造化エラー行と、利用者へ返す本文の一般化（AWS のエラーメッセージをそのまま返さない）
- 引用文書を開いた回数を assistant 行に加算（documentOpens / lastOpenedAt）→ 到達ファネル「資料を開いた」
- 言い換えの印（reformulatedAt）を直前の assistant 行に付ける → 暗黙の失敗信号
- 全イベント行の共通項目と errorFingerprint（契約: docs/features/development/rag-observability-contract.md）

どの関数も例外を外に出さない（テレメトリで本処理を止めない）。
"""
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone

from botocore.exceptions import ClientError

# 回答から次の質問までがこの秒数以内なら「言い換え」とみなす
REFORMULATION_WINDOW_SEC = 600

# ログ行の版。共通項目の意味や型を変えたら上げる（契約 §イベント契約）
SCHEMA_VERSION = 1

# errorFingerprint として記録する SHA-256 の先頭文字数（契約 §エラー指紋）
FINGERPRINT_LENGTH = 16

# botocore の operation_name → 失敗した段階
_STAGE_BY_OPERATION = {
    'Retrieve': 'retrieve',
    'InvokeModel': 'generate',
    'InvokeModelWithResponseStream': 'generate',
    'Converse': 'generate',
    'PutItem': 'save',
    'UpdateItem': 'save',
    'Query': 'history',
    'GetItem': 'history',
    'GetObject': 'document',
}

GENERIC_500_MESSAGE = '処理に失敗しました。時間をおいて再度お試しください。'


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _parse_ts(value):
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def request_id_of(event) -> str:
    """API Gateway のリクエスト ID（アクセスログの requestId と同じ値）。"""
    return ((event or {}).get('requestContext') or {}).get('requestId') or ''


def route_of(event) -> str:
    """API Gateway のリソースパス（/rag/query など）。パスパラメータや実 URL は含まれない。"""
    context = (event or {}).get('requestContext') or {}
    return context.get('resourcePath') or (event or {}).get('resource') or ''


def elapsed_ms(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def rag_logic_version() -> str:
    return os.environ.get('RAG_LOGIC_VERSION') or 'unknown'


def common_fields(event_name: str, *, request_id: str = '', route: str = '',
                  status_code: int | None = None, started_at: float | None = None) -> dict:
    """全イベント行に付く共通項目。HTTP 応答が決まる前の行は statusCode を null にする。"""
    return {
        'schemaVersion': SCHEMA_VERSION,
        'event': event_name,
        'requestId': request_id or '',
        'route': route or '',
        'statusCode': status_code,
        'latencyMs': elapsed_ms(started_at) if started_at is not None else None,
        'ragLogicVersion': rag_logic_version(),
    }


def stage_of(error: Exception) -> str:
    op = getattr(error, 'operation_name', '') or ''
    return _STAGE_BY_OPERATION.get(op, 'unknown')


def _exception_label(error: Exception) -> str:
    label = type(error).__name__
    if isinstance(error, ClientError):
        error_data = getattr(error, 'response', {}).get('Error', {})
        code = error_data.get('Code')
        if code:
            return f'{label} code={code}'
    return label


def error_fingerprint(stage: str, exception_class: str, error_code: str) -> str:
    """同一原因を集約するための指紋。段階・例外の型・エラーコードの SHA-256 の先頭 16 文字。

    入力は運用上の固定値だけで、利用者のデータ・例外の文面・ID は含まない（鍵も使わない）。
    よって同じ原因なら文面が違っても同じ値になる。
    """
    message = '|'.join(str(part or '').strip() for part in (stage, exception_class, error_code))
    return hashlib.sha256(message.encode('utf-8')).hexdigest()[:FINGERPRINT_LENGTH]


def _emit(payload: dict) -> None:
    try:
        print(json.dumps(payload, ensure_ascii=False, default=str))
    except Exception as e:  # noqa: BLE001
        print(f"[telemetry] emit failed: {_exception_label(e)}")


def log_request(event, response: dict, started_at: float) -> None:
    """成功・失敗を問わず 1 リクエスト 1 行。本文は出さず、件数と ID だけ。"""
    try:
        status = int((response or {}).get('statusCode') or 0)
        body = {}
        if status == 200 and (response or {}).get('body'):
            try:
                body = json.loads(response['body'])
            except (TypeError, ValueError):
                body = {}
        method = (event or {}).get('httpMethod') or ''
        if method == 'GET':
            return  # 文書解決は document_open で別に出す
        _emit({
            **common_fields('rag_request', request_id=request_id_of(event), route=route_of(event),
                            status_code=status, started_at=started_at),
            'responseType': body.get('responseType'),
            'pageCandidates': len(body.get('pageCandidates') or []),
            'sourceDocuments': len(body.get('sourceDocuments') or []),
            'priorityExpanded': body.get('priorityExpanded'),
        })
    except Exception as e:  # noqa: BLE001
        print(f"[telemetry] log_request failed: {_exception_label(e)}")


def error_response(headers: dict, error: Exception, started_at: float, event) -> dict:
    """500 の構造化エラー行を出し、利用者には一般化した本文と requestId だけを返す。"""
    request_id = request_id_of(event)
    exception_class = type(error).__name__
    if isinstance(error, ClientError):
        err = error.response.get('Error', {}) if hasattr(error, 'response') else {}
        code = err.get('Code') or 'ClientError'
        stage = stage_of(error)
    else:
        code = exception_class or 'InternalServerError'
        stage = 'unknown'
    _emit({
        **common_fields('rag_error', request_id=request_id, route=route_of(event),
                        status_code=500, started_at=started_at),
        'stage': stage,
        'errorCode': code,
        'exceptionClass': exception_class,
        'errorFingerprint': error_fingerprint(stage, exception_class, code),
    })
    return {
        'statusCode': 500,
        'headers': headers,
        'body': json.dumps({
            'error': 'InternalServerError',
            'message': GENERIC_500_MESSAGE,
            'requestId': request_id,
        }, ensure_ascii=False),
    }


def record_document_open(table, session_id: str, message_id: str, user_id: str, owns_session, doc_uri: str,
                         event=None, started_at: float | None = None) -> bool:
    """引用文書を開いた回答（assistant 行）に documentOpens を加算する。

    /doc?uri=…&s=<sessionId>&m=<messageId> から GET /rag/document?uri=&s=&m= で渡される。
    他人のセッションの行は触らない（owns_session で検証）。失敗しても文書の解決は止めない。
    """
    if not (session_id and message_id and user_id):
        return False
    try:
        if not owns_session(session_id, user_id):
            return False
        table.update_item(
            Key={'sessionId': session_id, 'messageId': message_id},
            UpdateExpression='ADD documentOpens :one SET lastOpenedAt = :now',
            ConditionExpression='attribute_exists(messageId) AND #role = :assistant',
            ExpressionAttributeNames={'#role': 'role'},
            ExpressionAttributeValues={':one': 1, ':now': _now_iso(), ':assistant': 'assistant'},
        )
    except ClientError as e:
        if e.response.get('Error', {}).get('Code') != 'ConditionalCheckFailedException':
            print(f"[telemetry] document_open update failed: {_exception_label(e)}")
        return False
    except Exception as e:  # noqa: BLE001
        print(f"[telemetry] document_open failed: {_exception_label(e)}")
        return False
    _emit({
        **common_fields('document_open', request_id=request_id_of(event), route=route_of(event),
                        status_code=200, started_at=started_at),
        'documentName': (doc_uri or '').rsplit('/', 1)[-1],
    })
    return True


def stamp_reformulation(table, chat_history: list, now: datetime | None = None,
                        event=None, started_at: float | None = None) -> bool:
    """新しい質問が来たとき、直前の回答が「候補あり」で、評価が無く、回答から 10 分以内なら reformulatedAt を付ける。

    chat_history は古い順（get_chat_history の戻り値）。集計側は reformulatedAt があり、👍 も資料クリックも無い行を
    「言い換え」として数える（後から 👍 や資料クリックが付けば数えない）。
    """
    if not chat_history:
        return False
    last = chat_history[-1]
    if last.get('role') != 'assistant' or last.get('responseType') != 'pages':
        return False
    if last.get('feedback') or last.get('reformulatedAt'):
        return False
    answered_at = _parse_ts(last.get('timestamp'))
    now = now or datetime.now(timezone.utc)
    if not answered_at or now - answered_at > timedelta(seconds=REFORMULATION_WINDOW_SEC):
        return False
    try:
        table.update_item(
            Key={'sessionId': last.get('sessionId'), 'messageId': last.get('messageId')},
            UpdateExpression='SET reformulatedAt = :now',
            ConditionExpression='attribute_exists(messageId) AND attribute_not_exists(reformulatedAt)',
            ExpressionAttributeValues={':now': now.isoformat().replace('+00:00', 'Z')},
        )
    except ClientError as e:
        if e.response.get('Error', {}).get('Code') != 'ConditionalCheckFailedException':
            print(f"[telemetry] reformulation update failed: {_exception_label(e)}")
        return False
    except Exception as e:  # noqa: BLE001
        print(f"[telemetry] reformulation failed: {_exception_label(e)}")
        return False
    _emit(common_fields('reformulation', request_id=request_id_of(event), route=route_of(event),
                        status_code=None, started_at=started_at))
    return True
