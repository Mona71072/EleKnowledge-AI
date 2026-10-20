"""調査ジョブのワーカー Lambda。受付 Lambda から非同期（Event）で 1 件ずつ起動される。

ジョブ行を読み、runner で調査し、段階イベントを逐次保存し、結果（または失敗）を保存する。
再試行は無効（MaximumRetryAttempts: 0）。二重実行はジョブ行の条件付き更新で防ぐ。
ログには段階名・件数・時間・終了理由・エラー種別だけを出す（質問・検索語・回答は出さない）。
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
    run_log.log('job', job_status, **fields)


def _save_history(runtime, job: dict, outcome: dict) -> None:
    """履歴への保存は付随の処理。失敗しても調査の結果は返す。"""
    try:
        chatlog.save_rows(runtime.chatlogs_table, chatlog.build_rows(job, outcome['result']))
    except Exception as error:  # noqa: BLE001
        run_log.log('history', 'error', error)


def _run(runtime, job: dict, deps, budget) -> None:
    job_id = job['jobId']
    recorder = recorder_module.StepRecorder(lambda event: runtime.store.append_step(job_id, event))
    try:
        outcome = runner.run_research(job, deps, recorder, budget)
    except ResearchFailure as failure:
        runtime.store.fail_job(job_id, failure.code, failure.message, failure.debug)
        _summary('failed', budget, error_code=failure.code)
        return
    except Exception as error:  # noqa: BLE001 - 利用者には一般化した失敗だけを返す
        run_log.log('job', 'error', error)
        runtime.store.fail_job(job_id, 'Internal', INTERNAL_MESSAGE)
        _summary('failed', budget, error_code='Internal')
        return
    _save_history(runtime, job, outcome)
    runtime.store.complete_job(job_id, outcome['result'], outcome['debug'])
    _summary('completed', budget, outcome=outcome)


def process_job(job_id: str, runtime, deps) -> None:
    job = runtime.store.get_job(job_id)
    if job is None:
        run_log.log('job', 'missing')
        return
    if not runtime.store.start_job(job_id):
        run_log.log('job', 'not_startable')  # 他のワーカーが実行中か、既に終わっている
        return
    try:
        if not isinstance(job.get('question'), str) or not job['question'].strip():
            runtime.store.fail_job(job_id, 'QuestionUnavailable', QUESTION_UNAVAILABLE_MESSAGE)
            run_log.log('job', 'failed', errorCode='QuestionUnavailable')
            return
        _run(runtime, job, deps, budget_module.Budget(runtime.limits))
    finally:
        runtime.store.release_lock(job['userId'], job_id)


def lambda_handler(event, context):
    job_id = event.get('jobId') if isinstance(event, dict) else None
    if not _canonical_uuid(job_id):
        run_log.log('handler', 'invalid_event')
        return None
    process_job(job_id, build_runtime(), build_deps())
    return None
