"""
EleKnowledge Metrics - Aggregator (EventBridge-triggered)

日次 KPI を chatlogs から集計し、metrics テーブルへ 1 日 1 行（scope=overall）と
時間帯別の行（scope=hourly）を書く。

日付の扱い（設計: docs/design-2026-09-10-metrics-v2.md §3 / docs/design-2026-09-10-dashboard-v2.md §6.4）
- 日付境界は JST（固定オフセット +09:00。DST 無し。実行環境の tz データベースに依存しない）
- metricDate は JST の日付 YYYY-MM-DD。chatlogs の timestamp（UTC ISO）を JST に変換して振り分ける

実行モード（EventBridge の Input で指定）
- {"mode": "daily"}   02:00 JST。前日を確定し、D-2・D-3 も再集計する
                      （回答の翌日以降に押された 👍👎 や資料クリックを回答日の行へ反映するため）
- {"mode": "hourly"}  毎時。当日を partial=true で上書きし、時間帯別の行も更新する
- {"date": "YYYY-MM-DD"}  手動再実行。JST のその日を確定扱いで集計する

冪等: 同じ metricDate + scope は PutItem で上書きされるため、再実行しても二重計上しない。
TTL: 日次 KPI は無期限保持（issue #86 決定）。ttl 属性は書かない。
"""
import json
import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get('AWS_REGION', 'ap-northeast-1')
dynamodb = boto3.resource('dynamodb', region_name=REGION)
cloudwatch = boto3.client('cloudwatch', region_name=REGION)

CHATLOGS_TABLE = os.environ.get('CHATLOGS_TABLE')
METRICS_TABLE = os.environ.get('METRICS_TABLE')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
# Optional: names used for CloudWatch lookups (best-effort; defaults derived from env)
RAG_FUNCTION_NAME = os.environ.get('RAG_FUNCTION_NAME', f'rag-{ENVIRONMENT}')
CHAT_FUNCTION_NAME = os.environ.get('CHAT_FUNCTION_NAME', f'chat-{ENVIRONMENT}')
RAG_API_NAME = os.environ.get('RAG_API_NAME', f'rag-api-{ENVIRONMENT}')

# 集計ロジックの版。集計の定義を変えたら上げる（read 側や Athena で行を区別するため）
LOGIC_VERSION = 2

# 日次確定時に再集計する日数（D-1 〜 D-REAGGREGATE_DAYS）
REAGGREGATE_DAYS = int(os.environ.get('REAGGREGATE_DAYS', '3'))

JST = timezone(timedelta(hours=9))

FEEDBACK_REASON_KEYS = ('wrong_doc', 'unresolved', 'bad_answer', 'other')

chatlogs_table = dynamodb.Table(CHATLOGS_TABLE)
metrics_table = dynamodb.Table(METRICS_TABLE)


# ----------------------------------------------------------------------------- time helpers
def jst_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(JST)


