"""orchestrator Lambda のユニットテスト"""
import importlib.util
import os
import pytest
from unittest.mock import MagicMock, patch

BASE = os.path.join(os.path.dirname(__file__), "../..")


def _load(name, rel_path):
    path = os.path.normpath(os.path.join(BASE, rel_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


orchestrator = _load("orchestrator_app", "lambda/troubleshooting/orchestrator/app.py")


# ---------------------------------------------------------------------------
# extract_user_id
# ---------------------------------------------------------------------------

def test_extract_user_id_present():
    event = {"requestContext": {"authorizer": {"userId": "user-sub-123"}}}
    assert orchestrator.extract_user_id(event) == "user-sub-123"


def test_extract_user_id_missing_authorizer():
    assert orchestrator.extract_user_id({}) == "anonymous"


def test_extract_user_id_empty_string():
    # 空文字も欠落と同じく 'anonymous' へフォールバック（missing_authorizer と同契約）。
    # 認証自体は API Gateway の Cognito Authorizer が上流で保証する。
    event = {"requestContext": {"authorizer": {"userId": ""}}}
    assert orchestrator.extract_user_id(event) == "anonymous"


# ---------------------------------------------------------------------------
# validate_input
# ---------------------------------------------------------------------------

def test_validate_input_construction_number_only():
    data = orchestrator.validate_input({
        "constructionNumber": "EIK54801",
        "troubleDescription": "停止してしまい復旧できない",
    })
    assert data["constructionNumber"] == "EIK54801"
    assert "model" not in data


def test_validate_input_model_only():
    data = orchestrator.validate_input({
        "model": "KE-LG",
        "troubleDescription": "停止してしまい復旧できない",
    })
    assert data["model"] == "KE-LG"
    assert "constructionNumber" not in data


def test_validate_input_neither_raises():
    with pytest.raises(orchestrator.ValidationError):
        orchestrator.validate_input({"troubleDescription": "説明がある"})


def test_validate_input_description_too_short():
    with pytest.raises(orchestrator.ValidationError):
        orchestrator.validate_input({"model": "KE-LG", "troubleDescription": "短"})


def test_validate_input_description_too_long():
    with pytest.raises(orchestrator.ValidationError):
        orchestrator.validate_input({"model": "KE-LG", "troubleDescription": "a" * 2001})


def test_validate_input_invalid_model():
    with pytest.raises(orchestrator.ValidationError):
        orchestrator.validate_input({"model": "UNKNOWN", "troubleDescription": "停止してしまい復旧できない"})


def test_validate_input_invalid_construction_number():
    with pytest.raises(orchestrator.ValidationError):
        orchestrator.validate_input({"constructionNumber": "ABC", "troubleDescription": "停止してしまい復旧できない"})


def test_validate_input_invalid_error_code():
    with pytest.raises(orchestrator.ValidationError):
        orchestrator.validate_input({
            "model": "KE-LG",
            "troubleDescription": "停止してしまい復旧できない",
            "errorCode": "invalid!",
        })


def test_validate_input_four_character_error_code_raises():
    with pytest.raises(orchestrator.ValidationError):
        orchestrator.validate_input({
            "model": "KE-LG",
            "troubleDescription": "停止してしまい復旧できない",
            "errorCode": "E001",
        })


def test_validate_input_with_all_fields():
    data = orchestrator.validate_input({
        "constructionNumber": "EIK54801",
        "model": "KE-LG",
        "troubleDescription": "停止してしまい復旧できない",
        "errorCode": "e34",
    })
    assert data["errorCode"] == "E34"
    assert data["model"] == "KE-LG"


# ---------------------------------------------------------------------------
# build_source_documents
# ---------------------------------------------------------------------------

def test_build_source_documents_raw_refs_only():
    orchestrator.DOCUMENTS_BUCKET = "test-bucket"
    orchestrator.s3_client = MagicMock()
    orchestrator.s3_client.generate_presigned_url.return_value = "https://presigned.example.com/file.pdf"

    raw_refs = [{
        "location": {"s3Location": {"uri": "s3://test-bucket/file.pdf"}},
        "metadata": {"title": "テストファイル", "document": "Trouble-Cases", "model": "KE-LG"},
        "score": 0.9,
    }]
    docs = orchestrator.build_source_documents(raw_refs)
    assert len(docs) == 1
    assert docs[0]["documentName"] == "file.pdf"
    assert docs[0]["sourceUri"] == "https://presigned.example.com/file.pdf"
    assert docs[0]["relevance"] == 0.9
    orchestrator.s3_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "test-bucket", "Key": "file.pdf"},
        ExpiresIn=orchestrator.PRESIGNED_URL_EXPIRES_IN,
    )


def test_build_source_documents_presigns_troubleshooting_markdown_uri():
    orchestrator.DOCUMENTS_BUCKET = "eleknowledge-ai-troubleshooting-docs"
    orchestrator.s3_client = MagicMock()
    orchestrator.s3_client.generate_presigned_url.return_value = "https://presigned.example.com/1505C0.md"

    raw_refs = [{
        "location": {"s3Location": {"uri": "s3://eleknowledge-ai-troubleshooting-docs/1505C0.md"}},
        "metadata": {},
        "score": 0.9,
    }]
    docs = orchestrator.build_source_documents(raw_refs)

    assert docs[0]["documentName"] == "1505C0.md"
    assert docs[0]["sourceUri"] == "https://presigned.example.com/1505C0.md"
    orchestrator.s3_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "eleknowledge-ai-troubleshooting-docs", "Key": "1505C0.md"},
        ExpiresIn=orchestrator.PRESIGNED_URL_EXPIRES_IN,
    )


