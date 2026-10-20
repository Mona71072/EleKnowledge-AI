"""調査ジョブの実際の応答サンプル（フロントとの契約テスト用）の生成と、コミット済みサンプルとの一致確認。

サンプルは tests/fixtures/knowledge/senpai-research-samples/*.json。受付 → ワーカー → 進捗 → 履歴の
実装を moto と偽の Bedrock/KB で動かして得た「実際の応答」で、固定の UUID・時刻にそろえてある。
バックエンドの形が変わるとこのテストが落ちる。意図した変更なら次で作り直して差分を確認する:

    REGEN_SENPAI_RESEARCH_SAMPLES=1 python -m pytest tests/unit/test_senpai_research_samples.py

決定的にするための固定（サンプルの内容は実装どおりで、これ以外は加工しない）:
- jobId・時刻・経過時間は固定。技術と法令の検索は同時でなく順番に実行する（イベント順を固定するため）。
- 履歴の ttl は 2100-01-01、daysUntilDeletion は 60 に置き換える（実行日で変わる値のため）。
"""
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import test_senpai_research_support as support
from test_senpai_research_runner import (
    FakeDeps, GOOD_ANSWER, SUFFICIENT, _directive, _law, _retrieval, _tech, _understanding,
)
from test_senpai_research_support import FakeClock, api_event, valid_body

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "knowledge" / "senpai-research-samples"
REGEN_ENV = "REGEN_SENPAI_RESEARCH_SAMPLES"
JOB_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
START_EPOCH = 1_800_000_000.0
FIXED_TTL = 4102444800  # 2100-01-01
FIXED_DAYS_UNTIL_DELETION = 60
QUESTION = "AXIEZ-LINKsのドアが開閉時に異音がします。建築基準法上の確認は必要ですか"
ANSWER = (
    "## 結論\nまずドアの調整状態を確認してください[T1][T2]。法令上の確認は[L1]の範囲です。\n\n"
    "## 根拠と手順\n"
    "- 戸の開閉調整の手順が記載されています[T1]。\n"
    "- 昇降機の構造は政令で定める基準によります[L1]。\n"
    "- 同機種の事例があります（ノウハウ・未承認）[K1]。別機種の事例[K2]は機種が異なる可能性があります（ノウハウ・未承認）。\n\n"
    "## 確認が必要な点\n- 階数と製造年が不明です[T9]。\n- 異音が出るタイミング。"
)


class ReadTimeoutError(Exception):
    """Bedrock の読み取りタイムアウト（クラス名で Timeout と判定される）。"""


def _card(kid, title, fit, status="draft"):
    return {"knowledgeId": kid, "cardVersion": 2, "title": title, "status": status,
            "modelFit": fit, "body": f"## 症状\n{title}"}


class MidRunDeps(FakeDeps):
    """2回目の十分性の判断に入った時点（再検索の後）で、進捗 API を呼んで途中経過を記録する。"""

    def __init__(self, capture, **kw):
        super().__init__(**kw)
        self.capture = capture
        self.sufficiency_calls = 0

    def call_model(self, purpose, system, user, max_tokens):
        if purpose == "sufficiency":
            self.sufficiency_calls += 1
            if self.sufficiency_calls == 2:
                self.capture()
        return super().call_model(purpose, system, user, max_tokens)


def _json(response):
    return {"statusCode": response["statusCode"], "body": json.loads(response["body"] or "null")}


