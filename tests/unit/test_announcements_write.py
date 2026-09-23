"""お知らせ write / publisher の DynamoDB 操作を FakeTable で検証する（issue #94）。

これまで create / update / delete と部分更新のバリデーションにテストが無く、
Bug B2〜B4・Risk R1・R7・R8 はすべてその空白にあった。
"""
import importlib.util
import os
import sys

import pytest
from botocore.exceptions import ClientError

BASE = os.path.join(os.path.dirname(__file__), "../..")

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")
os.environ.setdefault("ANNOUNCEMENTS_TABLE", "announcements-test")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    mod_dir = os.path.dirname(path)
    if mod_dir not in sys.path:
        sys.path.insert(0, mod_dir)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


write = _load("ann_write_ops", "lambda/announcements/write/app.py")
publisher = _load("ann_publisher_ops", "lambda/announcements/publisher/app.py")


class FakeTable:
    """put/get/delete/query の最小実装。"""

    def __init__(self, items=None):
        self.items = {it["announcementId"]: dict(it) for it in (items or [])}
        self.updates = []
        self.query_pages = []  # publisher 用: 事前に用意したページ

    def put_item(self, Item):
        self.items[Item["announcementId"]] = dict(Item)

    def get_item(self, Key):
        it = self.items.get(Key["announcementId"])
        return {"Item": dict(it)} if it else {}

    def delete_item(self, Key, ConditionExpression=None):
        aid = Key["announcementId"]
        if ConditionExpression and aid not in self.items:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException", "Message": "no such item"}},
                "DeleteItem",
            )
        self.items.pop(aid, None)
        return {}

    def query(self, **kwargs):
        # ページを順に返し、最後のページには LastEvaluatedKey を付けない
        page = self.query_pages.pop(0)
        resp = {"Items": page}
        if self.query_pages:
            resp["LastEvaluatedKey"] = {"announcementId": page[-1]["announcementId"]}
        return resp

    def update_item(self, **kwargs):
        self.updates.append(kwargs)
        aid = kwargs["Key"]["announcementId"]
        it = self.items.get(aid)
        if it is not None:
            it["status"] = "published"
        return {}


def _body(resp):
    import json
    return json.loads(resp["body"])


@pytest.fixture
def table(monkeypatch):
    fake = FakeTable()
    monkeypatch.setattr(write, "table", fake)
    return fake


# ----------------------------------------------------------------- create
def test_create_ignores_client_ttl(table):
    resp = write.create({
        "type": "notice", "severity": "info", "status": "published",
        "title": "t", "body": "b", "ttl": "1",  # 過去 epoch を渡しても保存されない（B2）
    }, actor="u")
    assert resp["statusCode"] == 201
    item = next(iter(table.items.values()))
    assert "ttl" not in item


def test_create_ids_do_not_collide_in_same_millisecond(table, monkeypatch):
    monkeypatch.setattr(write.time, "time", lambda: 1700000000.0)
    for _ in range(2):
        write.create({"type": "notice", "severity": "info", "status": "published", "title": "t"}, actor="u")
    assert len(table.items) == 2  # R5: 同一ミリ秒でも上書きしない


# ----------------------------------------------------------------- update
def _maintenance(aid="anc_1"):
    return {
        "announcementId": aid, "type": "maintenance", "title": "メンテ", "body": "",
        "severity": "warning", "status": "published",
        "publishAt": "2026-01-01T00:00:00.000Z",
        "startAt": "2026-01-10T00:00:00.000Z", "endAt": "2026-01-10T02:00:00.000Z",
        "createdAt": "2026-01-01T00:00:00.000Z", "updatedAt": "2026-01-01T00:00:00.000Z",
    }


def test_update_to_maintenance_requires_window_even_when_partial(table):
    table.put_item({**_maintenance(), "type": "notice", "startAt": None, "endAt": None})
    table.items["anc_1"].pop("startAt"); table.items["anc_1"].pop("endAt")
    resp = write.update("anc_1", {"type": "maintenance"}, actor="u")  # B3
    assert resp["statusCode"] == 400
    assert "startAt and endAt" in _body(resp)["message"]


def test_update_away_from_maintenance_drops_stale_window(table):
    table.put_item(_maintenance())
    resp = write.update("anc_1", {"type": "notice"}, actor="u")  # B4
    assert resp["statusCode"] == 200
    item = table.items["anc_1"]
    assert "startAt" not in item and "endAt" not in item


def test_update_away_from_maintenance_keeps_explicit_end_at(table):
    table.put_item(_maintenance())
    resp = write.update("anc_1", {"type": "notice", "endAt": "2026-02-01T00:00:00Z"}, actor="u")
    assert resp["statusCode"] == 200
    assert table.items["anc_1"]["endAt"] == "2026-02-01T00:00:00.000Z"
    assert "startAt" not in table.items["anc_1"]


def test_update_blank_window_removes_attribute_instead_of_null(table):
    table.put_item({**_maintenance(), "type": "notice"})
    resp = write.update("anc_1", {"endAt": ""}, actor="u")  # R7
    assert resp["statusCode"] == 200
    assert "endAt" not in table.items["anc_1"]


def test_update_maintenance_rejects_inverted_window(table):
    table.put_item(_maintenance())
    resp = write.update("anc_1", {"startAt": "2026-01-10T03:00:00Z"}, actor="u")
    assert resp["statusCode"] == 400


def test_update_not_found(table):
    assert write.update("missing", {"title": "x"}, actor="u")["statusCode"] == 404


# ----------------------------------------------------------------- delete
def test_delete_missing_returns_404(table):
    assert write.delete("missing")["statusCode"] == 404  # R8


def test_delete_existing_returns_200(table):
    table.put_item(_maintenance())
    assert write.delete("anc_1")["statusCode"] == 200
    assert "anc_1" not in table.items


# ----------------------------------------------------------------- publisher
def test_promote_due_reads_all_pages_before_updating(monkeypatch):
    fake = FakeTable()
    fake.query_pages = [
        [{"announcementId": "a1", "publishAt": "2026-01-01T00:00:00.000Z", "status": "scheduled"}],
        [{"announcementId": "a2", "publishAt": "2026-01-01T00:00:00.000Z", "status": "scheduled"}],
    ]
    monkeypatch.setattr(publisher, "table", fake)
    result = publisher.promote_due("2026-01-02T00:00:00Z")
    assert sorted(result["promoted"]) == ["a1", "a2"]  # R1: 2 ページ目も取りこぼさない
    assert len(fake.updates) == 2
    assert fake.query_pages == []  # 更新前に全ページを読み切っている
