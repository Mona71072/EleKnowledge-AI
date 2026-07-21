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
