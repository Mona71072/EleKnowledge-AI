"""
EleKnowledge Metrics - Read (admin only)

GET /admin/metrics/dashboard?trend=14|30|90   朝の画面（設計: docs/design-2026-09-10-dashboard-v2.md §2 / §6.3）
GET /admin/metrics/cost?month=YYYY-MM          コスト画面（同 §5）
GET /admin/metrics?period=today|week|month     旧形式（現行 UI 用。UI 切替後に削除）

日付は JST（固定オフセット +09:00）。日次行の metricDate は JST の日付。コスト行（scope=cost）は UTC 日。
「いま」の値だけは表示のたびに CloudWatch を直接読む（DescribeAlarms / GetMetricData / DescribeAlarmHistory）。
"""
import json
import os
import statistics
from datetime import date, datetime, timedelta, timezone

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError, ClientError

REGION = os.environ.get('AWS_REGION', 'ap-northeast-1')
dynamodb = boto3.resource('dynamodb', region_name=REGION)
cloudwatch = boto3.client('cloudwatch', region_name=REGION)

METRICS_TABLE = os.environ.get('METRICS_TABLE')
ANNOUNCEMENTS_TABLE = os.environ.get('ANNOUNCEMENTS_TABLE', '')
ADMIN_GROUP_NAME = os.environ.get('ADMIN_GROUP_NAME', 'admin')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
API_NAMES = [n.strip() for n in os.environ.get(
    'API_NAMES',
    f'rag-api-{ENVIRONMENT},chat-api-{ENVIRONMENT},auth-api-{ENVIRONMENT},announcements-monitoring-api-{ENVIRONMENT}',
).split(',') if n.strip()]
ALARM_PREFIX = os.environ.get('ALARM_PREFIX', f'EleKnowledge-{ENVIRONMENT}-')
BEDROCK_BUDGET_USD = float(os.environ.get('BEDROCK_BUDGET_USD', '100'))
BEDROCK_COST_SERVICE_NAME = os.environ.get('BEDROCK_COST_SERVICE_NAME', 'Claude Sonnet 5 (Amazon Bedrock Edition)')
AMPLIFY_COST_SERVICE_NAME = os.environ.get('AMPLIFY_COST_SERVICE_NAME', 'AWS Amplify')
LOG_GROUP_ENV = ENVIRONMENT

table = dynamodb.Table(METRICS_TABLE)
announcements_table = dynamodb.Table(ANNOUNCEMENTS_TABLE) if ANNOUNCEMENTS_TABLE else None

JST = timezone(timedelta(hours=9))

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,OPTIONS',
}

# ---- 旧形式の閾値（/admin/metrics 互換） --------------------------------------
THRESHOLDS = {
    'errorRate': [(0.01, 'good'), (0.05, 'warning'), (0.10, 'serious')],   # else critical
    'latencyP90': [(3.0, 'good'), (6.0, 'warning'), (10.0, 'serious')],
    'http5xx': [(0, 'good'), (5, 'warning'), (20, 'serious')],
}

# ---- v2 の閾値（設計 §2.8。アラームと同じ値） ------------------------------------
STATUS_ORDER = ['good', 'warning', 'serious', 'critical']
SLO_P90_MS = 20000       # Q1 決定: p90 20 s
P1_MAX_MS = 25000        # P1-rag-duration-max
TIMEOUT_MS = 29000       # API Gateway 統合タイムアウト
MIN_SAMPLES_FOR_P90 = 10
COST_SPIKE_FACTOR = 3.0
COST_SPIKE_FLOOR_USD = 1.0
FRESHNESS_WARN_HOUR_JST = 9
RATE_DENOMINATOR_MIN = 30
ACTUAL_VS_ESTIMATE_WARN_PCT = 20
SHARED_SERVICE_KEYWORDS = ('opensearch', 'titan', 'embed')
UNATTRIBUTED_SERVICE_KEYWORDS = ('cloudwatch', 'lambda', 'dynamodb', 'api gateway', 's3', 'cognito', 'waf', 'key management', 'secrets', 'sqs', 'glue', 'athena', 'eventbridge', 'sns', 'cloudtrail', 'config')


def worse(a: str, b: str) -> str:
    return STATUS_ORDER[max(STATUS_ORDER.index(a), STATUS_ORDER.index(b))]


def status_5xx(n: int) -> str:
    if n <= 0:
        return 'good'
    if n <= 5:
        return 'warning'
    if n <= 20:
        return 'serious'
    return 'critical'


def status_latency(p90_ms, max_ms) -> str:
    st = 'good'
    if p90_ms is not None:
        st = 'good' if p90_ms <= SLO_P90_MS else 'warning' if p90_ms <= P1_MAX_MS else 'serious' if p90_ms <= TIMEOUT_MS else 'critical'
    if max_ms is not None:
        if max_ms > TIMEOUT_MS:
            st = worse(st, 'serious')
        elif max_ms > P1_MAX_MS:
            st = worse(st, 'warning')
    return st


