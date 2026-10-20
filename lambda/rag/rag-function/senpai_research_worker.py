"""調査ジョブのワーカー Lambda。受付 Lambda から非同期（Event）で 1 件ずつ起動される。

ジョブ行を読み、runner で調査し、段階イベントを逐次保存し、結果（または失敗）を保存する。
再試行は無効（MaximumRetryAttempts: 0）。二重実行はジョブ行の条件付き更新で防ぐ。
ログには jobId・段階名・件数・時間・終了理由・エラー種別だけを出す（質問・検索語・回答は出さない）。

ジョブ行の状態はリース（expiresAt）で守る。期限を過ぎたジョブは開始も完了もできず（lost_lease）、
その場合は履歴にも保存しない。履歴は complete_job に成功した後にだけ保存する。
"""
import os
import uuid
from types import SimpleNamespace

import boto3

import senpai_research_budget as budget_module
import senpai_research_chatlog as chatlog
import senpai_research_config as config
import senpai_research_log as run_log
import senpai_research_recorder as recorder_module
import senpai_research_runner as runner
import senpai_research_store as store
from senpai_research_errors import ResearchFailure

INTERNAL_MESSAGE = '調査中にエラーが発生しました。時間をおいて再度お試しください。'
QUESTION_UNAVAILABLE_MESSAGE = '質問を読み込めませんでした。もう一度お試しください。'


def build_runtime() -> SimpleNamespace:
    """AWS に触れる部品（ジョブ表・ChatLogs・予算の上限）。受け取った jobId が正しいときだけ作る。"""
    dynamodb = boto3.resource('dynamodb')
    return SimpleNamespace(
        store=store.JobStore(dynamodb.Table(config.table_name())),
        chatlogs_table=dynamodb.Table(os.environ['CHATLOGS_TABLE']),
        limits=config.load_limits(),
    )


def build_deps():
    import senpai_research_rag  # noqa: PLC0415 - app.py の読み込みは必要になるまで遅らせる
    return senpai_research_rag.RagDeps()


def _canonical_uuid(value) -> bool:
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def _summary(job_status: str, budget, outcome=None, error_code: str = None) -> None:
    snapshot = budget.snapshot()
    fields = {
        'elapsedMs': snapshot['elapsedMs'], 'modelCalls': snapshot['modelCallsUsed'],
        'searches': snapshot['searchesUsed'],
    }
    if outcome is not None:
        fields.update(kind=outcome['kind'], stopReason=outcome['result']['stopReason'])
    if error_code:
        fields['errorCode'] = error_code
    run_log.log('job_finished', job_status, **fields)


def _save_history(runtime, job: dict, outcome: dict) -> None:
    """履歴への保存は付随の処理。失敗しても調査の結果は返す。"""
    try:
        chatlog.save_rows(runtime.chatlogs_table, chatlog.build_rows(job, outcome['result']))
    except Exception as error:  # noqa: BLE001
        run_log.log('history', 'error', error)


def _fail(runtime, job: dict, code: str, message: str, debug: dict = None) -> None:
    """ジョブを failed にし、システム起因の失敗として日次枠を返す（failed にできたときだけ・1 回だけ）。"""
    if runtime.store.fail_job(job['jobId'], code, message, debug):
        runtime.store.refund_slot(job)


def _complete(runtime, job: dict, outcome: dict, budget) -> None:
    job_id = job['jobId']
    try:
        completed = runtime.store.complete_job(job_id, outcome['result'], outcome['debug'])
    except Exception as error:  # noqa: BLE001 - 保存できない結果は失敗として終わらせる
        run_log.log('job', 'complete_error', error)
        _fail(runtime, job, 'Internal', INTERNAL_MESSAGE)
        _summary('failed', budget, error_code='Internal')
        return
    if not completed:
        # 期限切れ等でジョブが既に failed。利用者には失敗を返済済みなので、履歴にも残さない。
        _summary('lost_lease', budget, outcome=outcome)
        return
    _save_history(runtime, job, outcome)
    _summary('completed', budget, outcome=outcome)


