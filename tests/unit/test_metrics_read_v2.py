"""metrics read v2: JST の today、ユニーク利用者の和集合、鮮度、時間帯別。"""
import importlib.util
import os
import sys
from datetime import date, datetime, timezone

BASE = os.path.join(os.path.dirname(__file__), "../..")

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")
os.environ.setdefault("METRICS_TABLE", "metrics-test")


def _load():
    path = os.path.normpath(os.path.join(BASE, "lambda/metrics/read/app.py"))
    spec = importlib.util.spec_from_file_location("metrics_read_v2", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["metrics_read_v2"] = mod
    spec.loader.exec_module(mod)
    return mod


read = _load()


def test_today_is_jst(monkeypatch):
    # UTC 9/23 16:00 = JST 9/24 01:00 → today は 9/24
    monkeypatch.setattr(read, "_now", lambda: datetime(2026, 9, 23, 16, 0, tzinfo=timezone.utc))
    start, end, period = read.resolve_range({"period": "today"})
    assert start == end == date(2026, 9, 24) and period == "today"
    start, end, period = read.resolve_range({"period": "week"})
    assert start == date(2026, 9, 18) and end == date(2026, 9, 24)


def test_query_rows_follows_last_evaluated_key(monkeypatch):
    calls = []

    class _Table:
        def query(self, **kw):
            calls.append(kw)
            if "ExclusiveStartKey" not in kw:
                return {"Items": [{"metricDate": "a"}], "LastEvaluatedKey": {"k": 1}}
            return {"Items": [{"metricDate": "b"}]}

    monkeypatch.setattr(read, "table", _Table())
    rows = read.query_rows("overall", "2026-09-01", "2026-09-30")
    assert [r["metricDate"] for r in rows] == ["a", "b"]
    assert calls[1]["ExclusiveStartKey"] == {"k": 1}


def test_unique_users_union_with_legacy_fallback():
    items = [
        {"activeUsers": 3, "userIds": ["a", "b", "c"]},
        {"activeUsers": 2, "userIds": ["b", "d"]},
    ]
    assert read.unique_users(items) == 4
    legacy = [{"activeUsers": 5}, {"activeUsers": 2}]
    assert read.unique_users(legacy) == 5
    assert read.unique_users([]) == 0


def test_build_payload_freshness_and_hourly(monkeypatch):
    monkeypatch.setattr(read, "_now", lambda: datetime(2026, 9, 24, 0, 0, tzinfo=timezone.utc))
    items = [
        {"metricDate": "2026-09-23", "queries": 28, "likeRate": 0.8, "feedbackGood": 4, "feedbackBad": 1,
         "activeUsers": 16, "userIds": ["u1"], "aggregatedAt": "2026-09-23T17:03:00Z", "partial": False,
         "errorRate": 0, "latencyP90": 11.2, "http5xx": 0, "incidents": 0, "topDocuments": []},
        {"metricDate": "2026-09-24", "queries": 4, "likeRate": 0, "feedbackGood": 0, "feedbackBad": 0,
         "activeUsers": 3, "userIds": ["u1", "u2"], "aggregatedAt": "2026-09-23T23:40:00Z", "partial": True,
         "errorRate": 0, "latencyP90": 10.4, "http5xx": 0, "incidents": 0, "topDocuments": []},
    ]
    hourly = [
        {"metricDate": "2026-09-24T07", "queries": 1, "unreached": 0},
        {"metricDate": "2026-09-24T08", "queries": 3, "unreached": 1},
    ]
    payload = read.build_payload(items, "today", hourly)
    assert payload["freshness"] == {"latestDate": "2026-09-24", "aggregatedAt": "2026-09-23T23:40:00Z", "partial": True}
    assert payload["kpi"]["activeUsers"]["value"] == 2
    assert payload["series"]["queriesByHour"] == [
        {"hour": "07", "value": 1, "unreached": 0},
        {"hour": "08", "value": 3, "unreached": 1},
    ]
    # 既存の形は維持
    assert payload["kpi"]["queries"]["value"] == 32
    assert "queriesByDay" in payload["series"] and "health" in payload
