"""Unit tests for announcements & monitoring Lambdas (pure logic, no AWS calls)."""
import importlib.util
import os

BASE = os.path.join(os.path.dirname(__file__), "../..")

# Tables are created at module load; give them names + a region before importing.
os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")
os.environ.setdefault("ANNOUNCEMENTS_TABLE", "announcements-test")
os.environ.setdefault("METRICS_TABLE", "metrics-test")
os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


write = _load("ann_write", "lambda/announcements/write/app.py")
read = _load("ann_read", "lambda/announcements/read/app.py")
publisher = _load("ann_publisher", "lambda/announcements/publisher/app.py")
metrics_read = _load("metrics_read", "lambda/metrics/read/app.py")
aggregator = _load("metrics_aggregator", "lambda/metrics/aggregator/app.py")


# ----------------------------------------------------------------- admin gate
def _event_with_groups(groups):
    return {"requestContext": {"authorizer": {"claims": {"cognito:groups": groups}}}}


def test_is_admin_accepts_list_and_csv():
    assert write.is_admin(_event_with_groups(["admin", "ops"])) is True
    assert write.is_admin(_event_with_groups("ops,admin")) is True
    assert write.is_admin(_event_with_groups("users")) is False
    assert write.is_admin({"requestContext": {}}) is False


def test_metrics_read_admin_gate():
    assert metrics_read.is_admin(_event_with_groups("admin")) is True
    assert metrics_read.is_admin(_event_with_groups("")) is False


# ----------------------------------------------------------------- sanitize
def test_sanitize_strips_script_and_handlers():
    dirty = '# Title\n<script>alert(1)</script>\n<img src=x onerror="bad()">\n[x](javascript:evil)'
    clean = write.sanitize_markdown(dirty)
    assert "<script" not in clean.lower()
    assert "onerror" not in clean.lower()
    assert "javascript:" not in clean.lower()
    assert "# Title" in clean  # legitimate markdown preserved


# ----------------------------------------------------------------- validation
def test_validate_requires_maintenance_window():
    err = write.validate(
        {"type": "maintenance", "title": "x", "severity": "info", "status": "draft"},
        partial=False,
    )
    assert err and "maintenance" in err


def test_validate_rejects_bad_enum():
    err = write.validate(
        {"type": "bogus", "title": "x", "severity": "info", "status": "draft"},
        partial=False,
    )
    assert err and "type" in err


def test_validate_ok():
    assert write.validate(
        {"type": "notice", "title": "x", "severity": "info", "status": "draft"},
        partial=False,
    ) is None


# ----------------------------------------------------------------- read feed (due scheduled)
def test_get_published_includes_due_scheduled_and_sorts(monkeypatch):
    now = "2026-07-29T12:00:00Z"

    def fake_query(status, now_iso, fetch_limit):
        assert now_iso == now
        if status == "published":
            return [
                {
                    "announcementId": "a1",
                    "status": "published",
                    "publishAt": "2026-07-28T00:00:00Z",
                    "pinned": False,
                    "title": "old",
                },
                {
                    "announcementId": "a2",
                    "status": "published",
                    "publishAt": "2026-07-29T10:00:00Z",
                    "pinned": True,
                    "title": "pinned",
                },
            ]
        if status == "scheduled":
            return [
                {
                    "announcementId": "a3",
                    "status": "scheduled",
                    "publishAt": "2026-07-29T11:00:00Z",
                    "pinned": False,
                    "title": "due scheduled",
                },
                {
                    "announcementId": "a4",
                    "status": "scheduled",
                    "publishAt": "2026-07-20T00:00:00Z",
                    "endAt": "2026-07-21T00:00:00Z",
                    "title": "expired",
                },
            ]
        return []

    monkeypatch.setattr(read, "_query_by_status", fake_query)
    result = read.get_published(10, now)
    ids = [x["announcementId"] for x in result]
    assert ids[0] == "a2"  # pinned first
    assert "a3" in ids  # due scheduled included
    assert "a4" not in ids  # endAt passed
    # non-pinned: newer publishAt first
    non_pinned = [i for i in ids if i != "a2"]
    assert non_pinned == ["a3", "a1"]


def test_promote_due_updates_scheduled(monkeypatch):
    class FakeTable:
        def __init__(self):
            self.updated = []

        def query(self, **kwargs):
            return {
                "Items": [
                    {"announcementId": "anc_1", "status": "scheduled", "publishAt": "2026-07-01T00:00:00Z"},
                    {"announcementId": "anc_2", "status": "scheduled", "publishAt": "2026-07-02T00:00:00Z"},
                ]
            }

        def update_item(self, **kwargs):
            self.updated.append(kwargs["Key"]["announcementId"])

    fake = FakeTable()
    monkeypatch.setattr(publisher, "table", fake)
    result = publisher.promote_due("2026-07-29T00:00:00Z")
    assert result["count"] == 2
    assert result["promoted"] == ["anc_1", "anc_2"]


# ----------------------------------------------------------------- health status
def test_status_for_thresholds():
    assert metrics_read.status_for("errorRate", 0.005) == "good"
    assert metrics_read.status_for("errorRate", 0.03) == "warning"
    assert metrics_read.status_for("errorRate", 0.5) == "critical"
    assert metrics_read.status_for("http5xx", 0) == "good"
    assert metrics_read.status_for("http5xx", 10) == "serious"


# ----------------------------------------------------------------- aggregation
def test_aggregate_chat_counts_and_like_rate():
    items = [
        {"role": "user", "userId": "u1", "sessionId": "s1"},
        {"role": "assistant", "sessionId": "s1", "feedback": "good",
         "sourceDocuments": [{"documentName": "manual.pdf"}]},
        {"role": "user", "userId": "u2", "sessionId": "s2"},
        {"role": "assistant", "sessionId": "s2", "feedback": "bad",
         "sourceDocuments": [{"documentName": "manual.pdf"}]},
        {"role": "assistant", "sessionId": "s2", "feedback": "good"},
    ]
    agg = aggregator.aggregate_chat(items)
    assert agg["queries"] == 2
    assert agg["activeUsers"] == 2
    assert agg["sessions"] == 2
    assert agg["feedbackGood"] == 2 and agg["feedbackBad"] == 1
    assert abs(agg["likeRate"] - round(2 / 3, 4)) < 1e-9
    assert agg["topDocuments"][0] == {"name": "manual.pdf", "count": 2}


def test_aggregate_chat_empty():
    agg = aggregator.aggregate_chat([])
    assert agg["queries"] == 0 and agg["likeRate"] == 0.0 and agg["topDocuments"] == []