def status_cost_spike(estimate, recent_estimates: list) -> str:
    values = [v for v in recent_estimates if v is not None]
    if estimate is None or not values:
        return 'good'
    med = statistics.median(values)
    return 'warning' if (estimate > med * COST_SPIKE_FACTOR and estimate > COST_SPIKE_FLOOR_USD) else 'good'


def status_alarms(alarms: list, available: bool = True) -> str:
    if not available:
        return 'unknown'
    if any(a['severity'] == 'P1' for a in alarms):
        return 'critical'
    if alarms:
        return 'warning'
    return 'good'


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _today_jst():
    return _now().astimezone(JST).date()


def _response(status: int, body: dict) -> dict:
    return {
        'statusCode': status,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, ensure_ascii=False, default=str),
    }


def is_admin(event) -> bool:
    claims = (event.get('requestContext', {}) or {}).get('authorizer', {}).get('claims', {}) or {}
    groups = claims.get('cognito:groups', '')
    group_list = groups if isinstance(groups, list) else [g.strip() for g in str(groups).split(',') if g.strip()]
    return ADMIN_GROUP_NAME in group_list


def _num(v, default=0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _int_or_none(v):
    return None if v is None else int(_num(v))


def _float_or_none(v):
    return None if v is None else float(_num(v))


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def _jst_hhmm(iso_value) -> str | None:
    if not iso_value:
        return None
    text = str(iso_value)
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST).strftime('%H:%M')


# ============================================================================= queries
def query_rows(scope: str, lo: str, hi: str) -> list:
    """scope-metricDate の Query。1MB で切れても LastEvaluatedKey をたどる。"""
    items = []
    kwargs = {
        'IndexName': 'scope-metricDate-index',
        'KeyConditionExpression': Key('scope').eq(scope) & Key('metricDate').between(lo, hi),
        'ScanIndexForward': True,
    }
    while True:
        resp = table.query(**kwargs)
        items.extend(resp.get('Items', []))
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            return items
        kwargs['ExclusiveStartKey'] = lek


def query_snapshots(scope: str, start_date, end_date) -> list:
    """Daily snapshots only (metricDate length 10)."""
    items = query_rows(scope, start_date.isoformat(), end_date.isoformat() + '￿')
    return [it for it in items if len(it.get('metricDate', '')) == 10]


def query_hourly(day) -> list:
    prefix = day.isoformat()
    return query_rows('hourly', prefix + 'T00', prefix + 'T23')


def query_cost_month(month: str) -> list:
    return query_rows('cost', f'{month}-01', f'{month}-31')


def latest_eval() -> dict | None:
    try:
        resp = table.query(
            IndexName='scope-metricDate-index',
            KeyConditionExpression=Key('scope').eq('eval'),
            ScanIndexForward=False, Limit=1,
        )
    except ClientError:
        return None
    items = resp.get('Items', [])
    if not items:
        return None
    it = items[0]
    return {'date': it.get('metricDate'), 'hit': _int_or_none(it.get('hitInCandidates')), 'n': _int_or_none(it.get('labeled')),
            'logicVersion': it.get('logicVersion')}


# ============================================================================= live (CloudWatch)
def live_alarms() -> tuple[list, bool]:
    out = []
    kwargs = {'AlarmNamePrefix': ALARM_PREFIX, 'StateValue': 'ALARM', 'MaxRecords': 100}
    try:
        while True:
            resp = cloudwatch.describe_alarms(**kwargs)
            for a in resp.get('MetricAlarms', []):
                name = a['AlarmName'][len(ALARM_PREFIX):]
                ts = a.get('StateUpdatedTimestamp')
                out.append({'name': name, 'severity': 'P1' if name.startswith('P1-') else 'P2',
                            'since': _iso(ts) if hasattr(ts, 'astimezone') else None})
            token = resp.get('NextToken')
            if not token:
                break
            kwargs['NextToken'] = token
    except (ClientError, BotoCoreError) as e:
        print(f"[metrics-read] DescribeAlarms error: {e}")
        return out, False
    return out, True


