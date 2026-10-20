"""認証 Lambda のリクエスト本文検証テスト。"""
import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

import pytest


BASE = Path(__file__).resolve().parents[2]
AUTH_CASES = {
    "login": {"email": "user@example.com", "password": "Secret123!"},
    "signup": {"email": "user@example.com", "password": "Secret123!"},
    "verify": {"email": "user@example.com", "code": "123456"},
}
INVALID_BODIES = [
    pytest.param("{", id="malformed-json"),
    pytest.param("[]", id="json-array"),
    pytest.param('"private-body-sentinel"', id="json-string"),
    pytest.param({"email": 123, "password": "Secret123!", "code": "123456"}, id="numeric-email"),
]


def _load_auth_app(name):
    app_path = BASE / "lambda" / "auth" / name / "app.py"
    spec = importlib.util.spec_from_file_location(f"auth_{name}_under_test", app_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, {
        "COGNITO_USER_POOL_ID": "test-pool",
        "COGNITO_CLIENT_ID": "test-client",
        "USERS_TABLE": "test-users",
    }), patch("boto3.client", return_value=MagicMock()) as client_factory, patch(
        "boto3.resource", return_value=MagicMock()
    ):
        spec.loader.exec_module(module)
    module.cognito_client = client_factory.return_value
    return module


@pytest.mark.parametrize("handler_name", AUTH_CASES)
@pytest.mark.parametrize("body", INVALID_BODIES)
def test_invalid_json_or_field_types_return_validation_error(handler_name, body, caplog):
    module = _load_auth_app(handler_name)
    event_body = body if isinstance(body, str) else json.dumps(body)

    response = module.lambda_handler({"body": event_body}, None)

    assert response["statusCode"] == 400
    payload = json.loads(response["body"])
    assert payload["error"] == "ValidationError"
    assert payload["message"] == "Request body is invalid"
    assert module.cognito_client.mock_calls == []
    assert "private-body-sentinel" not in caplog.text
    assert "user@example.com" not in caplog.text
    assert "Secret123!" not in caplog.text
    assert caplog.records
    assert all(
        json.loads(record.message)["event"] == "auth_request_validation_failed"
        for record in caplog.records
    )


@pytest.mark.parametrize("handler_name", AUTH_CASES)
def test_missing_required_fields_return_validation_error(handler_name):
    module = _load_auth_app(handler_name)

    response = module.lambda_handler({"body": "{}"}, None)

    assert response["statusCode"] == 400
    assert json.loads(response["body"])["error"] == "ValidationError"
    assert module.cognito_client.mock_calls == []


@pytest.mark.parametrize("handler_name,body", [
    ("login", {"email": "user@example.com", "password": 123}),
    ("signup", {"email": "user@example.com", "password": 123}),
    ("verify", {"email": "user@example.com", "code": 123}),
])
def test_numeric_required_secret_returns_validation_error(handler_name, body):
    module = _load_auth_app(handler_name)

    response = module.lambda_handler({"body": json.dumps(body)}, None)

    assert response["statusCode"] == 400
    assert json.loads(response["body"])["error"] == "ValidationError"
    assert module.cognito_client.mock_calls == []


def test_optional_name_must_be_a_string():
    module = _load_auth_app("signup")
    body = {**AUTH_CASES["signup"], "name": 42}

    response = module.lambda_handler({"body": json.dumps(body)}, None)

    assert response["statusCode"] == 400
    assert json.loads(response["body"])["error"] == "ValidationError"
    assert module.cognito_client.mock_calls == []


def test_unknown_cognito_error_does_not_leak_provider_message():
    module = _load_auth_app("login")
    module.cognito_client.initiate_auth.side_effect = ClientError(
        {"Error": {"Code": "InternalErrorException", "Message": "secret-cognito-detail"}},
        "InitiateAuth",
    )

    response = module.lambda_handler({"body": json.dumps(AUTH_CASES["login"])}, None)

    assert response["statusCode"] == 500
    payload = json.loads(response["body"])
    assert payload["error"] == "InternalServerError"
    assert "secret-cognito-detail" not in response["body"]
    assert "InternalErrorException" not in response["body"]
