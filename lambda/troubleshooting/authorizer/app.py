"""
Cognito JWT Lambda Authorizer
Bearer トークンを Cognito User Pool の公開鍵で検証し、userId (sub) を context に付与する。
"""
import json
import os
import urllib.request
from functools import lru_cache

import jwt  # PyJWT[crypto] >= 2.8

COGNITO_REGION = os.environ.get("COGNITO_REGION", "")
USER_POOL_ID = os.environ.get("USER_POOL_ID", "")
APP_CLIENT_ID = os.environ.get("APP_CLIENT_ID", "")
JWKS_URL = (
    f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com"
    f"/{USER_POOL_ID}/.well-known/jwks.json"
)


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    with urllib.request.urlopen(JWKS_URL, timeout=5) as resp:
        return json.loads(resp.read())


def _build_policy(principal_id: str, effect: str, method_arn: str, user_id: str) -> dict:
    # method_arn example: arn:aws:execute-api:ap-northeast-1:123:abc123/dev/POST/analyze
    # -> arn:aws:execute-api:ap-northeast-1:123:abc123/* applies to every endpoint.
    parts = method_arn.split("/")
    wildcard_arn = "/".join(parts[:2]) + "/*" if len(parts) >= 2 else method_arn
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": wildcard_arn,
                }
            ],
        },
        "context": {"userId": user_id},
    }


def lambda_handler(event, context):
    raw_token = event.get("authorizationToken", "")
    method_arn = event["methodArn"]

    token = raw_token.removeprefix("Bearer ").strip()
    if not token:
        return _build_policy("unauthorized", "Deny", method_arn, "")

    try:
        jwks = _get_jwks()
        header = jwt.get_unverified_header(token)
        key_data = next(k for k in jwks["keys"] if k["kid"] == header["kid"])
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data))
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
        )
        user_id = claims["sub"]
        return _build_policy(user_id, "Allow", method_arn, user_id)
    except StopIteration:
        # kid が JWKs に見つからない（古いトークン / 不正トークン）
        return _build_policy("unauthorized", "Deny", method_arn, "")
    except Exception:
        return _build_policy("unauthorized", "Deny", method_arn, "")
