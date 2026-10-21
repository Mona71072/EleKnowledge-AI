"""工技先輩の調査ジョブ（試作）のテスト共通部品。テストは含まない。

rag-function 配下のモジュールは conftest の読み込み方式（importlib）で独立に読む。
各モジュールの兄弟モジュールは、読み込んだモジュールの属性（api.store など）から辿る。
"""
import json
import os
import time

import pytest

from conftest import _load_rag_module

USER_ID = "owner-1"
OTHER_USER_ID = "other-2"
CONVERSATION_ID = "11111111-1111-4111-8111-111111111111"
TURN_ID = "22222222-2222-4222-8222-222222222222"
CLIENT_REQUEST_ID = "33333333-3333-4333-8333-333333333333"
SECOND_CLIENT_REQUEST_ID = "44444444-4444-4444-8444-444444444444"
THIRD_CLIENT_REQUEST_ID = "55555555-5555-4555-8555-555555555555"
UNKNOWN_JOB_ID = "66666666-6666-4666-8666-666666666666"
QUESTION = "LINKsのドアが開閉時に異音。固有質問ZZZQ"
TABLE_NAME = "senpai-research-jobs-test"
WORKER_NAME = "senpai-research-worker-test"


def load_module(filename):
    """rag-function 配下のファイルを、テスト専用の名前で1回だけ読み込む。"""
    os.environ.setdefault("CHATLOGS_TABLE", "test-chatlogs")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
    stem = filename.removesuffix(".py")
    return _load_rag_module(f"{stem}_under_test", filename)


class FakeClock:
    """進められる時計（秒）。DynamoDB の期限判定とテストの経過時間に使う。"""

    def __init__(self, start=1_800_000_000.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def make_jobs_table(boto3, name=TABLE_NAME):
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    return dynamodb.create_table(
        TableName=name,
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def make_chatlogs_table(boto3, name="research-chatlogs"):
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    return dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {"AttributeName": "sessionId", "KeyType": "HASH"},
            {"AttributeName": "messageId", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": n, "AttributeType": "S"}
            for n in ("sessionId", "messageId", "userId", "timestamp")
        ],
        GlobalSecondaryIndexes=[{
            "IndexName": "userId-timestamp-index",
            "KeySchema": [
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }],
        BillingMode="PAY_PER_REQUEST",
    )


def api_event(body=None, *, method="POST", sub=USER_ID, groups="admin", job_id=None,
              query=None, raw_body=None):
    claims = {}
    if sub is not None:
        claims["sub"] = sub
    if groups is not None:
        claims["cognito:groups"] = groups
    event = {
        "httpMethod": method,
        "path": "/rag/senpai/research" + (f"/{job_id}" if job_id else ""),
        "pathParameters": {"jobId": job_id} if job_id else None,
        "queryStringParameters": query,
        "requestContext": {"authorizer": {"claims": claims}},
    }
    if method == "POST":
        event["body"] = raw_body if raw_body is not None else json.dumps(
            body if body is not None else valid_body()
        )
    return event


def valid_body(**overrides):
    body = {
        "question": QUESTION,
        "senpaiConversationId": CONVERSATION_ID,
        "senpaiTurnId": TURN_ID,
        "clientRequestId": CLIENT_REQUEST_ID,
    }
    body.update(overrides)
    return {key: value for key, value in body.items() if value is not None}


def body_of(response):
    return json.loads(response["body"] or "null")


@pytest.fixture
def research_env(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("SENPAI_RESEARCH_ENABLED", "true")
    monkeypatch.setenv("ADMIN_GROUP_NAME", "admin")
    monkeypatch.setenv("SENPAI_RESEARCH_TABLE", TABLE_NAME)
    monkeypatch.setenv("SENPAI_RESEARCH_WORKER_NAME", WORKER_NAME)
    monkeypatch.setenv("SENPAI_RESEARCH_DAILY_LIMIT", "20")
    monkeypatch.delenv("SENPAI_RESEARCH_JOB_TTL_SECONDS", raising=False)


def wall_clock():
    return time.time()
