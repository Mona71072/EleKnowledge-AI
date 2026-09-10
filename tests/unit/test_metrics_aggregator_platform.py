"""metrics aggregator v2: CloudWatch（API / Amplify / Cognito / Bedrock）・アラーム履歴・単価推定・Cost Explorer。"""
import importlib.util
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

import pytest
from botocore.exceptions import ClientError

BASE = os.path.join(os.path.dirname(__file__), "../..")

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")
os.environ.setdefault("METRICS_TABLE", "metrics-test")
os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
os.environ["API_NAMES"] = "rag-api-dev,chat-api-dev,auth-api-dev,announcements-monitoring-api-dev"
os.environ["ALARM_PREFIX"] = "EleKnowledge-dev-"
os.environ["AMPLIFY_APP_ID"] = "app123"
os.environ["COGNITO_USER_POOL_ID"] = "pool"
os.environ["COGNITO_CLIENT_ID"] = "client"
os.environ["BEDROCK_MODEL_ID"] = "global.anthropic.claude-sonnet-5"
os.environ["BEDROCK_COST_SERVICE_NAME"] = "Claude Sonnet 5 (Amazon Bedrock Edition)"


def _load():
    path = os.path.normpath(os.path.join(BASE, "lambda/metrics/aggregator/app.py"))
    spec = importlib.util.spec_from_file_location("metrics_aggregator_platform", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["metrics_aggregator_platform"] = mod
    spec.loader.exec_module(mod)
    return mod


agg = _load()
JST = agg.JST


class FakeCloudWatch:
    """メトリクス名（+ 主要ディメンション値）→ Datapoints を返す簡易フェイク。"""

    def __init__(self, table=None, history=None):
        self.table = table or {}
        self.history = history or []
        self.calls = []

    def get_metric_statistics(self, **kw):
        self.calls.append(kw)
        key = (kw["Namespace"], kw["MetricName"], kw["Dimensions"][0]["Value"])
        pts = self.table.get(key, [])
        return {"Datapoints": pts}

    def describe_alarm_history(self, **kw):
        return {"AlarmHistoryItems": self.history}


class FakeSSM:
    def __init__(self, value):
        self.value = value

    def get_parameter(self, Name):
        if self.value is None:
            raise ClientError({"Error": {"Code": "ParameterNotFound", "Message": "x"}}, "GetParameter")
        return {"Parameter": {"Value": self.value}}


def _dp(**kw):
    return kw


# ------------------------------------------------------------------ _cw_stats
def test_cw_stats_sums_and_maxes_across_datapoints(monkeypatch):
    cw = FakeCloudWatch({
        ("AWS/ApiGateway", "Latency", "rag-api-dev"): [
            {"Maximum": 18000, "SampleCount": 10, "ExtendedStatistics": {"p50": 9000, "p90": 11000}},
            {"Maximum": 28700, "SampleCount": 21, "ExtendedStatistics": {"p50": 10000, "p90": 23400}},
        ],
    })
    monkeypatch.setattr(agg, "cloudwatch", cw)
    out = agg._cw_stats("AWS/ApiGateway", "Latency", [{"Name": "ApiName", "Value": "rag-api-dev"}],
                        datetime(2026, 9, 23, tzinfo=timezone.utc), datetime(2026, 9, 24, tzinfo=timezone.utc),
                        statistics=["Maximum", "SampleCount"], extended=["p50", "p90"])
    assert out == {"Maximum": 28700, "SampleCount": 31, "p50": 10000, "p90": 23400}


def test_cw_stats_returns_zeros_on_error(monkeypatch):
    class Boom:
        def get_metric_statistics(self, **kw):
            raise ClientError({"Error": {"Code": "Throttling", "Message": "x"}}, "GetMetricStatistics")
    monkeypatch.setattr(agg, "cloudwatch", Boom())
    out = agg._cw_stats("AWS/ApiGateway", "Count", [{"Name": "ApiName", "Value": "x"}], None, None, statistics=["Sum"])
    assert out == {"Sum": 0.0}


def test_short_api_name():
    assert agg.short_api_name("rag-api-dev") == "rag"
    assert agg.short_api_name("announcements-monitoring-api-dev") == "app"
    assert agg.short_api_name("auth-api-prd") == "auth"


# ------------------------------------------------------------------ alarm history
def test_alarm_transitions_filters_prefix_and_states(monkeypatch):
    ts = datetime(2026, 9, 23, 14, 10, tzinfo=timezone.utc)
    cw = FakeCloudWatch(history=[
        {"AlarmName": "EleKnowledge-dev-P1-rag-api-5xx", "Timestamp": ts,
         "HistoryData": json.dumps({"newState": {"stateValue": "ALARM"}})},
        {"AlarmName": "EleKnowledge-dev-P1-rag-api-5xx", "Timestamp": ts + timedelta(minutes=15),
         "HistoryData": json.dumps({"newState": {"stateValue": "OK"}})},
        {"AlarmName": "EleKnowledge-dev-P2-rag-api-4xx-spike", "Timestamp": ts,
         "HistoryData": json.dumps({"newState": {"stateValue": "ALARM"}})},
        {"AlarmName": "OtherSystem-alarm", "Timestamp": ts,
         "HistoryData": json.dumps({"newState": {"stateValue": "ALARM"}})},
        {"AlarmName": "EleKnowledge-dev-P1-chat-api-5xx", "Timestamp": ts,
         "HistoryData": json.dumps({"newState": {"stateValue": "INSUFFICIENT_DATA"}})},
    ])
    monkeypatch.setattr(agg, "cloudwatch", cw)
    out = agg.alarm_transitions(ts - timedelta(hours=1), ts + timedelta(hours=1))
    assert [(t["alarm"], t["state"]) for t in out] == [
        ("P1-rag-api-5xx", "ALARM"), ("P1-rag-api-5xx", "OK"), ("P2-rag-api-4xx-spike", "ALARM"),
    ]
    assert out[0]["at"] == "2026-09-23T14:10:00Z"
    assert agg.count_p1_incidents(out) == 1


# ------------------------------------------------------------------ estimate / sole user
def test_estimate_cost_and_unit_prices(monkeypatch):
    prices = {"global.anthropic.claude-sonnet-5": {"inputPerMTok": 2.0, "outputPerMTok": 10.0}}
    assert agg.estimate_cost_usd(3_748_000, 578_000, "global.anthropic.claude-sonnet-5", prices) == pytest.approx(7.496 + 5.78, abs=1e-4)
    assert agg.estimate_cost_usd(1, 1, "unknown-model", prices) is None
    monkeypatch.setattr(agg, "ssm", FakeSSM(json.dumps(prices)))
    assert agg.unit_prices() == prices
    monkeypatch.setattr(agg, "ssm", FakeSSM(None))
    assert agg.unit_prices() == {}


def test_sole_user_ok_tolerance():
    assert agg.sole_user_ok({"invocations": 41}, pages=41) is True
    assert agg.sole_user_ok({"invocations": 45}, pages=41) is True     # 41*1.05+2 = 45.05
    assert agg.sole_user_ok({"invocations": 46}, pages=41) is False
    assert agg.sole_user_ok(None, pages=41) is None


# ------------------------------------------------------------------ aggregate_platform
def test_aggregate_platform_shapes_daily_fields(monkeypatch):
    day = date(2026, 9, 23)
    cw = FakeCloudWatch({
        ("AWS/ApiGateway", "Count", "rag-api-dev"): [{"Sum": 31}],
        ("AWS/ApiGateway", "5XXError", "rag-api-dev"): [{"Sum": 4}],
        ("AWS/ApiGateway", "4XXError", "rag-api-dev"): [{"Sum": 2}],
        ("AWS/ApiGateway", "Count", "chat-api-dev"): [{"Sum": 120}],
        ("AWS/ApiGateway", "Latency", "rag-api-dev"): [
            {"Maximum": 28700, "SampleCount": 31, "ExtendedStatistics": {"p50": 10200, "p90": 23400}}],
        ("AWS/AmplifyHosting", "Requests", "app123"): [{"Sum": 900}],
        ("AWS/AmplifyHosting", "5xxErrors", "app123"): [{"Sum": 1}],
        ("AWS/Cognito", "SignInSuccesses", "pool"): [{"Sum": 24}],
        ("AWS/Bedrock", "Invocations", "global.anthropic.claude-sonnet-5"): [{"Sum": 21}],
        ("AWS/Bedrock", "InputTokenCount", "global.anthropic.claude-sonnet-5"): [{"Sum": 120000}],
        ("AWS/Bedrock", "OutputTokenCount", "global.anthropic.claude-sonnet-5"): [{"Sum": 15000}],
    }, history=[
        {"AlarmName": "EleKnowledge-dev-P1-rag-duration-max", "Timestamp": datetime(2026, 9, 23, 14, 10, tzinfo=timezone.utc),
         "HistoryData": json.dumps({"newState": {"stateValue": "ALARM"}})},
    ])
    monkeypatch.setattr(agg, "cloudwatch", cw)
    monkeypatch.setattr(agg, "ssm", FakeSSM(json.dumps({"global.anthropic.claude-sonnet-5": {"inputPerMTok": 2.0, "outputPerMTok": 10.0}})))

    out = agg.aggregate_platform(day, {"pages": 21})
    assert out["apiCount"] == 151
    assert out["http5xx"] == 5                       # rag 4 + amplify 1
    assert out["http5xxByApi"] == {"rag": 4, "chat": 0, "auth": 0, "app": 0, "amplify": 1}
    assert out["http4xxByApi"]["rag"] == 2
    assert out["errorRate"] == round(5 / 151, 4)
    assert out["apiLatency"]["rag"] == {"p50Ms": 10200.0, "p90Ms": 23400.0, "maxMs": 28700.0, "count": 31}
    assert out["latencyP90"] == 23.4
    assert out["amplifyRequests"] == 900 and out["signIns"] == 24
    assert out["bedrock"]["invocations"] == 21 and out["bedrock"]["inputTokens"] == 120000
    assert out["estimatedBedrockCostUsd"] == pytest.approx(0.24 + 0.15, abs=1e-4)
    assert out["estimateSource"] == "cloudwatch"
    assert out["soleUserOk"] is True
    assert out["incidents"] == 1 and out["alarmTransitions"][0]["alarm"] == "P1-rag-duration-max"
    # 呼び出しは JST 日の UTC 窓（15:00Z 開始）
    first = cw.calls[0]
    assert first["StartTime"] == datetime(2026, 9, 22, 15, 0, tzinfo=timezone.utc)
    assert first["Period"] == 86400


# ------------------------------------------------------------------ Cost Explorer
class FakeCE:
    def __init__(self):
        self.calls = []

    def get_cost_and_usage(self, **kw):
        self.calls.append(kw)
        if "Filter" in kw:  # usage types of the Bedrock line
            return {"ResultsByTime": [
                {"TimePeriod": {"Start": "2026-09-21", "End": "2026-09-22"}, "Groups": [
                    {"Keys": ["APN1-Claude-Sonnet5-InputTokens"], "Metrics": {"UnblendedCost": {"Amount": "0.20"}}},
                    {"Keys": ["APN1-Claude-Sonnet5-OutputTokens"], "Metrics": {"UnblendedCost": {"Amount": "0.15"}}},
                    {"Keys": ["APN1-Claude-Sonnet5-CacheReadInputTokens"], "Metrics": {"UnblendedCost": {"Amount": "0.01"}}},
                ]},
                {"TimePeriod": {"Start": "2026-09-22", "End": "2026-09-23"}, "Groups": []},
            ]}
        return {"ResultsByTime": [
            {"TimePeriod": {"Start": "2026-09-21", "End": "2026-09-22"}, "Groups": [
                {"Keys": ["Claude Sonnet 5 (Amazon Bedrock Edition)"], "Metrics": {"UnblendedCost": {"Amount": "0.36"}}},
                {"Keys": ["Amazon OpenSearch Service"], "Metrics": {"UnblendedCost": {"Amount": "19.9"}}},
            ]},
            {"TimePeriod": {"Start": "2026-09-22", "End": "2026-09-23"}, "Groups": [
                {"Keys": ["Amazon OpenSearch Service"], "Metrics": {"UnblendedCost": {"Amount": "19.8"}}},
            ]},
        ]}


def test_fetch_cost_rows_splits_usage_types_and_settles(monkeypatch):
    ce = FakeCE()
    monkeypatch.setattr(agg, "ce", ce)

    class FixedDT(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 9, 24, 0, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(agg, "datetime", FixedDT)

    rows = agg.fetch_cost_rows(date(2026, 9, 21), date(2026, 9, 24))
    assert [r["metricDate"] for r in rows] == ["2026-09-21", "2026-09-22"]
    r0 = rows[0]
    assert r0["scope"] == "cost"
    assert r0["byService"]["Amazon OpenSearch Service"] == 19.9
    assert r0["total"] == pytest.approx(20.26)
    assert r0["bedrock"] == {"total": 0.36, "input": 0.2, "output": 0.15, "cache": 0.01, "other": 0.0,
                             "byUsageType": {"APN1-Claude-Sonnet5-InputTokens": 0.2, "APN1-Claude-Sonnet5-OutputTokens": 0.15,
                                             "APN1-Claude-Sonnet5-CacheReadInputTokens": 0.01}}
    assert r0["settled"] is True          # 9/21 <= 9/24 - 2
    assert rows[1]["settled"] is True and rows[1]["bedrock"]["total"] == 0.0
    # 2 回だけ呼ぶ（サービス別・使用タイプ別）
    assert len(ce.calls) == 2 and ce.calls[1]["Filter"]["Dimensions"]["Values"] == ["Claude Sonnet 5 (Amazon Bedrock Edition)"]


def test_classify_usage_type():
    assert agg.classify_usage_type("APN1-InputTokens") == "input"
    assert agg.classify_usage_type("APN1-OutputTokens") == "output"
    assert agg.classify_usage_type("APN1-CacheWriteInputTokens") == "cache"
    assert agg.classify_usage_type("Something") == "other"


def test_daily_mode_writes_cost_rows_and_survives_ce_failure(monkeypatch):
    calls = []
    monkeypatch.setattr(agg, "write_day", lambda day, partial, upto_hour=23: {"date": day.isoformat()})
    monkeypatch.setattr(agg, "jst_now", lambda: datetime(2026, 9, 24, 2, 0, tzinfo=JST))

    class Denied:
        def get_cost_and_usage(self, **kw):
            raise ClientError({"Error": {"Code": "AccessDeniedException", "Message": "explicit deny in a service control policy"}}, "GetCostAndUsage")
    monkeypatch.setattr(agg, "ce", Denied())
    out = agg.lambda_handler({"mode": "daily"}, None)
    assert out["statusCode"] == 200 and len(out["results"]) == 3
    assert "error" in out["cost"] and "service control policy" in out["cost"]["error"]

    # hourly では Cost Explorer を呼ばない
    monkeypatch.setattr(agg, "write_cost_rows", lambda: calls.append("cost"))
    out = agg.lambda_handler({"mode": "hourly"}, None)
    assert out["cost"] is None and calls == []


def test_cost_probe_reports_denied(monkeypatch):
    class Denied:
        def get_cost_and_usage(self, **kw):
            raise ClientError({"Error": {"Code": "AccessDeniedException", "Message": "nope"}}, "GetCostAndUsage")
    monkeypatch.setattr(agg, "ce", Denied())
    out = agg.lambda_handler({"mode": "cost-probe"}, None)
    assert out["ok"] is False and "AccessDenied" in out["error"]


# ------------------------------------------------------------------ new users / opens / reformulated
def test_count_new_users_uses_first_activity(monkeypatch):
    class FakeChatlogs:
        def query(self, **kw):
            uid = kw["KeyConditionExpression"]._values[1]
            first = {"u-new": "2026-09-23T01:00:00Z", "u-old": "2026-08-01T01:00:00Z"}[uid]
            return {"Items": [{"timestamp": first}]}
    monkeypatch.setattr(agg, "chatlogs_table", FakeChatlogs())
    assert agg.count_new_users(["u-new", "u-old"], date(2026, 9, 23)) == 1


def test_aggregate_chat_counts_opens_and_reformulation():
    items = [
        {"role": "assistant", "sessionId": "s1", "responseType": "pages", "documentOpens": 2, "timestamp": "2026-09-23T01:00:00Z"},
        {"role": "assistant", "sessionId": "s2", "responseType": "pages", "reformulatedAt": "2026-09-23T01:03:00Z", "timestamp": "2026-09-23T01:00:00Z"},
        {"role": "assistant", "sessionId": "s3", "responseType": "pages", "reformulatedAt": "x", "feedback": "good", "timestamp": "2026-09-23T01:00:00Z"},
        {"role": "assistant", "sessionId": "s4", "responseType": "pages", "reformulatedAt": "x", "documentOpens": 1, "timestamp": "2026-09-23T01:00:00Z"},
    ]
    out = agg.aggregate_chat(items)
    assert out["documentOpens"] == 3 and out["messagesWithOpen"] == 2
    assert out["reformulated"] == 1


def test_aggregate_chat_counts_open_triage_among_unreached():
    items = [
        {"role": "assistant", "responseType": "not_found", "timestamp": "2026-09-23T01:00:00Z"},                      # triage なし → open
        {"role": "assistant", "responseType": "pages", "feedback": "bad", "triage": {"status": "open"}, "timestamp": "x"},
        {"role": "assistant", "responseType": "pages", "feedback": "bad", "triage": {"status": "done"}, "timestamp": "x"},
        {"role": "assistant", "responseType": "pages", "feedback": "good", "timestamp": "x"},                          # 到達できずではない
    ]
    out = agg.aggregate_chat(items)
    assert out["unreached"] == 3 and out["triageOpen"] == 2
