"""The RAG research mode is dev-only, off by default, and role-separated."""

import json

import pytest


@pytest.fixture(scope="module")
def template():
    from test_iam_function_permissions import _template
    return _template("research-itai-template.yaml")


def _function(template, name):
    return template["Resources"][name]["Properties"]


def _actions(template, function_name):
    from test_iam_function_permissions import _policies, _policy_actions, _role_for_function
    role = _role_for_function(template, function_name)
    return _policy_actions(_policies(template, role))


def test_gateway_errors_have_cors_without_changing_auth_or_status(template):
    api = _function(template, "ResearchApi")
    for response_type in ("DEFAULT_4XX", "DEFAULT_5XX"):
        response = api["GatewayResponses"][response_type]
        assert "StatusCode" not in response
        headers = response["ResponseParameters"]["Headers"]
        assert headers["Access-Control-Allow-Origin"] == api["Cors"]["AllowOrigin"]
        assert headers["Access-Control-Allow-Headers"] == api["Cors"]["AllowHeaders"]
    assert api["Auth"]["DefaultAuthorizer"] == "CognitoAuthorizer"
    assert api["Auth"]["AddDefaultAuthorizerToCorsPreflight"] is False
    assert api["Auth"]["ResourcePolicy"]["IpRangeWhitelist"] == "AllowedIPList"


def test_research_mode_is_off_by_default_and_resources_are_dev_conditional(template):
    parameter = template["Parameters"]["ResearchModeEnabled"]
    assert parameter["Default"] == "off"
    assert parameter["AllowedValues"] == ["off", "beta", "on"]
    condition = json.dumps(template["Conditions"]["ResearchEnabled"])
    assert "Environment" in condition and "dev" in condition
    assert "ResearchModeEnabled" in condition and "off" in condition

    for name in (
        "ResearchJobsTable", "ResearchFailureQueue", "ResearchApiRole",
        "ResearchWorkerRole", "ResearchApiFunction", "ResearchWorker",
        "ResearchApi", "ResearchApiWebAclAssociation",
    ):
        assert template["Resources"][name]["Condition"] == "ResearchEnabled"


def test_jobs_table_has_expiry_and_user_session_index(template):
    table = _function(template, "ResearchJobsTable")
    assert table["BillingMode"] == "PAY_PER_REQUEST"
    assert table["KeySchema"] == [{"AttributeName": "pk", "KeyType": "HASH"}]
    assert table["TimeToLiveSpecification"] == {"AttributeName": "ttl", "Enabled": True}
    assert table["SSESpecification"]["SSEEnabled"] is True
    index = table["GlobalSecondaryIndexes"][0]
    assert index["IndexName"] == "userId-createdAt-index"
    assert [key["AttributeName"] for key in index["KeySchema"]] == ["userId", "createdAt"]


def test_api_routes_and_role_are_separate_from_bedrock_worker(template):
    api = _function(template, "ResearchApiFunction")
    routes = {(event["Properties"]["Method"], event["Properties"]["Path"])
              for event in api["Events"].values()}
    assert routes == {
        ("POST", "/rag/research"),
        ("GET", "/rag/research/{jobId}"),
        ("GET", "/rag/research"),
        ("GET", "/rag/research/quota"),
    }
    assert "BedrockModelId" not in api["Environment"]["Variables"]
    assert "bedrock:InvokeModel" not in _actions(template, "ResearchApiFunction")
    assert "bedrock:Retrieve" not in _actions(template, "ResearchApiFunction")
    assert "lambda:InvokeFunction" in _actions(template, "ResearchApiFunction")
    assert {"dynamodb:TransactWriteItems", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem"}.issubset(
        _actions(template, "ResearchApiFunction")
    )
    assert all(event["Properties"]["RestApiId"] == "ResearchApi" for event in api["Events"].values())


def test_worker_is_async_only_bounded_and_has_failure_destination(template):
    worker = _function(template, "ResearchWorker")
    assert worker["Handler"] == "research_worker.lambda_handler"
    assert "Events" not in worker
    assert worker["ReservedConcurrentExecutions"] == "WorkerReservedConcurrency"
    assert worker["EventInvokeConfig"]["MaximumRetryAttempts"] == 0
    assert worker["EventInvokeConfig"]["MaximumEventAgeInSeconds"] == 120
    destination = worker["EventInvokeConfig"]["DestinationConfig"]["OnFailure"]
    assert destination["Type"] == "SQS"
    assert destination["Destination"] == "ResearchFailureQueue.Arn"
    actions = _actions(template, "ResearchWorker")
    assert {
        "bedrock:Retrieve", "bedrock:InvokeModel", "sqs:SendMessage",
        "dynamodb:TransactWriteItems", "dynamodb:PutItem", "dynamodb:UpdateItem",
        "dynamodb:DeleteItem", "dynamodb:ConditionCheckItem",
    }.issubset(actions)
    assert "dynamodb:Scan" not in actions
    assert "lambda:InvokeFunction" not in actions