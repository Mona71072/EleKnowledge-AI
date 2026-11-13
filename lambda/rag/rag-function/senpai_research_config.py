"""工技先輩の調査ジョブ（試作）の設定。値はすべて環境変数（SAM パラメータ由来）から読む。"""
import os
from dataclasses import dataclass

import vocabulary_generated as vocabulary

# 画面の機種キー（rag-function の UI_MODEL_FILTERS と同じ6つ）。
# SYNC: tests/unit/test_senpai_research_steps.py::test_ui_model_types_match_rag_ui_model_filters
# 値の正本は knowledge/registry/applicability-vocabulary.json（vocabulary_generated.py に生成）。
UI_MODEL_TYPES = tuple(vocabulary.UI_MODEL_FILTERS)
QUESTION_MAX_CHARS = 2000
POLL_AFTER_MS = 1500
STATUS_VALUES = ('queued', 'running', 'completed', 'failed')
ACTIVE_STATUSES = ('queued', 'running')


def env_int(name: str, default: int, low: int, high: int) -> int:
    """範囲内の整数だけを受け付ける。不正値は既定値に戻す（起動を止めない）。"""
    try:
        value = int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default
    return min(max(value, low), high)


def feature_enabled() -> bool:
    # SECURITY: dev かつ明示的に有効化されたときだけ。本番では常に利用不可。
    return (
        os.environ.get('ENVIRONMENT') == 'dev'
        and os.environ.get('SENPAI_RESEARCH_ENABLED') == 'true'
    )


def is_admin(claims: dict) -> bool:
    groups = claims.get('cognito:groups', '')
    names = groups if isinstance(groups, list) else [
        g.strip() for g in str(groups).split(',') if g.strip()
    ]
    return (os.environ.get('ADMIN_GROUP_NAME', 'admin').strip() or 'admin') in names


def table_name() -> str:
    return os.environ.get('SENPAI_RESEARCH_TABLE', '').strip()


def worker_function_name() -> str:
    return os.environ.get('SENPAI_RESEARCH_WORKER_NAME', '').strip()


def daily_limit() -> int:
    return env_int('SENPAI_RESEARCH_DAILY_LIMIT', 20, 1, 1000)


def job_ttl_seconds() -> int:
    """進行中ジョブ・ロックの有効秒数（リース）。

    非同期起動の最大待ち（MaximumEventAgeInSeconds: 120）+ ワーカーの Timeout（180）以上にする。
    これより短いと、起動が遅れたジョブの実行中にロックが切れ、同じ人の調査が二重に走る。
    """
    return env_int('SENPAI_RESEARCH_JOB_TTL_SECONDS', 330, 330, 900)


def kb_read_timeout_seconds() -> int:
    """ナレッジベース検索 1 回の読み取り待ち（秒）。"""
    return env_int('SENPAI_RESEARCH_KB_READ_TIMEOUT', 12, 3, 30)


def model_read_timeout_seconds() -> int:
    """モデル 1 呼び出しの読み取り待ちの上限（秒）。実際は残り予算でさらに短くなる。"""
    return env_int('SENPAI_RESEARCH_MODEL_READ_TIMEOUT', 40, 5, 100)


def understand_model_id() -> str:
    return os.environ.get('SENPAI_UNDERSTAND_MODEL_ID', '').strip()


def _missing(names) -> list:
    return [name for name in names if not os.environ.get(name, '').strip()]


def missing_api_env() -> list:
    """受付 Lambda が動くのに必要な環境変数のうち、未設定のもの。"""
    return _missing(('SENPAI_RESEARCH_TABLE', 'SENPAI_RESEARCH_WORKER_NAME'))


def missing_worker_env() -> list:
    """ワーカー Lambda が動くのに必要な環境変数のうち、未設定のもの。"""
    return _missing(('SENPAI_RESEARCH_TABLE', 'CHATLOGS_TABLE'))


@dataclass(frozen=True)
class BudgetLimits:
    max_searches: int
    max_model_calls: int
    job_ms: int
    synth_reserve_ms: int
    # Lambda の残り時間から、強制終了されないために必ず残す時間（ミリ秒）。
    safety_ms: int = 10000
    max_input_bytes: int = 120000
    no_progress_limit: int = 2


def load_limits() -> BudgetLimits:
    return BudgetLimits(
        max_searches=env_int('SENPAI_RESEARCH_MAX_SEARCHES', 18, 1, 60),
        max_model_calls=env_int('SENPAI_RESEARCH_MAX_MODEL_CALLS', 10, 1, 20),
        job_ms=env_int('SENPAI_RESEARCH_JOB_BUDGET_MS', 90000, 5000, 90000),
        synth_reserve_ms=env_int('SENPAI_RESEARCH_SYNTH_RESERVE_MS', 45000, 45000, 45000),
        max_input_bytes=env_int('SENPAI_RESEARCH_MAX_INPUT_BYTES', 120000, 1000, 120000),
        no_progress_limit=env_int('SENPAI_RESEARCH_NO_PROGRESS_LIMIT', 2, 1, 3),
    )
