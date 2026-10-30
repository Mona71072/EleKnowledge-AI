"""POST /rag/senpai/research と GET /rag/senpai/research/{jobId} の契約テスト。"""
import json
import uuid

import pytest

import test_senpai_research_support as support
from test_senpai_research_support import (
    FakeClock, OTHER_USER_ID, USER_ID, api_event, body_of, research_env, valid_body,  # noqa: F401
)


@pytest.fixture
def api(research_env):
    import boto3
    from moto import mock_aws
    module = support.load_module("senpai_research_api.py")
    with mock_aws():
        table = support.make_jobs_table(boto3)
        clock = FakeClock()
        store = module.store.JobStore(table, clock=clock)
        invoked = []
        mp = pytest.MonkeyPatch()
        mp.setattr(module, "get_store", lambda: store)
        mp.setattr(module, "invoke_worker", lambda job_id: invoked.append(job_id))
        mp.setattr(module, "now", clock)
        module.test_ctx = type("Ctx", (), {"store": store, "invoked": invoked, "clock": clock, "table": table})
        try:
            yield module
        finally:
            mp.undo()


def _post(api, **overrides):
    return api.lambda_handler(api_event(valid_body(**overrides)), None)


def _finish(api, job_id, user=USER_ID):
    """ジョブを終わらせ、ロックを外す（ワーカーの後始末と同じ）。"""
    api.test_ctx.store.release_lock(user, job_id)


# ---------------------------------------------------------------- gates

class _Boom:
    def __getattr__(self, name):
        raise AssertionError("must not touch the store before the gate passes")


@pytest.mark.parametrize("env_name,flag,groups", [
    ("prod", "true", "admin"),
    ("dev", "false", "admin"),
    ("dev", "true", "users"),
    ("dev", "true", None),
])
def test_gate_rejects_before_any_store_or_worker_access(api, monkeypatch, env_name, flag, groups):
    monkeypatch.setenv("ENVIRONMENT", env_name)
    monkeypatch.setenv("SENPAI_RESEARCH_ENABLED", flag)
    monkeypatch.setattr(api, "get_store", lambda: _Boom())
    monkeypatch.setattr(api, "invoke_worker", lambda job_id: pytest.fail("worker invoked"))
    for method, job_id in (("POST", None), ("GET", support.UNKNOWN_JOB_ID)):
        response = api.lambda_handler(api_event(method=method, groups=groups, job_id=job_id), None)
        assert response["statusCode"] == 403
        assert body_of(response)["error"] == "FeatureUnavailable"


def test_options_preflight_is_answered_without_gate(api, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "prod")
    event = api_event(method="OPTIONS")
    response = api.lambda_handler(event, None)
    assert response["statusCode"] == 200
    assert "GET" in response["headers"]["Access-Control-Allow-Methods"]


def test_missing_sub_is_401(api):
    response = api.lambda_handler(api_event(valid_body(), sub=None), None)
    assert response["statusCode"] == 401


def test_other_methods_are_405(api):
    response = api.lambda_handler(api_event(method="DELETE"), None)
    assert response["statusCode"] == 405


# ---------------------------------------------------------------- validation

@pytest.mark.parametrize("overrides", [
    {"question": ""},
    {"question": "   "},
    {"question": "あ" * 2001},
    {"question": 123},
    {"question": None},
    {"senpaiConversationId": "not-a-uuid"},
    {"senpaiTurnId": "22222222-2222-4222-8222-22222222222"},
    {"clientRequestId": "x"},
    {"clientRequestId": None},
    {"modelType": "UNKNOWN"},
    {"modelType": 5},
    {"userId": "attacker"},
    {"extra": 1},
])
def test_invalid_bodies_are_400(api, overrides):
    body = valid_body()
    for key, value in overrides.items():
        if value is None:
            body.pop(key, None)
        else:
            body[key] = value
    response = api.lambda_handler(api_event(body), None)
    assert response["statusCode"] == 400, overrides
    assert body_of(response)["error"] == "ValidationError"
    assert api.test_ctx.invoked == []


@pytest.mark.parametrize("raw", ["not json", "[]", "null", ""])
def test_malformed_json_is_400(api, raw):
    response = api.lambda_handler(api_event(raw_body=raw), None)
    assert response["statusCode"] == 400


