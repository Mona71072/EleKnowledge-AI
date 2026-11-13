"""お知らせ write / publisher の DynamoDB 操作を FakeTable で検証する（issue #94）。

これまで create / update / delete と部分更新のバリデーションにテストが無く、
Bug B2〜B4・Risk R1・R7・R8 はすべてその空白にあった。
"""
import base64
import importlib.util
import json
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
read = _load("ann_read_ops", "lambda/announcements/read/app.py")


class FakeTable:
    """put/get/delete/query の最小実装。"""

    def __init__(self, items=None):
        self.items = {it["announcementId"]: dict(it) for it in (items or [])}
        self.updates = []
        self.puts = []
        self.gets = []
        self.after_get_item = None
        self.fail_conditional_put = False
        self.query_pages = []  # publisher 用: 事前に用意したページ

    def put_item(self, Item, **kwargs):
        self.puts.append({"Item": dict(Item), **kwargs})
        if self.fail_conditional_put:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException", "Message": "condition failed"}},
                "PutItem",
            )
        condition = kwargs.get("ConditionExpression")
        if condition:
            existing = self.items.get(Item["announcementId"])
            values = kwargs.get("ExpressionAttributeValues", {})
            for clause in condition.split(" AND "):
                if clause == "attribute_exists(announcementId)" and existing is None:
                    self._raise_conditional_put()
                if clause == "attribute_not_exists(updatedAt)" and existing and "updatedAt" in existing:
                    self._raise_conditional_put()
                if clause in ("updatedAt = :version", "createdAt = :version"):
                    attribute = clause.split(" = ")[0]
                    if existing is None or existing.get(attribute) != values.get(":version"):
                        self._raise_conditional_put()
        self.items[Item["announcementId"]] = dict(Item)

    def _raise_conditional_put(self):
        raise ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException", "Message": "condition failed"}},
            "PutItem",
        )

    def get_item(self, Key, **kwargs):
        self.gets.append({"Key": dict(Key), **kwargs})
        it = self.items.get(Key["announcementId"])
        response = {"Item": dict(it)} if it else {}
        if self.after_get_item:
            hook = self.after_get_item
            self.after_get_item = None
            hook(Key["announcementId"])
        return response

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


def test_update_uses_existing_version_condition_and_succeeds(table):
    table.put_item(_maintenance())

    resp = write.update("anc_1", {"title": "更新後"}, actor="u")

    assert resp["statusCode"] == 200
    put = table.puts[-1]
    assert "attribute_exists(announcementId)" in put["ConditionExpression"]
    assert "updatedAt = :version" in put["ConditionExpression"]
    assert put["ExpressionAttributeValues"][":version"] == "2026-01-01T00:00:00.000Z"
    assert table.items["anc_1"]["title"] == "更新後"
    assert table.gets[-1]["ConsistentRead"] is True


def test_update_falls_back_to_created_at_when_updated_at_is_missing(table):
    item = _maintenance()
    item.pop("updatedAt")
    table.put_item(item)

    resp = write.update("anc_1", {"title": "更新後"}, actor="u")

    assert resp["statusCode"] == 200
    put = table.puts[-1]
    assert "createdAt = :version" in put["ConditionExpression"]
    assert "attribute_not_exists(updatedAt)" in put["ConditionExpression"]
    assert put["ExpressionAttributeValues"][":version"] == item["createdAt"]


def test_update_without_version_attributes_uses_existence_condition(table):
    item = _maintenance()
    item.pop("updatedAt")
    item.pop("createdAt")
    table.put_item(item)

    resp = write.update("anc_1", {"title": "更新後"}, actor="u")

    assert resp["statusCode"] == 200
    put = table.puts[-1]
    assert put["ConditionExpression"] == "attribute_exists(announcementId) AND attribute_not_exists(updatedAt)"
    assert "ExpressionAttributeValues" not in put
    assert table.items["anc_1"]["title"] == "更新後"


