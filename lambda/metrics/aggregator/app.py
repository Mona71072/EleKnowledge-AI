"""
EleKnowledge Metrics - Aggregator (EventBridge-triggered)

Runs daily. Aggregates the previous day's chat activity from the chatlogs table
and pulls error/latency figures from CloudWatch, then writes one durable snapshot
row per day into the metrics table. Idempotent: re-running the same day overwrites
(PutItem keyed by metricDate+scope), so retries never double-count.

The chatlogs table is TTL-bounded (~60 days), so a filtered daily scan is small and
runs off-peak; the snapshot is what persists long-term (~13 months) after logs expire.

Event override (manual re-run):
  { "date": "2026-07-20" }  -> aggregate that UTC day
"""
import json
import os
from datetime import datetime, timedelta, timezone
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
METRIC_TTL_DAYS = int(os.environ.get('METRIC_TTL_DAYS', '400'))

chatlogs_table = dynamodb.Table(CHATLOGS_TABLE)
metrics_table = dynamodb.Table(METRICS_TABLE)


def target_day(event) -> str:
    if isinstance(event, dict) and event.get('date'):
        return event['date']
    # previous UTC day
    return (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()


def scan_day(date_str: str) -> list:
    """Paginated scan of chatlogs for a single UTC day (timestamp prefix)."""
    lo = f"{date_str}T00:00:00"
    hi = f"{date_str}T23:59:59.999999"
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


def aggregate_chat(items: list) -> dict:
    queries = 0
    sessions = set()
    active_users = set()
    good = bad = 0
    doc_counts = {}

    for it in items:
        role = it.get('role')
        session_id = it.get('sessionId')
        if session_id:
            sessions.add(session_id)
        if role == 'user':
            queries += 1
            if it.get('userId'):
                active_users.add(it['userId'])

        fb = it.get('feedback')
        if fb == 'good':
            good += 1
        elif fb == 'bad':
            bad += 1

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
        'feedbackGood': good,
        'feedbackBad': bad,
        'likeRate': like_rate,
        'topDocuments': top_documents,
    }


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


def aggregate_health(date_str: str) -> dict:
    """Best-effort CloudWatch pull; defaults to zeros if metrics are absent."""
    start = datetime.fromisoformat(f"{date_str}T00:00:00").replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)

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


def to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, list):
        return [to_decimal(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_decimal(v) for k, v in obj.items()}
    return obj


def lambda_handler(event, context):
    date_str = target_day(event or {})
    print(f"[aggregator] Aggregating metrics for {date_str}")

    items = scan_day(date_str)
    chat = aggregate_chat(items)
    health = aggregate_health(date_str)

    ttl = int((datetime.now(timezone.utc) + timedelta(days=METRIC_TTL_DAYS)).timestamp())
    snapshot = {
        'metricDate': date_str,
        'scope': 'overall',
        **chat,
        **health,
        'ttl': ttl,
        'aggregatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    }

    metrics_table.put_item(Item=to_decimal(snapshot))
    print(f"[aggregator] Wrote snapshot: {json.dumps({k: v for k, v in snapshot.items() if k != 'topDocuments'}, default=str)}")
    return {'statusCode': 200, 'date': date_str, 'queries': chat['queries'], 'likeRate': chat['likeRate']}
