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
            expression = kw["FilterExpression"]
            condition = expression
            while not hasattr(condition, "name"):
                condition = condition._values[0]
            if condition.name == "type":
                page = [it for it in page if it["type"] == "maintenance"]
            else:
                # DynamoDB は Limit 件を評価した後に FilterExpression を適用する。
                page = [it for it in page if not it.get("endAt") or it["endAt"] >= NOW]
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


class PaginatedAnnouncementsTable:
    """Limit の評価後に FilterExpression を適用する Query の簡易モデル。"""

    def __init__(self, items):
        self.items = items
        self.calls = []

    def query(self, **kw):
        self.calls.append(kw)
        status_condition = kw["KeyConditionExpression"]._values[0]
        status = status_condition._values[1]
        page_items = [it for it in self.items if it["status"] == status]
        page_items.sort(key=lambda it: it["publishAt"], reverse=True)
        offset = (kw.get("ExclusiveStartKey") or {}).get("offset", 0)
        limit = kw.get("Limit", len(page_items))
        evaluated = page_items[offset:offset + limit]
        next_offset = offset + len(evaluated)
        response = {"Items": [it for it in evaluated if "FilterExpression" not in kw or
                               not it.get("endAt") or it["endAt"] >= NOW]}
        if next_offset < len(page_items):
            response["LastEvaluatedKey"] = {"offset": next_offset}
        return response


def test_public_list_pages_past_expired_items_until_limit_is_filled(monkeypatch):
    mod = _load()
    expired = [
        {"announcementId": f"expired-{i}", "type": "notice", "status": "published",
         "publishAt": f"2026-09-09T{i % 24:02d}:00:00.000Z", "endAt": "2026-09-10T02:59:59.000Z"}
        for i in range(50)
    ]
    current = [
        {"announcementId": f"current-{i}", "type": "notice", "status": "published",
         "publishAt": f"2026-09-08T{i % 24:02d}:00:00.000Z"}
        for i in range(2)
    ]
    table = PaginatedAnnouncementsTable(expired + current)
    monkeypatch.setattr(mod, "table", table)

    result = mod.get_published(2, NOW)

    assert {it["announcementId"] for it in result} == {"current-0", "current-1"}
    assert len(table.calls) >= 2
    assert "ExclusiveStartKey" in table.calls[1]


def test_public_list_stops_after_page_limit(monkeypatch):
    mod = _load()
    expired = [
        {"announcementId": f"expired-{i}", "type": "notice", "status": "published",
         "publishAt": f"2026-09-09T{i % 24:02d}:00:00.000Z", "endAt": "2026-09-10T02:59:59.000Z"}
        for i in range(300)
    ]
    table = PaginatedAnnouncementsTable(expired)
    monkeypatch.setattr(mod, "table", table)

    assert mod.get_published(2, NOW) == []
    published_calls = [
        call for call in table.calls
        if call["KeyConditionExpression"]._values[0]._values[1] == "published"
    ]
    assert len(published_calls) == mod.MAX_ANNOUNCEMENT_QUERY_PAGES
    assert all(call["Limit"] == mod.ANNOUNCEMENT_QUERY_PAGE_SIZE for call in published_calls)