def live_last_60min(now: datetime) -> tuple[dict, bool]:
    start = now - timedelta(minutes=60)
    queries = []
    for i, name in enumerate(API_NAMES):
        for metric in ('Count', '5XXError'):
            queries.append({
                'Id': f'm{i}_{metric.lower()}',
                'MetricStat': {'Metric': {'Namespace': 'AWS/ApiGateway', 'MetricName': metric,
                                          'Dimensions': [{'Name': 'ApiName', 'Value': name}]},
                               'Period': 300, 'Stat': 'Sum'},
                'ReturnData': True,
            })
    rag = API_NAMES[0] if API_NAMES else f'rag-api-{ENVIRONMENT}'
    for stat, mid in (('p90', 'rag_p90'), ('Maximum', 'rag_max'), ('SampleCount', 'rag_count')):
        queries.append({
            'Id': mid,
            'MetricStat': {'Metric': {'Namespace': 'AWS/ApiGateway', 'MetricName': 'Latency',
                                      'Dimensions': [{'Name': 'ApiName', 'Value': rag}]},
                           'Period': 3600, 'Stat': stat},
            'ReturnData': True,
        })
    out = {'requests': 0, 'http5xx': 0, 'ragP90Ms': None, 'ragMaxMs': None, 'ragCount': 0}
    try:
        resp = cloudwatch.get_metric_data(MetricDataQueries=queries, StartTime=start, EndTime=now, ScanBy='TimestampAscending')
    except (ClientError, BotoCoreError) as e:
        print(f"[metrics-read] GetMetricData error: {e}")
        return out, False
    for r in resp.get('MetricDataResults', []):
        values = r.get('Values') or []
        mid = r.get('Id', '')
        if mid.endswith('_count') and not mid.startswith('rag'):
            out['requests'] += int(sum(values))
        elif mid.endswith('_5xxerror'):
            out['http5xx'] += int(sum(values))
        elif mid == 'rag_p90' and values:
            out['ragP90Ms'] = round(max(values), 1)
        elif mid == 'rag_max' and values:
            out['ragMaxMs'] = round(max(values), 1)
        elif mid == 'rag_count':
            out['ragCount'] = int(sum(values))
    return out, True


def live_alarm_transitions(now: datetime, hours: int = 24) -> tuple[list, bool]:
    out = []
    kwargs = {'HistoryItemType': 'StateUpdate', 'StartDate': now - timedelta(hours=hours), 'EndDate': now,
              'MaxRecords': 100, 'ScanBy': 'TimestampAscending'}
    try:
        while True:
            resp = cloudwatch.describe_alarm_history(**kwargs)
            for item in resp.get('AlarmHistoryItems', []):
                name = item.get('AlarmName', '')
                if not name.startswith(ALARM_PREFIX):
                    continue
                try:
                    data = json.loads(item.get('HistoryData') or '{}')
                except ValueError:
                    data = {}
                state = (data.get('newState') or {}).get('stateValue')
                if state not in ('ALARM', 'OK'):
                    continue
                ts = item.get('Timestamp')
                out.append({'alarm': name[len(ALARM_PREFIX):], 'state': state,
                            'at': _iso(ts) if hasattr(ts, 'astimezone') else str(ts)})
            token = resp.get('NextToken')
            if not token:
                break
            kwargs['NextToken'] = token
    except (ClientError, BotoCoreError) as e:
        print(f"[metrics-read] DescribeAlarmHistory error: {e}")
        return out, False
    return out, True


def active_notices(now: datetime) -> list:
    """公開中かつ未終了の告知（表示中）。announcements テーブルの GSI status-publishAt-index を使う。"""
    if announcements_table is None:
        return []
    now_iso = _iso(now)
    items = []
    try:
        for status in ('published', 'scheduled'):
            resp = announcements_table.query(
                IndexName='status-publishAt-index',
                KeyConditionExpression=Key('status').eq(status) & Key('publishAt').lte(now_iso),
                ScanIndexForward=False, Limit=20,
            )
            items.extend(resp.get('Items', []))
    except ClientError as e:
        print(f"[metrics-read] announcements query error: {e}")
        return []
    out = []
    for it in items:
        end = it.get('endAt')
        if end and str(end) < now_iso:
            continue
        out.append({
            'id': it.get('announcementId'),
            'title': it.get('title'),
            'severity': it.get('severity'),
            'since': it.get('publishAt'),
            'showInChat': bool(it.get('showInChat', it.get('severity') == 'critical')),
        })
    out.sort(key=lambda x: ({'critical': 0, 'warning': 1, 'info': 2}.get(x['severity'], 3), x['since'] or ''))
    return out


# ============================================================================= dashboard
def _by_date(rows: list) -> dict:
    return {r['metricDate']: r for r in rows}


def _latency_of(row: dict | None) -> dict:
    if not row:
        return {'p90Ms': None, 'p50Ms': None, 'maxMs': None, 'count': None}
    lat = (row.get('apiLatency') or {}).get('rag')
    if lat:
        return {'p90Ms': _float_or_none(lat.get('p90Ms')), 'p50Ms': _float_or_none(lat.get('p50Ms')),
                'maxMs': _float_or_none(lat.get('maxMs')), 'count': _int_or_none(lat.get('count'))}
    # 旧行: latencyP90 は秒
    p90 = row.get('latencyP90')
    return {'p90Ms': None if p90 is None else round(_num(p90) * 1000, 1), 'p50Ms': None, 'maxMs': None, 'count': None}


