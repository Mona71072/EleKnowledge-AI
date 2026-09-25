"""chat-management: 失敗一覧 v2（期間・振り分け・言い換え・ヒント・トレース要約）と PUT triage。"""
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

REPO = Path(__file__).resolve().parents[2]
APP_PATH = REPO / "lambda" / "chat" / "chat-management" / "app.py"


def load_app():
    os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("ADMIN_GROUP_NAME", "admin")
    with patch("boto3.resource") as resource:
        table = MagicMock()
        resource.return_value.Table.return_value = table
        spec = importlib.util.spec_from_file_location("chat_mgmt_v2", str(APP_PATH))
        mod = importlib.util.module_from_spec(spec)
        sys.modules.pop("chat_mgmt_v2", None)
        spec.loader.exec_module(mod)
        mod.chatlogs_table = table
        return mod, table


def _event(method, path, *, body=None, qs=None, sub="admin-1", groups="admin", path_params=None):
    return {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "queryStringParameters": qs or {},
        "body": json.dumps(body) if isinstance(body, dict) else body,
        "requestContext": {"authorizer": {"claims": {"sub": sub, "cognito:groups": groups}}},
    }


# ------------------------------------------------------------------ bounds / filters
def test_jst_day_bounds():
    mod, _ = load_app()
    lo, hi = mod.jst_day_bounds("2026-09-23", "2026-09-23")
    assert lo == "2026-09-22T15:00:00" and hi == "2026-09-23T15:00:00"
    assert lo <= "2026-09-23T14:59:59.999999Z" <= hi
    assert not (lo <= "2026-09-23T15:00:00Z" <= hi)
    assert mod.jst_day_bounds(None, None) == (None, None)
    with pytest.raises(ValueError):
        mod.jst_day_bounds("2026/09/23", None)


def _scan_capture(table):
    captured = {}

    def scan(**kw):
        captured.update(kw)
        return {"Items": [], "ScannedCount": 0}

    table.scan.side_effect = scan
    return captured


def test_failures_filter_since_until_and_open_triage():
    mod, table = load_app()
    captured = _scan_capture(table)
    mod.list_failure_messages(kind="all", since="2026-09-23", until="2026-09-23", triage="open")
    fe = captured["FilterExpression"]
    assert "#ts >= :lo" in fe and "#ts <= :hi" in fe
    assert "(attribute_not_exists(#tr) OR #tr.#st = :open)" in fe
    assert captured["ExpressionAttributeNames"]["#tr"] == "triage" and captured["ExpressionAttributeNames"]["#st"] == "status"
    assert captured["ExpressionAttributeValues"][":lo"] == "2026-09-22T15:00:00"
    # 未使用の値を渡さない（DynamoDB は unused value を拒否する）
    assert set(captured["ExpressionAttributeValues"]) == {":assistant", ":false", ":bad", ":not_found", ":lo", ":hi", ":open"}


def test_failures_kind_reformulated_and_done_triage():
    mod, table = load_app()
    captured = _scan_capture(table)
    mod.list_failure_messages(kind="reformulated", triage="done")
    fe = captured["FilterExpression"]
    assert "attribute_exists(reformulatedAt)" in fe and "feedback <> :good" in fe
    assert "(attribute_not_exists(documentOpens) OR documentOpens = :zero)" in fe
    assert captured["ExpressionAttributeValues"][":zero"] == 0
    assert "#tr.#st = :tst" in fe and captured["ExpressionAttributeValues"][":tst"] == "done"
    assert ":bad" not in captured["ExpressionAttributeValues"]


def test_failures_reports_truncation_and_pre_limit_match_count():
    mod, table = load_app()
    table.query.return_value = {"Items": []}
    table.scan.return_value = {
        "Items": [
            {"sessionId": "s1", "messageId": f"m{i}", "role": "assistant", "timestamp": f"2026-09-{i // 60 + 1:02d}T00:{i % 60:02d}:00Z", "feedback": "bad"}
            for i in range(101)
        ],
        "ScannedCount": 101,
    }

    out = mod.list_failure_messages(kind="bad", limit=100)

    assert out["count"] == 100
    assert out["matchedCount"] == 101
    assert out["truncated"] is True