@pytest.mark.parametrize("version_fields", ["updated", "created", "none"])
def test_update_rejects_second_put_from_same_legacy_version(table, monkeypatch, version_fields):
    item = _maintenance()
    if version_fields == "created":
        item.pop("updatedAt")
    elif version_fields == "none":
        item.pop("updatedAt")
        item.pop("createdAt")
    table.put_item(item)
    ticks = iter(("2026-11-13T00:00:01.000Z", "2026-11-13T00:00:02.000Z"))
    monkeypatch.setattr(write, "_now_iso", lambda: next(ticks))

    def concurrent_put(announcement_id):
        assert announcement_id == "anc_1"
        assert write.update(announcement_id, {"title": "先行編集"}, actor="first")["statusCode"] == 200

    table.after_get_item = concurrent_put
    response = write.update("anc_1", {"title": "後続編集"}, actor="second")

    assert response["statusCode"] == 409
    assert table.items["anc_1"]["title"] == "先行編集"


def test_update_does_not_resurrect_item_deleted_after_read(table):
    table.put_item(_maintenance())
    table.after_get_item = lambda announcement_id: table.items.pop(announcement_id)

    response = write.update("anc_1", {"title": "更新後"}, actor="u")

    assert response["statusCode"] == 409
    assert "anc_1" not in table.items


def test_update_allows_two_sequential_edits(table, monkeypatch):
    table.put_item(_maintenance())
    ticks = iter(("2026-11-13T00:00:01.000Z", "2026-11-13T00:00:02.000Z"))
    monkeypatch.setattr(write, "_now_iso", lambda: next(ticks))

    first = write.update("anc_1", {"title": "一回目"}, actor="u")
    second = write.update("anc_1", {"title": "二回目"}, actor="u")

    assert first["statusCode"] == second["statusCode"] == 200
    assert table.items["anc_1"]["title"] == "二回目"
    assert all(read["ConsistentRead"] is True for read in table.gets)


def test_update_conditional_conflict_returns_409_and_keeps_not_found_404(table):
    table.put_item(_maintenance())
    table.fail_conditional_put = True

    resp = write.update("anc_1", {"title": "競合"}, actor="u")

    assert resp["statusCode"] == 409
    assert _body(resp)["error"] == "Conflict"
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


def test_promote_due_conditions_on_read_publish_at_and_skips_conflicts(monkeypatch):
    class ConflictingTable(FakeTable):
        def update_item(self, **kwargs):
            self.updates.append(kwargs)
            if kwargs["Key"]["announcementId"] == "a1":
                raise ClientError(
                    {"Error": {"Code": "ConditionalCheckFailedException", "Message": "condition failed"}},
                    "UpdateItem",
                )

    fake = ConflictingTable()
    fake.query_pages = [[
        {"announcementId": "a1", "publishAt": "2026-01-01T00:00:00.000Z", "status": "scheduled"},
        {"announcementId": "a2", "publishAt": "2026-01-01T00:00:00.000Z", "status": "scheduled"},
    ]]
    monkeypatch.setattr(publisher, "table", fake)

    result = publisher.promote_due("2026-01-02T00:00:00Z")

    assert len(fake.updates) == 2
    assert "publishAt = :read_publish_at" in fake.updates[0]["ConditionExpression"]
    assert fake.updates[0]["ExpressionAttributeValues"][":read_publish_at"] == "2026-01-01T00:00:00.000Z"
    assert result["promoted"] == ["a2"]
    assert result["count"] == 1
    assert result["skipped_count"] == 1


