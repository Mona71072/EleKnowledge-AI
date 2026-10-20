"""調査ジョブ表（DynamoDB）: 条件付き書き込み・ユーザーごとのロック・日次上限・追記専用イベント。

1 テーブル・ハッシュキー `pk` だけ。Query / Scan は使わない（GetItem / PutItem /
UpdateItem / DeleteItem のみ）。
  JOB#<jobId>                      ジョブ本体（状態・段階イベント・結果）
  LOCK#<userId>                    同時実行1件のロック（期限つき）
  DAILY#<userId>#<JST日付>         1日の起動回数
  REQ#<userId>#<clientRequestId>   二重送信の防止（同じ要求は同じ jobId）
"""
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from botocore.exceptions import ClientError

JST = timezone(timedelta(hours=9))
JOB_RETENTION_SECONDS = 7 * 24 * 3600
DAILY_RETENTION_SECONDS = 3 * 24 * 3600
TIMEOUT_MESSAGE = '調査が時間内に完了しませんでした。もう一度お試しください。'
CONDITION_FAILED = 'ConditionalCheckFailedException'


def _to_ddb(value):
    """DynamoDB が受け付けない float を Decimal にして複製する。"""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: _to_ddb(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_ddb(item) for item in value]
    return value


def _is_condition_failure(error: ClientError) -> bool:
    return error.response.get('Error', {}).get('Code') == CONDITION_FAILED


def build_job_item(job_id: str, user_id: str, request: dict, *, now: float,
                   ttl_seconds: int, daily_day: str = None) -> dict:
    """新しいジョブ行。userId は呼び出し側が JWT から渡す。

    daily_day は日次枠を取った日（JST の日付）。失敗時に「取った日」の枠へ返すために持つ。
    """
    created = datetime.fromtimestamp(now, timezone.utc).isoformat().replace('+00:00', 'Z')
    item = {
        'pk': f'JOB#{job_id}',
        'jobId': job_id,
        'userId': user_id,
        'status': 'queued',
        'question': request['question'],
        'modelType': request.get('modelType'),
        'senpaiConversationId': request['senpaiConversationId'],
        'senpaiTurnId': request['senpaiTurnId'],
        'clientRequestId': request['clientRequestId'],
        'steps': [],
        'nextSeq': 1,
        'createdAt': created,
        'expiresAt': int(now) + ttl_seconds,
        'ttl': int(now) + JOB_RETENTION_SECONDS,
    }
    if daily_day:
        item['dailyDay'] = daily_day
    return item


