"""調査ジョブ表（DynamoDB）の条件付き書き込み・ロック・日次上限・追記専用イベントの契約テスト。"""
import pytest

import test_senpai_research_support as support
from test_senpai_research_support import FakeClock, USER_ID, OTHER_USER_ID

JOB_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
JOB_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"


@pytest.fixture
def env():
    import boto3
    from moto import mock_aws
    store_mod = support.load_module("senpai_research_store.py")
    with mock_aws():
        table = support.make_jobs_table(boto3)
        clock = FakeClock()
        yield store_mod, store_mod.JobStore(table, clock=clock), table, clock


def _item(store_mod, job_id=JOB_A, user=USER_ID, clock=None, **extra):
    request = {
        "question": support.QUESTION,
        "modelType": "AXIEZ-LINKs",
        "senpaiConversationId": support.CONVERSATION_ID,
        "senpaiTurnId": support.TURN_ID,
        "clientRequestId": support.CLIENT_REQUEST_ID,
    }
    request.update(extra)
    return store_mod.build_job_item(job_id, user, request, now=clock() if clock else 1_800_000_000.0,
                                    ttl_seconds=150)


def _step(seq, step="understand", status="running"):
    return {"seq": seq, "step": step, "labelJa": "質問を整理中", "status": status,
            "startedAt": "2026-10-20T01:00:00Z", "endedAt": None}


# ---------------------------------------------------------------- build_job_item

def test_job_item_is_queued_with_owner_and_seq_counter(env):
    store_mod, store, _table, clock = env
    item = _item(store_mod, clock=clock)
    assert item["pk"] == f"JOB#{JOB_A}"
    assert item["jobId"] == JOB_A
    assert item["userId"] == USER_ID
    assert item["status"] == "queued"
    assert item["steps"] == [] and item["nextSeq"] == 1
    assert item["expiresAt"] == int(clock()) + 150
    assert item["ttl"] >= int(clock()) + 6 * 24 * 3600  # 7 日保持


# ---------------------------------------------------------------- idempotency

def test_claim_request_returns_existing_job_for_same_client_request_id(env):
    _mod, store, *_ = env
    assert store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_A) == (JOB_A, True)
    assert store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_B) == (JOB_A, False)


def test_claim_request_replaces_expired_idempotency_row_before_ttl_deletion(env):
    _mod, store, table, clock = env
    key = f"REQ#{USER_ID}#{support.CLIENT_REQUEST_ID}"
    table.put_item(Item={"pk": key, "jobId": JOB_A, "ttl": int(clock()) - 1})

    assert table.get_item(Key={"pk": key}).get("Item") is not None
    assert store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_B) == (JOB_B, True)
    assert table.get_item(Key={"pk": key})["Item"]["jobId"] == JOB_B


def test_release_request_does_not_delete_a_claim_owned_by_another_job(env):
    _mod, store, *_ = env
    assert store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_A) == (JOB_A, True)

    store.release_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_B)

    assert store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_B) == (JOB_A, False)


def test_claim_request_is_scoped_per_user(env):
    _mod, store, *_ = env
    store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_A)
    assert store.claim_request(OTHER_USER_ID, support.CLIENT_REQUEST_ID, JOB_B) == (JOB_B, True)


def test_release_request_allows_reuse(env):
    _mod, store, *_ = env
    store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_A)
    store.release_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_A)
    assert store.claim_request(USER_ID, support.CLIENT_REQUEST_ID, JOB_B) == (JOB_B, True)


# ---------------------------------------------------------------- lock

def test_lock_allows_only_one_active_job_per_user(env):
    _mod, store, *_ = env
    assert store.acquire_lock(USER_ID, JOB_A, 150) is True
    assert store.acquire_lock(USER_ID, JOB_B, 150) is False
    assert store.acquire_lock(OTHER_USER_ID, JOB_B, 150) is True


def test_lock_release_only_by_owner_job(env):
    _mod, store, *_ = env
    store.acquire_lock(USER_ID, JOB_A, 150)
    store.release_lock(USER_ID, JOB_B)  # 別ジョブでは外れない
    assert store.acquire_lock(USER_ID, JOB_B, 150) is False
    store.release_lock(USER_ID, JOB_A)
    assert store.acquire_lock(USER_ID, JOB_B, 150) is True