def test_public_announcements_hide_actor_fields_but_admin_list_keeps_them(monkeypatch):
    public_rows = [
        {
            "announcementId": "public", "type": "notice", "status": "published",
            "severity": "info", "title": "告知", "body": "本文",
            "publishAt": "2026-09-10T02:00:00.000Z",
            "createdBy": "admin@example.com", "updatedBy": "admin2@example.com",
        },
        {
            "announcementId": "maintenance", "type": "maintenance", "status": "published",
            "severity": "warning", "title": "保守", "body": "本文",
            "publishAt": "2026-09-10T02:00:00.000Z",
            "startAt": "2026-09-10T02:00:00.000Z", "endAt": "2026-09-10T04:00:00.000Z",
            "createdBy": "admin@example.com", "updatedBy": "admin2@example.com",
        },
    ]

    class PublicRowsTable:
        def query(self, **kwargs):
            status = _status_of(kwargs["KeyConditionExpression"])
            rows = [item for item in public_rows if item["status"] == status]
            if "FilterExpression" in kwargs:
                expression = kwargs["FilterExpression"]
                condition = expression
                while not hasattr(condition, "name"):
                    condition = condition._values[0]
                if condition.name == "type":
                    rows = [item for item in rows if item["type"] == "maintenance"]
            return {"Items": [dict(item) for item in rows]}

    monkeypatch.setattr(read, "table", PublicRowsTable())
    monkeypatch.setattr(read, "_now_iso", lambda: "2026-09-10T03:00:00.000Z")

    response = read.lambda_handler({"httpMethod": "GET"}, None)
    body = _body(response)

    assert response["statusCode"] == 200
    assert all("createdBy" not in item and "updatedBy" not in item
               for item in body["announcements"] + body["activeMaintenance"])

    admin_table = GsiTable(public_rows)
    monkeypatch.setattr(write, "table", admin_table)
    admin_response = write.list_all({})
    assert admin_response["statusCode"] == 200
    assert admin_table.items["public"]["createdBy"] == "admin@example.com"
    assert admin_table.items["public"]["updatedBy"] == "admin2@example.com"
    active_response = write.list_active("2026-09-10T03:00:00.000Z")
    assert active_response["statusCode"] == 200
    active_item = _body(active_response)["announcements"][0]
    assert active_item["createdBy"] == "admin@example.com"
    assert active_item["updatedBy"] == "admin2@example.com"


# ----------------------------------------------------------------- admin list (R9)
def _status_of(cond):
    """KeyCondition（status = X、または status = X AND publishAt <= now）から X を取り出す。"""
    expr = cond.get_expression()
    if expr["operator"] == "AND":
        return _status_of(expr["values"][0])
    return expr["values"][1]


class GsiTable(FakeTable):
    """status-publishAt-index の Query を模擬する（publishAt 降順、ExclusiveStartKey、Limit）。Scan は持たない。"""

    def __init__(self, items=None):
        super().__init__(items)
        self.queries = []

    def query(self, **kwargs):
        self.queries.append(kwargs)
        assert kwargs["IndexName"] == "status-publishAt-index"
        assert kwargs["ScanIndexForward"] is False
        status = _status_of(kwargs["KeyConditionExpression"])
        rows = sorted(
            (dict(it) for it in self.items.values() if it["status"] == status),
            key=lambda it: it["publishAt"],
            reverse=True,
        )
        start = 0
        if "ExclusiveStartKey" in kwargs:
            esk = kwargs["ExclusiveStartKey"]
            start = next(i for i, it in enumerate(rows) if it["announcementId"] == esk["announcementId"]) + 1
        limit = kwargs["Limit"]
        page = rows[start:start + limit]
        resp = {"Items": page}
        if page and start + limit < len(rows):
            resp["LastEvaluatedKey"] = {k: page[-1][k] for k in ("status", "publishAt", "announcementId")}
        return resp


def _row(aid, status, publish_at):
    return {
        "announcementId": aid, "status": status, "publishAt": publish_at,
        "type": "notice", "severity": "info", "title": aid, "body": "",
    }


def _list(query=None):
    return write.list_all(query or {})


def _walk(table, limit):
    """nextToken を最後まで辿り、ページごとの応答を返す。"""
    pages, query = [], {"limit": str(limit)}
    for _ in range(50):
        resp = _list(query)
        assert resp["statusCode"] == 200
        body = _body(resp)
        pages.append(body)
        if not body["nextToken"]:
            return pages
        query = {"limit": str(limit), "nextToken": body["nextToken"]}
    raise AssertionError("paging did not terminate")


