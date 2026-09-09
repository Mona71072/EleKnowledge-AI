"""GET /rag/document（引用文書の解決）のテスト。

このエンドポイントは「認証済みなら誰でも、Lambda ロールが読める任意のオブジェクトに
署名 URL を発行させられる」状態にならないことが要なので、許可判定を重点的に検証する。
"""
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "lambda" / "rag" / "rag-function" / "app.py"

os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
os.environ.setdefault("KB_SOURCE_BUCKET", "kb-source-bucket")
os.environ.setdefault("KB_SOURCE_PREFIX", "docs/")
os.environ.setdefault("DOCUMENTS_BUCKET", "documents-test")

spec = importlib.util.spec_from_file_location("rag_app_doc", APP_PATH)
rag = importlib.util.module_from_spec(spec)
sys.modules["rag_app_doc"] = rag
with patch("boto3.client"), patch("boto3.resource"):
    spec.loader.exec_module(rag)

HEADERS = {"Content-Type": "application/json"}


def _event(uri=None, sub="user-1"):
    event = {
        "httpMethod": "GET",
        "requestContext": {"authorizer": {"claims": {"sub": sub}}} if sub else {},
    }
    if uri is not None:
        event["queryStringParameters"] = {"uri": uri}
    return event


# --- 許可判定 ---------------------------------------------------------------

@pytest.mark.parametrize("uri", [
    "s3://kb-source-bucket/docs/manual.pdf",
    "s3://kb-source-bucket/docs/nested/dir/spec.pdf",
    "s3://documents-test/anything.pdf",
])
def test_allowed_uris(uri):
    assert rag.is_allowed_document_uri(uri) is True


@pytest.mark.parametrize("uri", [
    "s3://kb-source-bucket/outside/secret.pdf",   # prefix 外
    "s3://other-bucket/docs/manual.pdf",          # 許可外バケット
    "s3://kb-source-bucket/docs/../outside.pdf",  # prefix 迂回
    "s3://kb-source-bucket",                      # キー無し
    "s3:///docs/manual.pdf",                      # バケット無し
    "https://example.com/evil.pdf",               # s3 以外
    "file:///etc/passwd",
    "",
    None,
])
def test_rejected_uris(uri):
    assert rag.is_allowed_document_uri(uri) is False


# --- ハンドラ ---------------------------------------------------------------

def test_returns_presigned_url_for_authenticated_user():
    fake_s3 = MagicMock()
    fake_s3.generate_presigned_url.return_value = "https://signed.example.com/manual.pdf"
    with patch.object(rag.boto3, "client", return_value=fake_s3):
        res = rag.handle_document_request(
            _event("s3://kb-source-bucket/docs/manual.pdf"), dict(HEADERS)
        )
    assert res["statusCode"] == 200
    body = json.loads(res["body"])
    assert body["url"] == "https://signed.example.com/manual.pdf"
    assert body["expiresIn"] == rag.PRESIGNED_URL_EXPIRES_IN
    # 署名 URL がキャッシュされないこと
    assert res["headers"]["Cache-Control"] == "no-store"


def test_unauthenticated_request_is_401():
    res = rag.handle_document_request(
        _event("s3://kb-source-bucket/docs/manual.pdf", sub=None), dict(HEADERS)
    )
    assert res["statusCode"] == 401


def test_disallowed_bucket_is_400_and_does_not_presign():
    fake_s3 = MagicMock()
    with patch.object(rag.boto3, "client", return_value=fake_s3):
        res = rag.handle_document_request(
            _event("s3://other-bucket/docs/manual.pdf"), dict(HEADERS)
        )
    assert res["statusCode"] == 400
    # 許可外はそもそも署名を試みない
    fake_s3.generate_presigned_url.assert_not_called()


def test_missing_uri_is_400():
    res = rag.handle_document_request(_event(), dict(HEADERS))
    assert res["statusCode"] == 400


def test_presign_failure_is_502():
    fake_s3 = MagicMock()
    fake_s3.generate_presigned_url.side_effect = RuntimeError("boom")
    with patch.object(rag.boto3, "client", return_value=fake_s3):
        res = rag.handle_document_request(
            _event("s3://documents-test/manual.pdf"), dict(HEADERS)
        )
    assert res["statusCode"] == 502
    # 内部の例外文をそのまま返さない
    assert "boom" not in res["body"]


# --- CITATION_URI_MODE（段階移行スイッチ） -----------------------------------
# 'presigned'（既定）の間は従来フロントを壊さず、's3' に切り替えたときだけ
# raw の s3:// URI を保存・返却することを固定する。

def _kb_result(uri="s3://kb-source-bucket/docs/manual.pdf", score=0.9):
    return {
        "content": {"text": "本文テキスト"},
        "score": score,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": uri,
            "category": "C資料",
            "model_type": "AXIEZ",
        },
    }


def test_default_citation_mode_is_presigned():
    # env 未指定の既定が presigned（デプロイ順の互換性の要）であること
    assert rag.CITATION_URI_MODE == "presigned"


def test_citations_presigned_mode_keeps_presigning(monkeypatch):
    fake_s3 = MagicMock()
    fake_s3.generate_presigned_url.return_value = "https://signed.example.com/manual.pdf"
    monkeypatch.setattr(rag, "CITATION_URI_MODE", "presigned")
    with patch.object(rag.boto3, "client", return_value=fake_s3):
        _, docs = rag.extract_citations_from_selected([_kb_result()])
    assert docs[0]["sourceUri"] == "https://signed.example.com/manual.pdf"


def test_citations_s3_mode_returns_raw_uri(monkeypatch):
    monkeypatch.setattr(rag, "CITATION_URI_MODE", "s3")
    with patch.object(
        rag.boto3, "client", side_effect=AssertionError("s3 モードでは presign しない")
    ):
        _, docs = rag.extract_citations_from_selected([_kb_result()])
    assert docs[0]["sourceUri"] == "s3://kb-source-bucket/docs/manual.pdf"


def test_page_candidates_follow_citation_mode(monkeypatch):
    monkeypatch.setattr(rag, "CITATION_URI_MODE", "s3")
    with patch.object(
        rag.boto3, "client", side_effect=AssertionError("s3 モードでは presign しない")
    ):
        cands = rag.build_page_candidates([_kb_result()])
    assert cands[0]["sourceUri"] == "s3://kb-source-bucket/docs/manual.pdf"

    fake_s3 = MagicMock()
    fake_s3.generate_presigned_url.return_value = "https://signed.example.com/manual.pdf"
    monkeypatch.setattr(rag, "CITATION_URI_MODE", "presigned")
    with patch.object(rag.boto3, "client", return_value=fake_s3):
        cands = rag.build_page_candidates([_kb_result()])
    assert cands[0]["sourceUri"] == "https://signed.example.com/manual.pdf"
