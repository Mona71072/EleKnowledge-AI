"""KB Search Lambda が利用者入力をログへ出さないことを確認する。"""
import importlib.util
import os

import pytest
from unittest.mock import MagicMock

BASE = os.path.join(os.path.dirname(__file__), "../..")
LAMBDA_PATHS = [
    "lambda/troubleshooting/kb-search1/app.py",
    "lambda/troubleshooting/kb-search2/app.py",
    "lambda/troubleshooting/kb-search3/app.py",
]


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("index,rel_path", list(enumerate(LAMBDA_PATHS)))
def test_lambda_handler_does_not_log_user_input(index, rel_path, caplog, mocker):
    module = _load(f"kb_search{index + 1}_logging_app", rel_path)
    marker = "個人名入りの不具合文_山田太郎_秘密の症状"
    event = {
        "actionGroup": "Troubleshooting",
        "function": "searchManual",
        "parameters": [
            {"name": "query", "value": marker},
            {"name": "controlSystem", "value": "VFGLF"},
        ],
    }
    mocker.patch.object(
        module.bedrock_client,
        "retrieve",
        return_value={
            "retrievalResults": [
                {"content": f"検索結果本文_{marker}", "score": 0.9, "location": {}, "metadata": {}}
            ]
        },
    )
    mocker.patch.object(module.dynamodb_resource, "Table", return_value=MagicMock())

    with caplog.at_level("INFO"):
        module.lambda_handler(event, None)

    assert marker not in caplog.text
    assert "actionGroup" in caplog.text
    assert "query" in caplog.text


@pytest.mark.parametrize("index,rel_path", list(enumerate(LAMBDA_PATHS)))
def test_lambda_handler_logs_exception_type_without_user_input(index, rel_path, caplog, mocker):
    module = _load(f"kb_search{index + 1}_logging_error_app", rel_path)
    marker = "例外に混入した入力_山田太郎_秘密"
    event = {
        "actionGroup": "Troubleshooting",
        "function": "searchManual",
        "parameters": [
            {"name": "query", "value": marker},
            {"name": "controlSystem", "value": "VFGLF"},
        ],
    }
    mocker.patch.object(module.bedrock_client, "retrieve", side_effect=RuntimeError(marker))

    with caplog.at_level("INFO"):
        module.lambda_handler(event, None)

    assert "error_type=KBSearchError" in caplog.text
    assert marker not in caplog.text
