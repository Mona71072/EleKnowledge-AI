"""kb-search1 / kb-search3 の write_citations() ユニットテスト
両 Lambda は同一の関数定義を持つため、kb-search1 を代表として使用する。
"""
import importlib.util
import os
import pytest
from unittest.mock import MagicMock

BASE = os.path.join(os.path.dirname(__file__), "../..")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kb_search = _load("kb_search1_app", "lambda/troubleshooting/kb-search1/app.py")


def _make_table_mock():
    table = MagicMock()
    table.update_item = MagicMock()
    return table


def _make_results(uris):
    return [
        {
            "content": "テスト内容",
            "score": 0.8,
            "location": {"s3Location": {"uri": uri}},
            "metadata": {"title": f"タイトル_{uri.split('/')[-1]}", "document": "Trouble-Cases", "model": "KE-LG"},
        }
        for uri in uris
    ]


# ---------------------------------------------------------------------------
# write_citations
# ---------------------------------------------------------------------------

def test_write_citations_calls_dynamodb(mocker):
    mock_table = _make_table_mock()
    mocker.patch.object(kb_search.dynamodb_resource, "Table", return_value=mock_table)

    results = _make_results(["s3://bucket/file.pdf"])
    kb_search.write_citations("session-001", results)

    mock_table.update_item.assert_called_once()
    call_kwargs = mock_table.update_item.call_args[1]
    citations = call_kwargs["ExpressionAttributeValues"][":c"]
    assert len(citations) == 1
    assert citations[0]["uri"] == "s3://bucket/file.pdf"
    assert citations[0]["document"] == "Trouble-Cases"


def test_write_citations_empty_session_id_skips(mocker):
    mock_table = _make_table_mock()
    mocker.patch.object(kb_search.dynamodb_resource, "Table", return_value=mock_table)

    kb_search.write_citations("", _make_results(["s3://bucket/file.pdf"]))

    mock_table.update_item.assert_not_called()


def test_write_citations_no_uri_skips_result(mocker):
    mock_table = _make_table_mock()
    mocker.patch.object(kb_search.dynamodb_resource, "Table", return_value=mock_table)

    results = [{"content": "内容", "score": 0.5, "location": {}, "metadata": {}}]
    kb_search.write_citations("session-001", results)

    # URI なしの結果だけなら citations リストが空 → update_item は呼ばれない
    mock_table.update_item.assert_not_called()


def test_write_citations_dynamodb_exception_does_not_raise(mocker):
    mock_table = _make_table_mock()
    mock_table.update_item.side_effect = Exception("DynamoDB error")
    mocker.patch.object(kb_search.dynamodb_resource, "Table", return_value=mock_table)

    # 例外がスローされずに完了する
    kb_search.write_citations("session-001", _make_results(["s3://bucket/file.pdf"]))


def test_write_citations_multiple_results(mocker):
    mock_table = _make_table_mock()
    mocker.patch.object(kb_search.dynamodb_resource, "Table", return_value=mock_table)

    uris = [f"s3://bucket/file{i}.pdf" for i in range(3)]
    kb_search.write_citations("session-001", _make_results(uris))

    citations = mock_table.update_item.call_args[1]["ExpressionAttributeValues"][":c"]
    assert len(citations) == 3
