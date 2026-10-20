"""chatlogs 日別キーのバックフィル（scripts/ops/backfill_chatlogs_metric_day.py）。issue #130。"""
import importlib.util
import os
from datetime import date

import pytest
from botocore.exceptions import ClientError

BASE = os.path.join(os.path.dirname(__file__), "../..")


def _load():
    path = os.path.normpath(os.path.join(BASE, "scripts/ops/backfill_chatlogs_metric_day.py"))
    spec = importlib.util.spec_from_file_location("backfill_chatlogs_metric_day", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bf = _load()


class FakeTable:
    """Scan は未キー行だけを返す（FilterExpression の代わり）。update_item は条件を再現する。"""

    def __init__(self, rows, queryable=None):
        self.rows = rows                  # 行のリスト（dict）
        self.updates = []
        self.queryable = queryable or {}  # "day#shard" → 件数

    def scan(self, **kw):
        if "ExclusiveStartKey" in kw:
            return {"Items": []}
        return {"Items": [dict(r) for r in self.rows if "metricDayShard" not in r]}

    def update_item(self, Key, UpdateExpression, ConditionExpression, ExpressionAttributeValues):
        row = next(r for r in self.rows if r["sessionId"] == Key["sessionId"] and r["messageId"] == Key["messageId"])
        if "metricDayShard" in row:
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException", "Message": "x"}}, "UpdateItem")
        self.updates.append((Key, ExpressionAttributeValues))
        row["metricDayShard"] = ExpressionAttributeValues[":s"]
        row["metricDay"] = ExpressionAttributeValues[":d"]
        return {}


def _rows():
    return [
        {"sessionId": "s1", "messageId": "m1", "timestamp": "2026-09-10T14:59:59.999999Z"},
        {"sessionId": "s1", "messageId": "m2", "timestamp": "2026-09-10T15:00:00Z", "deleted": True},
        {"sessionId": "s2", "messageId": "m3", "timestamp": "not-a-time"},
        {"sessionId": "s2", "messageId": "m4", "timestamp": "2026-09-11T01:00:00Z", "metricDayShard": "2026-09-11#3"},
    ]


def test_dry_run_counts_without_writing():
    table = FakeTable(_rows())
    summary = bf.run_backfill(table, apply=False, rps=0, shard_count=10, sleep=lambda s: None)
    assert summary["mode"] == "dry-run"
    assert summary["scanned"] == 3
    assert summary["would_update"] == 2
    assert summary["skipped_bad_timestamp"] == 1
    assert summary["perDay"] == {"2026-09-10": 1, "2026-09-11": 1}
    assert table.updates == []


def test_apply_writes_only_missing_keys_with_jst_day_and_condition():
    table = FakeTable(_rows())
    summary = bf.run_backfill(table, apply=True, rps=0, shard_count=10, sleep=lambda s: None)
    assert summary["updated"] == 2
    assert {k["messageId"] for k, _ in table.updates} == {"m1", "m2"}
    by_msg = {k["messageId"]: v for k, v in table.updates}
    assert by_msg["m1"][":d"] == "2026-09-10"       # UTC 14:59:59.999999 は JST 同日
    assert by_msg["m2"][":d"] == "2026-09-11"       # UTC 15:00 は JST 翌日
    assert by_msg["m1"][":s"].startswith("2026-09-10#")


def test_rerun_does_not_overwrite_already_keyed_rows():
    table = FakeTable(_rows())
    bf.run_backfill(table, apply=True, rps=0, shard_count=10, sleep=lambda s: None)
    second = bf.run_backfill(table, apply=True, rps=0, shard_count=10, sleep=lambda s: None)
    assert second.get("updated", 0) == 0 and second.get("errors", 0) == 0


def test_summary_never_contains_bodies_or_ids():
    rows = _rows()
    rows[0]["content"] = "秘密の本文"
    summary = bf.run_backfill(FakeTable(rows), apply=False, rps=0, shard_count=10, sleep=lambda s: None)
    text = repr(summary)
    assert "秘密の本文" not in text and "m1" not in text and "s1" not in text


def test_throttling_is_retried_with_backoff():
    calls = {"n": 0}
    sleeps = []

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ClientError({"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "x"}}, "UpdateItem")
        return "ok"

    assert bf._retry(flaky, sleep=sleeps.append) == "ok"
    assert calls["n"] == 3 and sleeps == [0.5, 1.0]


def test_other_errors_are_not_retried():
    def denied():
        raise ClientError({"Error": {"Code": "AccessDeniedException", "Message": "x"}}, "UpdateItem")

    with pytest.raises(ClientError):
        bf._retry(denied, sleep=lambda s: None)


def test_verify_compares_scan_counts_with_each_shard_query():
    rows = [
        {"sessionId": "s1", "messageId": "m1", "timestamp": "2026-09-10T03:00:00Z", "metricDay": "2026-09-10", "metricDayShard": "2026-09-10#0"},
        {"sessionId": "s1", "messageId": "m2", "timestamp": "2026-09-10T04:00:00Z", "metricDay": "2026-09-10", "metricDayShard": "2026-09-10#1"},
        {"sessionId": "s1", "messageId": "m3", "timestamp": "2026-09-10T05:00:00Z", "deleted": True, "metricDay": "2026-09-10", "metricDayShard": "2026-09-10#1"},
    ]

    class Table(FakeTable):
        def scan(self, **kw):
            return {"Items": [dict(r) for r in self.rows]}

        def query(self, IndexName, KeyConditionExpression, ExpressionAttributeValues, ProjectionExpression,
                  FilterExpression, ExpressionAttributeNames):
            assert IndexName == "metricDayShard-timestamp-index"
            assert ExpressionAttributeNames == {"#del": "deleted"}
            key = ExpressionAttributeValues[":k"]
            # FilterExpression（論理削除の除外）は DynamoDB 側で掛かる。ここでは同じ条件を再現する
            return {"Items": [dict(r) for r in self.rows
                              if r.get("metricDayShard") == key and r.get("deleted") is not True]}

    report = bf.verify_days(Table(rows), [date(2026, 9, 10)], shard_count=2)
    assert report == [{"day": "2026-09-10", "scan": 2, "query": 2, "match": True}]


def test_table_name_must_be_chatlogs_env():
    with pytest.raises(SystemExit):
        bf.main(["--table", "users-dev"])


@pytest.mark.parametrize("args", [
    ["--shards", "0"], ["--rps", "0"], ["--rps", "-1"],
    ["--verify-days", "-1"], ["--verify-days", "61"],
])
def test_invalid_migration_options_fail_before_aws_calls(monkeypatch, args):
    def unexpected_call(*_args):
        raise AssertionError("invalid input must not contact AWS")
    monkeypatch.setattr(bf, "_build_table", unexpected_call)
    with pytest.raises(SystemExit) as error:
        bf.main(["--table", "chatlogs-dev", *args])
    assert error.value.code == 2


def test_bad_timestamp_prevents_success_exit(monkeypatch):
    monkeypatch.setattr(bf, "_build_table", lambda *_: FakeTable(_rows()))
    assert bf.main(["--table", "chatlogs-dev"]) == 1