def test_admin_list_pages_cover_every_item_once_in_publish_order(monkeypatch):
    rows = [
        _row("a1", "published", "2026-05-01T00:00:00.000Z"),
        _row("a2", "draft", "2026-05-03T00:00:00.000Z"),
        _row("a3", "scheduled", "2026-05-03T00:00:00.000Z"),  # 同じ publishAt（併合の接頭辞性を確認）
        _row("a4", "published", "2026-05-03T00:00:00.000Z"),
        _row("a5", "draft", "2026-04-01T00:00:00.000Z"),
        _row("a6", "scheduled", "2026-05-02T00:00:00.000Z"),
        _row("a7", "published", "2026-05-02T00:00:00.000Z"),
    ]
    fake = GsiTable(rows)
    monkeypatch.setattr(write, "table", fake)

    pages = _walk(fake, limit=2)

    ids = [it["announcementId"] for page in pages for it in page["announcements"]]
    assert sorted(ids) == sorted(r["announcementId"] for r in rows)  # 欠落も重複もない
    publish = [it["publishAt"] for page in pages for it in page["announcements"]]
    assert publish == sorted(publish, reverse=True)
    assert all(len(page["announcements"]) <= 2 for page in pages)
    assert pages[-1]["nextToken"] is None
    assert len(pages) == 4  # 7 件を 2 件ずつ


def test_admin_list_single_page_has_null_next_token(monkeypatch):
    fake = GsiTable([_row("a1", "draft", "2026-05-01T00:00:00.000Z")])
    monkeypatch.setattr(write, "table", fake)
    body = _body(_list({"limit": "5"}))
    assert [it["announcementId"] for it in body["announcements"]] == ["a1"]
    assert body["nextToken"] is None


def test_admin_list_never_scans(monkeypatch):
    fake = GsiTable([_row("a1", "draft", "2026-05-01T00:00:00.000Z")])
    monkeypatch.setattr(write, "table", fake)
    assert not hasattr(fake, "scan")
    _list()
    assert fake.queries and all("IndexName" in q for q in fake.queries)


def test_admin_list_default_limit_and_handler_wiring(monkeypatch):
    rows = [_row(f"a{i:03d}", "published", f"2026-05-{i % 28 + 1:02d}T00:00:{i % 60:02d}.000Z") for i in range(60)]
    fake = GsiTable(rows)
    monkeypatch.setattr(write, "table", fake)
    event = {
        "httpMethod": "GET",
        "requestContext": {"authorizer": {"claims": {"cognito:groups": "admin", "email": "a@example.com"}}},
        "queryStringParameters": None,
    }
    body = json.loads(write.lambda_handler(event, None)["body"])
    assert len(body["announcements"]) == write.ADMIN_LIST_DEFAULT_LIMIT
    assert body["nextToken"]

    event["queryStringParameters"] = {"limit": "100", "nextToken": body["nextToken"]}
    second = json.loads(write.lambda_handler(event, None)["body"])
    assert len(second["announcements"]) == 10
    assert second["nextToken"] is None


@pytest.mark.parametrize("limit", ["0", "101", "-1", "abc", "1.5", ""])
def test_admin_list_rejects_bad_limit(monkeypatch, limit):
    monkeypatch.setattr(write, "table", GsiTable())
    resp = _list({"limit": limit})
    assert resp["statusCode"] == 400
    assert _body(resp)["error"] == "ValidationError"


def _token(payload):
    raw = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


@pytest.mark.parametrize("token", [
    "!!!not-base64!!!",
    "bm90LWpzb24",  # "not-json"
    _token([1, 2]),
    _token({"p": {"draft": {"status": "draft"}}, "d": []}),  # キー不足
    _token({"p": {"draft": {"status": "published", "publishAt": "x", "announcementId": "y"}}, "d": []}),
    _token({"p": {"archived": {"status": "archived", "publishAt": "x", "announcementId": "y"}}, "d": []}),
    _token({"p": {}, "d": ["archived"]}),
    _token({"p": {}, "d": "draft"}),
    _token({"p": {}, "d": [], "x": 1}),
    "a" * 5000,
])
def test_admin_list_rejects_broken_next_token(monkeypatch, token):
    fake = GsiTable([_row("a1", "draft", "2026-05-01T00:00:00.000Z")])
    monkeypatch.setattr(write, "table", fake)
    resp = _list({"nextToken": token})
    assert resp["statusCode"] == 400
    assert _body(resp)["error"] == "ValidationError"
    assert fake.queries == []  # 検証に失敗したら DynamoDB を呼ばない


