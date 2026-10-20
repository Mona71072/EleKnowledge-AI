"""chatlogs の日別集計キー（metricDay / metricDayShard）。

書き込み側（rag-function の save_message_to_dynamodb、chat-management の save_product_wish）が行に付け、
集計 Lambda（lambda/metrics/aggregator）が GSI metricDayShard-timestamp-index を Query するときの対応キー。
同じ内容を lambda/chat/chat-management/chatlog_metric_keys.py にも置く
（tests/unit/test_chatlog_metric_keys.py が両者の一致を確認する）。

- metricDay: timestamp を JST に変換した日付 YYYY-MM-DD（集計の日付境界と同じ）
- metricDayShard: "<metricDay>#<shard>"。shard = crc32(messageId) % CHATLOGS_METRIC_SHARDS。
  1 日の書込みを 1 つの partition に集めないための分散。集計は全シャードを Query する。

シャード数は移行後に固定する。既存キーはバックフィルで再配置しないため、変更時は別の移行計画が必要
（docs/ops-runbook.md の chatlogs 日別 GSI の節）。
"""
import os
import zlib
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
METRIC_DAY_SHARD_COUNT = int(os.environ.get('CHATLOGS_METRIC_SHARDS', '10'))


def parse_chatlog_timestamp(value):
    """chatlogs の timestamp（ISO 8601）を aware datetime にする。解釈できなければ None。

    'Z' 終端、マイクロ秒、オフセット付き、オフセット無し（= UTC とみなす）を受け付ける。
    集計 Lambda の parse_timestamp と同じ規則。
    """
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def metric_day_keys(timestamp: datetime, message_id: str,
                    shard_count: int = METRIC_DAY_SHARD_COUNT) -> dict:
    """timestamp（aware）と messageId から metricDay / metricDayShard を作る。"""
    if timestamp.tzinfo is None:
        raise ValueError('timestamp must be timezone-aware')
    if shard_count < 1:
        raise ValueError('shard_count must be at least 1')
    day = timestamp.astimezone(JST).date().isoformat()
    shard = zlib.crc32(message_id.encode('utf-8')) % shard_count
    return {'metricDay': day, 'metricDayShard': f'{day}#{shard}'}