def test_question_of_exactly_2000_chars_and_known_model_type_are_accepted(api):
    response = _post(api, question="あ" * 2000, modelType="AXIEZ-LINKs")
    assert response["statusCode"] == 202


# ---------------------------------------------------------------- create

def test_post_creates_queued_job_and_invokes_worker_once(api):
    response = _post(api, modelType="NEXCUBE")
    assert response["statusCode"] == 202
    body = body_of(response)
    assert uuid.UUID(body["jobId"])
    assert body["status"] == "queued" and body["pollAfterMs"] == 1500
    assert api.test_ctx.invoked == [body["jobId"]]
    job = api.test_ctx.store.get_job(body["jobId"])
    # SECURITY: the owner is the JWT sub; the body is never trusted for identity.
    assert job["userId"] == USER_ID
    assert job["question"] == support.QUESTION
    assert job["modelType"] == "NEXCUBE"


def test_same_client_request_id_returns_same_job_without_second_invoke(api):
    first = body_of(_post(api))
    again = _post(api)
    assert again["statusCode"] == 202
    assert body_of(again)["jobId"] == first["jobId"]
    assert api.test_ctx.invoked == [first["jobId"]]


def test_duplicate_request_during_initial_claim_keeps_the_first_claim(api):
    request = api.parse_request(api_event(valid_body()))
    store = api.test_ctx.store
    first_job_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    second_job_id = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
    assert store.claim_request(USER_ID, request["clientRequestId"], first_job_id) == (first_job_id, True)

    replay = api._claim_or_replay(store, USER_ID, request, second_job_id)

    assert replay == (first_job_id, "request_in_flight")
    assert store.claim_request(USER_ID, request["clientRequestId"], second_job_id) == (first_job_id, False)


def test_duplicate_post_during_initial_claim_returns_request_in_progress(api):
    first_job_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    assert api.test_ctx.store.claim_request(
        USER_ID, support.CLIENT_REQUEST_ID, first_job_id
    ) == (first_job_id, True)

    response = _post(api)

    assert response["statusCode"] == 409
    assert body_of(response)["error"] == "RequestInProgress"
    assert api.test_ctx.invoked == []
    assert api.test_ctx.store.claim_request(
        USER_ID, support.CLIENT_REQUEST_ID, "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
    ) == (first_job_id, False)


def test_orphaned_request_claim_can_be_reclaimed_after_lease(api):
    request = api.parse_request(api_event(valid_body()))
    store = api.test_ctx.store
    first_job_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    next_job_id = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
    assert store.claim_request(USER_ID, request["clientRequestId"], first_job_id) == (first_job_id, True)
    api.test_ctx.clock.advance(api.store.REQUEST_CLAIM_LEASE_SECONDS + 1)

    replay = api._claim_or_replay(store, USER_ID, request, next_job_id)

    assert replay is None
    assert store.claim_request(USER_ID, request["clientRequestId"], first_job_id) == (next_job_id, False)


def test_expired_request_replay_creates_new_job_without_returning_old_result(api):
    first = body_of(_post(api))
    store = api.test_ctx.store
    store.start_job(first["jobId"])
    store.complete_job(first["jobId"], {"kind": "answer", "answerMarkdown": "期限切れ"}, {})
    _finish(api, first["jobId"])
    now = int(api.test_ctx.clock())
    api.test_ctx.table.update_item(
        Key={"pk": f"JOB#{first['jobId']}"},
        UpdateExpression="SET #ttl = :expired",
        ExpressionAttributeNames={"#ttl": "ttl"},
        ExpressionAttributeValues={":expired": now - 1},
    )
    api.test_ctx.table.update_item(
        Key={"pk": f"REQ#{USER_ID}#{support.CLIENT_REQUEST_ID}"},
        UpdateExpression="SET #ttl = :expired",
        ExpressionAttributeNames={"#ttl": "ttl"},
        ExpressionAttributeValues={":expired": now - 1},
    )

    retry = _post(api)

    assert retry["statusCode"] == 202
    assert body_of(retry)["jobId"] != first["jobId"]
    assert api.test_ctx.invoked == [first["jobId"], body_of(retry)["jobId"]]