def _run(runtime, job: dict, deps, budget) -> None:
    job_id = job['jobId']
    recorder = recorder_module.StepRecorder(
        lambda event: runtime.store.append_step(job_id, event),
        resync=lambda: runtime.store.next_seq(job_id),
    )
    try:
        outcome = runner.run_research(job, deps, recorder, budget)
    except ResearchFailure as failure:
        _fail(runtime, job, failure.code, failure.message, failure.debug)
        _summary('failed', budget, error_code=failure.code)
        return
    except Exception as error:  # noqa: BLE001 - 利用者には一般化した失敗だけを返す
        run_log.log('job', 'error', error)
        _fail(runtime, job, 'Internal', INTERNAL_MESSAGE)
        _summary('failed', budget, error_code='Internal')
        return
    _complete(runtime, job, outcome, budget)


def _hard_limit_ms(limits, remaining_ms):
    """Lambda の残り時間から安全マージンを引いた、待ち時間の天井。残り時間が不明なら None。"""
    return None if remaining_ms is None else max(0, int(remaining_ms) - limits.safety_ms)


def process_job(job_id: str, runtime, deps, remaining_ms=None) -> None:
    run_log.set_job(job_id)
    try:
        job = runtime.store.get_job(job_id)
        if job is None:
            run_log.log('job', 'missing')
            return
        if not runtime.store.start_job(job_id):
            run_log.log('job', 'not_startable')  # 他のワーカーが実行中・既に終了・期限切れ
            return
        run_log.log('job_started', 'ok')
        try:
            budget = budget_module.Budget(
                runtime.limits, hard_limit_ms=_hard_limit_ms(runtime.limits, remaining_ms),
                call_cap_s=config.model_read_timeout_seconds())
            if not isinstance(job.get('question'), str) or not job['question'].strip():
                _fail(runtime, job, 'QuestionUnavailable', QUESTION_UNAVAILABLE_MESSAGE)
                _summary('failed', budget, error_code='QuestionUnavailable')
                return
            if hasattr(deps, 'bind_budget'):
                deps.bind_budget(budget)
            _run(runtime, job, deps, budget)
        finally:
            runtime.store.release_lock(job['userId'], job_id)
    finally:
        run_log.clear_job()


_cold = {'checked': False}


def warn_if_unconfigured() -> None:
    """コールドスタート時に、任意だが推奨の設定が欠けていれば警告する（整理用モデルが未設定だと大きいモデルで整理する）。"""
    if not config.understand_model_id():
        run_log.log('config', 'understand_model_unset')


def _fail_best_effort(job_id: str) -> None:
    """処理全体が落ちたとき、ジョブを failed にしてロックを外す（行が読めれば）。"""
    table_name = config.table_name()
    if not table_name:
        return
    try:
        job_store = store.JobStore(boto3.resource('dynamodb').Table(table_name))
        job = job_store.get_job(job_id)
        if job is None:
            return
        if job_store.fail_job(job_id, 'Internal', INTERNAL_MESSAGE):
            job_store.refund_slot(job)
        job_store.release_lock(job['userId'], job_id)
    except Exception as error:  # noqa: BLE001
        run_log.log('handler', 'cleanup_error', error)


def lambda_handler(event, context):
    job_id = event.get('jobId') if isinstance(event, dict) else None
    if not _canonical_uuid(job_id):
        run_log.log('handler', 'invalid_event')
        return None
    if not _cold['checked']:
        _cold['checked'] = True
        warn_if_unconfigured()
    run_log.set_job(job_id)
    try:
        missing = config.missing_worker_env()
        if missing:
            for name in missing:
                run_log.log('config', 'missing_env', name=name)
            raise RuntimeError('missing required environment')
        remaining = getattr(context, 'get_remaining_time_in_millis', None)
        process_job(job_id, build_runtime(), build_deps(),
                    remaining_ms=remaining() if callable(remaining) else None)
    except Exception as error:  # noqa: BLE001 - ここまでの保険。利用者にはジョブの失敗として見せる
        run_log.log('handler', 'error', error)
        _fail_best_effort(job_id)
    finally:
        run_log.clear_job()
    return None