# ----------------------------------------------------------------- active list（いま表示中）
NOW = "2026-06-01T00:00:00.000Z"


def _active_row(aid, status, publish_at, end_at=None):
    row = _row(aid, status, publish_at)
    if end_at is not None:
        row["endAt"] = end_at
    return row


def test_active_list_returns_items_past_the_first_page(monkeypatch):
    # 120 件（すべて表示中）。一覧の 1 ページ（50 件）より後ろの項目も必ず含まれる
    rows = [
        _active_row(f"a{i:03d}", "published", f"2026-05-{i % 28 + 1:02d}T00:00:{i % 60:02d}.000Z")
        for i in range(120)
    ]
    fake = GsiTable(rows)
    monkeypatch.setattr(write, "table", fake)
    body = _body(write.list_active(NOW))
    assert len(body["announcements"]) == 120
    assert {it["announcementId"] for it in body["announcements"]} == {r["announcementId"] for r in rows}
    assert "nextToken" not in body


def test_active_list_applies_the_visibility_rules(monkeypatch):
    rows = [
        _active_row("ok_published", "published", "2026-05-01T00:00:00.000Z"),
        _active_row("ok_no_end_str", "published", "2026-05-02T00:00:00.000Z", end_at=None),
        _active_row("ok_end_future", "published", "2026-05-03T00:00:00.000Z", end_at="2026-07-01T00:00:00.000Z"),
        _active_row("ok_due_scheduled", "scheduled", "2026-05-04T00:00:00.000Z"),
        _active_row("ng_ended", "published", "2026-05-05T00:00:00.000Z", end_at="2026-05-20T00:00:00.000Z"),
        _active_row("ng_future_scheduled", "scheduled", "2026-06-10T00:00:00.000Z"),
        _active_row("ng_draft", "draft", "2026-05-06T00:00:00.000Z"),
    ]
    fake = GsiTable(rows)
    monkeypatch.setattr(write, "table", fake)
    ids = [it["announcementId"] for it in _body(write.list_active(NOW))["announcements"]]
    assert ids == ["ok_due_scheduled", "ok_end_future", "ok_no_end_str", "ok_published"]  # publishAt 降順


def test_active_list_treats_legacy_timestamp_formats_by_value(monkeypatch):
    # 旧形式（秒のみ・オフセット付き）でも文字列比較ではなく時刻として判定する
    rows = [
        _active_row("legacy_ok", "published", "2026-05-31T23:00:00+00:00", end_at="2026-06-02T00:00:00Z"),
        _active_row("legacy_ended", "published", "2026-05-01T00:00:00Z", end_at="2026-05-31T23:59:59+00:00"),
    ]
    fake = GsiTable(rows)
    monkeypatch.setattr(write, "table", fake)
    ids = [it["announcementId"] for it in _body(write.list_active(NOW))["announcements"]]
    assert ids == ["legacy_ok"]


def test_active_list_is_query_only_and_routed_by_handler(monkeypatch):
    fake = GsiTable([_active_row("a1", "published", "2026-05-01T00:00:00.000Z")])
    monkeypatch.setattr(write, "table", fake)
    monkeypatch.setattr(write, "_now_iso", lambda: NOW)
    assert not hasattr(fake, "scan")
    event = {
        "httpMethod": "GET",
        "resource": "/admin/announcements/active",
        "path": "/admin/announcements/active",
        "pathParameters": None,
        "requestContext": {"authorizer": {"claims": {"cognito:groups": "admin", "email": "a@example.com"}}},
    }
    body = json.loads(write.lambda_handler(event, None)["body"])
    assert [it["announcementId"] for it in body["announcements"]] == ["a1"]
    assert "nextToken" not in body  # 一覧のページングとは別の応答
    assert all(q["IndexName"] == "status-publishAt-index" for q in fake.queries)


def test_active_list_requires_admin(monkeypatch):
    monkeypatch.setattr(write, "table", GsiTable())
    event = {
        "httpMethod": "GET",
        "resource": "/admin/announcements/active",
        "requestContext": {"authorizer": {"claims": {"cognito:groups": "user"}}},
    }
    assert write.lambda_handler(event, None)["statusCode"] == 403
