"""GSI migration with real DynamoDB expressions and synthetic data only.

Default: moto. Opt in to AWS with RUN_AWS_DYNAMODB_INTEGRATION=1 and
AWS_PROFILE. A uniquely named table owned by this run is the only write target.
"""
import importlib.util
import os
import sys
import time
import uuid
from contextlib import nullcontext
from datetime import date, datetime, timezone
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

ROOT = Path(__file__).resolve().parents[2]


def load(name, relative):
    source = ROOT / relative
    old_path = list(sys.path)
    before = set(sys.modules)
    sys.path.insert(0, str(source.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = old_path
        for key in set(sys.modules) - before:
            loaded = sys.modules.get(key)
            if str(getattr(loaded, "__file__", "")).startswith(str(source.parent)):
                sys.modules.pop(key, None)


@pytest.fixture
def synthetic_table(monkeypatch):
    real_aws = os.environ.get("RUN_AWS_DYNAMODB_INTEGRATION") == "1"
    if real_aws and not os.environ.get("AWS_PROFILE"):
        pytest.fail("real AWS requires an explicit operator AWS_PROFILE")
    region = os.environ.get("AWS_DEFAULT_REGION", "ap-northeast-1")
    name = "eleknowledge-gsi-eval-dev-" + uuid.uuid4().hex[:12]
    with nullcontext() if real_aws else mock_aws():
        session = boto3.Session(region_name=region)
        ddb = session.resource("dynamodb")
        table = ddb.create_table(
            TableName=name,
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[{"AttributeName": key, "AttributeType": "S"} for key in
                                  ("sessionId", "messageId", "timestamp", "metricDayShard")],
            KeySchema=[{"AttributeName": "sessionId", "KeyType": "HASH"},
                       {"AttributeName": "messageId", "KeyType": "RANGE"}],
            GlobalSecondaryIndexes=[{
                "IndexName": "metricDayShard-timestamp-index",
                "KeySchema": [{"AttributeName": "metricDayShard", "KeyType": "HASH"},
                              {"AttributeName": "timestamp", "KeyType": "RANGE"}],
                "Projection": {"ProjectionType": "ALL"},
            }],
            Tags=[{"Key": "Purpose", "Value": "PR183SyntheticTest"}],
        )
        created_arn = table.table_arn
        try:
            table.wait_until_exists(WaiterConfig={"Delay": 1, "MaxAttempts": 60})
            monkeypatch.setenv("CHATLOGS_TABLE", name)
            monkeypatch.setenv("METRICS_TABLE", "unused-synthetic-metrics")
            monkeypatch.setenv("CHATLOGS_METRIC_SHARDS", "10")
            monkeypatch.setenv("AWS_REGION", region)
            yield table
        finally:
            # Only the table newly created by this fixture may be removed.
            assert table.name == name and table.table_arn == created_arn
            table.delete()
            table.wait_until_not_exists(WaiterConfig={"Delay": 1, "MaxAttempts": 60})


class SmallPages:
    def __init__(self, table):
        self.table = table
        self.query_calls = 0

    def query(self, **kwargs):
        self.query_calls += 1
        return self.table.query(**kwargs, Limit=2)


def test_backfill_writers_and_aggregation_agree(synthetic_table, monkeypatch):
    table = synthetic_table
    backfill = load("integration_backfill", "scripts/ops/backfill_chatlogs_metric_day.py")
    agg = load("integration_agg", "lambda/metrics/aggregator/app.py")
    rag = load("integration_rag", "lambda/rag/rag-function/app.py")
    chat = load("integration_chat", "lambda/chat/chat-management/app.py")
    rag.chatlogs_table = chat.chatlogs_table = table
    # Old rows have no GSI key. Include both sides of midnight JST and deleted rows.
    with table.batch_writer() as batch:
        for i in range(36):
            batch.put_item(Item={
                "sessionId": "synthetic-old", "messageId": f"old-{i}",
                "timestamp": "2026-10-01T14:59:59.999999Z" if i < 12 else "2026-10-01T15:00:00Z",
                "role": "assistant" if i % 2 else "user", "userId": "synthetic-user",
                "content": "synthetic fixture", "deleted": i % 7 == 0,
                "responseType": "not_found" if i % 3 == 0 else "pages",
                "feedback": "good" if i % 3 else "bad",
            })
    assert backfill.run_backfill(table, False, 0, 10)["would_update"] == 36
    result = backfill.run_backfill(table, True, 0, 10, sleep=lambda _: None)
    assert result["updated"] == 36 and not result.get("errors")
    assert backfill.run_backfill(table, True, 0, 10).get("updated", 0) == 0

    message_id = rag.save_message_to_dynamodb("synthetic-new", "synthetic-user", "user", "synthetic question")
    wish = chat.save_product_wish("synthetic-user", "synthetic wish")
    for sid, mid in (("synthetic-new", message_id), ("wish-synthetic-user", wish["messageId"])):
        item = table.get_item(Key={"sessionId": sid, "messageId": mid}, ConsistentRead=True).get("Item")
        assert item and item["metricDayShard"].startswith(item["metricDay"] + "#")

    rows = table.scan(ConsistentRead=True)["Items"]
    assert len(rows) == 38
    assert all("metricDayShard" in row for row in rows)
    days = sorted({date.fromisoformat(row["metricDay"]) for row in rows})
    small_pages = SmallPages(table)
    agg.chatlogs_table = small_pages
    deadline = time.monotonic() + 60
    while True:
        queried = {day: agg.query_day(day) for day in days}
        expected = {day: [r for r in rows if r["metricDay"] == day.isoformat() and r.get("deleted") is not True] for day in days}
        if all(len(queried[day]) == len(expected[day]) for day in days):
            break
        assert time.monotonic() < deadline, "GSI did not converge before the verification deadline"
        time.sleep(1)
    assert small_pages.query_calls > len(days) * 10  # pagination actually happened
    for day in days:
        assert agg.aggregate_chat(queried[day]) == agg.aggregate_chat(expected[day])
    assert all(r["match"] for r in backfill.verify_days(table, days, 10))
