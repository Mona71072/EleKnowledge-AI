"""chat-archive Lambda: 失敗バッチの生レコード保全（PR #96 レビュー指摘）。"""
import importlib.util
import os
import sys

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")
os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("ARCHIVE_BUCKET", "archive-test")


def _load():
    path = os.path.normpath(os.path.join(BASE, "lambda/chat-archive/app.py"))
    spec = importlib.util.spec_from_file_location("chat_archive_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["chat_archive_app"] = mod
    spec.loader.exec_module(mod)
    return mod


class Ctx:
    aws_request_id = "req-1"


class FakeS3:
    def __init__(self, fail_prefix=None):
        self.puts = []
        self.fail_prefix = fail_prefix

    def put_object(self, **kw):
        if self.fail_prefix and kw["Key"].startswith(self.fail_prefix):
            raise RuntimeError("s3 down for " + kw["Key"])
        self.puts.append(kw)
        return {}


EVENT = {"Records": [{
    "eventName": "INSERT", "eventID": "e1",
    "dynamodb": {"ApproximateCreationDateTime": 1760000000,
                 "Keys": {"sessionId": {"S": "s1"}, "messageId": {"S": "m1"}},
                 "NewImage": {"sessionId": {"S": "s1"}, "messageId": {"S": "m1"}, "content": {"S": "hi"}}},
}]}


def test_success_writes_gzip_archive(monkeypatch):
    mod = _load()
    s3 = FakeS3(); monkeypatch.setattr(mod, "s3", s3)
    out = mod.handler(EVENT, Ctx())
    assert out["archived"] == 1 and out["key"].startswith("chatlogs/dt=")
    assert len(s3.puts) == 1


def test_failure_preserves_raw_records_then_reraises(monkeypatch):
    mod = _load()
    s3 = FakeS3(fail_prefix="chatlogs/"); monkeypatch.setattr(mod, "s3", s3)
    with pytest.raises(RuntimeError):
        mod.handler(EVENT, Ctx())
    assert len(s3.puts) == 1
    key = s3.puts[0]["Key"]
    assert key.startswith("failed/dt=") and key.endswith("req-1.json")
    body = s3.puts[0]["Body"].decode("utf-8")
    assert "e1" in body and "RuntimeError" in body


def test_failure_when_s3_fully_down_still_reraises(monkeypatch):
    mod = _load()
    s3 = FakeS3(fail_prefix=""); monkeypatch.setattr(mod, "s3", s3)  # every put fails
    with pytest.raises(RuntimeError):
        mod.handler(EVENT, Ctx())
    assert s3.puts == []