def test_build_source_documents_presigns_nested_s3_key():
    orchestrator.DOCUMENTS_BUCKET = "test-bucket"
    orchestrator.s3_client = MagicMock()
    orchestrator.s3_client.generate_presigned_url.return_value = "https://presigned.example.com/manual.md"

    raw_refs = [{
        "location": {"s3Location": {"uri": "s3://test-bucket/manuals/1505C0.md"}},
        "metadata": {},
        "score": 0.9,
    }]
    orchestrator.build_source_documents(raw_refs)

    orchestrator.s3_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "test-bucket", "Key": "manuals/1505C0.md"},
        ExpiresIn=orchestrator.PRESIGNED_URL_EXPIRES_IN,
    )


def test_build_source_documents_dynamo_citations_only():
    orchestrator.DOCUMENTS_BUCKET = "test-bucket"
    orchestrator.s3_client = MagicMock()
    orchestrator.s3_client.generate_presigned_url.return_value = "https://presigned.example.com/case.pdf"

    dynamo = [{
        "uri": "s3://test-bucket/case.pdf",
        "title": "KE-LG 事例",
        "document": "Trouble-Cases",
        "model": "KE-LG",
        "score": "0.85",
    }]
    docs = orchestrator.build_source_documents([], dynamo)
    assert len(docs) == 1
    assert docs[0]["documentName"] == "case.pdf"
    assert docs[0]["relevance"] == pytest.approx(0.85)


def test_build_source_documents_deduplication():
    orchestrator.DOCUMENTS_BUCKET = "test-bucket"
    orchestrator.s3_client = MagicMock()
    orchestrator.s3_client.generate_presigned_url.return_value = "https://presigned.example.com/dup.pdf"

    raw_refs = [{
        "location": {"s3Location": {"uri": "s3://test-bucket/dup.pdf"}},
        "metadata": {"title": "重複", "document": "Trouble-Cases", "model": "KE-LG"},
        "score": 0.9,
    }]
    dynamo = [{
        "uri": "s3://test-bucket/dup.pdf",
        "title": "重複（DynamoDB）",
        "document": "Trouble-Cases",
        "model": "KE-LG",
        "score": "0.8",
    }]
    docs = orchestrator.build_source_documents(raw_refs, dynamo)
    # 重複 URI は 1 件のみ（raw_refs が優先）
    assert len(docs) == 1
    assert docs[0]["relevance"] == pytest.approx(0.9)


def test_build_source_documents_includes_md():
    orchestrator.DOCUMENTS_BUCKET = "test-bucket"
    orchestrator.s3_client = MagicMock()
    orchestrator.s3_client.generate_presigned_url.return_value = "https://presigned.example.com/readme.md"

    raw_refs = [{
        "location": {"s3Location": {"uri": "s3://test-bucket/readme.md"}},
        "metadata": {},
        "score": 0.7,
    }]
    docs = orchestrator.build_source_documents(raw_refs)
    assert docs[0]["documentName"] == "readme.md"
    assert docs[0]["sourceUri"] == "https://presigned.example.com/readme.md"


def test_build_source_documents_keeps_uri_for_unconfigured_bucket():
    orchestrator.DOCUMENTS_BUCKET = "expected-bucket"
    orchestrator.s3_client = MagicMock()
    uri = "s3://other-bucket/1505C0.md"

    raw_refs = [{"location": {"s3Location": {"uri": uri}}, "metadata": {}, "score": 0.7}]
    docs = orchestrator.build_source_documents(raw_refs)

    assert docs[0]["sourceUri"] == uri
    orchestrator.s3_client.generate_presigned_url.assert_not_called()


@pytest.mark.parametrize("uri", [
    "s3://test-bucket",
    "s3:///1505C0.md",
    "https://example.com/1505C0.md",
])
def test_build_source_documents_keeps_uri_when_not_signable(uri):
    orchestrator.DOCUMENTS_BUCKET = "test-bucket"
    orchestrator.s3_client = MagicMock()

    raw_refs = [{"location": {"s3Location": {"uri": uri}}, "metadata": {}, "score": 0.7}]
    docs = orchestrator.build_source_documents(raw_refs)

    assert docs[0]["sourceUri"] == uri
    orchestrator.s3_client.generate_presigned_url.assert_not_called()


def test_build_source_documents_skips_empty_uri():
    orchestrator.DOCUMENTS_BUCKET = "test-bucket"
    orchestrator.s3_client = MagicMock()

    raw_refs = [{"location": {}, "metadata": {}, "score": 0.5}]
    docs = orchestrator.build_source_documents(raw_refs)
    assert docs == []


def test_build_source_documents_none_dynamo():
    orchestrator.DOCUMENTS_BUCKET = ""
    orchestrator.s3_client = MagicMock()

    # dynamo_citations=None でもクラッシュしない
    docs = orchestrator.build_source_documents([], None)
    assert docs == []
