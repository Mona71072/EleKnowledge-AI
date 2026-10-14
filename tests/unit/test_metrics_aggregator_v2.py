"""metrics aggregator v2: JST 境界・毎時 partial・D-1〜D-3 再集計・時間帯別の行。"""
import importlib.util
import os
import sys
from datetime import date, datetime, timedelta, timezone

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")
os.environ.setdefault("METRICS_TABLE", "metrics-test")
os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")


def _load():
    path = os.path.normpath(os.path.join(BASE, "lambda/metrics/aggregator/app.py"))
    spec = importlib.util.spec_from_file_location("metrics_aggregator_v2", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["metrics_aggregator_v2"] = mod
    spec.loader.exec_module(mod)
    return mod


agg = _load()
JST = agg.JST


class FakeTable:
    def __init__(self):
        self.items = []

    def put_item(self, Item):
        self.items.append(Item)


# ------------------------------------------------------------------ JST boundary
def test_jst_date_of_splits_at_utc_15h():
    # UTC 14:59:59 は JST 23:59:59 → 同じ日、UTC 15:00 は JST 翌日 00:00
    assert agg.jst_date_of("2026-09-10T14:59:59.999999Z") == date(2026, 9, 10)
    assert agg.jst_date_of("2026-09-10T15:00:00Z") == date(2026, 9, 11)
    # オフセット無しは UTC とみなす（旧データ）
    assert agg.jst_date_of("2026-09-10T15:00:00") == date(2026, 9, 11)
    # +09:00 表記もそのまま JST 日付になる
    assert agg.jst_date_of("2026-09-11T00:30:00+09:00") == date(2026, 9, 11)
    assert agg.jst_date_of("garbage") is None
    assert agg.jst_date_of(None) is None


def test_query_day_reads_every_shard_of_the_gsi_without_scan(monkeypatch):
    """日別 GSI の全シャードを Query する。Scan は呼ばない（issue #130）。"""
    class NoScan:
        def scan(self, **kw):
            raise AssertionError("aggregator must not Scan chatlogs")

    class ShardedQuery(NoScan):
        def __init__(self):
            self.calls = []

        def query(self, **kw):
            self.calls.append(kw)
            shard_key = kw["KeyConditionExpression"]._values[1]
            if kw.get("ExclusiveStartKey"):
                return {"Items": [{"deleted": False}]}
            # シャード #0 だけ 2 ページ目がある
            if shard_key.endswith("#0"):
                return {"Items": [{"role": "user"}], "LastEvaluatedKey": {"k": "1"}}
            return {"Items": [{"role": "user", "deleted": True}] if shard_key.endswith("#1") else []}

    fake = ShardedQuery()
    monkeypatch.setattr(agg, "chatlogs_table", fake)
    monkeypatch.setattr(agg, "METRIC_DAY_SHARD_COUNT", 3)
    items = agg.query_day(date(2026, 9, 10))

    assert [c["IndexName"] for c in fake.calls][0] == "metricDayShard-timestamp-index"
    assert len({c["IndexName"] for c in fake.calls}) == 1
    assert len(fake.calls) == 4                     # shard 0 は 2 ページ、shard 1 と 2 は 1 回
    assert fake.calls[0]["KeyConditionExpression"]._values[1] == "2026-09-10#0"
    assert [c["KeyConditionExpression"]._values[1] for c in fake.calls][-2:] == ["2026-09-10#1", "2026-09-10#2"]
    # ページング分も含めて全件返る（deleted の除外は FilterExpression の側で行う）
    assert len(items) == 3
    assert "FilterExpression" in fake.calls[0] and fake.calls[0]["ExpressionAttributeNames"] == {"#del": "deleted"}


def test_shard_key_helpers_match_writer_format():
    assert agg.METRIC_DAY_INDEX_NAME == "metricDayShard-timestamp-index"


# ------------------------------------------------------------------ plan (modes)
def test_plan_daily_reaggregates_three_days():
    now = datetime(2026, 9, 24, 2, 0, tzinfo=JST)
    days = agg.plan({"mode": "daily"}, now)
    assert [d.isoformat() for d, _, _ in days] == ["2026-09-23", "2026-09-22", "2026-09-21"]
    assert all(partial is False and upto == 23 for _, partial, upto in days)


def test_plan_default_is_daily():
    now = datetime(2026, 9, 24, 2, 0, tzinfo=JST)
    assert len(agg.plan({}, now)) == 3
    assert len(agg.plan(None, now)) == 3


def test_plan_hourly_targets_today_partial_up_to_current_hour():
    now = datetime(2026, 9, 24, 8, 40, tzinfo=JST)
    days = agg.plan({"mode": "hourly"}, now)
    assert days == [(date(2026, 9, 24), True, 8)]


def test_plan_manual_date_is_final():
    now = datetime(2026, 9, 24, 8, 40, tzinfo=JST)
    assert agg.plan({"date": "2026-09-01"}, now) == [(date(2026, 9, 1), False, 23)]


# ------------------------------------------------------------------ aggregate_chat (new fields)
def _items():
    return [
        {"role": "user", "userId": "u1", "sessionId": "s1", "timestamp": "2026-09-10T00:10:00Z"},
        {"role": "assistant", "sessionId": "s1", "responseType": "pages", "feedback": "good",
         "timestamp": "2026-09-10T00:10:20Z", "sourceDocuments": [{"documentName": "a.pdf"}]},
        {"role": "user", "userId": "u2", "sessionId": "s2", "timestamp": "2026-09-10T03:00:00Z"},
        {"role": "assistant", "sessionId": "s2", "responseType": "not_found", "feedback": "bad",
         "feedbackReason": "wrong_doc", "timestamp": "2026-09-10T03:00:30Z"},
        {"role": "user", "userId": "u1", "sessionId": "s1", "timestamp": "2026-09-10T03:05:00Z"},
        {"role": "assistant", "sessionId": "s1", "responseType": "clarify", "timestamp": "2026-09-10T03:05:10Z"},
        {"role": "assistant", "sessionId": "s3", "responseType": "pages", "feedback": "bad",
         "timestamp": "2026-09-10T05:00:00Z"},
        {"role": "product_wish", "userId": "u3", "sessionId": "wish-u3", "timestamp": "2026-09-10T06:00:00Z"},
    ]


def test_aggregate_chat_new_fields():
    out = agg.aggregate_chat(_items())
    assert out["queries"] == 3
    assert out["activeUsers"] == 2 and out["userIds"] == ["u1", "u2"]
    assert out["sessions"] == 3          # wish のセッションは数えない
    assert out["notFound"] == 1 and out["clarify"] == 1 and out["pages"] == 2
    assert out["feedbackGood"] == 1 and out["feedbackBad"] == 2
    assert out["feedbackReasons"] == {"wrong_doc": 1, "unresolved": 0, "bad_answer": 0, "other": 0, "none": 1}
    assert out["unreached"] == 2         # not_found+bad は 1 件、pages+bad が 1 件
    assert out["productWishes"] == 1
    assert out["topDocuments"] == [{"name": "a.pdf", "count": 1}]


def test_aggregate_hourly_buckets_by_jst_hour():
    hourly = agg.aggregate_hourly(_items())
    assert set(hourly) == set(range(24))
    # 00:10Z = 09:10 JST
    assert hourly[9]["queries"] == 1 and hourly[9]["pages"] == 1 and hourly[9]["feedbackGood"] == 1
    # 03:00Z = 12:00 JST
    assert hourly[12]["queries"] == 2 and hourly[12]["notFound"] == 1 and hourly[12]["clarify"] == 1
    assert hourly[12]["activeUsers"] == 2 and hourly[12]["unreached"] == 1
    assert hourly[14]["unreached"] == 1
    assert hourly[0] == {"queries": 0, "notFound": 0, "clarify": 0, "pages": 0,
                         "feedbackGood": 0, "feedbackBad": 0, "unreached": 0, "activeUsers": 0}


# ------------------------------------------------------------------ write_day
def test_write_day_writes_daily_and_hourly_rows_without_ttl(monkeypatch):
    fake = FakeTable()
    monkeypatch.setattr(agg, "metrics_table", fake)
    monkeypatch.setattr(agg, "query_day", lambda day: _items())
    monkeypatch.setattr(agg, "aggregate_platform", lambda day, chat: {"errorRate": 0.0, "latencyP90": 1.0, "http5xx": 0, "incidents": 0})
    monkeypatch.setattr(agg, "count_new_users", lambda ids, day: 0)

    result = agg.write_day(date(2026, 9, 10), partial=True, upto_hour=8)
    assert result["date"] == "2026-09-10" and result["partial"] is True

    daily = [i for i in fake.items if i["scope"] == "overall"]
    hourly = [i for i in fake.items if i["scope"] == "hourly"]
    assert len(daily) == 1 and len(hourly) == 9          # 00〜08 時
    row = daily[0]
    assert row["metricDate"] == "2026-09-10" and row["partial"] is True
    assert "ttl" not in row
    assert row["logicVersion"] == agg.LOGIC_VERSION
    assert row["queries"] == 3
    assert hourly[0]["metricDate"] == "2026-09-10T00" and hourly[-1]["metricDate"] == "2026-09-10T08"


def test_write_day_final_writes_24_hourly_rows(monkeypatch):
    fake = FakeTable()
    monkeypatch.setattr(agg, "metrics_table", fake)
    monkeypatch.setattr(agg, "query_day", lambda day: [])
    monkeypatch.setattr(agg, "aggregate_platform", lambda day, chat: {"errorRate": 0.0, "latencyP90": 0.0, "http5xx": 0, "incidents": 0})
    monkeypatch.setattr(agg, "count_new_users", lambda ids, day: 0)
    agg.write_day(date(2026, 9, 10), partial=False)
    daily = [i for i in fake.items if i["scope"] == "overall"]
    assert daily[0]["partial"] is False and daily[0]["queries"] == 0
    assert len([i for i in fake.items if i["scope"] == "hourly"]) == 24


def test_lambda_handler_daily_runs_three_days(monkeypatch):
    calls = []
    monkeypatch.setattr(agg, "write_day", lambda day, partial, upto_hour=23: calls.append((day.isoformat(), partial)) or {"date": day.isoformat()})
    monkeypatch.setattr(agg, "jst_now", lambda: datetime(2026, 9, 24, 2, 0, tzinfo=JST))
    monkeypatch.setattr(agg, "write_cost_rows", lambda: {"costRows": 0})
    out = agg.lambda_handler({"mode": "daily"}, None)
    assert out["statusCode"] == 200
    assert calls == [("2026-09-23", False), ("2026-09-22", False), ("2026-09-21", False)]