def test_second_active_job_is_409_and_does_not_use_quota(api, monkeypatch):
    monkeypatch.setenv("SENPAI_RESEARCH_DAILY_LIMIT", "2")
    first = body_of(_post(api))
    blocked = _post(api, clientRequestId=support.SECOND_CLIENT_REQUEST_ID)
    assert blocked["statusCode"] == 409
    assert body_of(blocked)["error"] == "JobInProgress"
    _finish(api, first["jobId"])
    # 409 の要求は日次の枠を使っていない: 上限2のうち、2件目はまだ通る
    second = _post(api, clientRequestId=support.SECOND_CLIENT_REQUEST_ID)
    assert second["statusCode"] == 202
    _finish(api, body_of(second)["jobId"])
    third = _post(api, clientRequestId=support.THIRD_CLIENT_REQUEST_ID)
    assert third["statusCode"] == 429


def test_daily_limit_is_429_and_releases_lock(api, monkeypatch):
    monkeypatch.setenv("SENPAI_RESEARCH_DAILY_LIMIT", "2")
    for client_id in (support.CLIENT_REQUEST_ID, support.SECOND_CLIENT_REQUEST_ID):
        response = _post(api, clientRequestId=client_id)
        assert response["statusCode"] == 202
        _finish(api, body_of(response)["jobId"])
    third = _post(api, clientRequestId=support.THIRD_CLIENT_REQUEST_ID)
    assert third["statusCode"] == 429
    assert body_of(third)["error"] == "DailyLimitExceeded"
    # 上限超過でロックが残らない: 別ユーザーは影響なし、本人も 409 ではなく 429 のまま
    assert api.test_ctx.store.acquire_lock(USER_ID, "dddddddd-dddd-4ddd-8ddd-dddddddddddd", 150) is True


def test_rejected_request_can_be_retried_with_same_client_request_id(api):
    first = body_of(_post(api))
    blocked = _post(api, clientRequestId=support.SECOND_CLIENT_REQUEST_ID)
    assert blocked["statusCode"] == 409
    _finish(api, first["jobId"])
    retry = _post(api, clientRequestId=support.SECOND_CLIENT_REQUEST_ID)
    assert retry["statusCode"] == 202


def test_worker_start_failure_marks_job_failed_and_frees_the_user(api, monkeypatch):
    def broken(job_id):
        raise RuntimeError("invoke denied")
    monkeypatch.setattr(api, "invoke_worker", broken)
    response = _post(api)
    assert response["statusCode"] == 502
    payload = body_of(response)
    assert payload["error"] == "StartFailed"
    assert "Traceback" not in response["body"] and "invoke denied" not in response["body"]
    monkeypatch.setattr(api, "invoke_worker", lambda job_id: None)
    assert _post(api, clientRequestId=support.SECOND_CLIENT_REQUEST_ID)["statusCode"] == 202


def test_unexpected_error_is_unified_500_without_stack_trace(api, monkeypatch):
    monkeypatch.setattr(api, "get_store", lambda: (_ for _ in ()).throw(RuntimeError("secret detail")))
    response = _post(api)
    assert response["statusCode"] == 500
    assert body_of(response)["error"] == "InternalError"
    assert "secret detail" not in response["body"]


# ---------------------------------------------------------------- status GET

def _get(api, job_id, user=USER_ID, **query):
    return api.lambda_handler(
        api_event(method="GET", sub=user, job_id=job_id, query=query or None), None
    )


def _seed_steps(api, job_id, count):
    store = api.test_ctx.store
    for seq in range(1, count + 1):
        store.append_step(job_id, {
            "seq": seq, "step": "understand", "labelJa": "質問を整理中", "status": "running",
            "startedAt": "2026-10-20T01:00:00Z", "endedAt": None,
        })


def test_status_returns_only_steps_after_seq_and_poll_hint(api):
    job_id = body_of(_post(api))["jobId"]
    api.test_ctx.store.start_job(job_id)
    _seed_steps(api, job_id, 4)
    body = body_of(_get(api, job_id, afterSeq="2"))
    assert body["status"] == "running"
    assert [s["seq"] for s in body["steps"]] == [3, 4]
    assert body["pollAfterMs"] == 1500
    assert "result" not in body and "error" not in body