def funnel_row(rows: list) -> dict:
    """1 日または複数日の合算。資料を開いた（messagesWithOpen）は行に無ければ未計測。"""
    if not rows:
        return {'signIns': None, 'queries': None, 'pages': None, 'opened': None, 'good': None,
                'unreached': None, 'notFound': None, 'bad': None, 'reformulated': None}

    def total(key):
        vals = [r.get(key) for r in rows if r.get(key) is not None]
        return int(sum(_num(v) for v in vals)) if vals else None

    opened = total('messagesWithOpen')
    return {
        'signIns': total('signIns'),
        'queries': total('queries'),
        'pages': total('pages'),
        'opened': 'unmeasured' if opened is None else opened,
        'good': total('feedbackGood'),
        'unreached': total('unreached'),
        'notFound': total('notFound'),
        'bad': total('feedbackBad'),
        'reformulated': total('reformulated'),
    }


def events_from(rows: list, live: list, today: date) -> list:
    """アラーム遷移を「出来事」の行にする。ALARM に続く同名の OK は継続時間として畳む。"""
    seen = set()
    transitions = []
    for r in rows:
        for t in r.get('alarmTransitions') or []:
            key = (t.get('alarm'), t.get('state'), t.get('at'))
            if key not in seen:
                seen.add(key)
                transitions.append(dict(t))
    for t in live:
        key = (t.get('alarm'), t.get('state'), t.get('at'))
        if key not in seen:
            seen.add(key)
            transitions.append(dict(t))
    transitions.sort(key=lambda t: t.get('at') or '')

    open_alarms = {}
    events = []
    for t in transitions:
        alarm = t['alarm']
        if t['state'] == 'ALARM':
            ev = {'at': t['at'], 'kind': 'alarm', 'alarm': alarm, 'severity': 'P1' if alarm.startswith('P1-') else 'P2',
                  'title': alarm, 'durationSec': None, 'resolvedAt': None, **log_hint(alarm, t['at'])}
            open_alarms[alarm] = ev
            events.append(ev)
        else:
            ev = open_alarms.pop(alarm, None)
            if ev:
                ev['resolvedAt'] = t['at']
                try:
                    a = datetime.fromisoformat(ev['at'].replace('Z', '+00:00'))
                    b = datetime.fromisoformat(t['at'].replace('Z', '+00:00'))
                    ev['durationSec'] = int((b - a).total_seconds())
                except ValueError:
                    pass
            else:
                events.append({'at': t['at'], 'kind': 'ok', 'alarm': alarm, 'severity': 'P1' if alarm.startswith('P1-') else 'P2',
                               'title': alarm, 'durationSec': None, 'resolvedAt': None, **log_hint(alarm, t['at'])})
    events.sort(key=lambda e: e['at'], reverse=True)
    return events


def log_hint(alarm: str, at_iso: str) -> dict:
    """アラーム名から、最初に見るロググループと保存クエリ、時間範囲（前後 15 分）を決める（設計 §4.4）。"""
    name = alarm.split('-', 1)[1] if '-' in alarm else alarm   # P1-xxx → xxx
    env = LOG_GROUP_ENV
    if name.startswith('rag-api-4xx') or name.startswith('chat-api-4xx') or name.startswith('auth-api-4xx'):
        api = name.split('-api')[0]
        group, query = f'/aws/apigateway/{api}-api-{env}', f'EleKnowledge/{env}/api-4xx-breakdown'
    elif name.startswith('rag-duration'):
        group, query = f'/aws/lambda/rag-{env}', f'EleKnowledge/{env}/slow-requests'
    elif name.startswith('rag-'):
        group, query = f'/aws/lambda/rag-{env}', f'EleKnowledge/{env}/rag-error-lines'
    elif name.startswith('chat-archive'):
        group, query = f'/aws/lambda/eleknowledge-chat-archive-{env}', None
    elif name.startswith('chat-'):
        group, query = f'/aws/lambda/chat-{env}', f'EleKnowledge/{env}/chat-error-lines'
    elif name.startswith('auth-api') or name.startswith('login-'):
        group, query = f'/aws/apigateway/auth-api-{env}', f'EleKnowledge/{env}/api-4xx-breakdown'
    elif name.startswith('metrics-'):
        group, query = f'/aws/lambda/metrics-aggregator-{env}', None
    elif name.startswith('cognito'):
        group, query = None, None
    else:
        group, query = None, None
    try:
        at = datetime.fromisoformat(at_iso.replace('Z', '+00:00'))
        window = {'from': _iso(at - timedelta(minutes=15)), 'to': _iso(at + timedelta(minutes=15))}
    except (ValueError, AttributeError):
        window = {'from': None, 'to': None}
    return {'logGroup': group, 'queryName': query, **window}