def test_failures_marks_exact_limit_as_not_truncated():
    mod, table = load_app()
    table.query.return_value = {"Items": []}
    table.scan.return_value = {
        "Items": [
            {"sessionId": "s1", "messageId": f"m{i}", "role": "assistant", "timestamp": f"2026-09-{i // 60 + 1:02d}T00:{i % 60:02d}:00Z", "feedback": "bad"}
            for i in range(100)
        ],
        "ScannedCount": 100,
    }

    out = mod.list_failure_messages(kind="bad", limit=100)

    assert out["matchedCount"] == 100
    assert out["truncated"] is False


def test_failures_bad_request_on_invalid_date():
    mod, _ = load_app()
    resp = mod.lambda_handler(_event("GET", "/chat/admin/failures", qs={"since": "yesterday"}), None)
    assert resp["statusCode"] == 400


# ------------------------------------------------------------------ enrichment
def test_failures_items_include_opened_reformulated_triage_hints_and_trace():
    mod, table = load_app()
    assistant = {
        "sessionId": "s1", "messageId": "a1", "role": "assistant", "timestamp": "2026-09-23T01:47:00Z",
        "feedback": "bad", "feedbackReason": "wrong_doc", "responseType": "pages", "content": "回答",
        "queryFilters": {"modelType": "AXIEZ", "category": ["spec", "tech_info"]},
        "documentOpens": 2, "reformulatedAt": "2026-09-23T01:50:00Z",
        "triage": {"status": "in_progress", "cause": "snippet", "note": "表崩れ", "ref": "#112"},
        "retrievalTrace": {"retrieve": {"mergedCount": 26}, "generation": {"inputTokens": 3700, "outputTokens": 500},
                           "latencyMs": {"total": 10400},
                           "candidates": [{"rank": 1, "score": 0.41, "selected": True}, {"rank": 2, "score": 0.35, "excludedBy": "model_scope"},
                                          {"rank": 3, "score": 0.34, "excludedBy": "model_scope"}, {"rank": 4, "score": 0.30, "excludedBy": "model_scope"}]},
    }
    table.scan.return_value = {"Items": [assistant], "ScannedCount": 1}
    table.query.return_value = {"Items": [
        {"sessionId": "s1", "messageId": "u0", "role": "user", "timestamp": "2026-09-23T01:40:00Z", "content": "最初"},
        {"sessionId": "s1", "messageId": "c0", "role": "assistant", "timestamp": "2026-09-23T01:40:10Z", "responseType": "clarify"},
        {"sessionId": "s1", "messageId": "u1", "role": "user", "timestamp": "2026-09-23T01:46:00Z", "content": "かご枠の水平"},
        assistant,
    ]}
    out = mod.list_failure_messages(kind="all")
    it = out["failures"][0]
    assert it["userQuery"] == "かご枠の水平"
    assert it["opened"] == 2 and it["reformulated"] is False        # 資料を開いたので言い換えではない
    assert it["signals"] == ["bad"]
    assert it["triage"]["status"] == "in_progress" and it["triage"]["ref"] == "#112"
    assert it["traceSummary"] == {"mergedCount": 26, "selectedCount": 1, "excludedByModelScope": 3, "topScore": 0.41,
                                  "inputTokens": 3700, "outputTokens": 500, "latencyMs": {"total": 10400}}
    hints = it["hints"]
    assert any("機種スコープで 3 件除外" in h for h in hints)
    assert any("上位スコアが弱い（0.41）" in h for h in hints)
    assert any("資料は開かれた（2 件）" in h for h in hints)
    assert any("聞き返し後" in h for h in hints)
    assert out["triage"] == "all"


def test_build_hints_reformulation_and_category_narrowing():
    mod, _ = load_app()
    item = {"responseType": "not_found", "reformulatedAt": "x", "queryFilters": {"category": ["spec", "std"]}}
    hints = mod.build_hints(item, {"mergedCount": 3, "topScore": 0.6, "excludedByModelScope": 0})
    assert hints == ["カテゴリ過絞り（候補 3 件）", "言い換え後に評価なし → 暗黙の失敗"]
    assert mod.build_hints({"responseType": "pages"}, None) == []


