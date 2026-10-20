"""chatlogs の日別集計キー（metricDay / metricDayShard）。書込み側 2 か所の一致と JST 境界（issue #130）。"""
import importlib.util
import os
from datetime import datetime, timezone

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")
PATHS = [
    os.path.normpath(os.path.join(BASE, "lambda/rag/rag-function/chatlog_metric_keys.py")),
    os.path.normpath(os.path.join(BASE, "lambda/chat/chat-management/chatlog_metric_keys.py")),
]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RAG_KEYS = _load(PATHS[0], "chatlog_metric_keys_rag")
CHAT_KEYS = _load(PATHS[1], "chatlog_metric_keys_chat")


def test_two_copies_are_identical():
    assert open(PATHS[0], encoding="utf-8").read() == open(PATHS[1], encoding="utf-8").read()


@pytest.mark.parametrize("mod", [RAG_KEYS, CHAT_KEYS])
def test_jst_boundary_decides_metric_day(mod):
    # UTC 14:59:59.999999 は JST 23:59:59 → 同じ日。UTC 15:00 は JST 翌日 00:00
    before = datetime(2026, 9, 10, 14, 59, 59, 999999, tzinfo=timezone.utc)
    at = datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc)
    assert mod.metric_day_keys(before, "msg_1")["metricDay"] == "2026-09-10"
    assert mod.metric_day_keys(at, "msg_1")["metricDay"] == "2026-09-11"


@pytest.mark.parametrize("mod", [RAG_KEYS, CHAT_KEYS])
def test_shard_is_stable_and_within_range(mod):
    ts = datetime(2026, 9, 10, 3, 0, tzinfo=timezone.utc)
    first = mod.metric_day_keys(ts, "msg_abc", shard_count=10)
    assert first == mod.metric_day_keys(ts, "msg_abc", shard_count=10)
    day, shard = first["metricDayShard"].split("#")
    assert day == first["metricDay"] == "2026-09-10"
    assert 0 <= int(shard) < 10
    # 件数の多い日でも同じ partition に集まりすぎない（messageId の違いで複数のシャードに散る）
    shards = {mod.metric_day_keys(ts, f"msg_{i}", shard_count=10)["metricDayShard"] for i in range(200)}
    assert len(shards) == 10


def test_parse_timestamp_accepts_z_and_offsets():
    parsed = RAG_KEYS.parse_chatlog_timestamp("2026-09-10T15:00:00.123456Z")
    assert parsed == datetime(2026, 9, 10, 15, 0, 0, 123456, tzinfo=timezone.utc)
    assert RAG_KEYS.parse_chatlog_timestamp("2026-09-11T00:30:00+09:00").utcoffset().total_seconds() == 9 * 3600
    assert RAG_KEYS.parse_chatlog_timestamp("2026-09-10T15:00:00").tzinfo == timezone.utc
    assert RAG_KEYS.parse_chatlog_timestamp("garbage") is None
    assert RAG_KEYS.parse_chatlog_timestamp(None) is None


def test_naive_datetime_is_rejected():
    with pytest.raises(ValueError):
        RAG_KEYS.metric_day_keys(datetime(2026, 9, 10, 3, 0), "msg_1")