def parse_timestamp(value) -> datetime | None:
    """chatlogs の timestamp（ISO 8601）を aware datetime にする。

    'Z' 終端、マイクロ秒、+09:00 オフセット、オフセット無し（= UTC とみなす）を受け付ける。
    解釈できないものは None。
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


def jst_date_of(value) -> date | None:
    dt = parse_timestamp(value)
    return dt.astimezone(JST).date() if dt else None


def jst_hour_of(value) -> int | None:
    dt = parse_timestamp(value)
    return dt.astimezone(JST).hour if dt else None


def utc_window_for_jst_day(day: date) -> tuple[datetime, datetime]:
    """JST のその日 [00:00, 24:00) を UTC の aware datetime で返す。"""
    start = datetime(day.year, day.month, day.day, tzinfo=JST).astimezone(timezone.utc)
    return start, start + timedelta(days=1)


def scan_bounds_for_jst_day(day: date) -> tuple[str, str]:
    """Scan の FilterExpression 用の文字列境界（chatlogs の timestamp は UTC ISO 文字列）。"""
    start, end = utc_window_for_jst_day(day)
    lo = start.strftime('%Y-%m-%dT%H:%M:%S')
    hi = (end - timedelta(microseconds=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')
    return lo, hi


def parse_day(value: str) -> date:
    return date.fromisoformat(value)


# ----------------------------------------------------------------------------- chatlogs
def scan_day(day: date) -> list:
    """Paginated scan of chatlogs for a single JST day (UTC timestamp window)."""
    lo, hi = scan_bounds_for_jst_day(day)
    items = []
    kwargs = {
        'FilterExpression': '#ts BETWEEN :lo AND :hi AND (attribute_not_exists(#del) OR #del = :false)',
        'ExpressionAttributeNames': {'#ts': 'timestamp', '#del': 'deleted'},
        'ExpressionAttributeValues': {':lo': lo, ':hi': hi, ':false': False},
    }
    while True:
        resp = chatlogs_table.scan(**kwargs)
        items.extend(resp.get('Items', []))
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            break
        kwargs['ExclusiveStartKey'] = lek
    return items


def _is_unreached(item: dict) -> bool:
    """到達できなかった回答: not_found か 👎（重複は 1 件）。"""
    return item.get('role') == 'assistant' and (
        item.get('responseType') == 'not_found' or item.get('feedback') == 'bad'
    )


def aggregate_chat(items: list) -> dict:
    queries = 0
    sessions = set()
    active_users = set()
    good = bad = 0
    reasons = {k: 0 for k in FEEDBACK_REASON_KEYS}
    reasons['none'] = 0
    not_found = clarify = pages = 0
    wishes = 0
    unreached = 0
    doc_counts = {}

    for it in items:
        role = it.get('role')
        session_id = it.get('sessionId')
        if session_id and role in ('user', 'assistant'):
            sessions.add(session_id)
        if role == 'user':
            queries += 1
            if it.get('userId'):
                active_users.add(it['userId'])
        elif role == 'product_wish':
            wishes += 1

        fb = it.get('feedback')
        if fb == 'good':
            good += 1
        elif fb == 'bad':
            bad += 1
            reason = it.get('feedbackReason')
            if reason in reasons:
                reasons[reason] += 1
            else:
                reasons['none'] += 1

        rt = it.get('responseType')
        if role == 'assistant':
            if rt == 'not_found':
                not_found += 1
            elif rt == 'clarify':
                clarify += 1
            elif rt == 'pages':
                pages += 1
            if _is_unreached(it):
                unreached += 1

        for doc in it.get('sourceDocuments', []) or []:
            name = doc.get('documentName') or doc.get('title')
            if name:
                doc_counts[name] = doc_counts.get(name, 0) + 1

    top_documents = sorted(
        [{'name': n, 'count': c} for n, c in doc_counts.items()],
        key=lambda x: x['count'], reverse=True
    )[:10]

    like_rate = round(good / (good + bad), 4) if (good + bad) else 0.0
    return {
        'queries': queries,
        'sessions': len(sessions),
        'activeUsers': len(active_users),
        'userIds': sorted(active_users),
        'feedbackGood': good,
        'feedbackBad': bad,
        'likeRate': like_rate,
        'feedbackReasons': reasons,
        'notFound': not_found,
        'clarify': clarify,
        'pages': pages,
        'unreached': unreached,
        'productWishes': wishes,
        'topDocuments': top_documents,
    }


def aggregate_hourly(items: list) -> dict:
    """JST の時間帯（0〜23）ごとの件数。値が無い時間帯はゼロ行。"""
    hours = {h: {'queries': 0, 'notFound': 0, 'clarify': 0, 'pages': 0,
                 'feedbackGood': 0, 'feedbackBad': 0, 'unreached': 0, 'users': set()}
             for h in range(24)}
    for it in items:
        hour = jst_hour_of(it.get('timestamp'))
        if hour is None:
            continue
        h = hours[hour]
        role = it.get('role')
        if role == 'user':
            h['queries'] += 1
            if it.get('userId'):
                h['users'].add(it['userId'])
        elif role == 'assistant':
            rt = it.get('responseType')
            if rt == 'not_found':
                h['notFound'] += 1
            elif rt == 'clarify':
                h['clarify'] += 1
            elif rt == 'pages':
                h['pages'] += 1
            if _is_unreached(it):
                h['unreached'] += 1
        fb = it.get('feedback')
        if fb == 'good':
            h['feedbackGood'] += 1
        elif fb == 'bad':
            h['feedbackBad'] += 1
    out = {}
    for hour, h in hours.items():
        row = {k: v for k, v in h.items() if k != 'users'}
        row['activeUsers'] = len(h['users'])
        out[hour] = row
    return out


# ----------------------------------------------------------------------------- CloudWatch
def _cw_sum(namespace, metric, dimensions, start, end):
    try:
        resp = cloudwatch.get_metric_statistics(
            Namespace=namespace, MetricName=metric, Dimensions=dimensions,
            StartTime=start, EndTime=end, Period=86400, Statistics=['Sum'],
        )
        pts = resp.get('Datapoints', [])
        return sum(p['Sum'] for p in pts)
    except ClientError as e:
        print(f"[aggregator] CloudWatch {metric} error: {e}")
        return 0.0


def _cw_p90(namespace, metric, dimensions, start, end):
    try:
        resp = cloudwatch.get_metric_statistics(
            Namespace=namespace, MetricName=metric, Dimensions=dimensions,
            StartTime=start, EndTime=end, Period=86400, ExtendedStatistics=['p90'],
        )
        pts = resp.get('Datapoints', [])
        if not pts:
            return 0.0
        return max(p['ExtendedStatistics']['p90'] for p in pts)
    except ClientError as e:
        print(f"[aggregator] CloudWatch p90 {metric} error: {e}")
        return 0.0


def aggregate_health(day: date) -> dict:
    """Best-effort CloudWatch pull for the JST day; defaults to zeros if metrics are absent."""
    start, end = utc_window_for_jst_day(day)

    invocations = 0.0
    errors = 0.0
    for fn in (RAG_FUNCTION_NAME, CHAT_FUNCTION_NAME):
        dims = [{'Name': 'FunctionName', 'Value': fn}]
        invocations += _cw_sum('AWS/Lambda', 'Invocations', dims, start, end)
        errors += _cw_sum('AWS/Lambda', 'Errors', dims, start, end)
    error_rate = round(errors / invocations, 4) if invocations else 0.0

    http5xx = _cw_sum('AWS/ApiGateway', '5XXError', [{'Name': 'ApiName', 'Value': RAG_API_NAME}], start, end)
    # RAG response latency p90 in seconds (Lambda Duration is ms)
    dur_ms = _cw_p90('AWS/Lambda', 'Duration', [{'Name': 'FunctionName', 'Value': RAG_FUNCTION_NAME}], start, end)
    latency_p90 = round(dur_ms / 1000.0, 2)

    return {
        'errorRate': error_rate,
        'latencyP90': latency_p90,
        'http5xx': int(http5xx),
        'incidents': 0,  # populated from alarms if/when wired
    }


# ----------------------------------------------------------------------------- write
def to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, list):
        return [to_decimal(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_decimal(v) for k, v in obj.items()}
    return obj


def build_daily_snapshot(day: date, chat: dict, health: dict, partial: bool, aggregated_at: str) -> dict:
    return {
        'metricDate': day.isoformat(),
        'scope': 'overall',
        **chat,
        **health,
        'partial': partial,
        'logicVersion': LOGIC_VERSION,
        'aggregatedAt': aggregated_at,
    }


def build_hourly_rows(day: date, hourly: dict, upto_hour: int, aggregated_at: str) -> list:
    rows = []
    for hour in range(0, upto_hour + 1):
        counts = hourly.get(hour) or {}
        rows.append({
            'metricDate': f"{day.isoformat()}T{hour:02d}",
            'scope': 'hourly',
            **counts,
            'logicVersion': LOGIC_VERSION,
            'aggregatedAt': aggregated_at,
        })
    return rows


def write_day(day: date, partial: bool, upto_hour: int = 23) -> dict:
    """1 日分を集計して日次行と時間帯別の行を書く。"""
    aggregated_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    items = scan_day(day)
    chat = aggregate_chat(items)
    health = aggregate_health(day)
    snapshot = build_daily_snapshot(day, chat, health, partial, aggregated_at)
    metrics_table.put_item(Item=to_decimal(snapshot))

    hourly = aggregate_hourly(items)
    for row in build_hourly_rows(day, hourly, upto_hour, aggregated_at):
        metrics_table.put_item(Item=to_decimal(row))

    summary = {k: v for k, v in snapshot.items() if k not in ('topDocuments', 'userIds')}
    print(f"[aggregator] Wrote snapshot: {json.dumps(summary, default=str)}")
    return {'date': day.isoformat(), 'partial': partial, 'queries': chat['queries'], 'likeRate': chat['likeRate']}


def plan(event, now_jst: datetime) -> list:
    """イベントから (day, partial, upto_hour) の集計計画を作る。"""
    event = event or {}
    if event.get('date'):
        return [(parse_day(event['date']), False, 23)]
    mode = event.get('mode') or 'daily'
    today = now_jst.date()
    if mode == 'hourly':
        return [(today, True, now_jst.hour)]
    # daily: D-1 を確定し、後付けの投票・クリックを拾うため D-2..D-N も再集計
    return [(today - timedelta(days=n), False, 23) for n in range(1, REAGGREGATE_DAYS + 1)]


def lambda_handler(event, context):
    results = []
    for day, partial, upto_hour in plan(event, jst_now()):
        print(f"[aggregator] Aggregating {day.isoformat()} (partial={partial}, upto_hour={upto_hour})")
        results.append(write_day(day, partial, upto_hour))
    return {'statusCode': 200, 'results': results}