def month_actual(cost_rows: list) -> tuple[float | None, str | None]:
    settled = [r for r in cost_rows if r.get('settled')]
    if not settled:
        return None, None
    total = sum(_num((r.get('bedrock') or {}).get('total')) for r in settled)
    return round(total, 2), max(r['metricDate'] for r in settled)


def build_dashboard(now: datetime, rows: list, hourly_today: list, alarms: list, last60: dict,
                    live_transitions: list, notices: list, cost_rows: list, eval_row: dict | None, trend_days: int,
                    cloudwatch_available: bool = True) -> dict:
    today = now.astimezone(JST).date()
    yesterday = today - timedelta(days=1)
    by = _by_date(rows)
    y = by.get(yesterday.isoformat())
    t = by.get(today.isoformat())

    # --- now
    fresh_status = 'good'
    if y is None and now.astimezone(JST).hour >= FRESHNESS_WARN_HOUR_JST:
        fresh_status = 'warning'
    now_block = {
        'alarms': alarms,
        'status': status_alarms(alarms, available=cloudwatch_available),
        'cloudwatchAvailable': cloudwatch_available,
        'last60min': last60,
        'freshness': {
            'yesterdayAggregatedAt': y.get('aggregatedAt') if y else None,
            'todayPartialAt': t.get('aggregatedAt') if t and t.get('partial') else None,
            'status': fresh_status,
        },
        'activeNotices': notices,
    }

    # --- yesterday
    p1 = _int_or_none(y.get('incidents')) if y else None
    http5xx = _int_or_none(y.get('http5xx')) if y else None
    inc_status = 'good'
    if y:
        inc_status = worse(status_5xx(http5xx or 0), 'serious' if (p1 or 0) >= 1 else 'good')
    lat = _latency_of(y)
    show_p90 = lat['count'] is None or lat['count'] >= MIN_SAMPLES_FOR_P90
    recent_estimates = [_float_or_none(by[d].get('estimatedBedrockCostUsd')) for d in
                        [(yesterday - timedelta(days=n)).isoformat() for n in range(1, 8)] if d in by]
    est = _float_or_none(y.get('estimatedBedrockCostUsd')) if y else None
    actual, actual_through = month_actual(cost_rows)
    same_weekday = by.get((yesterday - timedelta(days=7)).isoformat())
    yesterday_block = {
        'date': yesterday.isoformat(),
        'exists': y is not None,
        'incidents': {'p1Transitions': p1, 'http5xx': http5xx,
                      'byApi': {k: int(_num(v)) for k, v in (y.get('http5xxByApi') or {}).items()} if y else {},
                      'status': inc_status},
        'latency': {**lat, 'showP90': show_p90, 'status': status_latency(lat['p90Ms'] if show_p90 else None, lat['maxMs']) if y else 'good'},
        'unreached': {'total': _int_or_none(y.get('unreached')) if y else None,
                      'notFound': _int_or_none(y.get('notFound')) if y else None,
                      'bad': _int_or_none(y.get('feedbackBad')) if y else None,
                      'reformulated': _int_or_none(y.get('reformulated')) if y else None,
                      'open': _int_or_none(y.get('triageOpen')) if y else None},
        'usage': {'queries': _int_or_none(y.get('queries')) if y else None,
                  'uniqueUsers': _int_or_none(y.get('activeUsers')) if y else None,
                  'newUsers': _int_or_none(y.get('newUsers')) if y else None,
                  'queriesSameWeekdayLastWeek': _int_or_none(same_weekday.get('queries')) if same_weekday else None},
        'bedrockCost': {'estimatedUsd': est, 'estimateSource': y.get('estimateSource') if y else None,
                        'monthActualUsd': actual, 'actualThrough': actual_through,
                        'status': status_cost_spike(est, recent_estimates)},
    }

    today_block = None
    if t and t.get('partial'):
        today_block = {'asOf': _jst_hhmm(t.get('aggregatedAt')), 'queries': _int_or_none(t.get('queries')),
                       'unreached': _int_or_none(t.get('unreached')), 'http5xx': _int_or_none(t.get('http5xx'))}

    # --- funnel
    last7 = [by[d] for d in [(yesterday - timedelta(days=n)).isoformat() for n in range(0, 7)] if d in by]
    funnel = {'yesterday': funnel_row([y] if y else []), 'last7d': funnel_row(last7),
              'last7dRange': {'from': (yesterday - timedelta(days=6)).isoformat(), 'to': yesterday.isoformat()},
              'showRates': bool(last7 and sum(int(_num(r.get('queries'))) for r in last7) >= RATE_DENOMINATOR_MIN)}

    # --- trend
    trend_rows = [by[d] for d in [(yesterday - timedelta(days=n)).isoformat() for n in range(trend_days - 1, -1, -1)] if d in by]
    trend = {
        'days': trend_days,
        'queriesByDay': [{'date': r['metricDate'], 'total': int(_num(r.get('queries'))), 'unreached': int(_num(r.get('unreached')))} for r in trend_rows],
        'latencyByDay': [{'date': r['metricDate'], **{k: v for k, v in _latency_of(r).items() if k in ('p90Ms', 'maxMs')}} for r in trend_rows],
        'hourlyToday': [{'hour': it['metricDate'][-2:], 'queries': int(_num(it.get('queries'))), 'unreached': int(_num(it.get('unreached')))} for it in hourly_today],
    }

    # --- events (last 7 days incl. today partial)
    event_rows = [by[d] for d in [(today - timedelta(days=n)).isoformat() for n in range(0, 8)] if d in by]
    events = events_from(event_rows, live_transitions, today)

    # --- reference
    doc_counts = {}
    for r in [by[d] for d in [(yesterday - timedelta(days=n)).isoformat() for n in range(0, 30)] if d in by]:
        for d in r.get('topDocuments') or []:
            if d.get('name'):
                doc_counts[d['name']] = doc_counts.get(d['name'], 0) + int(_num(d.get('count')))
    top_docs = sorted([{'name': n, 'count': c} for n, c in doc_counts.items()], key=lambda x: x['count'], reverse=True)[:10]

    return {
        'generatedAt': _iso(now),
        'today': today.isoformat(),
        'now': now_block,
        'yesterday': yesterday_block,
        'todaySoFar': today_block,
        'funnel': funnel,
        'trend': trend,
        'events': events,
        'reference': {'topDocuments': top_docs, 'lastEval': eval_row},
        'thresholds': {'sloP90Ms': SLO_P90_MS, 'p1MaxMs': P1_MAX_MS, 'timeoutMs': TIMEOUT_MS, 'rateDenominatorMin': RATE_DENOMINATOR_MIN},
    }


