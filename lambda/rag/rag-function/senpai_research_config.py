"""工技先輩の調査ジョブ（試作）の設定。値はすべて環境変数（SAM パラメータ由来）から読む。"""
import os
from dataclasses import dataclass

# 画面の機種キー（rag-function の UI_MODEL_FILTERS と同じ6つ）。
# SYNC: tests/unit/test_senpai_research_steps.py::test_ui_model_types_match_rag_ui_model_filters
UI_MODEL_TYPES = (
    'AXIEZ', 'AXIEZ-LINKs', 'NEXCUBE', 'メルシティ', 'メルワイド', 'エスカレーター',
)
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
    """進行中ジョブ・ロックの有効秒数。ワーカーの Timeout（120秒）より少し長く取る。"""
    return env_int('SENPAI_RESEARCH_JOB_TTL_SECONDS', 150, 30, 900)


@dataclass(frozen=True)
class BudgetLimits:
    max_searches: int
    max_model_calls: int
    job_ms: int
    synth_reserve_ms: int


def load_limits() -> BudgetLimits:
    return BudgetLimits(
        max_searches=env_int('SENPAI_RESEARCH_MAX_SEARCHES', 6, 1, 20),
        max_model_calls=env_int('SENPAI_RESEARCH_MAX_MODEL_CALLS', 4, 1, 10),
        job_ms=env_int('SENPAI_RESEARCH_JOB_BUDGET_MS', 60000, 5000, 110000),
        synth_reserve_ms=env_int('SENPAI_RESEARCH_SYNTH_RESERVE_MS', 20000, 0, 100000),
    )
