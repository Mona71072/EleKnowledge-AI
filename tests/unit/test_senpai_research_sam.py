"""調査ジョブ（試作）の SAM 定義: 既定オフ・dev 限定・最小権限・上限値の契約テスト。"""
import json

import pytest

RESOURCES = (
    "SenpaiResearchJobsTable", "SenpaiResearchApiLambdaRole", "SenpaiResearchApiFunction",
    "SenpaiResearchWorkerLambdaRole", "SenpaiResearchWorkerFunction",
)


@pytest.fixture(scope="module")
def template():
    from test_iam_function_permissions import _template
    return _template("phase2-template.yaml")


def _function(template, name):
    return template["Resources"][name]["Properties"]


def _actions(template, function_name):
    from test_iam_function_permissions import _policies, _policy_actions, _role_for_function
    role = _role_for_function(template, function_name)
    return _policy_actions(_policies(template, role))


# ---------------------------------------------------------------- パラメータと条件

def test_parameters_are_off_by_default_with_documented_limits(template):
    params = template["Parameters"]
    assert params["SenpaiResearchEnabled"]["Default"] == "false"
    assert params["SenpaiResearchEnabled"]["AllowedValues"] == ["true", "false"]
    assert int(params["SenpaiResearchDailyLimit"]["Default"]) == 20
    assert int(params["SenpaiResearchMaxSearches"]["Default"]) == 18
    assert int(params["SenpaiResearchMaxModelCalls"]["Default"]) == 10
    assert int(params["SenpaiResearchJobBudgetMs"]["Default"]) == 90000
    for name in ("SenpaiResearchDailyLimit", "SenpaiResearchMaxSearches",
                 "SenpaiResearchMaxModelCalls", "SenpaiResearchJobBudgetMs"):
        assert "MinValue" in params[name] and "MaxValue" in params[name], name
    assert params["SenpaiUnderstandModelId"]["Default"] == ""
    assert params["SenpaiUnderstandModelIdType"]["Default"] == "system-profile"
    # 整理用モデルも BedrockModelId と同じ形式に限る（IAM をこの値から組み立てるため）
    assert params["SenpaiUnderstandModelId"]["AllowedPattern"] == params["QueryRewriteModelId"]["AllowedPattern"]


def test_condition_requires_dev_and_the_flag(template):
    condition = template["Conditions"]["SenpaiResearchDevEnabled"]
    text = json.dumps(condition)
    assert "Environment" in text and "dev" in text and "SenpaiResearchEnabled" in text and "true" in text


def test_all_resources_and_outputs_are_conditional(template):
    # SECURITY: 本番や無効時に、経路・表・Bedrock/KB 権限つきロールを作らない。
    for name in RESOURCES:
        assert template["Resources"][name].get("Condition") == "SenpaiResearchDevEnabled", name
    for name in ("SenpaiResearchApiFunctionArn", "SenpaiResearchWorkerFunctionArn"):
        assert template["Outputs"][name].get("Condition") == "SenpaiResearchDevEnabled", name


# ---------------------------------------------------------------- 表

def test_jobs_table_is_ttl_encrypted_and_has_no_secondary_index(template):
    table = _function(template, "SenpaiResearchJobsTable")
    assert table["BillingMode"] == "PAY_PER_REQUEST"
    assert [(k["AttributeName"], k["KeyType"]) for k in table["KeySchema"]] == [("pk", "HASH")]
    assert table["TimeToLiveSpecification"] == {"Enabled": True, "AttributeName": "ttl"}
    assert table["SSESpecification"]["SSEEnabled"] is True
    assert "GlobalSecondaryIndexes" not in table


# ---------------------------------------------------------------- 受付 Lambda

def test_api_function_routes_env_and_timeout(template):
    function = _function(template, "SenpaiResearchApiFunction")
    assert function["CodeUri"] == "../../lambda/rag/rag-function/"
    assert function["Handler"] == "senpai_research_api.lambda_handler"
    routes = {(e["Properties"]["Method"], e["Properties"]["Path"]) for e in function["Events"].values()}
    assert routes == {("POST", "/rag/senpai/research"), ("GET", "/rag/senpai/research/{jobId}")}
    for event in function["Events"].values():
        assert event["Properties"]["RestApiId"] == "RagApi"
        assert "Auth" not in event["Properties"]  # 既定の Cognito 認可が適用される
    env = function["Environment"]["Variables"]
    assert env["ENVIRONMENT"] == "Environment" and env["ADMIN_GROUP_NAME"] == "admin"
    assert env["SENPAI_RESEARCH_ENABLED"] == "true"
    assert env["SENPAI_RESEARCH_DAILY_LIMIT"] == "SenpaiResearchDailyLimit"
    assert env["SENPAI_RESEARCH_TABLE"] == "SenpaiResearchJobsTable"
    assert env["SENPAI_RESEARCH_WORKER_NAME"] == "SenpaiResearchWorkerFunction"
    assert int(function["Timeout"]) < 29  # API Gateway の統合タイムアウト以内
    assert "BEDROCK_MODEL_ID" not in env  # 受付は生成しない


