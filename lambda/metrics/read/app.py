"""
EleKnowledge Metrics - Read (admin only)

GET /admin/metrics?period=today|week|month|custom&from=&to=&scope=overall

Reads pre-aggregated daily snapshots from the metrics table (no heavy scans),
shapes them into KPI / time-series / rankings / health for the dashboard.
"""
import json
import os
from datetime import datetime, timedelta, timezone

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))

METRICS_TABLE = os.environ.get('METRICS_TABLE')
ADMIN_GROUP_NAME = os.environ.get('ADMIN_GROUP_NAME', 'admin')
table = dynamodb.Table(METRICS_TABLE)

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,OPTIONS',
}

# Health thresholds -> status (good/warning/serious/critical)
THRESHOLDS = {
    'errorRate': [(0.01, 'good'), (0.05, 'warning'), (0.10, 'serious')],   # else critical
    'latencyP90': [(3.0, 'good'), (6.0, 'warning'), (10.0, 'serious')],
    'http5xx': [(0, 'good'), (5, 'warning'), (20, 'serious')],
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


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


def status_for(name: str, value: float) -> str:
    for limit, label in THRESHOLDS.get(name, []):
        if value <= limit:
            return label
    return 'critical'


def resolve_range(qs: dict):
    period = (qs.get('period') or 'week').lower()
    today = _now().date()
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


def query_snapshots(scope: str, start_date, end_date) -> list:
    """Query daily snapshots for a scope across a date range.

    Uses GSI scope-metricDate-index (PK=scope, SK=metricDate) so a single Query
    returns the range with no table scan. Hourly rows (metricDate length 13) are
    excluded so only daily snapshots (length 10) feed the dashboard.
    """
    lo, hi = start_date.isoformat(), end_date.isoformat() + '￿'
    resp = table.query(
        IndexName='scope-metricDate-index',
        KeyConditionExpression=Key('scope').eq(scope) & Key('metricDate').between(lo, hi),
        ScanIndexForward=True,
    )
    items = resp.get('Items', [])
    return [it for it in items if len(it.get('metricDate', '')) == 10]


def build_payload(items: list, period: str) -> dict:
    queries_by_day = [{'date': it['metricDate'], 'value': int(_num(it.get('queries')))} for it in items]
    like_by_day = [{'date': it['metricDate'], 'value': round(_num(it.get('likeRate')), 4)} for it in items]

    total_queries = sum(int(_num(it.get('queries'))) for it in items)
    total_good = sum(int(_num(it.get('feedbackGood'))) for it in items)
    total_bad = sum(int(_num(it.get('feedbackBad'))) for it in items)
    like_rate = round(total_good / (total_good + total_bad), 4) if (total_good + total_bad) else 0.0
    active_users = max((int(_num(it.get('activeUsers'))) for it in items), default=0)

    # deltas: compare last day vs previous available day
    def delta(seq):
        if len(seq) < 2:
            return 0.0
        return round(seq[-1]['value'] - seq[-2]['value'], 4)

    latest = items[-1] if items else {}
    err = _num(latest.get('errorRate'))
    lat = _num(latest.get('latencyP90'))
    x5 = _num(latest.get('http5xx'))

    # Aggregate top documents across range
    doc_counts = {}
    for it in items:
        for d in it.get('topDocuments', []) or []:
            name = d.get('name')
            if name:
                doc_counts[name] = doc_counts.get(name, 0) + int(_num(d.get('count')))
    top_documents = sorted(
        [{'name': n, 'count': c} for n, c in doc_counts.items()],
        key=lambda x: x['count'], reverse=True
    )[:5]

    return {
        'period': period,
        'generatedAt': _now().isoformat().replace('+00:00', 'Z'),
        'kpi': {
            'likeRate': {'value': like_rate, 'delta': delta(like_by_day)},
            'queries': {'value': total_queries, 'delta': delta(queries_by_day)},
            'activeUsers': {'value': active_users},
        },
        'series': {
            'queriesByDay': queries_by_day,
            'likeRateByDay': like_by_day,
        },
        'topDocuments': top_documents,
        'health': {
            'errorRate': {'value': round(err, 4), 'status': status_for('errorRate', err)},
            'latencyP90': {'value': round(lat, 2), 'status': status_for('latencyP90', lat)},
            'http5xx': {'value': int(x5), 'status': status_for('http5xx', x5)},
            'openIncidents': int(_num(latest.get('incidents'))),
        },
    }


def lambda_handler(event, context):
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    if method == 'OPTIONS':
        return _response(200, {})

    if not is_admin(event):
        return _response(403, {'error': 'Forbidden', 'message': 'Admin privilege required'})

    try:
        qs = event.get('queryStringParameters') or {}
        scope = qs.get('scope') or 'overall'
        start_date, end_date, period = resolve_range(qs)
        items = query_snapshots(scope, start_date, end_date)
        return _response(200, build_payload(items, period))

    except ClientError as e:
        print(f"[metrics-read] ClientError: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'Failed to load metrics'})
    except Exception as e:  # noqa: BLE001
        print(f"[metrics-read] Unexpected error: {e}")
        return _response(500, {'error': 'InternalServerError', 'message': 'An unexpected error occurred'})