def test_expired_lock_can_be_taken_over(env):
    _mod, store, _table, clock = env
    store.acquire_lock(USER_ID, JOB_A, 150)
    clock.advance(151)
    assert store.acquire_lock(USER_ID, JOB_B, 150) is True
    store.release_lock(USER_ID, JOB_A)  # 古いジョブの解放が新しいロックを壊さない
    assert store.acquire_lock(USER_ID, "cccccccc-cccc-4ccc-8ccc-cccccccccccc", 150) is False


# ---------------------------------------------------------------- daily limit

def test_daily_slot_counts_up_to_limit_then_refuses(env):
    _mod, store, *_ = env
    assert store.take_daily_slot(USER_ID, 2) is True
    assert store.take_daily_slot(USER_ID, 2) is True
    assert store.take_daily_slot(USER_ID, 2) is False
    assert store.take_daily_slot(OTHER_USER_ID, 2) is True


def test_daily_slot_can_be_returned(env):
    _mod, store, *_ = env
    store.take_daily_slot(USER_ID, 1)
    store.return_daily_slot(USER_ID)
    assert store.take_daily_slot(USER_ID, 1) is True


def test_daily_slot_resets_on_next_jst_day(env):
    _mod, store, _table, clock = env
    assert store.take_daily_slot(USER_ID, 1) is True
    assert store.take_daily_slot(USER_ID, 1) is False
    clock.advance(24 * 3600)
    assert store.take_daily_slot(USER_ID, 1) is True


# ---------------------------------------------------------------- job lifecycle

def test_create_and_get_job_round_trip(env):
    store_mod, store, _table, clock = env
    store.create_job(_item(store_mod, clock=clock))
    job = store.get_job(JOB_A)
    assert job["userId"] == USER_ID and job["status"] == "queued"
    assert store.get_job(JOB_B) is None


def test_get_job_hides_expired_item_before_ttl_deletion(env):
    store_mod, store, table, clock = env
    item = _item(store_mod, clock=clock)
    item["ttl"] = int(clock()) - 1
    store.create_job(item)

    assert table.get_item(Key={"pk": f"JOB#{JOB_A}"}).get("Item") is not None
    assert store.get_job(JOB_A) is None


def test_start_job_only_from_queued(env):
    store_mod, store, _table, clock = env
    store.create_job(_item(store_mod, clock=clock))
    assert store.start_job(JOB_A) is True
    assert store.start_job(JOB_A) is False  # 二重実行の防止
    assert store.get_job(JOB_A)["status"] == "running"


def test_append_step_is_append_only_and_sequence_checked(env):
    store_mod, store, _table, clock = env
    store.create_job(_item(store_mod, clock=clock))
    assert store.append_step(JOB_A, _step(1)) is True
    assert store.append_step(JOB_A, _step(2, status="done")) is True
    # 同じ seq・飛んだ seq は拒否される
    assert store.append_step(JOB_A, _step(2)) is False
    assert store.append_step(JOB_A, _step(5)) is False
    job = store.get_job(JOB_A)
    assert [s["seq"] for s in job["steps"]] == [1, 2]
    assert job["nextSeq"] == 3


def test_complete_job_stores_result_and_debug_floats_as_decimals(env):
    store_mod, store, _table, clock = env
    store.create_job(_item(store_mod, clock=clock))
    store.start_job(JOB_A)
    assert store.complete_job(JOB_A, {"kind": "answer"}, {"tools": [{"topScores": [0.61, 0.5]}]}) is True
    job = store.get_job(JOB_A)
    assert job["status"] == "completed"
    assert job["result"] == {"kind": "answer"}
    assert float(job["debug"]["tools"][0]["topScores"][0]) == pytest.approx(0.61)


def test_complete_after_failure_is_refused(env):
    store_mod, store, _table, clock = env
    store.create_job(_item(store_mod, clock=clock))
    store.start_job(JOB_A)
    assert store.fail_job(JOB_A, "Timeout", "時間内に完了しませんでした") is True
    assert store.complete_job(JOB_A, {"kind": "answer"}, {}) is False
    job = store.get_job(JOB_A)
    assert job["status"] == "failed"
    assert job["error"] == {"code": "Timeout", "message": "時間内に完了しませんでした"}


def test_expire_job_fails_only_stale_active_jobs(env):
    store_mod, store, _table, clock = env
    store.create_job(_item(store_mod, clock=clock))
    assert store.expire_job(JOB_A) is False  # まだ期限内
    clock.advance(151)
    assert store.expire_job(JOB_A) is True
    job = store.get_job(JOB_A)
    assert job["status"] == "failed" and job["error"]["code"] == "Timeout"
    assert store.expire_job(JOB_A) is False  # 終わったジョブには何もしない
