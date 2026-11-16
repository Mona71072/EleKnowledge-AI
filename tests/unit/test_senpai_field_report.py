"""先輩チャット「結果を残す」Lambda（/rag/senpai/field-reports）の契約テスト。

ChatLogs の保存行（rag-function が書く形）と報告テーブルを moto で用意し、
ハンドラーを API Gateway のイベント経由で端から端まで通す。
"""
import importlib.util
import json
import os
import sys
import time
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO / "lambda" / "rag" / "senpai-field-report"

CONVERSATION_ID = "11111111-1111-4111-8111-111111111111"
TURN_ID = "22222222-2222-4222-8222-222222222222"
OTHER_TURN_ID = "33333333-3333-4333-8333-333333333333"
USER_ID = "owner-1"
FINDING = "現場で分かった固有の内容ZZZ-FINDING"
CONDITION = "固有の条件ZZZ-CONDITION"

_CACHE = {}


def _load_module():
    if "app" in _CACHE:
        return _CACHE["app"]
    os.environ.setdefault("CHATLOGS_TABLE", "test-chatlogs")
    os.environ.setdefault("FIELD_REPORTS_TABLE", "test-field-reports")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
    sys.path.insert(0, str(REPORT_DIR))
    before = set(sys.modules)
    try:
        spec = importlib.util.spec_from_file_location(
            "senpai_field_report_app_under_test", str(REPORT_DIR / "app.py")
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(REPORT_DIR))
        for key, loaded in list(sys.modules.items()):
            if key not in before and str(getattr(loaded, "__file__", "")).startswith(str(REPORT_DIR)) \
                    and key != "senpai_field_report_app_under_test":
                del sys.modules[key]
    _CACHE["app"] = mod
    return mod


@pytest.fixture(scope="module")
def report_app():
    return _load_module()