# ============================================================================= cost
def classify_service(name: str) -> str:
    """Cost Explorer のサービス名を 4 分類（設計 §5.2）に振り分ける。"""
    n = (name or '').lower()
    if name == BEDROCK_COST_SERVICE_NAME:
        return 'bedrock'
    if name == AMPLIFY_COST_SERVICE_NAME:
        return 'amplify'
    if any(k in n for k in SHARED_SERVICE_KEYWORDS):
        return 'shared'
    if 'bedrock' in n:
        return 'otherSystems'
    if any(k in n for k in UNATTRIBUTED_SERVICE_KEYWORDS):
        return 'unattributed'
    return 'otherSystems'


def build_cost(now: datetime, month: str, cost_rows: list, daily_rows: list, budget_usd: float) -> dict:
    settled = [r for r in cost_rows if r.get('settled')]
    settled_through = max((r['metricDate'] for r in settled), default=None)

    buckets = {'bedrock': 0.0, 'amplify': 0.0, 'unattributed': {}, 'shared': {}, 'otherSystems': {}}
    bedrock_split = {'input': 0.0, 'output': 0.0, 'cache': 0.0, 'other': 0.0}
    for r in settled:
        for svc, usd in (r.get('byService') or {}).items():
            cls = classify_service(svc)
            usd = _num(usd)
            if cls == 'bedrock':
                buckets['bedrock'] += usd
            elif cls == 'amplify':
                buckets['amplify'] += usd
            else:
                buckets[cls][svc] = buckets[cls].get(svc, 0.0) + usd
        b = r.get('bedrock') or {}
        for k in bedrock_split:
            bedrock_split[k] += _num(b.get(k))

    def rounded(d):
        return {k: round(v, 2) for k, v in sorted(d.items(), key=lambda kv: -kv[1])}

    confirmed_total = buckets['bedrock'] + buckets['amplify']

    # --- checks
    month_daily = [r for r in daily_rows if r['metricDate'].startswith(month)]
    sole_flags = [r.get('soleUserOk') for r in month_daily if r.get('soleUserOk') is not None]
    invocations = sum(int(_num((r.get('bedrock') or {}).get('invocations'))) for r in month_daily if r.get('bedrock'))
    pages = sum(int(_num(r.get('pages'))) for r in month_daily)
    model_ids = sorted({(r.get('bedrock') or {}).get('modelId') for r in month_daily if (r.get('bedrock') or {}).get('modelId')})
    sole_ok = None if not sole_flags else all(sole_flags)

    settled_dates = {r['metricDate'] for r in settled}
    estimate_same_days = [ _float_or_none(r.get('estimatedBedrockCostUsdUtc')) for r in daily_rows if r['metricDate'] in settled_dates]
    estimate_same_days = [v for v in estimate_same_days if v is not None]
    estimate_total = round(sum(estimate_same_days), 2) if estimate_same_days else None
    diff_pct = None
    if estimate_total and buckets['bedrock']:
        diff_pct = round((buckets['bedrock'] / estimate_total - 1) * 100, 1)
    ave_status = 'good' if diff_pct is None or abs(diff_pct) <= ACTUAL_VS_ESTIMATE_WARN_PCT else 'warning'

    # --- per query / projection
    month_queries = sum(int(_num(r.get('queries'))) for r in month_daily if not r.get('partial'))
    month_pages = sum(int(_num(r.get('pages'))) for r in month_daily if not r.get('partial'))
    per_query = round(buckets['bedrock'] / month_queries, 4) if month_queries and buckets['bedrock'] else None
    per_answer = round(buckets['bedrock'] / month_pages, 4) if month_pages and buckets['bedrock'] else None
    projection = [{'queriesPerDay': n, 'monthlyUsd': round(n * per_query * 30, 0) if per_query else None} for n in (100, 300, 1000)]

    days_elapsed = len(settled_dates)
    forecast = round(buckets['bedrock'] / days_elapsed * 30, 2) if days_elapsed else None

    return {
        'generatedAt': _iso(now),
        'month': month,
        'settledThrough': settled_through,
        'basis': 'UTC',
        'confirmed': {
            'total': round(confirmed_total, 2),
            'bedrock': {'service': BEDROCK_COST_SERVICE_NAME, 'total': round(buckets['bedrock'], 2),
                        **{k: round(v, 2) for k, v in bedrock_split.items()}},
            'amplify': round(buckets['amplify'], 2),
            'budgetUsd': budget_usd,
            'budgetPct': round(buckets['bedrock'] / budget_usd * 100, 1) if budget_usd else None,
            'forecastUsd': forecast,
        },
        'unattributed': {'total': round(sum(buckets['unattributed'].values()), 2), 'byService': rounded(buckets['unattributed']), 'note': 'tag_pending'},
        'shared': {'total': round(sum(buckets['shared'].values()), 2), 'byService': rounded(buckets['shared'])},
        'otherSystems': {'total': round(sum(buckets['otherSystems'].values()), 2), 'byService': rounded(buckets['otherSystems'])},
        'checks': {
            'soleUser': {'ok': sole_ok, 'invocations': invocations, 'answers': pages,
                         'detail': f'Bedrock 呼び出し {invocations} 回 / 候補あり回答 {pages} 件'},
            'actualVsEstimate': {'actual': round(buckets['bedrock'], 2), 'estimate': estimate_total, 'diffPct': diff_pct, 'status': ave_status,
                                 'days': days_elapsed},
            'modelIds': model_ids,
        },
        'daily': [{'date': r['metricDate'], 'bedrockUsd': round(_num((r.get('bedrock') or {}).get('total')), 4),
                   'totalUsd': round(_num(r.get('total')), 2), 'settled': bool(r.get('settled'))} for r in cost_rows],
        'queriesDaily': [{'date': r['metricDate'], 'queries': int(_num(r.get('queries')))} for r in daily_rows if r['metricDate'].startswith(month)],
        'perQuery': {'actualUsd': per_query, 'perAnswerUsd': per_answer, 'queries': month_queries, 'answers': month_pages,
                     'traceMedianUsd': None, 'traceP90Usd': None},
        'projection': projection,
    }


