"""有効なメンテ告知が通常告知の件数に押し出されないこと（issue #94 B1、PR #95 レビュー）。"""
import importlib.util
import os
import sys

BASE = os.path.join(os.path.dirname(__file__), "../..")
os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")
os.environ.setdefault("ANNOUNCEMENTS_TABLE", "announcements-test")


def _load():
    path = os.path.normpath(os.path.join(BASE, "lambda/announcements/read/app.py"))
    mod_dir = os.path.dirname(path)
    if mod_dir not in sys.path:
        sys.path.insert(0, mod_dir)
    spec = importlib.util.spec_from_file_location("ann_read_maint", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ann_read_maint"] = mod
    spec.loader.exec_module(mod)
    return mod


NOW = "2026-09-10T03:00:00.000Z"
OLD_MAINT = {
    "announcementId": "m-old", "type": "maintenance", "status": "published", "severity": "critical",
    "publishAt": "2026-08-01T00:00:00.000Z",
    "startAt": "2026-09-10T02:00:00.000Z", "endAt": "2026-09-10T05:00:00.000Z",
}
NEWER = [
    {"announcementId": f"n{i}", "type": "notice", "status": "published", "severity": "info",
     "publishAt": f"2026-09-0{1 + i % 9}T{i % 24:02d}:00:00.000Z"}
    for i in range(31)
]


class FakeTable:
    """status-publishAt-index の Query を模す（published のみ返す。FilterExpression 有無で絞る）。"""

    def __init__(self, items):
        self.items = items

    def query(self, **kw):
        page = [it for it in self.items if it["status"] == "published"]
        page.sort(key=lambda x: x["publishAt"], reverse=True)
        if "FilterExpression" in kw:
            page = [it for it in page if it["type"] == "maintenance"]
        limit = kw.get("Limit")
        if limit:
            page = page[:limit]
        return {"Items": page}


def test_active_maintenance_not_starved_by_newer_notices(monkeypatch):
    mod = _load()
    monkeypatch.setattr(mod, "table", FakeTable(NEWER + [OLD_MAINT]))
    # 通常一覧（30 件要求）には古いメンテ告知が入らない = レビューで再現された条件
    listed = {it["announcementId"] for it in mod.get_published(30, NOW)}
    assert "m-old" not in listed
    # 独立した取得では必ず拾える
    active = mod.get_active_maintenance(NOW)
    assert [it["announcementId"] for it in active] == ["m-old"]


def test_active_maintenance_excludes_outside_window(monkeypatch):
    mod = _load()
    ended = {**OLD_MAINT, "announcementId": "m-ended", "endAt": "2026-09-10T02:30:00.000Z"}
    future = {**OLD_MAINT, "announcementId": "m-future",
              "startAt": "2026-09-11T00:00:00.000Z", "endAt": "2026-09-11T01:00:00.000Z"}
    monkeypatch.setattr(mod, "table", FakeTable([ended, future, OLD_MAINT]))
    assert [it["announcementId"] for it in mod.get_active_maintenance(NOW)] == ["m-old"]
