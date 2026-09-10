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

- {"mode": "cost-probe"}  Cost Explorer を 1 回だけ呼んで結果をログに出す（Lambda ロールで呼べるかの確認。設計 §8.1）

日次行には chatlogs 由来の KPI に加えて、CloudWatch（API Gateway / Amplify / Cognito / Bedrock）と
アラーム履歴、SSM 単価による推定 Bedrock 費を入れる。daily では Cost Explorer から直近 3 日（UTC 日）の
実額を scope=cost の行として保存する（設計: docs/design-2026-09-10-dashboard-v2.md §5.4 / §6.1）。

冪等: 同じ metricDate + scope は PutItem で上書きされるため、再実行しても二重計上しない。
TTL: 日次 KPI は無期限保持（issue #86 決定）。ttl 属性は書かない。
"""
import json
import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
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
# 監視対象 API（順番は rag, chat, auth, app）。短縮名は short_api_name() で決める
API_NAMES = [n.strip() for n in os.environ.get(
    'API_NAMES',
    f'rag-api-{ENVIRONMENT},chat-api-{ENVIRONMENT},auth-api-{ENVIRONMENT},announcements-monitoring-api-{ENVIRONMENT}',
).split(',') if n.strip()]
ALARM_PREFIX = os.environ.get('ALARM_PREFIX', f'EleKnowledge-{ENVIRONMENT}-')
AMPLIFY_APP_ID = os.environ.get('AMPLIFY_APP_ID', '')
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID', '')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID', '')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', '')
# Cost Explorer 上の Bedrock モデル行のサービス名（モデルごとに別サービスとして出る）
BEDROCK_COST_SERVICE_NAME = os.environ.get('BEDROCK_COST_SERVICE_NAME', 'Claude Sonnet 5 (Amazon Bedrock Edition)')
UNIT_PRICE_PARAM = os.environ.get('UNIT_PRICE_PARAM', f'/eleknowledge/{ENVIRONMENT}/bedrock-unit-price')
COST_EXPLORER_ENABLED = os.environ.get('COST_EXPLORER_ENABLED', 'true').lower() == 'true'
COST_DAYS = int(os.environ.get('COST_DAYS', '3'))
# 「唯一の利用者」判定: Bedrock 呼び出し数が「候補あり」回答数 × 1.05 + 2 を超えたら他利用者あり
SOLE_USER_TOLERANCE = 0.05

# Cost Explorer のエンドポイントは us-east-1 のみ
ce = boto3.client('ce', region_name='us-east-1')
ssm = boto3.client('ssm', region_name=REGION)

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
    document_opens = 0
    messages_with_open = 0
    reformulated = 0
    triage_open = 0
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
                # 未振り分け: 到達できなかった回答のうち triage が無いか open のもの（設計 §9.4）
                if (it.get('triage') or {}).get('status', 'open') == 'open':
                    triage_open += 1
            opens = int(it.get('documentOpens') or 0)
            if opens > 0:
                document_opens += opens
                messages_with_open += 1
            # 言い換え: 回答直後に同じセッションで次の質問が来て、👍 も資料クリックも無い（別立て B2）
            if it.get('reformulatedAt') and fb != 'good' and opens == 0:
                reformulated += 1

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
        'triageOpen': triage_open,
        'documentOpens': document_opens,
        'messagesWithOpen': messages_with_open,
        'reformulated': reformulated,
        'productWishes': wishes,
        'topDocuments': top_documents,
    }


def count_new_users(user_ids: list, day: date) -> int:
    """その日に初めて発話した利用者の数。GSI userId-timestamp-index で最古の行を 1 件引く。"""
    new_users = 0
    for uid in user_ids:
        try:
            resp = chatlogs_table.query(
                IndexName='userId-timestamp-index',
                KeyConditionExpression=Key('userId').eq(uid),
                ScanIndexForward=True,
                Limit=1,
                ProjectionExpression='#ts',
                ExpressionAttributeNames={'#ts': 'timestamp'},
            )
        except ClientError as e:
            print(f"[aggregator] newUsers query error for user: {e}")
            continue
        first = (resp.get('Items') or [{}])[0].get('timestamp')
        if first and jst_date_of(first) == day:
            new_users += 1
    return new_users


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
def _cw_stats(namespace, metric, dimensions, start, end, statistics=None, extended=None) -> dict:
    """GetMetricStatistics を 1 日 1 期間で呼び、Sum / SampleCount は合算、Maximum と百分位は最大値で丸める。

    複数の datapoint が返った場合（期間の丸め）の百分位は近似になる。件数が無ければ 0。
    """
    kwargs = {
        'Namespace': namespace, 'MetricName': metric, 'Dimensions': dimensions,
        'StartTime': start, 'EndTime': end, 'Period': 86400,
    }
    if statistics:
        kwargs['Statistics'] = statistics
    if extended:
        kwargs['ExtendedStatistics'] = extended
    out = {k: 0.0 for k in (statistics or []) + (extended or [])}
    try:
        resp = cloudwatch.get_metric_statistics(**kwargs)
    except ClientError as e:
        print(f"[aggregator] CloudWatch {namespace}/{metric} error: {e}")
        return out
    for p in resp.get('Datapoints', []):
        for k in statistics or []:
            v = p.get(k)
            if v is None:
                continue
            out[k] = max(out[k], v) if k == 'Maximum' else out[k] + v
        for k in extended or []:
            v = (p.get('ExtendedStatistics') or {}).get(k)
            if v is not None:
                out[k] = max(out[k], v)
    return out


def _cw_sum(namespace, metric, dimensions, start, end) -> float:
    return _cw_stats(namespace, metric, dimensions, start, end, statistics=['Sum'])['Sum']


def short_api_name(api_name: str) -> str:
    """rag-api-dev → rag、announcements-monitoring-api-dev → app。"""
    base = api_name.split('-api')[0]
    return 'app' if base == 'announcements-monitoring' else base


def aggregate_api(start, end) -> dict:
    by_api = {}
    for name in API_NAMES:
        dims = [{'Name': 'ApiName', 'Value': name}]
        by_api[short_api_name(name)] = {
            'count': int(_cw_sum('AWS/ApiGateway', 'Count', dims, start, end)),
            'http5xx': int(_cw_sum('AWS/ApiGateway', '5XXError', dims, start, end)),
            'http4xx': int(_cw_sum('AWS/ApiGateway', '4XXError', dims, start, end)),
        }
    rag_name = API_NAMES[0] if API_NAMES else RAG_API_NAME
    lat = _cw_stats('AWS/ApiGateway', 'Latency', [{'Name': 'ApiName', 'Value': rag_name}], start, end,
                    statistics=['Maximum', 'SampleCount'], extended=['p50', 'p90'])
    return {
        'byApi': by_api,
        'latency': {'rag': {
            'p50Ms': round(lat['p50'], 1), 'p90Ms': round(lat['p90'], 1),
            'maxMs': round(lat['Maximum'], 1), 'count': int(lat['SampleCount']),
        }},
    }


def aggregate_amplify(start, end) -> dict | None:
    if not AMPLIFY_APP_ID:
        return None
    dims = [{'Name': 'App', 'Value': AMPLIFY_APP_ID}]
    return {
        'requests': int(_cw_sum('AWS/AmplifyHosting', 'Requests', dims, start, end)),
        'http5xx': int(_cw_sum('AWS/AmplifyHosting', '5xxErrors', dims, start, end)),
        'http4xx': int(_cw_sum('AWS/AmplifyHosting', '4xxErrors', dims, start, end)),
    }


def aggregate_sign_ins(start, end) -> int | None:
    if not (COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID):
        return None
    dims = [{'Name': 'UserPool', 'Value': COGNITO_USER_POOL_ID}, {'Name': 'UserPoolClient', 'Value': COGNITO_CLIENT_ID}]
    return int(_cw_sum('AWS/Cognito', 'SignInSuccesses', dims, start, end))


def aggregate_bedrock(start, end) -> dict | None:
    """AWS/Bedrock の ModelId 別メトリクス。アカウント内でそのモデルを使う全システムの合計（設計 §5.5）。"""
    if not BEDROCK_MODEL_ID:
        return None
    dims = [{'Name': 'ModelId', 'Value': BEDROCK_MODEL_ID}]
    return {
        'modelId': BEDROCK_MODEL_ID,
        'invocations': int(_cw_sum('AWS/Bedrock', 'Invocations', dims, start, end)),
        'inputTokens': int(_cw_sum('AWS/Bedrock', 'InputTokenCount', dims, start, end)),
        'outputTokens': int(_cw_sum('AWS/Bedrock', 'OutputTokenCount', dims, start, end)),
        'throttles': int(_cw_sum('AWS/Bedrock', 'InvocationThrottles', dims, start, end)),
        'serverErrors': int(_cw_sum('AWS/Bedrock', 'InvocationServerErrors', dims, start, end)),
    }


def alarm_transitions(start, end) -> list:
    """EleKnowledge のアラームの ALARM / OK 遷移。DescribeAlarmHistory は名前の前方一致で絞れないため
    アカウント全体の履歴を取り、prefix でクライアント側に絞る。"""
    out = []
    kwargs = {'HistoryItemType': 'StateUpdate', 'StartDate': start, 'EndDate': end,
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
                out.append({
                    'alarm': name[len(ALARM_PREFIX):],
                    'state': state,
                    'at': ts.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z') if hasattr(ts, 'astimezone') else str(ts),
                })
            token = resp.get('NextToken')
            if not token:
                break
            kwargs['NextToken'] = token
    except ClientError as e:
        print(f"[aggregator] DescribeAlarmHistory error: {e}")
    return out


def count_p1_incidents(transitions: list) -> int:
    return sum(1 for t in transitions if t['state'] == 'ALARM' and t['alarm'].startswith('P1-'))


# ----------------------------------------------------------------------------- unit price / estimate
def unit_prices() -> dict:
    """SSM の単価表 {modelId: {inputPerMTok, outputPerMTok}}。無ければ空。"""
    try:
        resp = ssm.get_parameter(Name=UNIT_PRICE_PARAM)
        return json.loads(resp['Parameter']['Value']) or {}
    except (ClientError, ValueError, KeyError) as e:
        print(f"[aggregator] unit price unavailable: {e}")
        return {}


def estimate_cost_usd(input_tokens: int, output_tokens: int, model_id: str, prices: dict) -> float | None:
    price = (prices or {}).get(model_id)
    if not price:
        return None
    usd = (input_tokens / 1e6) * float(price.get('inputPerMTok', 0)) + (output_tokens / 1e6) * float(price.get('outputPerMTok', 0))
    return round(usd, 4)


def sole_user_ok(bedrock: dict | None, pages: int) -> bool | None:
    """Bedrock 呼び出し数 ≒ 「候補あり」回答数なら、そのモデルの利用者は EleKnowledge だけ（設計 §5.5 C5）。"""
    if not bedrock:
        return None
    return bedrock['invocations'] <= pages * (1 + SOLE_USER_TOLERANCE) + 2


def aggregate_platform(day: date, chat: dict) -> dict:
    """CloudWatch とアラーム履歴から、その JST 日のシステム側の値をまとめる。"""
    start, end = utc_window_for_jst_day(day)
    api = aggregate_api(start, end)
    amplify = aggregate_amplify(start, end)
    sign_ins = aggregate_sign_ins(start, end)
    bedrock = aggregate_bedrock(start, end)
    # 実額（Cost Explorer は UTC 日）との突合用に UTC 日でも取る
    utc_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    bedrock_utc = aggregate_bedrock(utc_start, utc_start + timedelta(days=1))
    transitions = alarm_transitions(start, end)

    by_api = dict(api['byApi'])
    api_count = sum(v['count'] for v in by_api.values())
    http5xx_by = {k: v['http5xx'] for k, v in by_api.items()}
    http4xx_by = {k: v['http4xx'] for k, v in by_api.items()}
    if amplify is not None:
        http5xx_by['amplify'] = amplify['http5xx']
    http5xx = sum(http5xx_by.values())

    prices = unit_prices() if bedrock else {}
    estimate = estimate_cost_usd(bedrock['inputTokens'], bedrock['outputTokens'], bedrock['modelId'], prices) if bedrock else None
    estimate_utc = estimate_cost_usd(bedrock_utc['inputTokens'], bedrock_utc['outputTokens'], bedrock_utc['modelId'], prices) if bedrock_utc else None

    rag_lat = api['latency']['rag']
    return {
        'apiCount': api_count,
        'apiByName': by_api,
        'http5xx': http5xx,
        'http5xxByApi': http5xx_by,
        'http4xxByApi': http4xx_by,
        'errorRate': round(http5xx / api_count, 4) if api_count else 0.0,
        'apiLatency': api['latency'],
        # 旧 read API 互換（秒）。新 read は apiLatency を使う
        'latencyP90': round(rag_lat['p90Ms'] / 1000.0, 2),
        'amplifyRequests': amplify['requests'] if amplify else None,
        'amplify': amplify,
        'signIns': sign_ins,
        'bedrock': bedrock,
        'bedrockUtc': bedrock_utc,
        'estimatedBedrockCostUsd': estimate,
        'estimatedBedrockCostUsdUtc': estimate_utc,
        'estimateSource': 'cloudwatch' if estimate is not None else None,
        'soleUserOk': sole_user_ok(bedrock, chat.get('pages', 0)),
        'alarmTransitions': transitions,
        'incidents': count_p1_incidents(transitions),
    }


# ----------------------------------------------------------------------------- Cost Explorer
def classify_usage_type(usage_type: str) -> str:
    u = (usage_type or '').lower()
    if 'cache' in u:
        return 'cache'
    if 'input' in u:
        return 'input'
    if 'output' in u:
        return 'output'
    return 'other'


def fetch_cost_rows(start_day: date, end_day_exclusive: date) -> list:
    """Cost Explorer を 2 回呼び（サービス別、Bedrock 行の使用タイプ別）、UTC 日ごとの scope=cost 行を作る。"""
    period = {'Start': start_day.isoformat(), 'End': end_day_exclusive.isoformat()}
    by_service = ce.get_cost_and_usage(
        TimePeriod=period, Granularity='DAILY', Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
    )
    by_usage = ce.get_cost_and_usage(
        TimePeriod=period, Granularity='DAILY', Metrics=['UnblendedCost'],
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': [BEDROCK_COST_SERVICE_NAME]}},
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}],
    )
    fetched_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    today_utc = datetime.now(timezone.utc).date()

    def amount(group):
        return round(float(group['Metrics']['UnblendedCost']['Amount']), 4)

    usage_by_day = {}
    for r in by_usage.get('ResultsByTime', []):
        d = r['TimePeriod']['Start']
        split = {'input': 0.0, 'output': 0.0, 'cache': 0.0, 'other': 0.0}
        raw = {}
        for g in r.get('Groups', []):
            ut = g['Keys'][0]
            split[classify_usage_type(ut)] += amount(g)
            raw[ut] = amount(g)
        usage_by_day[d] = (split, raw)

    rows = []
    for r in by_service.get('ResultsByTime', []):
        d = r['TimePeriod']['Start']
        services = {g['Keys'][0]: amount(g) for g in r.get('Groups', [])}
        split, raw = usage_by_day.get(d, ({'input': 0.0, 'output': 0.0, 'cache': 0.0, 'other': 0.0}, {}))
        bedrock_total = services.get(BEDROCK_COST_SERVICE_NAME, 0.0)
        rows.append({
            'metricDate': d,
            'scope': 'cost',
            'byService': {k: round(v, 4) for k, v in services.items()},
            'total': round(sum(services.values()), 4),
            'bedrockService': BEDROCK_COST_SERVICE_NAME,
            'bedrock': {
                'total': round(bedrock_total, 4),
                'input': round(split['input'], 4),
                'output': round(split['output'], 4),
                'cache': round(split['cache'], 4),
                'other': round(split['other'], 4),
                'byUsageType': raw,
            },
            # D-2 以前は確定扱い（Cost Explorer の反映遅れを見込む）
            'settled': date.fromisoformat(d) <= today_utc - timedelta(days=2),
            'fetchedAt': fetched_at,
            'logicVersion': LOGIC_VERSION,
        })
    return rows


def write_cost_rows() -> dict:
    today_utc = datetime.now(timezone.utc).date()
    start = today_utc - timedelta(days=COST_DAYS)
    rows = fetch_cost_rows(start, today_utc)
    for row in rows:
        metrics_table.put_item(Item=to_decimal(row))
    print(f"[aggregator] Wrote {len(rows)} cost rows ({start} .. {today_utc - timedelta(days=1)})")
    return {'costRows': len(rows)}


def cost_probe() -> dict:
    """Cost Explorer が Lambda ロールで呼べるかを 1 回だけ確かめる（0.01 USD）。"""
    today_utc = datetime.now(timezone.utc).date()
    try:
        resp = ce.get_cost_and_usage(
            TimePeriod={'Start': (today_utc - timedelta(days=1)).isoformat(), 'End': today_utc.isoformat()},
            Granularity='DAILY', Metrics=['UnblendedCost'], GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
        )
        services = [g['Keys'][0] for r in resp.get('ResultsByTime', []) for g in r.get('Groups', [])]
        print(f"[aggregator] cost-probe OK: {len(services)} services")
        return {'ok': True, 'services': len(services)}
    except ClientError as e:
        print(f"[aggregator] cost-probe DENIED: {e}")
        return {'ok': False, 'error': str(e)}


# ----------------------------------------------------------------------------- write
def to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, list):
        return [to_decimal(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_decimal(v) for k, v in obj.items()}
    return obj


def build_daily_snapshot(day: date, chat: dict, platform: dict, partial: bool, aggregated_at: str) -> dict:
    return {
        'metricDate': day.isoformat(),
        'scope': 'overall',
        **chat,
        **platform,
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
    chat['newUsers'] = count_new_users(chat.get('userIds') or [], day)
    platform = aggregate_platform(day, chat)
    snapshot = build_daily_snapshot(day, chat, platform, partial, aggregated_at)
    metrics_table.put_item(Item=to_decimal(snapshot))

    hourly = aggregate_hourly(items)
    for row in build_hourly_rows(day, hourly, upto_hour, aggregated_at):
        metrics_table.put_item(Item=to_decimal(row))

    summary = {k: v for k, v in snapshot.items() if k not in ('topDocuments', 'userIds', 'alarmTransitions', 'apiByName')}
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
    event = event or {}
    if event.get('mode') == 'cost-probe':
        return {'statusCode': 200, **cost_probe()}

    results = []
    for day, partial, upto_hour in plan(event, jst_now()):
        print(f"[aggregator] Aggregating {day.isoformat()} (partial={partial}, upto_hour={upto_hour})")
        results.append(write_day(day, partial, upto_hour))

    cost = None
    if (event.get('mode') or 'daily') == 'daily' and not event.get('date') and COST_EXPLORER_ENABLED:
        try:
            cost = write_cost_rows()
        except (ClientError, KeyError, ValueError) as e:
            # 実額の取得失敗で KPI を止めない（画面には「未取得」と出る）
            print(f"[aggregator] Cost Explorer failed: {e}")
            cost = {'error': str(e)}
    return {'statusCode': 200, 'results': results, 'cost': cost}