class Lab:
    """1 つのシナリオを動かす実験場: moto の表・固定化した時計・ワーカーの同期実行。"""

    def __init__(self, mods, mp):
        import boto3
        self.api, self.worker = mods
        self.boto3 = boto3
        self.mp = mp

    def _fixed_time(self):
        base = datetime(2027, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
        ticks = {"n": 0}

        def now_iso():
            ticks["n"] += 1
            return (base + timedelta(seconds=ticks["n"])).isoformat().replace("+00:00", "Z")

        monotonic = {"t": 0.0}

        def clock():
            monotonic["t"] += 0.05
            return monotonic["t"]

        return now_iso, clock

    def open(self):
        api, worker, mp = self.api, self.worker, self.mp
        self.jobs = support.make_jobs_table(self.boto3)
        self.chatlogs = support.make_chatlogs_table(self.boto3)
        self.clock = FakeClock(START_EPOCH)
        self.store = api.store.JobStore(self.jobs, clock=self.clock)
        self.runtime = SimpleNamespace(
            store=self.store, chatlogs_table=self.chatlogs, limits=worker.config.load_limits())
        now_iso, monotonic = self._fixed_time()
        recorder_cls, budget_cls = worker.recorder_module.StepRecorder, worker.budget_module.Budget
        mp.setattr(worker.recorder_module, "StepRecorder", lambda append, resync=None: recorder_cls(append, now_iso=now_iso, resync=resync))
        mp.setattr(worker.budget_module, "Budget", lambda limits, **kw: budget_cls(limits, clock=monotonic, **kw))
        mp.setattr(worker.runner.search, "run_parallel", lambda tasks: [task() for task in tasks])
        build_rows = worker.chatlog.build_rows
        mp.setattr(worker.chatlog, "build_rows", lambda job, result: build_rows(
            job, result, now=datetime(2027, 1, 15, 8, 5, 0, tzinfo=timezone.utc), epoch=int(START_EPOCH)))
        mp.setattr(api, "get_store", lambda: self.store)
        mp.setattr(api, "now", self.clock)
        mp.setattr(api, "uuid", SimpleNamespace(uuid4=lambda: uuid.UUID(JOB_ID), UUID=uuid.UUID))
        self.use_deps(None)
        return self

    def use_deps(self, deps):
        self.mp.setattr(
            self.api, "invoke_worker",
            (lambda job_id: self.worker.process_job(job_id, self.runtime, deps)) if deps else (lambda job_id: None))

    def post(self, **overrides):
        return self.api.lambda_handler(api_event(valid_body(question=QUESTION, **overrides)), None)

    def get(self, **query):
        return self.api.lambda_handler(
            api_event(method="GET", job_id=JOB_ID, query=query or None), None)

    def run(self, deps, **overrides):
        """ジョブを最後まで動かし、(受付の応答, 最終の進捗の応答) を返す。"""
        self.use_deps(deps)
        accepted = self.post(**overrides)
        return _json(accepted), _json(self.get())


def _answer_deps():
    return FakeDeps(
        understand=_understanding(lawRelevant=True, queries={
            "tech": "AXIEZ-LINKs ドア 開閉 異音", "law": "昇降機 構造 基準", "knowhow": "ドア 異音"}),
        tech=lambda q, m: _retrieval(_tech("TI-1.pdf", 3, "戸の開閉調整の手順", 0.82),
                                     _tech("TI-2.pdf", 5, "戸まわりの点検項目", 0.64)),
        law=lambda q: _retrieval(_law("第三十五条", 0.71)),
        cards=[_card("KH-AX-001", "ドア開閉時の異音", "matched"),
               _card("KH-NX-014", "戸の擦り音（別機種）", "other_product"),
               _card("KH-GEN-003", "ドア全般の点検メモ", "general")],
        hints=["TI-2024-017"], synth=ANSWER)


def _mid_run_samples(lab):
    captured = {}

    def capture():
        everything = _json(lab.get())
        steps = everything["body"]["steps"]
        captured["status-running.json"] = everything
        captured["status-running-after-seq.json"] = _json(lab.get(afterSeq=str(steps[2]["seq"])))

    def tech(query, model):
        return _retrieval(_tech("TI-9.pdf", 1, "調整の補足", 0.7)) if "調整" in query \
            else _retrieval(_tech("TI-1.pdf", 3, "戸の開閉調整の手順", 0.82))

    deps = MidRunDeps(
        capture, understand=_understanding(), tech=tech,
        sufficiency=[_directive(sufficient=False, action="retry_search", query="ドア 調整 異音", target="tech"),
                     SUFFICIENT],
        synth=GOOD_ANSWER)
    lab.run(deps)
    return captured


def _history_sample(lab, chat_loader):
    for row in lab.chatlogs.scan()["Items"]:
        lab.chatlogs.update_item(
            Key={"sessionId": row["sessionId"], "messageId": row["messageId"]},
            UpdateExpression="SET #t = :t", ExpressionAttributeNames={"#t": "ttl"},
            ExpressionAttributeValues={":t": FIXED_TTL})
    chat, _table = chat_loader()
    chat.chatlogs_table = lab.chatlogs
    from test_senpai_history import _chat_event
    response = chat.lambda_handler(_chat_event(
        f"/chat/sessions/{support.CONVERSATION_ID}/messages", qs={"context": "senpai"},
        sub=support.USER_ID, path_params={"sessionId": support.CONVERSATION_ID}), None)
    sample = _json(response)
    for message in sample["body"]["messages"]:
        message["daysUntilDeletion"] = FIXED_DAYS_UNTIL_DELETION
    return sample


def _error_samples(lab, mp):
    api = lab.api
    samples = []

    def record(name, response, request):
        samples.append({"name": name, "request": request, **_json(response)})

    def event(**kw):
        return api.lambda_handler(api_event(**kw), None)

    mp.setenv("ENVIRONMENT", "prod")
    record("feature_unavailable", event(), "POST (prod, または無効、または管理者でない)")
    mp.setenv("ENVIRONMENT", "dev")
    record("unauthorized", event(sub=None), "POST (sub なし)")
    record("validation_error_post", event(body=valid_body(question="")), "POST (question が空)")
    record("validation_error_after_seq",
           api.lambda_handler(api_event(method="GET", job_id=JOB_ID, query={"afterSeq": "x"}), None),
           "GET ?afterSeq=x")
    record("job_not_found", api.lambda_handler(api_event(method="GET", job_id=JOB_ID), None),
           "GET (他人のジョブ・存在しない・UUID でない jobId は同じ)")
    record("method_not_allowed", event(method="DELETE"), "DELETE")
    lab.use_deps(None)
    lab.post()
    record("job_in_progress", api.lambda_handler(api_event(valid_body(
        clientRequestId=support.SECOND_CLIENT_REQUEST_ID)), None), "POST (前のジョブが実行中)")
    lab.store.release_lock(support.USER_ID, JOB_ID)
    mp.setenv("SENPAI_RESEARCH_DAILY_LIMIT", "1")
    record("daily_limit_exceeded", api.lambda_handler(api_event(valid_body(
        clientRequestId=support.THIRD_CLIENT_REQUEST_ID)), None), "POST (1日の上限超過)")
    mp.setenv("SENPAI_RESEARCH_DAILY_LIMIT", "20")
    mp.setattr(api, "invoke_worker", lambda job_id: (_ for _ in ()).throw(RuntimeError("denied")))
    mp.setattr(api, "uuid", SimpleNamespace(
        uuid4=lambda: uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"), UUID=uuid.UUID))
    lab.store.release_lock(support.USER_ID, JOB_ID)
    record("start_failed", api.lambda_handler(api_event(valid_body(
        clientRequestId="99999999-9999-4999-8999-999999999999")), None), "POST (ワーカーを起動できない)")
    mp.setattr(api, "get_store", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    record("internal_error", event(), "POST (想定外の例外)")
    return samples


def generate_samples() -> dict:
    """ファイル名 → 内容。各シナリオは新しい moto 環境で動かす。"""
    from moto import mock_aws
    mods = (support.load_module("senpai_research_api.py"), support.load_module("senpai_research_worker.py"))
    from test_senpai_history import _load_chat_app
    out = {}

    def scenario(body):
        mp = pytest.MonkeyPatch()
        mp.setenv("ENVIRONMENT", "dev")
        mp.setenv("SENPAI_RESEARCH_ENABLED", "true")
        mp.setenv("ADMIN_GROUP_NAME", "admin")
        mp.setenv("SENPAI_RESEARCH_TABLE", support.TABLE_NAME)
        mp.setenv("SENPAI_RESEARCH_WORKER_NAME", support.WORKER_NAME)
        mp.setenv("SENPAI_RESEARCH_DAILY_LIMIT", "20")
        mp.setenv("AWS_DEFAULT_REGION", "ap-northeast-1")
        try:
            with mock_aws():
                return body(Lab(mods, mp).open(), mp)
        finally:
            mp.undo()

    def answer(lab, _mp):
        accepted, final = lab.run(_answer_deps())
        out["post-accepted.json"], out["status-answer.json"] = accepted, final
        out["history-detail.json"] = _history_sample(lab, _load_chat_app)

    def clarify(lab, _mp):
        directive = _directive(sufficient=False, action="clarify",
                               clarifyQuestions=["機種は何ですか（AXIEZ・NEXCUBE など）", "異音はドアの開閉のどの位置で出ますか"])
        out["status-clarify.json"] = lab.run(FakeDeps(sufficiency=directive))[1]

    def not_found(lab, _mp):
        out["status-not-found.json"] = lab.run(FakeDeps(tech=lambda q, m: _retrieval(), cards=[]))[1]

    def failed(lab, _mp):
        out["status-failed-timeout.json"] = lab.run(FakeDeps(synth=ReadTimeoutError("read timeout")))[1]

    scenario(answer)
    scenario(lambda lab, mp: out.update(_mid_run_samples(lab)))
    scenario(clarify)
    scenario(not_found)
    scenario(failed)
    out["errors.json"] = scenario(_error_samples)
    return out


def _render(content) -> str:
    return json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def test_committed_samples_match_freshly_generated_output():
    generated = {name: _render(content) for name, content in generate_samples().items()}
    if os.environ.get(REGEN_ENV) == "1":
        SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        for name, text in generated.items():
            (SAMPLES_DIR / name).write_text(text, encoding="utf-8")
    committed = {path.name: path.read_text(encoding="utf-8") for path in SAMPLES_DIR.glob("*.json")}
    hint = (f"バックエンドの応答が変わりました。意図した変更なら {REGEN_ENV}=1 を付けて"
            " tests/unit/test_senpai_research_samples.py を実行してサンプルを作り直し、"
            "フロントの契約テストも合わせて直してください")
    assert set(committed) == set(generated), hint
    for name, text in generated.items():
        assert committed[name] == text, f"{name}: {hint}"


def test_samples_cover_the_contract_shapes():
    samples = generate_samples()
    running = samples["status-running.json"]["body"]
    assert running["status"] == "running" and running["pollAfterMs"] == 1500
    by_start = {}
    for step in running["steps"]:
        by_start.setdefault((step["step"], step["startedAt"]), []).append(step["status"])
    assert ["running", "done"] in by_start.values()
    assert ("retry_search", "running") in [(s["step"], s["status"]) for s in running["steps"]]
    assert running["steps"][-1]["status"] == "running" and running["steps"][-1]["endedAt"] is None
    answer = samples["status-answer.json"]["body"]
    assert answer["status"] == "completed" and answer["pollAfterMs"] == 0 and "debug" in answer
    knowhow = answer["result"]["sources"]["knowhow"]
    assert {c["modelFit"] for c in knowhow["used"]} >= {"matched", "other_product"}
    assert knowhow["candidates"] and answer["result"]["unverifiedRefs"] == ["T9"]
    assert samples["status-clarify.json"]["body"]["result"]["kind"] == "clarify"
    assert samples["status-not-found.json"]["body"]["result"]["kind"] == "not_found"
    assert samples["status-failed-timeout.json"]["body"]["error"]["code"] == "Timeout"
    messages = samples["history-detail.json"]["body"]["messages"]
    assert [(m["role"], m["ragMode"]) for m in messages] == [
        ("user", "senpai_research"), ("assistant", "senpai_research")]
    assert "researchResult" in messages[1]