# ============================================================================= legacy (/admin/metrics)
def status_for(name: str, value: float) -> str:
    for limit, label in THRESHOLDS.get(name, []):
        if value <= limit:
            return label
    return 'critical'


def resolve_range(qs: dict):
    period = (qs.get('period') or 'week').lower()
    today = _today_jst()
    if period == 'today':
        start = today
    elif period == 'month':
        start = today - timedelta(days=29)
    elif period == 'custom' and qs.get('from') and qs.get('to'):
        start = datetime.fromisoformat(qs['from']).date()
        return start, datetime.fromisoformat(qs['to']).date(), 'custom'
    else:  # week (default)
        start = today - timedelta(days=6)
        period = 'week'
    return start, today, period


def unique_users(items: list) -> int:
    union = set()
    legacy_max = 0
    for it in items:
        ids = it.get('userIds')
        if isinstance(ids, list):
            union.update(ids)
        else:
            legacy_max = max(legacy_max, int(_num(it.get('activeUsers'))))
    return max(len(union), legacy_max)


def freshness(items: list) -> dict:
    latest = items[-1] if items else {}
    return {'latestDate': latest.get('metricDate'), 'aggregatedAt': latest.get('aggregatedAt'), 'partial': bool(latest.get('partial', False))}


def build_payload(items: list, period: str, hourly: list | None = None) -> dict:
    queries_by_day = [{'date': it['metricDate'], 'value': int(_num(it.get('queries')))} for it in items]
    like_by_day = [{'date': it['metricDate'], 'value': round(_num(it.get('likeRate')), 4)} for it in items]
    total_queries = sum(int(_num(it.get('queries'))) for it in items)
    total_good = sum(int(_num(it.get('feedbackGood'))) for it in items)
    total_bad = sum(int(_num(it.get('feedbackBad'))) for it in items)
    like_rate = round(total_good / (total_good + total_bad), 4) if (total_good + total_bad) else 0.0

    def delta(seq):
        return round(seq[-1]['value'] - seq[-2]['value'], 4) if len(seq) >= 2 else 0.0

    latest = items[-1] if items else {}
    err, lat, x5 = _num(latest.get('errorRate')), _num(latest.get('latencyP90')), _num(latest.get('http5xx'))
    doc_counts = {}
    for it in items:
        for d in it.get('topDocuments', []) or []:
            if d.get('name'):
                doc_counts[d['name']] = doc_counts.get(d['name'], 0) + int(_num(d.get('count')))
    top_documents = sorted([{'name': n, 'count': c} for n, c in doc_counts.items()], key=lambda x: x['count'], reverse=True)[:5]
    series = {'queriesByDay': queries_by_day, 'likeRateByDay': like_by_day}
    if hourly is not None:
        series['queriesByHour'] = [{'hour': it['metricDate'][-2:], 'value': int(_num(it.get('queries'))), 'unreached': int(_num(it.get('unreached')))} for it in hourly]
    return {
        'period': period,
        'generatedAt': _iso(_now()),
        'freshness': freshness(items),
        'kpi': {'likeRate': {'value': like_rate, 'delta': delta(like_by_day)},
                'queries': {'value': total_queries, 'delta': delta(queries_by_day)},
                'activeUsers': {'value': unique_users(items)}},
        'series': series,
        'topDocuments': top_documents,
        'health': {'errorRate': {'value': round(err, 4), 'status': status_for('errorRate', err)},
                   'latencyP90': {'value': round(lat, 2), 'status': status_for('latencyP90', lat)},
                   'http5xx': {'value': int(x5), 'status': status_for('http5xx', x5)},
                   'openIncidents': int(_num(latest.get('incidents')))},
    }