def test_triage_defaults_to_open_and_wishes_carry_session_and_triage():
    mod, table = load_app()
    assert mod.normalize_triage({})["status"] == "open"
    table.scan.return_value = {"Items": [{"sessionId": "wish-u1", "messageId": "w1", "role": "product_wish", "content": "要望", "timestamp": "t",
                                          "userId": "u1", "triage": {"status": "done", "ref": "#104"}}], "ScannedCount": 1}
    out = mod.list_product_wishes()
    assert out["wishes"][0]["sessionId"] == "wish-u1" and out["wishes"][0]["triage"]["status"] == "done"


# ------------------------------------------------------------------ PUT triage
def test_put_triage_updates_row_with_actor():
    mod, table = load_app()
    resp = mod.lambda_handler(_event(
        "PUT", "/chat/admin/messages/s1/a1/triage",
        body={"status": "done", "cause": "search", "note": "年度で絞ると落ちる", "ref": "G017"},
        path_params={"sessionId": "s1", "messageId": "a1"},
    ), None)
    assert resp["statusCode"] == 200
    kw = table.update_item.call_args.kwargs
    assert kw["Key"] == {"sessionId": "s1", "messageId": "a1"}
    t = kw["ExpressionAttributeValues"][":t"]
    assert t["status"] == "done" and t["cause"] == "search" and t["ref"] == "G017" and t["by"] == "admin-1" and t["at"].endswith("Z")
    assert "#role = :assistant OR #role = :wish" in kw["ConditionExpression"]
    assert json.loads(resp["body"])["triage"]["status"] == "done"


def test_put_triage_parses_ids_from_path_when_params_missing():
    mod, table = load_app()
    resp = mod.lambda_handler(_event("PUT", "/dev/chat/admin/messages/wish-u1/w%201/triage", body={"status": "in_progress"}), None)
    assert resp["statusCode"] == 200
    assert table.update_item.call_args.kwargs["Key"] == {"sessionId": "wish-u1", "messageId": "w 1"}


@pytest.mark.parametrize("body", [{"status": "nope"}, {"status": "done", "cause": "bogus"}, {"status": "open", "note": "x" * 201}])
def test_put_triage_validation(body):
    mod, table = load_app()
    resp = mod.lambda_handler(_event("PUT", "/chat/admin/messages/s1/a1/triage", body=body, path_params={"sessionId": "s1", "messageId": "a1"}), None)
    assert resp["statusCode"] == 400
    table.update_item.assert_not_called()


def test_put_triage_forbidden_and_not_found():
    mod, table = load_app()
    resp = mod.lambda_handler(_event("PUT", "/chat/admin/messages/s1/a1/triage", body={"status": "done"},
                                     path_params={"sessionId": "s1", "messageId": "a1"}, groups="user"), None)
    assert resp["statusCode"] == 403
    table.update_item.side_effect = ClientError({"Error": {"Code": "ConditionalCheckFailedException", "Message": "x"}}, "UpdateItem")
    resp = mod.lambda_handler(_event("PUT", "/chat/admin/messages/s1/missing/triage", body={"status": "done"},
                                     path_params={"sessionId": "s1", "messageId": "missing"}), None)
    assert resp["statusCode"] == 404


# ------------------------------------------------------------------ regression: unused expression names
@pytest.mark.parametrize("kind", ["all", "bad", "not_found", "reformulated"])
@pytest.mark.parametrize("triage", ["all", "open", "done"])
@pytest.mark.parametrize("since", [None, "2026-09-05"])
def test_failures_expression_names_exactly_match_expression(kind, triage, since):
    """式で使っていない別名を渡すと DynamoDB が ValidationException（"unused in expressions"）を返す。
    2026-09-11 に kind=reformulated（と旧来の kind=bad）で #rt が余って 500 になった回帰防止。"""
    import re
    mod, table = load_app()
    captured = _scan_capture(table)
    mod.list_failure_messages(kind=kind, since=since, until=since, triage=triage)
    used = set(re.findall(r"#\w+", captured["FilterExpression"]))
    assert set(captured["ExpressionAttributeNames"]) == used
