"""POST /rag/senpai/research（受付）と GET /rag/senpai/research/{jobId}（進捗）。

開発環境・管理者限定の試作。受付 Lambda は軽く保ち、重い処理（検索・生成）は別の
ワーカー Lambda を非同期起動して行う。この関数は Bedrock・ナレッジベースを呼ばない。
契約: docs/features/development/senpai-research-contract.md
"""
import json
import re
import time
import uuid

import boto3
from botocore.config import Config

import senpai_research_config as config
import senpai_research_http as http
import senpai_research_store as store

ALLOWED_BODY_KEYS = frozenset({
    'question', 'senpaiConversationId', 'senpaiTurnId', 'clientRequestId', 'modelType',
})
REQUIRED_BODY_KEYS = ('question', 'senpaiConversationId', 'senpaiTurnId', 'clientRequestId')
AFTER_SEQ_PATTERN = re.compile(r'^[0-9]{1,9}$')
INVALID_REQUEST_MESSAGE = '質問と相談の識別情報を確認してください'
NOT_FOUND = ('JobNotFound', '調査が見つかりません')

_cache = {}


def now() -> float:
    return time.time()


def _log(stage: str, status: str, error: Exception = None, job_id: str = None) -> None:
    # SECURITY: 段階名・例外クラス・jobId（UUID。本文ではない）だけ。質問・回答・userId・トークンは出さない。
    record = {'event': 'senpai_research_api', 'stage': stage, 'status': status}
    if job_id:
        record['jobId'] = job_id
    if error is not None:
        record['errorClass'] = type(error).__name__
    print(json.dumps(record, separators=(',', ':')))


def get_store() -> store.JobStore:
    if 'store' not in _cache:
        table = boto3.resource('dynamodb').Table(config.table_name())
        _cache['store'] = store.JobStore(table)
    return _cache['store']


def invoke_worker(job_id: str) -> None:
    """ワーカーを非同期（Event）で起動する。ペイロードは jobId だけ（質問は載せない）。"""
    if 'lambda' not in _cache:
        _cache['lambda'] = boto3.client(
            'lambda',
            config=Config(connect_timeout=2, read_timeout=5, retries={'total_max_attempts': 2}),
        )
    _cache['lambda'].invoke(
        FunctionName=config.worker_function_name(),
        InvocationType='Event',
        Payload=json.dumps({'jobId': job_id}).encode('utf-8'),
    )


def _canonical_uuid(value) -> bool:
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def parse_request(event: dict):
    """本文を検証して要求 dict を返す。不正なら None。"""
    raw = event.get('body')
    try:
        body = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return None
    if not isinstance(body, dict) or not set(body) <= ALLOWED_BODY_KEYS:
        return None
    if not all(key in body for key in REQUIRED_BODY_KEYS):
        return None
    question = body['question']
    if not isinstance(question, str) or not question.strip():
        return None
    question = question.strip()
    if len(question) > config.QUESTION_MAX_CHARS:
        return None
    if not all(_canonical_uuid(body[key]) for key in REQUIRED_BODY_KEYS[1:]):
        return None
    model_type = body.get('modelType')
    if model_type is not None and model_type not in config.UI_MODEL_TYPES:
        return None
    return {
        'question': question,
        'modelType': model_type,
        'senpaiConversationId': body['senpaiConversationId'],
        'senpaiTurnId': body['senpaiTurnId'],
        'clientRequestId': body['clientRequestId'],
    }


def _accepted(job_id: str, status: str) -> dict:
    return http.respond(202, {'jobId': job_id, 'status': status, 'pollAfterMs': config.POLL_AFTER_MS})


def _undo_reservation(job_store, user_id: str, request: dict, *, lock_job_id: str = None,
                      slot_day: str = None) -> None:
    """途中で断った要求が、ロック・日次枠・二重送信登録を残さないようにする。

    slot_day は日次枠を取った日。指定したときだけ、その日の枠を返す。
    """
    if slot_day:
        job_store.return_daily_slot(user_id, slot_day)
    if lock_job_id:
        job_store.release_lock(user_id, lock_job_id)
    job_store.release_request(user_id, request['clientRequestId'])


def _claim_or_replay(job_store, user_id: str, request: dict, job_id: str):
    """二重送信の登録。登録済みで job 行も在れば (既存 jobId, 状態)、無ければ登録し直して None を返す。"""
    for _attempt in range(2):
        existing_id, created = job_store.claim_request(user_id, request['clientRequestId'], job_id)
        if created:
            return None
        existing = job_store.get_job(existing_id)
        if existing is not None:
            return existing_id, existing['status']
        # 登録だけが残り、ジョブ行が無い（前回の受付が途中で落ちた）。登録を外して作り直す。
        job_store.release_request(user_id, request['clientRequestId'])
    raise RuntimeError('request replay raced twice')


