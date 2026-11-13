"""orchestrator Lambda が例外本文・利用者入力をログへ出さないことを確認する。"""
import importlib.util
import json
import os

from botocore.exceptions import ClientError

BASE = os.path.join(os.path.dirname(__file__), "../..")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


orchestrator = _load("orchestrator_logging_app", "lambda/troubleshooting/orchestrator/app.py")

MARKER = "例外に混入した入力_山田太郎_秘密の症状"


def _event():
    return {
        "requestContext": {
            "authorizer": {"userId": "u1", "claims": {"cognito:groups": "admin"}}
        },
        "body": json.dumps({"model": "KE-LG", "troubleDescription": "ブレーカーが落ちる症状です"}),
    }


def test_lambda_error_logs_type_and_code_without_exception_text(caplog, mocker):
    mocker.patch.object(orchestrator, "init_session", side_effect=RuntimeError(MARKER))
    with caplog.at_level("INFO"):
        response = orchestrator.lambda_handler(_event(), None)

    assert response["statusCode"] == 500
    assert MARKER not in response["body"]
    assert "error_type=RuntimeError" in caplog.text
    assert MARKER not in caplog.text


def test_lambda_error_logs_client_error_code(caplog, mocker):
    err = ClientError({"Error": {"Code": "ThrottlingException", "Message": MARKER}}, "InvokeAgent")
    mocker.patch.object(orchestrator, "init_session", side_effect=err)
    with caplog.at_level("INFO"):
        orchestrator.lambda_handler(_event(), None)

    assert "error_type=ClientError" in caplog.text
    assert "error_code=ThrottlingException" in caplog.text
    assert MARKER not in caplog.text


def test_presign_failure_logs_without_exception_text(caplog, mocker):
    mocker.patch.object(orchestrator, "DOCUMENTS_BUCKET", "bucket")
    mocker.patch.object(
        orchestrator.s3_client, "generate_presigned_url", side_effect=RuntimeError(MARKER)
    )
    with caplog.at_level("INFO"):
        result = orchestrator._presign_source_uri("s3://bucket/key.pdf")

    assert result == "s3://bucket/key.pdf"
    assert "error_type=RuntimeError" in caplog.text
    assert MARKER not in caplog.text