# ============================================================================= handler
def handle_dashboard(qs: dict) -> dict:
    now = _now()
    today = now.astimezone(JST).date()
    try:
        trend_days = int(qs.get('trend') or 14)
    except ValueError:
        trend_days = 14
    trend_days = min(max(trend_days, 7), 90)
    rows = query_snapshots('overall', today - timedelta(days=max(trend_days, 31)), today)
    hourly_today = query_hourly(today)
    month = now.strftime('%Y-%m')
    cost_rows = query_cost_month(month)
    alarms, alarms_available = live_alarms()
    last60, last60_available = live_last_60min(now)
    live_transitions, transitions_available = live_alarm_transitions(now)
    payload = build_dashboard(
        now, rows, hourly_today, alarms, last60, live_transitions,
        active_notices(now), cost_rows, latest_eval(), trend_days,
        cloudwatch_available=alarms_available and last60_available and transitions_available,
    )
    return payload


def handle_cost(qs: dict) -> dict:
    now = _now()
    month = qs.get('month') or now.strftime('%Y-%m')
    try:
        datetime.strptime(month, '%Y-%m')
    except ValueError:
        month = now.strftime('%Y-%m')
    cost_rows = query_cost_month(month)
    first = date.fromisoformat(f'{month}-01')
    daily_rows = query_snapshots('overall', first, first + timedelta(days=31))
    return build_cost(now, month, cost_rows, daily_rows, BEDROCK_BUDGET_USD)


def lambda_handler(event, context):
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    if method == 'OPTIONS':
        return _response(200, {})

    if not is_admin(event):
        return _response(403, {'error': 'Forbidden', 'message': 'Admin privilege required'})

    path = (event.get('path') or event.get('rawPath') or '').rstrip('/')
    try:
        qs = event.get('queryStringParameters') or {}
        if path.endswith('/admin/metrics/dashboard'):
            return _response(200, handle_dashboard(qs))
        if path.endswith('/admin/metrics/cost'):
            return _response(200, handle_cost(qs))
        scope = qs.get('scope') or 'overall'
        start_date, end_date, period = resolve_range(qs)
        items = query_snapshots(scope, start_date, end_date)
        hourly = query_hourly(end_date) if period == 'today' else None
        return _response(200, build_payload(items, period, hourly))

    except ClientError as e:
        print(f"[metrics-read] ClientError: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'Failed to load metrics'})
    except Exception as e:  # noqa: BLE001
        print(f"[metrics-read] Unexpected error: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'An unexpected error occurred'})
