"""authorizer Lambda のユニットテスト"""
import importlib.util
import os
import json
import time
import pytest
from unittest.mock import patch, MagicMock
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import jwt

BASE = os.path.join(os.path.dirname(__file__), "../..")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


authorizer = _load("authorizer_app", "lambda/troubleshooting/authorizer/app.py")

METHOD_ARN = "arn:aws:execute-api:us-east-1:123456789012:apiid/stage/POST/analyze"
APP_CLIENT_ID = "test-client-id"


def _gen_rsa_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    return private_key, private_key.public_key()


def _make_jwks(public_key, kid="test-kid"):
    pub_numbers = public_key.public_numbers()

    def _b64(n):
        import base64
        return base64.urlsafe_b64encode(
            n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
        ).rstrip(b"=").decode()

    return {
        "keys": [{
            "kty": "RSA",
            "use": "sig",
            "kid": kid,
            "alg": "RS256",
            "n": _b64(pub_numbers.n),
            "e": _b64(pub_numbers.e),
        }]
    }


def _make_token(private_key, sub="user-sub-001", kid="test-kid", exp_offset=3600, audience=APP_CLIENT_ID):
    return jwt.encode(
        {"sub": sub, "exp": int(time.time()) + exp_offset, "aud": audience},
        private_key,
        algorithm="RS256",
        headers={"kid": kid},
    )


# ---------------------------------------------------------------------------
# _build_policy
# ---------------------------------------------------------------------------

def test_build_policy_allow():
    policy = authorizer._build_policy("user-123", "Allow", METHOD_ARN, "user-123")
    assert policy["policyDocument"]["Statement"][0]["Effect"] == "Allow"
    assert policy["context"]["userId"] == "user-123"
    assert policy["principalId"] == "user-123"


def test_build_policy_deny():
    policy = authorizer._build_policy("unauthorized", "Deny", METHOD_ARN, "")
    assert policy["policyDocument"]["Statement"][0]["Effect"] == "Deny"
    assert policy["context"]["userId"] == ""


# ---------------------------------------------------------------------------
# lambda_handler — 異常系
# ---------------------------------------------------------------------------

def test_no_token_returns_deny():
    event = {"authorizationToken": "", "methodArn": METHOD_ARN}
    result = authorizer.lambda_handler(event, None)
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Deny"


def test_invalid_token_returns_deny(mocker):
    private_key, public_key = _gen_rsa_keypair()
    jwks = _make_jwks(public_key)
    mocker.patch.object(authorizer, "_get_jwks", return_value=jwks)
    authorizer.APP_CLIENT_ID = APP_CLIENT_ID

    event = {"authorizationToken": "Bearer not.a.jwt.token", "methodArn": METHOD_ARN}
    result = authorizer.lambda_handler(event, None)
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Deny"


def test_expired_token_returns_deny(mocker):
    private_key, public_key = _gen_rsa_keypair()
    jwks = _make_jwks(public_key)
    mocker.patch.object(authorizer, "_get_jwks", return_value=jwks)
    authorizer.APP_CLIENT_ID = APP_CLIENT_ID

    token = _make_token(private_key, exp_offset=-3600)
    event = {"authorizationToken": f"Bearer {token}", "methodArn": METHOD_ARN}
    result = authorizer.lambda_handler(event, None)
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Deny"


def test_unknown_kid_returns_deny(mocker):
    private_key, public_key = _gen_rsa_keypair()
    jwks = _make_jwks(public_key, kid="known-kid")
    mocker.patch.object(authorizer, "_get_jwks", return_value=jwks)
    authorizer.APP_CLIENT_ID = APP_CLIENT_ID

    token = _make_token(private_key, kid="unknown-kid")
    event = {"authorizationToken": f"Bearer {token}", "methodArn": METHOD_ARN}
    result = authorizer.lambda_handler(event, None)
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Deny"


# ---------------------------------------------------------------------------
# lambda_handler — 正常系
# ---------------------------------------------------------------------------

def test_valid_token_returns_allow_with_user_id(mocker):
    private_key, public_key = _gen_rsa_keypair()
    jwks = _make_jwks(public_key)
    mocker.patch.object(authorizer, "_get_jwks", return_value=jwks)
    authorizer.APP_CLIENT_ID = APP_CLIENT_ID

    token = _make_token(private_key, sub="user-sub-999")
    event = {"authorizationToken": f"Bearer {token}", "methodArn": METHOD_ARN}
    result = authorizer.lambda_handler(event, None)

    assert result["policyDocument"]["Statement"][0]["Effect"] == "Allow"
    assert result["context"]["userId"] == "user-sub-999"
    assert result["principalId"] == "user-sub-999"