def test_api_role_is_minimal(template):
    actions = _actions(template, "SenpaiResearchApiFunction")
    assert actions == {"dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem",
                       "dynamodb:DeleteItem", "lambda:InvokeFunction"}
    from test_iam_function_permissions import _policies, _role_for_function
    policies = json.dumps(_policies(template, _role_for_function(template, "SenpaiResearchApiFunction")))
    # 起動できるのは調査ワーカーだけ
    assert "SenpaiResearchWorkerFunction" in policies
    assert "SenpaiResearchJobsTable" in policies
    assert "ChatLogs" not in policies and "bedrock" not in policies


# ---------------------------------------------------------------- ワーカー Lambda

def test_worker_function_is_async_only_with_no_retry_and_180s_timeout(template):
    function = _function(template, "SenpaiResearchWorkerFunction")
    assert function["CodeUri"] == "../../lambda/rag/rag-function/"
    assert function["Handler"] == "senpai_research_worker.lambda_handler"
    assert "Events" not in function  # API から直接は呼べない
    assert int(function["Timeout"]) == 180
    assert function["EventInvokeConfig"]["MaximumRetryAttempts"] == 0
    assert function["Role"] != _function(template, "SenpaiResearchApiFunction")["Role"]


def test_worker_env_mirrors_rag_function_and_adds_research_settings(template):
    env = _function(template, "SenpaiResearchWorkerFunction")["Environment"]["Variables"]
    rag_env = _function(template, "RagFunction")["Environment"]["Variables"]
    for key in ("KNOWLEDGE_BASE_ID", "LAW_KNOWLEDGE_BASE_ID", "LAW_RAG_ENABLED", "KNOWHOW_ENABLED",
                "KNOWHOW_INDEX_BUCKET", "KNOWHOW_INDEX_KEY", "BEDROCK_MODEL_ID", "KB_PROFILE_JSON",
                "MODEL_PROFILE_JSON", "RAG_SEARCH_TYPE", "KB_SOURCE_BUCKET", "KB_SOURCE_PREFIX",
                "CHATLOGS_TABLE", "DOCUMENTS_BUCKET", "LAW_DATA_BUCKET_NAME", "LAW_DATA_BUCKET_OWNER",
                "CITATION_URI_MODE", "GENERATION_THINKING", "GENERATION_EFFORT", "ENVIRONMENT"):
        assert env[key] == rag_env[key], key
    assert "RERANK_MODEL_ARN" not in env and "QUERY_REWRITE_MODEL_ID" not in env  # 試作では使わない
    assert env["SENPAI_RESEARCH_TABLE"] == "SenpaiResearchJobsTable"
    assert env["SENPAI_UNDERSTAND_MODEL_ID"] == "SenpaiUnderstandModelId"
    assert env["SENPAI_RESEARCH_MAX_SEARCHES"] == "SenpaiResearchMaxSearches"
    assert env["SENPAI_RESEARCH_MAX_MODEL_CALLS"] == "SenpaiResearchMaxModelCalls"
    assert env["SENPAI_RESEARCH_JOB_BUDGET_MS"] == "SenpaiResearchJobBudgetMs"
    # Bedrock の読み取り待ちは、ジョブ全体の上限より十分短く、Lambda の Timeout 内に収める
    assert int(env["BEDROCK_READ_TIMEOUT"]) < 60
    assert int(env["BEDROCK_MAX_ATTEMPTS"]) == 0