@pytest.fixture(autouse=True)
def report_env(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("SENPAI_FIELD_REPORTS_ENABLED", "true")
    monkeypatch.setenv("ADMIN_GROUP_NAME", "admin")
    monkeypatch.delenv("FIELD_REPORT_TTL_DAYS", raising=False)


def _card(knowledge_id="KH-A", version=3, scope_status="verified", product_lines=("AXIEZ",)):
    scope = {"product_lines": list(product_lines), "control_methods": ["VFGH"]}
    if scope_status:
        scope["scope_status"] = scope_status
    if scope_status == "verified":
        scope["scope_verified_by"] = "reviewer"
        scope["scope_verified_at"] = "2026-10-20"
    return {
        "knowledgeId": knowledge_id, "cardVersion": Decimal(version), "sha256": "a" * 64,
        "title": "合成カード", "status": "approved", "usage": "navigation_only",
        "body": "カード本文ZZZ-CARD", "searchTerms": [], "sourceRefs": [], "modelScope": scope,
    }


def _row(role, mode, *, user=USER_ID, turn=TURN_ID, conversation=CONVERSATION_ID,
         timestamp="2026-10-20T01:00:05Z", **extra):
    session = f"{mode}-session-{user}"
    row = {
        "sessionId": session,
        "messageId": f"{session}-{role}-{turn}-{timestamp}",
        "userId": user,
        "role": role,
        "ragMode": mode,
        "content": "回答本文ZZZ-ANSWER",
        "timestamp": timestamp,
        "ttl": int(time.time()) + 3600,
        "senpaiConversationId": conversation,
        "senpaiTurnId": turn,
    }
    row.update(extra)
    return row


def _technical(cards=None, model_type="NEXCUBE", **extra):
    knowhow = {"status": "matched", "indexVersion": "idx-1",
               "matches": cards if cards is not None else [_card(), _card("KH-B", 1, "unverified", ("NEXCUBE",))],
               "searchTerms": []}
    filters = {"modelType": model_type} if model_type else {}
    return _row("assistant", "normal", knowhow=knowhow, queryFilters=filters, responseType="pages", **extra)


def _make_tables():
    import boto3
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    chatlogs = dynamodb.create_table(
        TableName="field-report-chatlogs",
        KeySchema=[{"AttributeName": "sessionId", "KeyType": "HASH"},
                   {"AttributeName": "messageId", "KeyType": "RANGE"}],
        AttributeDefinitions=[{"AttributeName": n, "AttributeType": "S"}
                              for n in ("sessionId", "messageId", "userId", "timestamp")],
        GlobalSecondaryIndexes=[{
            "IndexName": "userId-timestamp-index",
            "KeySchema": [{"AttributeName": "userId", "KeyType": "HASH"},
                          {"AttributeName": "timestamp", "KeyType": "RANGE"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
        BillingMode="PAY_PER_REQUEST",
    )
    reports = dynamodb.create_table(
        TableName="field-reports",
        KeySchema=[{"AttributeName": "reportId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": n, "AttributeType": "S"}
                              for n in ("reportId", "userId", "createdAt", "reviewState")],
        GlobalSecondaryIndexes=[
            {"IndexName": "userId-createdAt-index",
             "KeySchema": [{"AttributeName": "userId", "KeyType": "HASH"},
                           {"AttributeName": "createdAt", "KeyType": "RANGE"}],
             "Projection": {"ProjectionType": "ALL"}},
            {"IndexName": "reviewState-createdAt-index",
             "KeySchema": [{"AttributeName": "reviewState", "KeyType": "HASH"},
                           {"AttributeName": "createdAt", "KeyType": "RANGE"}],
             "Projection": {"ProjectionType": "ALL"}},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    return chatlogs, reports


@pytest.fixture
def env(report_app):
    from moto import mock_aws
    with mock_aws():
        chatlogs, reports = _make_tables()
        old = (report_app.chatlogs_table, report_app.reports_table)
        report_app.chatlogs_table, report_app.reports_table = chatlogs, reports
        try:
            yield report_app, chatlogs, reports
        finally:
            report_app.chatlogs_table, report_app.reports_table = old


def _body(**overrides):
    body = {
        "senpaiConversationId": CONVERSATION_ID,
        "senpaiTurnId": TURN_ID,
        "finding": FINDING,
        "condition": CONDITION,
        "modelType": "NEXCUBE",
        "cardReactions": [
            {"knowledgeId": "KH-A", "cardVersion": 3, "reaction": "not_matched"},
            {"knowledgeId": "KH-B", "cardVersion": 1, "reaction": "matched"},
        ],
        "confirmed": True,
    }
    body.update(overrides)
    return {key: value for key, value in body.items() if value is not None}


def _event(body=None, *, sub=USER_ID, groups="admin", method="POST", raw_body=None, query=None):
    claims = {}
    if sub is not None:
        claims["sub"] = sub
    if groups is not None:
        claims["cognito:groups"] = groups
    event = {
        "httpMethod": method,
        "path": "/rag/senpai/field-reports",
        "requestContext": {"authorizer": {"claims": claims}},
        "queryStringParameters": query,
    }
    if method == "POST":
        event["body"] = raw_body if raw_body is not None else json.dumps(body if body is not None else _body())
    return event


def _call(app, event):
    response = app.lambda_handler(event, None)
    return response["statusCode"], json.loads(response["body"] or "null")


def _seed(chatlogs, *rows):
    for row in rows or (_row("user", "normal", timestamp="2026-10-20T01:00:00Z"), _technical()):
        chatlogs.put_item(Item=row)


# --- gates -----------------------------------------------------------------

@pytest.mark.parametrize("env_name,flag,groups", [
    ("prod", "true", "admin"), ("dev", "false", "admin"), ("dev", "true", "users"), ("dev", "true", None),
])
def test_feature_is_dev_admin_only_and_off_unless_flagged(env, monkeypatch, env_name, flag, groups):
    app, chatlogs, reports = env
    _seed(chatlogs)
    monkeypatch.setenv("ENVIRONMENT", env_name)
    monkeypatch.setenv("SENPAI_FIELD_REPORTS_ENABLED", flag)
    status, _ = _call(app, _event(groups=groups))
    assert status == 403
    assert reports.scan()["Items"] == []


def test_options_preflight_returns_cors_without_gates(env, monkeypatch):
    app, _, _ = env
    monkeypatch.setenv("ENVIRONMENT", "prod")
    response = app.lambda_handler({"httpMethod": "OPTIONS"}, None)
    assert response["statusCode"] == 200
    assert "GET" in response["headers"]["Access-Control-Allow-Methods"]


def test_missing_subject_is_unauthorized(env):
    app, chatlogs, _ = env
    _seed(chatlogs)
    assert _call(app, _event(sub=None))[0] == 401


# --- input validation ------------------------------------------------------

@pytest.mark.parametrize("override", [
    {"finding": ""}, {"finding": "   "}, {"finding": "あ" * 501}, {"condition": "あ" * 301},
    {"modelType": "UNKNOWN-MODEL"}, {"confirmed": False}, {"confirmed": None},
    {"senpaiTurnId": "not-a-uuid"}, {"senpaiTurnId": "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"},
    {"cardReactions": [{"knowledgeId": "KH-A", "cardVersion": 3, "reaction": "maybe"}]},
    {"cardReactions": [{"knowledgeId": "KH-A", "cardVersion": "3", "reaction": "matched"}]},
    {"cardReactions": [{"knowledgeId": "KH-A", "cardVersion": 3, "reaction": "matched", "extra": 1}]},
    {"cardReactions": [{"knowledgeId": "KH-A", "cardVersion": 3, "reaction": "matched"}] * 2},
    {"cardReactions": "KH-A"},
    {"userId": "attacker"},
    {"conversation": "全文を貼り付け"},
])
def test_invalid_bodies_are_rejected_without_saving(env, override):
    app, chatlogs, reports = env
    _seed(chatlogs)
    status, payload = _call(app, _event(_body(**override)))
    assert status == 400
    assert payload["error"] == "ValidationError"
    assert reports.scan()["Items"] == []


def test_non_json_body_is_validation_error(env):
    app, chatlogs, _ = env
    _seed(chatlogs)
    assert _call(app, _event(raw_body="{not json"))[0] == 400


# --- ownership and card verification ---------------------------------------

def test_turn_of_another_user_is_not_found(env):
    app, chatlogs, reports = env
    _seed(chatlogs, _technical(user="someone-else"))
    status, _ = _call(app, _event())
    assert status == 404
    assert reports.scan()["Items"] == []


def test_expired_turn_rows_are_not_found(env):
    app, chatlogs, _ = env
    _seed(chatlogs, _technical(ttl=int(time.time()) - 10))
    assert _call(app, _event())[0] == 404


def test_card_not_referenced_in_this_turn_is_rejected(env):
    app, chatlogs, reports = env
    _seed(chatlogs, _technical(cards=[_card("KH-A", 3)]))
    body = _body(cardReactions=[{"knowledgeId": "KH-OTHER", "cardVersion": 1, "reaction": "matched"}])
    status, payload = _call(app, _event(body))
    assert status == 400 and payload["error"] == "UnknownCard"
    assert reports.scan()["Items"] == []


def test_card_version_must_match_the_saved_answer(env):
    app, chatlogs, _ = env
    _seed(chatlogs, _technical(cards=[_card("KH-A", 3)]))
    body = _body(cardReactions=[{"knowledgeId": "KH-A", "cardVersion": 4, "reaction": "matched"}])
    assert _call(app, _event(body))[1]["error"] == "UnknownCard"


def test_reactions_from_another_turn_cannot_be_borrowed(env):
    app, chatlogs, _ = env
    _seed(chatlogs, _technical(cards=[]), _technical(turn=OTHER_TURN_ID, cards=[_card("KH-A", 3)]))
    body = _body(cardReactions=[{"knowledgeId": "KH-A", "cardVersion": 3, "reaction": "matched"}])
    assert _call(app, _event(body))[1]["error"] == "UnknownCard"


def test_report_without_cards_is_allowed_when_turn_exists(env):
    app, chatlogs, _ = env
    _seed(chatlogs, _row("user", "law", timestamp="2026-10-20T01:00:00Z"))
    status, payload = _call(app, _event(_body(cardReactions=[], modelType=None, condition=None)))
    assert status == 200
    assert payload["cardReactions"] == []
    assert "modelType" not in payload


# --- saved row --------------------------------------------------------------

def test_success_saves_candidate_with_server_derived_fields(env):
    app, chatlogs, reports = env
    _seed(chatlogs)
    before = int(time.time())
    status, payload = _call(app, _event())
    assert status == 200

    items = reports.scan()["Items"]
    assert len(items) == 1
    item = items[0]
    assert item["reportId"] == f"field-report-{TURN_ID}"
    assert item["userId"] == USER_ID
    assert item["senpaiConversationId"] == CONVERSATION_ID and item["senpaiTurnId"] == TURN_ID
    assert item["reviewState"] == "unconfirmed"
    assert item["finding"] == FINDING and item["condition"] == CONDITION
    assert item["modelType"] == "NEXCUBE"
    assert item["turnModelType"] == "NEXCUBE"
    reactions = {r["knowledgeId"]: r for r in item["cardReactions"]}
    assert reactions["KH-A"]["reaction"] == "not_matched"
    assert reactions["KH-A"]["cardVersion"] == 3
    assert reactions["KH-A"]["cardScopeStatus"] == "verified"
    assert reactions["KH-A"]["cardProductScope"] == ["AXIEZ"]
    assert reactions["KH-B"]["cardScopeStatus"] == "unverified"
    # 180 days by default; never copies the conversation or the card body.
    assert before + 180 * 86400 - 5 <= int(item["ttl"]) <= int(time.time()) + 180 * 86400 + 5
    stored = json.dumps(item, default=str, ensure_ascii=False)
    assert "ZZZ-ANSWER" not in stored and "ZZZ-CARD" not in stored

    assert payload["reportId"] == item["reportId"]
    assert payload["reviewState"] == "unconfirmed"
    assert "userId" not in payload and "ttl" not in payload


def test_ttl_days_can_be_configured_within_bounds(env, monkeypatch):
    app, chatlogs, reports = env
    _seed(chatlogs)
    monkeypatch.setenv("FIELD_REPORT_TTL_DAYS", "30")
    _call(app, _event())
    ttl = int(reports.scan()["Items"][0]["ttl"])
    assert abs(ttl - (int(time.time()) + 30 * 86400)) < 10


@pytest.mark.parametrize("value", ["0", "-1", "abc", "4000"])
def test_invalid_ttl_days_fall_back_to_default(report_app, monkeypatch, value):
    monkeypatch.setenv("FIELD_REPORT_TTL_DAYS", value)
    assert report_app.field_report_store.ttl_days_from_env() == 180


def test_control_characters_are_removed_and_newlines_kept(env):
    app, chatlogs, reports = env
    _seed(chatlogs)
    _call(app, _event(_body(finding="一行目\r\n二行目\x07\x1b")))
    assert reports.scan()["Items"][0]["finding"] == "一行目\n二行目"


def test_second_submit_returns_existing_report_unchanged(env):
    app, chatlogs, reports = env
    _seed(chatlogs)
    first = _call(app, _event())[1]
    status, second = _call(app, _event(_body(finding="別の内容")))
    assert status == 200
    assert second == first
    assert len(reports.scan()["Items"]) == 1


def test_existing_row_of_another_owner_is_never_returned(env):
    app, chatlogs, reports = env
    _seed(chatlogs)
    reports.put_item(Item={"reportId": f"field-report-{TURN_ID}", "userId": "someone-else",
                           "createdAt": "2026-10-20T00:00:00Z", "reviewState": "unconfirmed",
                           "finding": "他人の報告ZZZ-OTHER"})
    status, payload = _call(app, _event())
    assert status == 409
    assert "ZZZ-OTHER" not in json.dumps(payload, ensure_ascii=False)


# --- GET -------------------------------------------------------------------

def test_get_lists_only_own_reports_of_the_conversation(env):
    app, chatlogs, reports = env
    _seed(chatlogs)
    _call(app, _event())
    reports.put_item(Item={"reportId": "field-report-x", "userId": "someone-else",
                           "senpaiConversationId": CONVERSATION_ID, "senpaiTurnId": OTHER_TURN_ID,
                           "createdAt": "2026-10-20T02:00:00Z", "reviewState": "unconfirmed",
                           "finding": "他人ZZZ-OTHER", "cardReactions": []})
    status, payload = _call(app, _event(method="GET", query={"senpaiConversationId": CONVERSATION_ID}))
    assert status == 200
    assert [r["senpaiTurnId"] for r in payload["reports"]] == [TURN_ID]
    assert "ZZZ-OTHER" not in json.dumps(payload, ensure_ascii=False)


@pytest.mark.parametrize("query", [None, {}, {"senpaiConversationId": "bad"}])
def test_get_requires_a_canonical_conversation_id(env, query):
    app, _, _ = env
    assert _call(app, _event(method="GET", query=query))[0] == 400


def test_get_and_post_use_queries_never_scan(env, monkeypatch):
    app, chatlogs, _ = env
    _seed(chatlogs)

    def forbid(*_args, **_kwargs):
        raise AssertionError("scan is not allowed")

    for table in (app.chatlogs_table, app.reports_table):
        monkeypatch.setattr(table, "scan", forbid)
    assert _call(app, _event())[0] == 200
    assert _call(app, _event(method="GET", query={"senpaiConversationId": CONVERSATION_ID}))[0] == 200


# --- logging ---------------------------------------------------------------

def test_logs_are_structured_and_contain_no_content_or_identifiers(env, capsys):
    app, chatlogs, _ = env
    _seed(chatlogs)
    _call(app, _event())
    _call(app, _event(_body(cardReactions=[{"knowledgeId": "KH-NOPE", "cardVersion": 1, "reaction": "matched"}])))
    out = capsys.readouterr().out
    for secret in (FINDING, CONDITION, USER_ID, TURN_ID, CONVERSATION_ID, "KH-A", "KH-NOPE"):
        assert secret not in out
    for line in filter(None, out.splitlines()):
        assert json.loads(line)["event"] == "senpai_field_report"


# --- SAM -------------------------------------------------------------------

def _sam():
    from test_iam_function_permissions import _template
    return _template("phase2-template.yaml")


def test_sam_flag_defaults_off_and_all_resources_are_conditional():
    template = _sam()
    param = template["Parameters"]["SenpaiFieldReportsEnabled"]
    assert param["Default"] == "false" and param["AllowedValues"] == ["true", "false"]
    condition = str(template["Conditions"]["SenpaiFieldReportsDevEnabled"])
    assert "dev" in condition and "SenpaiFieldReportsEnabled" in condition
    for name in ("SenpaiFieldReportsTable", "SenpaiFieldReportLambdaRole", "SenpaiFieldReportFunction"):
        assert template["Resources"][name]["Condition"] == "SenpaiFieldReportsDevEnabled"


def test_sam_table_has_ttl_gsis_and_pitr():
    table = _sam()["Resources"]["SenpaiFieldReportsTable"]["Properties"]
    assert table["TimeToLiveSpecification"] == {"Enabled": True, "AttributeName": "ttl"}
    assert table["PointInTimeRecoverySpecification"]["PointInTimeRecoveryEnabled"] is True
    assert {g["IndexName"] for g in table["GlobalSecondaryIndexes"]} == {
        "userId-createdAt-index", "reviewState-createdAt-index",
    }
    assert table["SSESpecification"]["SSEEnabled"] is True


def test_sam_function_routes_and_env():
    function = _sam()["Resources"]["SenpaiFieldReportFunction"]["Properties"]
    assert function["CodeUri"] == "../../lambda/rag/senpai-field-report/"
    routes = {(e["Properties"]["Path"], e["Properties"]["Method"]) for e in function["Events"].values()}
    assert routes == {("/rag/senpai/field-reports", "POST"), ("/rag/senpai/field-reports", "GET")}
    for event in function["Events"].values():
        assert event["Properties"]["RestApiId"] == "RagApi" and "Auth" not in event["Properties"]
    env = function["Environment"]["Variables"]
    assert env["SENPAI_FIELD_REPORTS_ENABLED"] == "true"
    assert env["ADMIN_GROUP_NAME"] == "admin"
    assert env["FIELD_REPORT_TTL_DAYS"] == "180"
    assert "SenpaiFieldReportsTable" in str(env["FIELD_REPORTS_TABLE"])


def test_sam_role_is_minimal_and_separate():
    from test_iam_function_permissions import _policies, _policy_actions, _role_for_function
    template = _sam()
    role = _role_for_function(template, "SenpaiFieldReportFunction")
    others = {_role_for_function(template, n) for n in ("RagFunction", "ChatManagementFunction", "SenpaiSynthesisFunction")}
    assert role not in others
    actions = _policy_actions(_policies(template, role))
    assert actions == {"dynamodb:Query", "dynamodb:GetItem", "dynamodb:PutItem"}
    assert "dynamodb:Scan" not in actions
    assert "bedrock" not in str(_policies(template, role))


# --- loop closure: Lambda row → export JSON → scope review queue ------------

def test_saved_reports_exported_as_json_reorder_the_scope_review_queue(env, tmp_path):
    app, chatlogs, reports = env
    _seed(chatlogs)
    assert _call(app, _event())[0] == 200

    # Export as plain JSON (DynamoDB numbers become ints), the format the queue script reads.
    export = tmp_path / "export.json"
    items = json.loads(json.dumps(reports.scan()["Items"], default=int, ensure_ascii=False))
    export.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")

    root = tmp_path / "knowledge"
    cards = root / "cards" / "practice-guides"
    cards.mkdir(parents=True)
    (cards / "KH-A.md").write_text(
        "---\nknowledge_id: KH-A\ncard_version: 3\nkind: practice_guide\nstatus: approved\ntitle: \"AXIEZ のカード\"\n"
        "model_scope:\n  product_lines: [\"AXIEZ\"]\n  scope_status: verified\n"
        "  scope_verified_by: reviewer\n  scope_verified_at: \"2026-10-20\"\n---\n\n# body\n",
        encoding="utf-8",
    )
    (cards / "KH-B.md").write_text(
        "---\nknowledge_id: KH-B\ncard_version: 1\nkind: practice_guide\nstatus: draft\ntitle: NEXCUBE\n"
        "model_scope:\n  product_lines: [NEXCUBE]\n---\n\n# body\n",
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location(
        "scope_queue_e2e", REPO / "scripts" / "knowledge" / "build_scope_review_queue.py"
    )
    queue_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = queue_module
    spec.loader.exec_module(queue_module)
    out = tmp_path / "QUEUE.md"
    assert queue_module.main(["--knowledge-root", str(root), "--output", str(out),
                              "--field-reports", str(export)]) == 0

    p0 = out.read_text(encoding="utf-8").split("## P0", 1)[1].split("\n## P1", 1)[0]
    row = next(line for line in p0.splitlines() if line.startswith("| [KH-A]"))
    cells = [cell.strip() for cell in row.split("|")]
    assert cells[2] == "v3（現行）"
    assert cells[4] == "検証済み"
    assert cells[5] == "1"   # 当てはまらなかった
    assert cells[6] == "1"   # reported on NEXCUBE, card names only AXIEZ
    assert "KH-B v1（1 件）" in p0  # matched only → reference line
    aggregate = (root / "queues" / "scope-review" / "field-reports.json").read_text(encoding="utf-8")
    for secret in (FINDING, CONDITION, USER_ID, TURN_ID, CONVERSATION_ID):
        assert secret not in aggregate and secret not in out.read_text(encoding="utf-8")


# --- 調査ジョブ（ragMode=senpai_research）の回答に対する「結果を残す」 ---------------

def _research_assistant(used=(("KH-R1", 2),), candidates=(("KH-R2", 1),), model_type="AXIEZ-LINKs", **extra):
    def entry(pair, extra_keys):
        return {"knowledgeId": pair[0], "cardVersion": Decimal(pair[1]), "title": "調査のカード", **extra_keys}

    result = {
        "kind": "answer", "answerMarkdown": "回答本文ZZZ-ANSWER",
        "sources": {"tech": [], "law": [], "knowhow": {
            "used": [{**entry(p, {"ref": f"K{i}", "status": "draft", "modelFit": "matched"})}
                     for i, p in enumerate(used, start=1)],
            "candidates": [entry(p, {}) for p in candidates]}},
        "understanding": {"modelType": model_type},
    }
    filters = {"modelType": model_type} if model_type else {}
    return _row("assistant", "senpai_research", researchResult=result, queryFilters=filters,
                responseType="pages", **extra)


def _research_body(*pairs, **overrides):
    reactions = [{"knowledgeId": k, "cardVersion": v, "reaction": "not_matched"} for k, v in pairs]
    return _body(cardReactions=reactions, modelType="AXIEZ-LINKs", **overrides)


def test_research_turn_accepts_used_and_candidate_cards(env):
    app, chatlogs, reports = env
    _seed(chatlogs, _row("user", "senpai_research", timestamp="2026-10-20T01:00:00Z"), _research_assistant())
    status, payload = _call(app, _event(_research_body(("KH-R1", 2), ("KH-R2", 1))))
    assert status == 200
    item = reports.scan()["Items"][0]
    reactions = {r["knowledgeId"]: r for r in item["cardReactions"]}
    assert set(reactions) == {"KH-R1", "KH-R2"}
    for reaction in reactions.values():
        # 調査結果には範囲情報が無いので、確認済みとは扱わない
        assert reaction["cardScopeStatus"] == "unverified"
        assert reaction["cardProductScope"] == []
    assert item["turnModelType"] == "AXIEZ-LINKs"
    assert "ZZZ-ANSWER" not in json.dumps(item, default=str, ensure_ascii=False)


@pytest.mark.parametrize("pair", [("KH-OTHER", 1), ("KH-R1", 9)])
def test_research_turn_rejects_unreferenced_card_or_wrong_version(env, pair):
    app, chatlogs, reports = env
    _seed(chatlogs, _research_assistant())
    status, payload = _call(app, _event(_research_body(pair)))
    assert status == 400 and payload["error"] == "UnknownCard"
    assert reports.scan()["Items"] == []


def test_research_cards_of_another_turn_cannot_be_borrowed(env):
    app, chatlogs, _ = env
    _seed(chatlogs, _research_assistant(used=(), candidates=()),
          _research_assistant(turn=OTHER_TURN_ID, timestamp="2026-10-20T01:00:09Z"))
    assert _call(app, _event(_research_body(("KH-R1", 2))))[1]["error"] == "UnknownCard"


@pytest.mark.parametrize("result", [None, "text", {"sources": None}, {"sources": {"knowhow": []}},
                                    {"sources": {"knowhow": {"used": [5, {"knowledgeId": "KH-R1"}],
                                                             "candidates": "x"}}}])
def test_malformed_research_result_yields_no_cards_and_does_not_crash(env, result):
    app, chatlogs, _ = env
    _seed(chatlogs, _row("assistant", "senpai_research", researchResult=result))
    assert _call(app, _event(_research_body(("KH-R1", 2))))[1]["error"] == "UnknownCard"


def test_research_user_row_cards_are_ignored(env):
    app, chatlogs, _ = env
    row = _research_assistant()
    row["role"] = "user"
    _seed(chatlogs, row)
    assert _call(app, _event(_research_body(("KH-R1", 2))))[1]["error"] == "UnknownCard"


def test_research_rows_do_not_downgrade_a_verified_normal_card(env):
    app, _chatlogs, _ = env
    module = app.field_report_store
    rows = [_technical(cards=[_card("KH-R1", 2)]), _research_assistant()]
    assert module.referenced_cards(rows)[("KH-R1", 2)]["cardScopeStatus"] == "verified"
    assert module.referenced_cards(list(reversed(rows)))[("KH-R1", 2)]["cardScopeStatus"] == "verified"


def test_research_turn_report_flows_through_the_scope_review_queue(env, tmp_path):
    app, chatlogs, reports = env
    _seed(chatlogs, _research_assistant())
    assert _call(app, _event(_research_body(("KH-R1", 2))))[0] == 200
    export = tmp_path / "export.json"
    items = json.loads(json.dumps(reports.scan()["Items"], default=int, ensure_ascii=False))
    export.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")

    root = tmp_path / "knowledge"
    cards = root / "cards" / "practice-guides"
    cards.mkdir(parents=True)
    (cards / "KH-R1.md").write_text(
        "---\nknowledge_id: KH-R1\ncard_version: 2\nkind: practice_guide\nstatus: approved\ntitle: \"調査のカード\"\n"
        "model_scope:\n  product_lines: [\"AXIEZ\"]\n  scope_status: verified\n"
        "  scope_verified_by: reviewer\n  scope_verified_at: \"2026-10-20\"\n---\n\n# body\n",
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location(
        "scope_queue_research", REPO / "scripts" / "knowledge" / "build_scope_review_queue.py")
    queue_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = queue_module
    spec.loader.exec_module(queue_module)
    out = tmp_path / "QUEUE.md"
    assert queue_module.main(["--knowledge-root", str(root), "--output", str(out),
                              "--field-reports", str(export)]) == 0
    text = out.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| [KH-R1]"))
    cells = [cell.strip() for cell in row.split("|")]
    assert cells[2] == "v2（現行）"
    assert cells[5] == "1"  # 当てはまらなかった（調査の回答に対する報告も数える）