class JobStore:
    def __init__(self, table, clock=time.time):
        self._table = table
        self._clock = clock

    # ------------------------------------------------------------ 二重送信

    def claim_request(self, user_id: str, client_request_id: str, job_id: str) -> tuple:
        """要求を登録する。既に登録済みなら (既存の jobId, False)。"""
        key = f'REQ#{user_id}#{client_request_id}'
        for _attempt in range(2):
            try:
                self._table.put_item(
                    Item={'pk': key, 'jobId': job_id,
                          'ttl': int(self._clock()) + JOB_RETENTION_SECONDS},
                    ConditionExpression='attribute_not_exists(pk)',
                )
                return job_id, True
            except ClientError as error:
                if not _is_condition_failure(error):
                    raise
            existing = self._table.get_item(Key={'pk': key}, ConsistentRead=True).get('Item')
            if existing:
                return existing['jobId'], False
        raise RuntimeError('request claim raced twice')

    def release_request(self, user_id: str, client_request_id: str) -> None:
        self._table.delete_item(Key={'pk': f'REQ#{user_id}#{client_request_id}'})

    # ------------------------------------------------------------ ロック

    def acquire_lock(self, user_id: str, job_id: str, ttl_seconds: int) -> bool:
        now = int(self._clock())
        try:
            self._table.put_item(
                Item={'pk': f'LOCK#{user_id}', 'jobId': job_id,
                      'expiresAt': now + ttl_seconds, 'ttl': now + ttl_seconds + 3600},
                ConditionExpression='attribute_not_exists(pk) OR expiresAt < :now',
                ExpressionAttributeValues={':now': now},
            )
            return True
        except ClientError as error:
            if _is_condition_failure(error):
                return False
            raise

    def release_lock(self, user_id: str, job_id: str) -> None:
        """自分のジョブのロックだけを外す（引き継がれた新しいロックは壊さない）。"""
        try:
            self._table.delete_item(
                Key={'pk': f'LOCK#{user_id}'},
                ConditionExpression='jobId = :job',
                ExpressionAttributeValues={':job': job_id},
            )
        except ClientError as error:
            if not _is_condition_failure(error):
                raise

    # ------------------------------------------------------------ 日次上限

    def daily_day(self) -> str:
        """日次枠の日付（JST）。"""
        return datetime.fromtimestamp(self._clock(), JST).date().isoformat()

    def _daily_key(self, user_id: str, day: str = None) -> str:
        return f'DAILY#{user_id}#{day or self.daily_day()}'

    def take_daily_slot(self, user_id: str, limit: int, day: str = None) -> bool:
        try:
            self._table.update_item(
                Key={'pk': self._daily_key(user_id, day)},
                UpdateExpression='ADD cnt :one SET #ttl = :ttl',
                ConditionExpression='attribute_not_exists(cnt) OR cnt < :limit',
                ExpressionAttributeNames={'#ttl': 'ttl'},
                ExpressionAttributeValues={
                    ':one': 1, ':limit': limit,
                    ':ttl': int(self._clock()) + DAILY_RETENTION_SECONDS,
                },
            )
            return True
        except ClientError as error:
            if _is_condition_failure(error):
                return False
            raise

    def return_daily_slot(self, user_id: str, day: str = None) -> None:
        try:
            self._table.update_item(
                Key={'pk': self._daily_key(user_id, day)},
                UpdateExpression='ADD cnt :minus',
                ConditionExpression='cnt > :zero',
                ExpressionAttributeValues={':minus': -1, ':zero': 0},
            )
        except ClientError as error:
            if not _is_condition_failure(error):
                raise

    def refund_slot(self, job: dict) -> None:
        """システム起因で失敗したジョブの日次枠を、枠を取った日へ返す。

        fail_job / expire_job が True を返した（＝そのジョブを failed にできた）ときだけ呼ぶ。
        その更新は 1 ジョブにつき 1 回しか成功しないので、返却も 1 回になる。
        """
        self.return_daily_slot(job['userId'], job.get('dailyDay'))

    # ------------------------------------------------------------ ジョブ

    def create_job(self, item: dict) -> None:
        self._table.put_item(
            Item=_to_ddb(item), ConditionExpression='attribute_not_exists(pk)'
        )

    def get_job(self, job_id: str):
        return self._table.get_item(Key={'pk': f'JOB#{job_id}'}, ConsistentRead=True).get('Item')

    def _update_if(self, job_id: str, update: str, condition: str, names=None, values=None) -> bool:
        kwargs = {
            'Key': {'pk': f'JOB#{job_id}'},
            'UpdateExpression': update,
            'ConditionExpression': condition,
            'ExpressionAttributeValues': _to_ddb(values or {}),
        }
        all_names = {'#status': 'status', **(names or {})}
        used = {k: v for k, v in all_names.items() if k in update or k in condition}
        if used:
            kwargs['ExpressionAttributeNames'] = used
        try:
            self._table.update_item(**kwargs)
            return True
        except ClientError as error:
            if _is_condition_failure(error):
                return False
            raise

    def start_job(self, job_id: str) -> bool:
        return self._update_if(
            job_id, 'SET #status = :running, startedAt = :now',
            '#status = :queued AND expiresAt > :now',
            values={':running': 'running', ':queued': 'queued', ':now': int(self._clock())},
        )

    def next_seq(self, job_id: str) -> int:
        """保存先が次に受け付ける seq（記録側が番号を取り直すために使う）。"""
        job = self.get_job(job_id) or {}
        return int(job.get('nextSeq') or 1)

    def append_step(self, job_id: str, event: dict) -> bool:
        """イベントを末尾に足す。seq が次の番号と一致するときだけ（追記専用・単調増加）。"""
        return self._update_if(
            job_id, 'SET steps = list_append(steps, :event), nextSeq = :next',
            'nextSeq = :seq',
            values={':event': [event], ':next': event['seq'] + 1, ':seq': event['seq']},
        )

    def complete_job(self, job_id: str, result: dict, debug: dict) -> bool:
        return self._update_if(
            job_id, 'SET #status = :done, #result = :result, debug = :debug, finishedAt = :now',
            '#status = :running AND expiresAt > :now', names={'#result': 'result'},
            values={':done': 'completed', ':running': 'running', ':result': result,
                    ':debug': debug, ':now': int(self._clock())},
        )

    def fail_job(self, job_id: str, code: str, message: str, debug: dict = None) -> bool:
        return self._update_if(
            job_id,
            'SET #status = :failed, #error = :error, debug = :debug, finishedAt = :now',
            '#status IN (:queued, :running)', names={'#error': 'error'},
            values={':failed': 'failed', ':queued': 'queued', ':running': 'running',
                    ':error': {'code': code, 'message': message}, ':debug': debug or {},
                    ':now': int(self._clock())},
        )

    def expire_job(self, job_id: str) -> bool:
        """期限切れの進行中ジョブだけを Timeout で終わらせる。"""
        return self._update_if(
            job_id, 'SET #status = :failed, #error = :error, finishedAt = :now',
            '#status IN (:queued, :running) AND expiresAt < :now', names={'#error': 'error'},
            values={':failed': 'failed', ':queued': 'queued', ':running': 'running',
                    ':error': {'code': 'Timeout', 'message': TIMEOUT_MESSAGE},
                    ':now': int(self._clock())},
        )
