"""完了した調査の質問と回答を ChatLogs に残す（相談履歴から開き直すため）。

- ragMode=senpai_research、既存の先輩タグ（senpaiConversationId / senpaiTurnId）付き。TTL は 60 日。
- 通常の /chat 履歴（タグなしの行だけを出す）には現れない。
- 回答の日別集計（metricDay）には混ぜない。まとめ行（senpai_synthesis）と同じ扱い。
"""
import time
from datetime import datetime, timezone

from botocore.exceptions import ClientError

import senpai_research_store as store

RAG_MODE = 'senpai_research'
TTL_SECONDS = 60 * 24 * 60 * 60
RESPONSE_TYPES = {'answer': 'pages', 'clarify': 'clarify', 'not_found': 'not_found'}


def session_id_for(job_id: str) -> str:
    return f'senpai-research-{job_id}'


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def build_rows(job: dict, result: dict, *, now: datetime = None, epoch: int = None) -> tuple:
    """(質問の行, 回答の行)。メッセージ ID はジョブ固有で決まるので、再実行しても重複しない。"""
    now = now or datetime.now(timezone.utc)
    ttl = (int(time.time()) if epoch is None else epoch) + TTL_SECONDS
    job_id = job['jobId']
    base = {
        'sessionId': session_id_for(job_id),
        'userId': job['userId'],
        'ragMode': RAG_MODE,
        'ttl': ttl,
        'senpaiConversationId': job['senpaiConversationId'],
        'senpaiTurnId': job['senpaiTurnId'],
    }
    user_row = {
        **base, 'messageId': f'senpai-research-q-{job_id}', 'role': 'user',
        'content': job['question'], 'timestamp': job.get('createdAt') or _iso(now),
    }
    assistant_row = {
        **base, 'messageId': f'senpai-research-a-{job_id}', 'role': 'assistant',
        'content': result['answerMarkdown'], 'timestamp': _iso(now),
        'responseType': RESPONSE_TYPES.get(result['kind'], 'pages'),
        'clarifyQuestions': list(result.get('clarifyQuestions') or []),
        'researchResult': result,
    }
    model_type = (result.get('understanding') or {}).get('modelType')
    if model_type:
        assistant_row['queryFilters'] = {'modelType': model_type}
    return store._to_ddb(user_row), store._to_ddb(assistant_row)


def save_rows(table, rows: tuple) -> None:
    """条件付きで保存する。既にある行は上書きしない。"""
    for row in rows:
        try:
            table.put_item(Item=row, ConditionExpression='attribute_not_exists(messageId)')
        except ClientError as error:
            if error.response.get('Error', {}).get('Code') != store.CONDITION_FAILED:
                raise
