"""metrics read v2: ダッシュボード（いま・昨日・ファネル・推移・出来事）とコスト画面の組み立て。"""
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")
os.environ.setdefault("METRICS_TABLE", "metrics-test")
os.environ.setdefault("ANNOUNCEMENTS_TABLE", "announcements-test")
os.environ["API_NAMES"] = "rag-api-dev,chat-api-dev,auth-api-dev,announcements-monitoring-api-dev"
os.environ["ALARM_PREFIX"] = "EleKnowledge-dev-"


def _load():
    path = os.path.normpath(os.path.join(BASE, "lambda/metrics/read/app.py"))
    spec = importlib.util.spec_from_file_location("metrics_read_dashboard", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["metrics_read_dashboard"] = mod
    spec.loader.exec_module(mod)
    return mod


read = _load()
JST = read.JST
NOW = datetime(2026, 9, 23, 23, 41, tzinfo=timezone.utc)   # JST 9/24 08:41


def _day(d, **kw):
    row = {"metricDate": d, "scope": "overall", "queries": 28, "unreached": 2, "notFound": 1, "feedbackBad": 1,
           "feedbackGood": 4, "pages": 22, "signIns": 21, "messagesWithOpen": 13, "activeUsers": 16, "newUsers": 2,
           "incidents": 0, "http5xx": 0, "http5xxByApi": {"rag": 0, "chat": 0, "auth": 0, "app": 0, "amplify": 0},
           "apiLatency": {"rag": {"p50Ms": 9800, "p90Ms": 11200, "maxMs": 17800, "count": 28}},
           "estimatedBedrockCostUsd": 0.38, "estimateSource": "cloudwatch", "aggregatedAt": "2026-09-23T17:03:00Z",
           "partial": False, "alarmTransitions": [], "topDocuments": [{"name": "a.pdf", "count": 3}], "reformulated": 2}
    row.update(kw)
    return row


def _rows():
    rows = []
    for n in range(1, 31):
        d = (datetime(2026, 9, 24, tzinfo=JST).date() - timedelta(days=n)).isoformat()
        rows.append(_day(d))
    rows.append(_day("2026-09-24", partial=True, queries=4, unreached=0, http5xx=0, aggregatedAt="2026-09-23T23:40:00Z"))
    return sorted(rows, key=lambda r: r["metricDate"])


# ------------------------------------------------------------------ thresholds (§2.8)
def test_status_latency_slo_20s():
    assert read.status_latency(11200, 17800) == "good"
    assert read.status_latency(20000, 17800) == "good"
    assert read.status_latency(23400, 24000) == "warning"
    assert read.status_latency(23400, 28700) == "warning"      # max > 25 s は注意以上
    assert read.status_latency(26000, 28000) == "serious"
    assert read.status_latency(23400, 30000) == "serious"      # max > 29 s
    assert read.status_latency(30000, 31000) == "critical"
    assert read.status_latency(None, None) == "good"


def test_status_5xx_and_alarms():
    assert read.status_5xx(0) == "good" and read.status_5xx(3) == "warning" and read.status_5xx(21) == "critical"
    assert read.status_alarms([]) == "good"
    assert read.status_alarms([{"severity": "P2"}]) == "warning"
    assert read.status_alarms([{"severity": "P2"}, {"severity": "P1"}]) == "critical"


def test_status_cost_spike_needs_factor_and_floor():
    assert read.status_cost_spike(0.62, [0.36, 0.38, 0.40]) == "good"     # < 3×
    assert read.status_cost_spike(0.9, [0.1, 0.1, 0.1]) == "good"         # 3× 超だが 1 USD 未満
    assert read.status_cost_spike(1.5, [0.3, 0.4, 0.35]) == "warning"
    assert read.status_cost_spike(None, [0.3]) == "good"
    assert read.status_cost_spike(5.0, []) == "good"


# ------------------------------------------------------------------ dashboard assembly
def test_build_dashboard_calm_morning():
    rows = _rows()
    hourly = [{"metricDate": "2026-09-24T08", "queries": 3, "unreached": 0}]
    alarms = []
    last60 = {"requests": 2, "http5xx": 0, "ragP90Ms": None, "ragMaxMs": 10400.0, "ragCount": 2}
    cost_rows = [{"metricDate": f"2026-09-{d:02d}", "scope": "cost", "settled": d <= 21,
                  "bedrock": {"total": 0.3}, "byService": {}} for d in range(1, 23)]
    out = read.build_dashboard(NOW, rows, hourly, alarms, last60, [], [], cost_rows, {"date": "2026-09-22", "hit": 11, "n": 14}, 14)

    assert out["today"] == "2026-09-24"
    assert out["now"]["status"] == "good"
    assert out["now"]["freshness"] == {"yesterdayAggregatedAt": "2026-09-23T17:03:00Z", "todayPartialAt": "2026-09-23T23:40:00Z", "status": "good"}
    y = out["yesterday"]
    assert y["date"] == "2026-09-23" and y["exists"] is True
    assert y["incidents"]["status"] == "good" and y["incidents"]["byApi"]["rag"] == 0
    assert y["latency"]["p90Ms"] == 11200 and y["latency"]["showP90"] is True and y["latency"]["status"] == "good"
    assert y["unreached"] == {"total": 2, "notFound": 1, "bad": 1, "reformulated": 2, "open": None}
    assert y["usage"]["queriesSameWeekdayLastWeek"] == 28
    assert y["bedrockCost"]["monthActualUsd"] == pytest.approx(0.3 * 21, abs=0.01)
    assert y["bedrockCost"]["actualThrough"] == "2026-09-21"
    assert y["bedrockCost"]["status"] == "good"
    assert out["todaySoFar"] == {"asOf": "08:40", "queries": 4, "unreached": 0, "http5xx": 0}
    f = out["funnel"]
    assert f["yesterday"]["opened"] == 13 and f["last7d"]["queries"] == 28 * 7 and f["showRates"] is True
    assert f["last7dRange"] == {"from": "2026-09-17", "to": "2026-09-23"}
    assert len(out["trend"]["queriesByDay"]) == 14 and out["trend"]["queriesByDay"][-1]["date"] == "2026-09-23"
    assert out["trend"]["hourlyToday"] == [{"hour": "08", "queries": 3, "unreached": 0}]
    assert out["events"] == []
    assert out["reference"]["topDocuments"][0] == {"name": "a.pdf", "count": 90}
    assert out["reference"]["lastEval"]["hit"] == 11


def test_build_dashboard_incident_morning():
    rows = _rows()
    by = {r["metricDate"]: r for r in rows}
    by["2026-09-23"].update({"incidents": 1, "http5xx": 4, "http5xxByApi": {"rag": 4}, "unreached": 5,
                             "apiLatency": {"rag": {"p50Ms": 12000, "p90Ms": 23400, "maxMs": 28700, "count": 31}},
                             "alarmTransitions": [
                                 {"alarm": "P1-rag-duration-max", "state": "ALARM", "at": "2026-09-23T14:10:00Z"},
                                 {"alarm": "P1-rag-duration-max", "state": "OK", "at": "2026-09-23T14:25:00Z"},
                             ]})
    alarms = [{"name": "P1-rag-api-5xx", "severity": "P1", "since": "2026-09-23T22:52:00Z"}]
    live = [{"alarm": "P1-rag-api-5xx", "state": "ALARM", "at": "2026-09-23T22:52:00Z"}]
    out = read.build_dashboard(NOW, rows, [], alarms, {"requests": 14, "http5xx": 3, "ragP90Ms": None, "ragMaxMs": 12100, "ragCount": 6},
                               live, [{"id": "anc_9", "title": "障害中", "severity": "critical", "since": "2026-09-23T23:05:00Z", "showInChat": True}],
                               [], None, 14)
    assert out["now"]["status"] == "critical" and out["now"]["activeNotices"][0]["id"] == "anc_9"
    y = out["yesterday"]
    assert y["incidents"]["status"] == "serious"          # P1 遷移あり
    assert y["latency"]["status"] == "warning"            # p90 23.4 s, max 28.7 s
    events = out["events"]
    assert [e["title"] for e in events] == ["P1-rag-api-5xx", "P1-rag-duration-max"]
    assert events[0]["durationSec"] is None and events[0]["resolvedAt"] is None
    assert events[1]["durationSec"] == 900 and events[1]["resolvedAt"] == "2026-09-23T14:25:00Z"
    assert events[1]["logGroup"] == "/aws/lambda/rag-dev" and events[1]["queryName"] == "EleKnowledge/dev/slow-requests"
    assert events[1]["from"] == "2026-09-23T13:55:00Z" and events[1]["to"] == "2026-09-23T14:25:00Z"


def test_build_dashboard_missing_yesterday_is_warning_after_9am():
    rows = [r for r in _rows() if r["metricDate"] != "2026-09-23"]
    out = read.build_dashboard(NOW, rows, [], [], {"requests": 0, "http5xx": 0, "ragP90Ms": None, "ragMaxMs": None, "ragCount": 0}, [], [], [], None, 14)
    assert out["yesterday"]["exists"] is False
    assert out["now"]["freshness"]["status"] == "good"       # 08:41 JST はまだ猶予
    later = NOW + timedelta(hours=1)                         # 09:41 JST
    out = read.build_dashboard(later, rows, [], [], {"requests": 0, "http5xx": 0, "ragP90Ms": None, "ragMaxMs": None, "ragCount": 0}, [], [], [], None, 14)
    assert out["now"]["freshness"]["status"] == "warning"


def test_latency_of_legacy_row_and_small_sample():
    assert read._latency_of({"latencyP90": 11.2}) == {"p90Ms": 11200.0, "p50Ms": None, "maxMs": None, "count": None}
    rows = _rows()
    by = {r["metricDate"]: r for r in rows}
    by["2026-09-23"]["apiLatency"] = {"rag": {"p50Ms": 9000, "p90Ms": 26000, "maxMs": 12000, "count": 3}}
    out = read.build_dashboard(NOW, rows, [], [], {"requests": 0, "http5xx": 0, "ragP90Ms": None, "ragMaxMs": None, "ragCount": 0}, [], [], [], None, 14)
    # 件数 3 → p90 を使わず（showP90=False）、色は最大値だけで決まる
    assert out["yesterday"]["latency"]["showP90"] is False and out["yesterday"]["latency"]["status"] == "good"


def test_funnel_row_marks_unmeasured_opens():
    assert read.funnel_row([{"queries": 5, "pages": 4, "feedbackGood": 1}])["opened"] == "unmeasured"
    assert read.funnel_row([])["queries"] is None


def test_log_hint_maps_alarm_names():
    assert read.log_hint("P2-rag-api-4xx-spike", "2026-09-20T05:11:00Z")["queryName"] == "EleKnowledge/dev/api-4xx-breakdown"
    assert read.log_hint("P2-rag-api-4xx-spike", "2026-09-20T05:11:00Z")["logGroup"] == "/aws/apigateway/rag-api-dev"
    assert read.log_hint("P1-chat-api-5xx", "x")["queryName"] == "EleKnowledge/dev/chat-error-lines"
    assert read.log_hint("P1-cognito-email-errors", "x")["logGroup"] is None


# ------------------------------------------------------------------ live helpers
def test_live_last_60min_sums_and_percentiles(monkeypatch):
    class CW:
        def get_metric_data(self, **kw):
            assert len(kw["MetricDataQueries"]) == 4 * 2 + 3
            return {"MetricDataResults": [
                {"Id": "m0_count", "Values": [3, 5]}, {"Id": "m1_count", "Values": [6]},
                {"Id": "m0_5xxerror", "Values": [1, 2]}, {"Id": "m1_5xxerror", "Values": []},
                {"Id": "rag_p90", "Values": [12100.0]}, {"Id": "rag_max", "Values": [12100.0]}, {"Id": "rag_count", "Values": [6]},
            ]}
    monkeypatch.setattr(read, "cloudwatch", CW())
    out = read.live_last_60min(NOW)
    assert out == {"requests": 14, "http5xx": 3, "ragP90Ms": 12100.0, "ragMaxMs": 12100.0, "ragCount": 6}


def test_live_alarms_classifies_severity(monkeypatch):
    class CW:
        def describe_alarms(self, **kw):
            assert kw["StateValue"] == "ALARM" and kw["AlarmNamePrefix"] == "EleKnowledge-dev-"
            return {"MetricAlarms": [
                {"AlarmName": "EleKnowledge-dev-P1-rag-api-5xx", "StateUpdatedTimestamp": NOW},
                {"AlarmName": "EleKnowledge-dev-P2-rag-api-4xx-spike", "StateUpdatedTimestamp": NOW},
            ]}
    monkeypatch.setattr(read, "cloudwatch", CW())
    out = read.live_alarms()
    assert [(a["name"], a["severity"]) for a in out] == [("P1-rag-api-5xx", "P1"), ("P2-rag-api-4xx-spike", "P2")]
    assert out[0]["since"] == "2026-09-23T23:41:00Z"


def test_active_notices_filters_ended_and_sorts(monkeypatch):
    class T:
        def query(self, **kw):
            status = kw["KeyConditionExpression"]._values[0]._values[1]
            if status == "published":
                return {"Items": [
                    {"announcementId": "a1", "title": "情報", "severity": "info", "publishAt": "2026-09-09T14:10:00.000Z", "status": "published"},
                    {"announcementId": "a9", "title": "障害中", "severity": "critical", "publishAt": "2026-09-23T23:05:00.000Z", "status": "published"},
                    {"announcementId": "a0", "title": "終了済み", "severity": "info", "publishAt": "2026-09-01T00:00:00.000Z", "endAt": "2026-09-17T00:00:00.000Z"},
                ]}
            return {"Items": []}
    monkeypatch.setattr(read, "announcements_table", T())
    out = read.active_notices(NOW)
    assert [n["id"] for n in out] == ["a9", "a1"]
    assert out[0]["showInChat"] is True and out[1]["showInChat"] is False


# ------------------------------------------------------------------ cost
def test_build_cost_buckets_checks_and_projection():
    cost_rows = []
    for d in range(1, 24):
        cost_rows.append({"metricDate": f"2026-09-{d:02d}", "scope": "cost", "settled": d <= 22, "total": 25.0,
                          "byService": {"Claude Sonnet 5 (Amazon Bedrock Edition)": 0.3, "AWS Amplify": 0.46,
                                        "Amazon OpenSearch Service": 19.9, "AmazonCloudWatch": 0.15, "AWS WAF": 0.5,
                                        "Claude Sonnet 4.6 (Amazon Bedrock Edition)": 30.0, "AWS Lambda": 0.001},
                          "bedrock": {"total": 0.3, "input": 0.18, "output": 0.11, "cache": 0.01, "other": 0.0}})
    daily_rows = []
    for d in range(1, 23):
        daily_rows.append({"metricDate": f"2026-09-{d:02d}", "queries": 20, "pages": 16, "partial": False, "soleUserOk": True,
                           "bedrock": {"invocations": 16, "modelId": "global.anthropic.claude-sonnet-5"},
                           "estimatedBedrockCostUsdUtc": 0.28})
    out = read.build_cost(NOW, "2026-09", cost_rows, daily_rows, 100.0)
    c = out["confirmed"]
    assert out["settledThrough"] == "2026-09-22"
    assert c["bedrock"]["total"] == pytest.approx(6.6, abs=0.01) and c["amplify"] == pytest.approx(10.12, abs=0.01)
    assert c["total"] == pytest.approx(16.72, abs=0.01) and c["budgetPct"] == pytest.approx(6.6, abs=0.1)
    assert c["forecastUsd"] == pytest.approx(9.0, abs=0.01)
    assert out["shared"]["byService"] == {"Amazon OpenSearch Service": pytest.approx(437.8, abs=0.1)}
    assert set(out["unattributed"]["byService"]) == {"AmazonCloudWatch", "AWS WAF", "AWS Lambda"}
    assert out["otherSystems"]["byService"] == {"Claude Sonnet 4.6 (Amazon Bedrock Edition)": 660.0}
    ck = out["checks"]
    assert ck["soleUser"]["ok"] is True and ck["soleUser"]["invocations"] == 16 * 22
    assert ck["actualVsEstimate"]["estimate"] == pytest.approx(0.28 * 22, abs=0.01)
    assert ck["actualVsEstimate"]["diffPct"] == pytest.approx(7.1, abs=0.2) and ck["actualVsEstimate"]["status"] == "good"
    assert ck["modelIds"] == ["global.anthropic.claude-sonnet-5"]
    assert out["perQuery"]["actualUsd"] == pytest.approx(6.6 / 440, abs=1e-4)
    assert out["projection"][2]["queriesPerDay"] == 1000 and out["projection"][2]["monthlyUsd"] == pytest.approx(450, abs=1)
    assert len(out["daily"]) == 23 and out["daily"][-1]["settled"] is False


def test_classify_service():
    assert read.classify_service("Claude Sonnet 5 (Amazon Bedrock Edition)") == "bedrock"
    assert read.classify_service("AWS Amplify") == "amplify"
    assert read.classify_service("Amazon OpenSearch Service") == "shared"
    assert read.classify_service("Amazon Titan Text Embeddings V2 (Amazon Bedrock Edition)") == "shared"
    assert read.classify_service("Claude Sonnet 4.6 (Amazon Bedrock Edition)") == "otherSystems"
    assert read.classify_service("Amazon DynamoDB") == "unattributed"
    assert read.classify_service("Amazon Elastic Compute Cloud") == "otherSystems"


# ------------------------------------------------------------------ routing
def _event(path, groups="admin", qs=None):
    return {"httpMethod": "GET", "path": path, "queryStringParameters": qs or {},
            "requestContext": {"authorizer": {"claims": {"cognito:groups": groups}}}}


def test_routes_dashboard_and_cost(monkeypatch):
    monkeypatch.setattr(read, "handle_dashboard", lambda qs: {"kind": "dashboard", "trend": qs.get("trend")})
    monkeypatch.setattr(read, "handle_cost", lambda qs: {"kind": "cost", "month": qs.get("month")})
    resp = read.lambda_handler(_event("/dev/admin/metrics/dashboard", qs={"trend": "30"}), None)
    assert resp["statusCode"] == 200 and json.loads(resp["body"]) == {"kind": "dashboard", "trend": "30"}
    resp = read.lambda_handler(_event("/admin/metrics/cost/", qs={"month": "2026-08"}), None)
    assert json.loads(resp["body"]) == {"kind": "cost", "month": "2026-08"}
    assert read.lambda_handler(_event("/admin/metrics/cost", groups="user"), None)["statusCode"] == 403
