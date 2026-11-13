"""troubleshooting db-search Lambda: 工事番号なしと DynamoDB 障害の書き分け。"""
import importlib.util
import os
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

BASE = os.path.join(os.path.dirname(__file__), "../..")

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


db_search = _load("troubleshooting_db_search_app", "lambda/troubleshooting/db-search/app.py")


@pytest.fixture
def table(monkeypatch):
    mock_table = MagicMock()
    resource = MagicMock()
    resource.Table.return_value = mock_table
    monkeypatch.setattr(db_search, "dynamodb", resource)
    return mock_table


def _event(number="EIK54801"):
    return {
        "actionGroup": "db-search",
        "apiPath": "/site-info",
        "httpMethod": "GET",
        "parameters": {"constructionNumber": number},
    }


def test_missing_item_keeps_not_found_message(table):
    table.get_item.return_value = {}
    with pytest.raises(db_search.DBSearchError) as exc:
        db_search.query_dynamodb("EIK00000")
    assert "見つかりません" in str(exc.value)


def test_dynamodb_client_error_becomes_connection_failure(table):
    table.get_item.side_effect = ClientError(
        {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "x"}},
        "GetItem",
    )
    with pytest.raises(db_search.DBSearchError) as exc:
        db_search.query_dynamodb("EIK54801")
    assert "接続に失敗" in str(exc.value)


def test_existing_item_is_returned(table):
    item = {"constructionNumber": "EIK54801", "sitesName": "テスト現場"}
    table.get_item.return_value = {"Item": item}
    assert db_search.query_dynamodb("EIK54801") == item


def test_handler_reports_not_found_message(table):
    table.get_item.return_value = {}
    response = db_search.lambda_handler(_event("EIK00000"), None)
    body = response["response"]["responseBody"]["TEXT"]["body"]
    assert response["response"]["httpStatusCode"] == 400
    assert "見つかりません" in body
    assert "接続に失敗" not in body