def test_queue_worker_lock_and_polling_bounds_are_consistent(template, monkeypatch):
    import re
    from pathlib import Path
    import test_senpai_research_support as support
    config = support.load_module('senpai_research_config.py')
    for name in list(__import__('os').environ):
        if name.startswith('SENPAI_RESEARCH_'):
            monkeypatch.delenv(name)
    worker = _function(template, 'SenpaiResearchWorkerFunction')
    api = _function(template, 'SenpaiResearchApiFunction')
    limits = config.load_limits()
    assert (limits.max_searches, limits.max_model_calls, limits.job_ms) == (18, 10, 90000)
    params = template['Parameters']
    for param, attr in [('SenpaiResearchMaxSearches', 'max_searches'),
                        ('SenpaiResearchMaxModelCalls', 'max_model_calls'),
                        ('SenpaiResearchJobBudgetMs', 'job_ms'), ('SenpaiResearchMaxInputBytes', 'max_input_bytes'),
                        ('SenpaiResearchNoProgressLimit', 'no_progress_limit')]:
        assert int(params[param]['Default']) == getattr(limits, attr)
    lock = int(api['Environment']['Variables']['SENPAI_RESEARCH_JOB_TTL_SECONDS'])
    queue = worker['EventInvokeConfig']['MaximumEventAgeInSeconds']
    assert queue + worker['Timeout'] + 30 <= lock == config.job_ttl_seconds()
    assert params['SenpaiResearchJobBudgetMs']['MaxValue'] / 1000 + 45 + 30 <= worker['Timeout']
    polling = (Path(__file__).resolve().parents[2] / 'frontend/src/lib/research-polling.mjs').read_text(encoding='utf-8')
    poll_ms = int(re.search(r'POLL_GIVE_UP_MS = (\d+)', polling).group(1))
    assert (lock + 30) * 1000 <= poll_ms
    monkeypatch.setenv('SENPAI_RESEARCH_JOB_TTL_SECONDS', '1')
    monkeypatch.setenv('SENPAI_RESEARCH_JOB_BUDGET_MS', '999999')
    assert config.job_ttl_seconds() == lock
    assert config.load_limits().job_ms == params['SenpaiResearchJobBudgetMs']['MaxValue']


def test_worker_role_is_least_privilege(template):
    actions = _actions(template, "SenpaiResearchWorkerFunction")
    assert actions == {
        "bedrock:Retrieve", "bedrock:InvokeModel",
        "dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:PutItem",
        "s3:GetObject", "kms:Decrypt",
    }
    assert not any(a.endswith(("Scan", "Query")) for a in actions)
    assert "lambda:InvokeFunction" not in actions and "bedrock:Rerank" not in actions


def test_worker_policies_are_scoped_to_their_resources(template):
    from test_iam_function_permissions import _policies, _role_for_function
    text = json.dumps(_policies(template, _role_for_function(template, "SenpaiResearchWorkerFunction")))
    # ジョブ表・ChatLogs への書き込み先、ノウハウ索引の1オブジェクト、法令の読み取り範囲
    assert "SenpaiResearchJobsTable" in text and "ChatLogsTableArn" in text
    assert "KnowhowIndexKey" in text and "LawDataBucketName" in text
    # 整理用モデルは設定されたときだけ許可される
    assert "HasSenpaiUnderstandModelId" in text and "SenpaiUnderstandModelId" in text
    # 文書バケット・KB データソースバケットは読めない（出典の署名 URL を作らないため）
    assert "DocumentsBucketName" not in text and "KnowledgeBaseDataSourceBucket" not in text


def test_chatlogs_access_is_put_only(template):
    from test_iam_function_permissions import _policies, _role_for_function
    policies = _policies(template, _role_for_function(template, "SenpaiResearchWorkerFunction"))
    chat = [p for p in policies if isinstance(p, dict) and p.get("PolicyName") == "ChatLogsPut"]
    assert len(chat) == 1
    statements = chat[0]["PolicyDocument"]["Statement"]
    assert [s["Action"] for s in statements] == [["dynamodb:PutItem"]] or [s["Action"] for s in statements] == ["dynamodb:PutItem"]


def test_rag_function_and_other_roles_are_untouched(template):
    rag_env = _function(template, "RagFunction")["Environment"]["Variables"]
    assert not any(key.startswith("SENPAI_RESEARCH") for key in rag_env)
    assert not any(key.startswith("SENPAI_RESEARCH") for key in
                   _function(template, "ChatManagementFunction")["Environment"]["Variables"])


# ---------------------------------------------------------------- 堅牢化（監査 F1 / F2）

def test_job_lease_covers_async_event_age_plus_worker_timeout(template):
    api_env = _function(template, "SenpaiResearchApiFunction")["Environment"]["Variables"]
    worker = _function(template, "SenpaiResearchWorkerFunction")
    needed = int(worker["EventInvokeConfig"]["MaximumEventAgeInSeconds"]) + int(worker["Timeout"])
    assert int(api_env["SENPAI_RESEARCH_JOB_TTL_SECONDS"]) >= needed


def test_worker_waits_are_bounded_below_the_job_budget(template):
    env = _function(template, "SenpaiResearchWorkerFunction")["Environment"]["Variables"]
    assert 3 <= int(env["SENPAI_RESEARCH_KB_READ_TIMEOUT"]) <= 30
    assert 5 <= int(env["SENPAI_RESEARCH_MODEL_READ_TIMEOUT"]) <= 60