def _create(event: dict, user_id: str) -> dict:
    request = parse_request(event)
    if request is None:
        return http.error(400, 'ValidationError', INVALID_REQUEST_MESSAGE)
    job_store = get_store()
    job_id = str(uuid.uuid4())
    replay = _claim_or_replay(job_store, user_id, request, job_id)
    if replay is not None:
        return _accepted(*replay)
    if not job_store.acquire_lock(user_id, job_id, config.job_ttl_seconds()):
        _undo_reservation(job_store, user_id, request)
        return http.error(409, 'JobInProgress', '前の調査が実行中です。完了してからお試しください')
    day = job_store.daily_day()
    if not job_store.take_daily_slot(user_id, config.daily_limit(), day):
        _undo_reservation(job_store, user_id, request, lock_job_id=job_id)
        return http.error(429, 'DailyLimitExceeded', '本日の調査回数の上限に達しました')
    try:
        job_store.create_job(store.build_job_item(
            job_id, user_id, request, now=now(), ttl_seconds=config.job_ttl_seconds(), daily_day=day
        ))
    except Exception:
        # ジョブ行を作れなかった要求は、ロック・日次枠・登録を残さない（再送で作り直せる）。
        _undo_reservation(job_store, user_id, request, lock_job_id=job_id, slot_day=day)
        raise
    try:
        invoke_worker(job_id)
    except Exception as error:  # noqa: BLE001 - 失敗は利用者に一般化して返す
        _log('invoke_worker', 'error', error, job_id)
        job_store.fail_job(job_id, 'Internal', '調査を開始できませんでした。時間をおいて再度お試しください')
        _undo_reservation(job_store, user_id, request, lock_job_id=job_id, slot_day=day)
        return http.error(502, 'StartFailed', '調査を開始できませんでした。時間をおいて再度お試しください')
    _log('create', 'ok', job_id=job_id)
    return _accepted(job_id, 'queued')


def build_status_payload(job: dict, *, after_seq: int, include_debug: bool) -> dict:
    """GET の応答。段階イベントは afterSeq より新しいものだけ。"""
    status = job['status']
    active = status in config.ACTIVE_STATUSES
    payload = {
        'jobId': job['jobId'],
        'status': status,
        'steps': sorted(
            (step for step in job.get('steps') or [] if step['seq'] > after_seq),
            key=lambda step: step['seq'],
        ),
        'pollAfterMs': config.POLL_AFTER_MS if active else 0,
    }
    if status == 'completed':
        payload['result'] = job.get('result') or {}
    if status == 'failed':
        payload['error'] = job.get('error') or {'code': 'Internal', 'message': '調査に失敗しました'}
    if include_debug and job.get('debug'):
        payload['debug'] = job['debug']
    return payload


def _parse_after_seq(event: dict):
    params = event.get('queryStringParameters') or {}
    if 'afterSeq' not in params:
        return 0
    raw = params['afterSeq']
    if not isinstance(raw, str) or not AFTER_SEQ_PATTERN.fullmatch(raw):
        return None
    return int(raw)


def _expire_if_stale(job_store, job: dict) -> dict:
    """期限切れの進行中ジョブは Timeout で終わらせ、ロックを外す（残さない）。"""
    if job['status'] in config.ACTIVE_STATUSES and job.get('expiresAt', 0) < now():
        if job_store.expire_job(job['jobId']):
            job_store.refund_slot(job)  # 時間切れはシステム起因。枠を取った日へ 1 回だけ返す
            job_store.release_lock(job['userId'], job['jobId'])
        return job_store.get_job(job['jobId']) or job
    return job


def _status(event: dict, user_id: str, *, is_admin: bool) -> dict:
    job_id = (event.get('pathParameters') or {}).get('jobId')
    after_seq = _parse_after_seq(event)
    if after_seq is None:
        return http.error(400, 'ValidationError', 'afterSeq は 0 以上の整数で指定してください')
    if not _canonical_uuid(job_id):
        return http.error(404, *NOT_FOUND)
    job_store = get_store()
    job = job_store.get_job(job_id)
    # SECURITY: 他人のジョブは存在しないのと同じ応答にする。
    if job is None or job.get('userId') != user_id:
        return http.error(404, *NOT_FOUND)
    job = _expire_if_stale(job_store, job)
    return http.respond(200, build_status_payload(job, after_seq=after_seq, include_debug=is_admin))


def lambda_handler(event, context):
    method = http.method_of(event)
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': http.HEADERS, 'body': ''}
    claims = http.claims_of(event)
    # SECURITY: 本番・無効時・非管理者は、DB・ワーカーに触れる前に 403。
    if not (config.feature_enabled() and config.is_admin(claims)):
        return http.error(403, 'FeatureUnavailable', '先輩チャットの調査は開発環境の管理者のみ利用できます')
    # SECURITY: userId は JWT の sub だけ。本文・クエリからは受け取らない。
    user_id = claims.get('sub') or ''
    if not user_id:
        return http.error(401, 'Unauthorized', 'ログインが必要です')
    missing = config.missing_api_env()
    if missing:
        for name in missing:
            _log('config', 'missing_env:' + name)
        return http.error(500, 'InternalError', '処理中にエラーが発生しました')
    try:
        if method == 'POST':
            return _create(event, user_id)
        if method == 'GET':
            return _status(event, user_id, is_admin=True)
        return http.error(405, 'MethodNotAllowed', '許可されていないメソッドです')
    except Exception as error:  # noqa: BLE001 - スタックトレースを返さない
        _log('handler', 'error', error)
        return http.error(500, 'InternalError', '処理中にエラーが発生しました')