def test_status_without_after_seq_returns_all_steps(api):
    job_id = body_of(_post(api))["jobId"]
    _seed_steps(api, job_id, 3)
    assert [s["seq"] for s in body_of(_get(api, job_id))["steps"]] == [1, 2, 3]


@pytest.mark.parametrize("value", ["abc", "-1", "1.5", ""])
def test_bad_after_seq_is_400(api, value):
    job_id = body_of(_post(api))["jobId"]
    assert _get(api, job_id, afterSeq=value)["statusCode"] == 400


def test_other_users_and_unknown_jobs_are_404(api):
    job_id = body_of(_post(api))["jobId"]
    assert _get(api, job_id, user=OTHER_USER_ID)["statusCode"] == 404
    assert _get(api, support.UNKNOWN_JOB_ID)["statusCode"] == 404
    assert _get(api, "not-a-uuid")["statusCode"] == 404
    # 他人のジョブの存在を内容で漏らさない: 本文は存在しない場合と同じ
    assert _get(api, job_id, user=OTHER_USER_ID)["body"] == _get(api, support.UNKNOWN_JOB_ID)["body"]


def test_completed_job_returns_result_and_admin_debug(api):
    job_id = body_of(_post(api))["jobId"]
    store = api.test_ctx.store
    store.start_job(job_id)
    store.complete_job(job_id, {"kind": "answer", "answerMarkdown": "結論"},
                       {"queries": {"tech": ["q"]}, "tools": [{"topScores": [0.61]}]})
    body = body_of(_get(api, job_id))
    assert body["status"] == "completed"
    assert body["result"]["answerMarkdown"] == "結論"
    assert body["debug"]["queries"] == {"tech": ["q"]}
    assert body["debug"]["tools"][0]["topScores"] == [0.61]
    assert body["pollAfterMs"] == 0
    assert "error" not in body


def test_status_hides_expired_completed_result_while_ttl_deletion_is_pending(api):
    job_id = body_of(_post(api))["jobId"]
    store = api.test_ctx.store
    store.start_job(job_id)
    store.complete_job(job_id, {"kind": "answer", "answerMarkdown": "期限切れの回答"}, {})
    store._table.update_item(
        Key={"pk": f"JOB#{job_id}"},
        UpdateExpression="SET #ttl = :expired",
        ExpressionAttributeNames={"#ttl": "ttl"},
        ExpressionAttributeValues={":expired": int(api.test_ctx.clock()) - 1},
    )

    assert api.test_ctx.table.get_item(Key={"pk": f"JOB#{job_id}"}).get("Item") is not None
    response = _get(api, job_id)
    assert response["statusCode"] == 404
    assert "期限切れの回答" not in response["body"]


def test_debug_is_hidden_from_non_admin_callers(api):
    job_id = body_of(_post(api))["jobId"]
    store = api.test_ctx.store
    store.start_job(job_id)
    store.complete_job(job_id, {"kind": "answer"}, {"queries": {}})
    # ゲートが管理者だけに絞るため、同じ関数の debug 判定を直接確認する
    assert "debug" not in api.build_status_payload(store.get_job(job_id), after_seq=0, include_debug=False)
    assert "debug" in api.build_status_payload(store.get_job(job_id), after_seq=0, include_debug=True)


def test_failed_job_returns_error_code_and_message(api):
    job_id = body_of(_post(api))["jobId"]
    store = api.test_ctx.store
    store.start_job(job_id)
    store.fail_job(job_id, "BudgetExceeded", "上限に達しました")
    body = body_of(_get(api, job_id))
    assert body["status"] == "failed"
    assert body["error"] == {"code": "BudgetExceeded", "message": "上限に達しました"}
    assert "result" not in body


def test_stale_active_job_is_failed_with_timeout_and_frees_the_user(api):
    job_id = body_of(_post(api))["jobId"]
    api.test_ctx.clock.advance(1000)
    body = body_of(_get(api, job_id))
    assert body["status"] == "failed"
    assert body["error"]["code"] == "Timeout"
    assert "Traceback" not in json.dumps(body)
    # ロックは期限切れなので新しいジョブを始められる
    assert _post(api, clientRequestId=support.SECOND_CLIENT_REQUEST_ID)["statusCode"] == 202
