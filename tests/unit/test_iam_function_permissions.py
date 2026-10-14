"""SAM の Lambda 実行ロールが機能ごとの権限境界を保つことを確認する。"""

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


class CloudFormationLoader(yaml.SafeLoader):
    """CloudFormation intrinsic tag の内容を通常の YAML 値として読み込む。"""


def _construct_tagged_value(loader, _tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


CloudFormationLoader.add_multi_constructor("!", _construct_tagged_value)


def _template(name):
    path = ROOT / "infrastructure" / "sam" / name
    return yaml.load(path.read_text(), Loader=CloudFormationLoader)


def _role_for_function(template, function_name):
    role = template["Resources"][function_name]["Properties"]["Role"]
    return role.split(".")[0]


def _policies(template, role_name):
    return template["Resources"][role_name]["Properties"].get("Policies", [])


def _policy_actions(policies):
    actions = set()

    def collect(value):
        if isinstance(value, list):
            for item in value:
                collect(item)
        elif isinstance(value, dict):
            if "PolicyDocument" in value:
                collect(value["PolicyDocument"].get("Statement", []))
            elif "Action" in value:
                action = value["Action"]
                actions.update(action if isinstance(action, list) else [action])
            else:
                for item in value.values():
                    collect(item)

    collect(policies)
    return actions


def _find_policy(policies, policy_name):
    if isinstance(policies, list):
        for policy in policies:
            found = _find_policy(policy, policy_name)
            if found:
                return found
    elif isinstance(policies, dict):
        if policies.get("PolicyName") == policy_name:
            return policies
        for value in policies.values():
            found = _find_policy(value, policy_name)
            if found:
                return found
    return None


def _policy_statements(policies):
    statements = []
    if isinstance(policies, list):
        for policy in policies:
            statements.extend(_policy_statements(policy))
    elif isinstance(policies, dict):
        if "PolicyDocument" in policies:
            statements.extend(_policy_statements(policies["PolicyDocument"].get("Statement", [])))
        elif "Action" in policies:
            statements.append(policies)
        else:
            for value in policies.values():
                statements.extend(_policy_statements(value))
    return statements


def test_auth_functions_have_only_their_users_table_operations():
    template = _template("phase1-template.yaml")
    resources = template["Resources"]

    signup_role = _role_for_function(template, "SignupFunction")
    login_role = _role_for_function(template, "LoginFunction")
    verify_role = _role_for_function(template, "VerifyFunction")

    assert len({signup_role, login_role, verify_role}) == 3
    assert _policy_actions(_policies(template, signup_role)) == {"dynamodb:PutItem"}
    assert _policy_actions(_policies(template, login_role)) == {"dynamodb:UpdateItem"}
    assert _policy_actions(_policies(template, verify_role)) == set()
    for role_name in (signup_role, login_role, verify_role):
        properties = resources[role_name]["Properties"]
        assert properties["ManagedPolicyArns"] == [
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        ]
        assert "ChatLogsTable" not in str(properties.get("Policies", []))
        assert "s3:" not in str(properties.get("Policies", []))
        assert "cognito-idp:" not in str(properties.get("Policies", []))

    signup_resources = resources[signup_role]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"][0]["Resource"]
    login_resources = resources[login_role]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"][0]["Resource"]
    assert signup_resources == login_resources == ["UsersTable.Arn"]


def test_rag_deployments_require_a_reviewed_source_version():
    import re

    template = _template("phase2-template.yaml")
    version = template["Parameters"]["RagLogicVersion"]
    assert "Default" not in version
    assert re.fullmatch(version["AllowedPattern"], "b9188925")
    assert not re.fullmatch(version["AllowedPattern"], "unknown")
    assert not re.fullmatch(version["AllowedPattern"], "main")
    env = template["Resources"]["RagFunction"]["Properties"]["Environment"]["Variables"]
    assert env["RAG_LOGIC_VERSION"] == "RagLogicVersion"


def test_rag_and_chat_roles_are_separate_and_restrict_api_actions():
    template = _template("phase2-template.yaml")
    rag_role = _role_for_function(template, "RagFunction")
    chat_role = _role_for_function(template, "ChatManagementFunction")

    assert rag_role != chat_role
    rag_actions = _policy_actions(_policies(template, rag_role))
    chat_actions = _policy_actions(_policies(template, chat_role))

    assert rag_actions == {
        "bedrock:Retrieve", "bedrock:InvokeModel", "bedrock:Rerank",
        "lambda:InvokeFunction", "dynamodb:PutItem", "dynamodb:UpdateItem",
        "dynamodb:Query", "s3:GetObject", "kms:Decrypt",
    }
    kms_statements = [
        statement
        for statement in _policy_statements(_policies(template, rag_role))
        if statement.get("Action") == "kms:Decrypt"
    ]
    assert len(kms_statements) == 1
    assert kms_statements[0]["Resource"] == "LawDataBucketKmsKeyArn"
    assert kms_statements[0]["Condition"]["StringEquals"]["kms:ViaService"] == "s3.${AWS::Region}.amazonaws.com"
    assert "LawFullTextDevEnabled" in str(_policies(template, rag_role))
    # kms:Decrypt は顧客管理キー指定時だけ。AWS 管理キー（空指定）では GetObject のみ
    kms_condition = template["Conditions"]["HasLawDataBucketKmsKey"]
    assert kms_condition[0] == "LawFullTextDevEnabled"
    assert "LawDataBucketKmsKeyArn" in str(kms_condition)
    assert "LawDataBucketKmsKeyArn" not in str(template["Conditions"]["LawFullTextDevEnabled"])
    assert "HasLawDataBucketKmsKey" in str(_policies(template, rag_role))
    rerank_policy = _find_policy(_policies(template, rag_role), "RerankAccess")
    assert rerank_policy is not None
    rerank_policy = rerank_policy["PolicyDocument"]["Statement"][0]
    assert rerank_policy["Resource"] == "*"

    rag_statements = _policy_statements(_policies(template, rag_role))
    rag_resources = [statement.get("Resource") for statement in rag_statements]
    assert all(
        resource != "*" or statement.get("Action") == ["bedrock:Rerank"]
        for statement in rag_statements
        for resource in [statement.get("Resource")]
    )
    assert any("knowledge-base/${KnowledgeBaseId}" in str(resource) for resource in rag_resources)
    assert any("${KnowledgeBaseSourcePrefix}*" in str(resource) for resource in rag_resources)
    assert all("/index/" not in str(resource) for resource in rag_resources)

    assert chat_actions == {
        "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query", "dynamodb:Scan"
    }
    assert not any(action.startswith("bedrock:") or action.startswith("s3:") or action.startswith("lambda:") for action in chat_actions)
    chat_statements = _policy_statements(_policies(template, chat_role))
    table_arn = "ChatLogsTableArn"
    index_arn = "${TableArn}/index/userId-timestamp-index"
    assert all(statement.get("Resource") != "*" for statement in chat_statements)
    assert any("Scan" in str(statement.get("Action")) and table_arn in str(statement.get("Resource")) for statement in chat_statements)
    table_query = next(
        statement for statement in chat_statements
        if "dynamodb:Query" in statement.get("Action", [])
        and isinstance(statement.get("Resource"), list)
        and any(isinstance(resource, dict) and "Fn::ImportValue" in resource for resource in statement["Resource"])
    )
    index_query = next(
        statement for statement in chat_statements
        if statement.get("Action") == ["dynamodb:Query"]
        and index_arn in str(statement.get("Resource"))
    )
    assert set(table_query["Action"]) == {
        "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query", "dynamodb:Scan"
    }
    assert table_query["Resource"] == [{"Fn::ImportValue": "${ProjectName}-${Environment}-ChatLogsTableArn"}]
    assert index_arn in str(index_query["Resource"])
    assert all(index_arn not in str(statement.get("Resource")) for statement in chat_statements if statement.get("Action") != ["dynamodb:Query"])

    rag_policy_names = {policy["PolicyName"] for policy in _policies(template, rag_role) if isinstance(policy, dict)}
    chat_policy_names = {policy["PolicyName"] for policy in _policies(template, chat_role) if isinstance(policy, dict)}
    assert "InvokeSelfForSessionTitle" in rag_policy_names
    assert "InvokeSelfForSessionTitle" not in chat_policy_names


def test_rag_invoke_model_is_limited_to_configured_models():
    template = _template("phase2-template.yaml")
    rag_role = _role_for_function(template, "RagFunction")
    invoke_statements = [
        statement for statement in _policy_statements(_policies(template, rag_role))
        if statement.get("Action") == ["bedrock:InvokeModel"]
    ]
    # !If は読み込み時に値の列へ展開されるため、Resource は文字列として確認する
    resources = [str(statement.get("Resource")) for statement in invoke_statements]
    joined = " ".join(resources)

    assert "inference-profile/*" not in joined
    assert "application-inference-profile/*" not in joined
    assert "arn:aws:bedrock:*::foundation-model/*" in joined
    assert "inference-profile/${BedrockModelId}" in joined
    assert "foundation-model/${FoundationModelId}" in joined
    assert "QueryRewriteModelId" in joined

    # 基盤モデルは推論プロファイル経由に限る。条件のない foundation-model 許可を作らない
    for statement in invoke_statements:
        if "foundation-model/" in str(statement.get("Resource")):
            assert "bedrock:InferenceProfileArn" in str(statement.get("Condition"))


def test_rag_model_id_types_are_refs_and_conditions_avoid_string_functions():
    template = _template("phase2-template.yaml")
    text = (ROOT / "infrastructure" / "sam" / "phase2-template.yaml").read_text()
    conditions_text = text[text.index("\nConditions:"):text.index("\nGlobals:")]

    # CloudFormation の Conditions では Fn::Select / Fn::Split を使えない
    assert "Select" not in conditions_text
    assert "Split" not in conditions_text

    parameters = template["Parameters"]
    for name in ("BedrockModelIdType", "QueryRewriteModelIdType"):
        assert parameters[name]["Default"] == "system-profile"
        assert parameters[name]["AllowedValues"] == ["system-profile", "application-profile"]

    conditions = template["Conditions"]
    assert conditions["BedrockModelIdIsApplicationProfile"] == [
        "BedrockModelIdType", "application-profile"
    ]
    assert conditions["QueryRewriteModelIdIsApplicationProfile"] == [
        "QueryRewriteModelIdType", "application-profile"
    ]


def test_bedrock_model_id_patterns_accept_configured_models_only():
    template = _template("phase2-template.yaml")
    parameters = template["Parameters"]
    model_pattern = re.compile(parameters["BedrockModelId"]["AllowedPattern"])
    rewrite_pattern = re.compile(parameters["QueryRewriteModelId"]["AllowedPattern"])

    for model_id in (
        "jp.anthropic.claude-haiku-4-5-20251001-v1:0",
        "global.anthropic.claude-sonnet-5",
        "global.openai.gpt-6-luna",
        "arn:aws:bedrock:ap-northeast-1:123456789012:application-inference-profile/abc123DEF",
    ):
        assert model_pattern.fullmatch(model_id), model_id
        assert rewrite_pattern.fullmatch(model_id), model_id
    assert rewrite_pattern.fullmatch("")

    # 基盤モデル ID（接頭辞なし）や区切りが余分な ID は組み立てられないため拒否する
    for model_id in ("anthropic.claude-haiku-4-5-20251001-v1:0", "global.anthropic.claude.sonnet", "*"):
        assert not model_pattern.fullmatch(model_id), model_id
        assert not rewrite_pattern.fullmatch(model_id), model_id


def test_archive_and_metrics_roles_match_their_data_paths():
    archive_template = _template("chat-archive-template.yaml")
    archive_role = _role_for_function(archive_template, "ArchiveFunction")
    archive_policies = _policies(archive_template, archive_role)
    archive_actions = _policy_actions(archive_policies)

    assert archive_actions == {
        "dynamodb:GetRecords", "dynamodb:GetShardIterator", "dynamodb:DescribeStream",
        "dynamodb:ListStreams", "s3:PutObject", "s3:ListBucket",
    }
    archive_s3 = next(
        statement for statement in _policy_statements(archive_policies)
        if statement.get("Action") == "s3:PutObject"
    )
    assert archive_s3["Resource"] == "arn:aws:s3:::${ArchiveBucket}/*"
    assert archive_s3["Condition"] == {
        "StringEquals": {"s3:ResourceAccount": "AWS::AccountId"}
    }
    archive_list = next(
        statement for statement in _policy_statements(archive_policies)
        if statement.get("Action") == "s3:ListBucket"
    )
    assert archive_list["Resource"] == "ArchiveBucket.Arn"

    metrics_template = _template("announcements-monitoring-template.yaml")
    aggregator_role = _role_for_function(metrics_template, "MetricsAggregatorFunction")
    reader_role = _role_for_function(metrics_template, "MetricsReadFunction")
    aggregator_actions = _policy_actions(_policies(metrics_template, aggregator_role))
    reader_actions = _policy_actions(_policies(metrics_template, reader_role))

    assert aggregator_actions == {
        "dynamodb:Scan", "dynamodb:Query", "dynamodb:PutItem",
        "cloudwatch:GetMetricStatistics", "cloudwatch:DescribeAlarmHistory",
        "ce:GetCostAndUsage", "ssm:GetParameter",
    }
    assert reader_actions == {
        "dynamodb:Query", "cloudwatch:DescribeAlarms",
        "cloudwatch:DescribeAlarmHistory", "cloudwatch:GetMetricData",
    }
    aggregator_statements = _policy_statements(_policies(metrics_template, aggregator_role))
    aggregator_scan = next(statement for statement in aggregator_statements if statement.get("Action") == ["dynamodb:Scan"])
    assert "/index/" not in str(aggregator_scan["Resource"])
    aggregator_query = next(statement for statement in aggregator_statements if statement.get("Action") == ["dynamodb:Query"])
    assert "index/userId-timestamp-index" in str(aggregator_query["Resource"])
    assert "index/*" not in str(aggregator_query["Resource"])
    assert "GetMetricData" not in aggregator_actions
    reader_statements = _policy_statements(_policies(metrics_template, reader_role))
    reader_queries = [statement for statement in reader_statements if statement.get("Action") == ["dynamodb:Query"]]
    assert len(reader_queries) == 2
    assert any(statement["Resource"] == ["${MetricsTable.Arn}/index/scope-metricDate-index"] for statement in reader_queries)
    assert any("index/status-publishAt-index" in str(statement["Resource"]) for statement in reader_queries)
    assert all("index/*" not in str(statement["Resource"]) for statement in reader_queries)
