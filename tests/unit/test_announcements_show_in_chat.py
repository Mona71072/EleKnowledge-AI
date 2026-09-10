"""お知らせ: チャット画面にも出す印（showInChat）の保存（設計 2026-09-10 dashboard v2 §10.4）。"""
import importlib.util
import os
import sys

import pytest

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


write = _load("ann_write_chat", "lambda/announcements/write/app.py")


class FakeTable:
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        self.items[Item["announcementId"]] = dict(Item)

    def get_item(self, Key):
        it = self.items.get(Key["announcementId"])
        return {"Item": dict(it)} if it else {}


@pytest.fixture
def table(monkeypatch):
    fake = FakeTable()
    monkeypatch.setattr(write, "table", fake)
    return fake


def _one(table):
    return next(iter(table.items.values()))


def test_create_defaults_show_in_chat_from_severity(table):
    write.create({"type": "notice", "severity": "critical", "status": "published", "title": "障害中"}, actor="u")
    assert _one(table)["showInChat"] is True
    table.items.clear()
    write.create({"type": "notice", "severity": "info", "status": "published", "title": "情報"}, actor="u")
    assert _one(table)["showInChat"] is False


def test_create_respects_explicit_show_in_chat(table):
    write.create({"type": "notice", "severity": "critical", "status": "draft", "title": "t", "showInChat": False}, actor="u")
    assert _one(table)["showInChat"] is False
    table.items.clear()
    write.create({"type": "update", "severity": "info", "status": "draft", "title": "t", "showInChat": True}, actor="u")
    assert _one(table)["showInChat"] is True


def test_update_toggles_show_in_chat_and_keeps_it_when_absent(table):
    table.put_item({"announcementId": "anc_1", "type": "notice", "title": "t", "body": "", "severity": "info",
                    "status": "published", "publishAt": "2026-01-01T00:00:00.000Z", "showInChat": True})
    resp = write.update("anc_1", {"title": "t2"}, actor="u")
    assert resp["statusCode"] == 200 and table.items["anc_1"]["showInChat"] is True
    resp = write.update("anc_1", {"showInChat": False}, actor="u")
    assert resp["statusCode"] == 200 and table.items["anc_1"]["showInChat"] is False


def test_update_end_now_keeps_other_fields(table):
    """表示終了は endAt を今にする更新（削除ではない）。"""
    table.put_item({"announcementId": "anc_9", "type": "notice", "title": "障害中", "body": "", "severity": "critical",
                    "status": "published", "publishAt": "2026-09-23T23:05:00.000Z", "showInChat": True, "pinned": True})
    resp = write.update("anc_9", {"endAt": "2026-09-24T01:30:00.000Z"}, actor="u")
    assert resp["statusCode"] == 200
    it = table.items["anc_9"]
    assert it["endAt"] == "2026-09-24T01:30:00.000Z" and it["title"] == "障害中" and it["showInChat"] is True
