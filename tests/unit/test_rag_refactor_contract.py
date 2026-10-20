"""Characterization tests that lock RAG behavior before structural refactoring.

These tests intentionally assert existing public behavior rather than proposing
new retrieval rules.  They provide a safety net while app.py is split into
smaller modules.
"""
import copy
import io
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from botocore.session import get_session
from botocore.validate import validate_parameters
from botocore.exceptions import ClientError, ReadTimeoutError


@pytest.fixture(scope="module")
def rag(rag_app):
    return rag_app


def _result(uri: str, score: float, text: str, *, chunk_id: str = "", category: str = "C資料"):
    metadata = {
        "x-amz-bedrock-kb-source-uri": uri,
        "category": category,
        "model_type": "AXIEZ",
    }
    if chunk_id:
        metadata["x-amz-bedrock-kb-chunk-id"] = chunk_id
    return {
        "score": score,
        "metadata": metadata,
        "content": {"text": text},
    }


def test_query_normalization_is_nfkc_and_space_collapsed(rag):
    assert rag.normalize_query_text("  ＡＸＩＥＺ　 火管  ") == "AXIEZ 火管"


def test_abbreviation_expansion_preserves_unknown_text(rag):
    assert rag.expand_query_abbreviations("火管の解除条件") == "火災管制の解除条件"
    assert rag.expand_query_abbreviations("未知語") == "未知語"


def test_merge_retrieval_results_keeps_best_duplicate_chunk(rag):
    low = _result("s3://bucket/a.pdf", 0.41, "same", chunk_id="c1")
    high = _result("s3://bucket/a.pdf", 0.82, "same", chunk_id="c1")
    other = _result("s3://bucket/b.pdf", 0.65, "other", chunk_id="c2")

    merged = rag.merge_retrieval_results([low, other], [high])

    assert len(merged) == 2
    assert merged[0]["score"] == 0.82
    assert merged[1]["score"] == 0.65


def test_merge_retrieval_results_keeps_distinct_image_chunks(rag):
    first = {
        "score": 0.7,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://bucket/drawing.pdf",
            "x-amz-bedrock-kb-chunk-id": "image-1",
        },
        "content": {"type": "IMAGE", "byteContent": "abc"},
    }
    second = {
        "score": 0.6,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://bucket/drawing.pdf",
            "x-amz-bedrock-kb-chunk-id": "image-2",
        },
        "content": {"type": "IMAGE", "byteContent": "def"},
    }

    merged = rag.merge_retrieval_results([first, second])

    assert len(merged) == 2


def test_selection_limits_chunks_per_document(rag):
    results = [
        _result("s3://bucket/a.pdf", 0.91, "a1", chunk_id="1"),
        _result("s3://bucket/a.pdf", 0.90, "a2", chunk_id="2"),
        _result("s3://bucket/a.pdf", 0.89, "a3", chunk_id="3"),
        _result("s3://bucket/b.pdf", 0.88, "b1", chunk_id="4"),
    ]

    selected = rag.select_retrieval_results(results, mode="normal")

    a_results = [
        r for r in selected
        if r["metadata"]["x-amz-bedrock-kb-source-uri"] == "s3://bucket/a.pdf"
    ]
    assert len(a_results) == 2
    assert any(
        r["metadata"]["x-amz-bedrock-kb-source-uri"] == "s3://bucket/b.pdf"
        for r in selected
    )


def test_selection_rejects_results_below_current_normal_threshold(rag):
    results = [
        _result("s3://bucket/a.pdf", 0.299, "below"),
        _result("s3://bucket/b.pdf", 0.300, "edge"),
    ]

    selected = rag.select_retrieval_results(results, mode="normal")

    assert [r["content"]["text"] for r in selected] == ["edge"]


def test_modeless_filter_applies_category_allowlist(rag):
    # PR #55/#57/#58 マージ後の develop 挙動: フィルタ未指定でもカテゴリ許可リストを
    # 常時適用し、web-crawler / TEST 由来のノイズ文書を検索母集団から遮断する
    # （None は返らない）。根拠: docs/verification-2026-08-26-kb-vqv-metadata.md
    assert rag.build_kb_filter({}) == {
        "in": {"key": "category", "value": list(rag.ALLOWED_CATEGORY_VALUES)}
    }


def test_normalize_mode_keeps_explicit_category(rag):
    mode, filters = rag.normalize_mode_and_filters(
        "spec", {"category": "drawing", "modelType": "AXIEZ"}
    )

    assert mode == "normal"
    assert filters == {"category": "drawing", "modelType": "AXIEZ"}


def test_law_rag_requires_dev_flag_and_knowledge_base(rag):
    assert rag.law_rag_is_enabled("dev", "true", "ABCDEFGHIJ")
    assert not rag.law_rag_is_enabled("prd", "true", "ABCDEFGHIJ")
    assert not rag.law_rag_is_enabled("dev", "false", "ABCDEFGHIJ")
    assert not rag.law_rag_is_enabled("dev", "true", "")


def test_law_filter_only_includes_current_law_documents(rag):
    assert rag.build_law_kb_filter() == {
        "andAll": [
            {"equals": {"key": "source_type", "value": "law"}},
            {"equals": {"key": "status", "value": "current"}},
            {"equals": {"key": "document_granularity", "value": "provision_unit"}},
        ]
    }


def _law_unit_result(rag, index=1, text="検索断片"):
    return {
        "score": 0.9,
        "content": {"text": text},
        "metadata": {
            "source_type": "law", "status": "current",
            "document_granularity": "provision_unit", "law_id": "123",
            "law_title": "検証法令", "law_number": "法律第一号",
            "provision_reference": f"第{index}条", "provision_type": "main",
            "source_url": f"https://laws.e-gov.go.jp/law/123#Mp-At_{index}",
            rag.KB_PROFILE.source_uri_key: f"s3://law-bucket/kb/egov/123/123_20260101_ABC/main/{index:05d}.txt",
        },
    }


def _configure_law_full_text(rag, monkeypatch, body="条文全文"):
    monkeypatch.setattr(rag, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag, "LAW_KNOWLEDGE_BASE_ID", "ABCDEFGHIJ")
    monkeypatch.setattr(rag, "LAW_DATA_BUCKET_NAME", "law-bucket")
    monkeypatch.setattr(rag, "LAW_DATA_BUCKET_OWNER", "123456789012")
    client = MagicMock()
    payload = body.encode("utf-8")
    client.get_object.side_effect = lambda **kwargs: {
        "ContentLength": len(payload), "Body": io.BytesIO(payload)
    }
    monkeypatch.setattr(rag, "law_full_text_s3", client)
    return client


def test_law_full_text_preserves_tail_and_same_citations(rag, monkeypatch, capsys):
    body = "条文の前半" * 300 + "第十三項の予備電源要件"
    client = _configure_law_full_text(rag, monkeypatch, body)
    result = _law_unit_result(rag)
    original = copy.deepcopy(result)

    prepared = rag.prepare_law_references([result, copy.deepcopy(result)], request_id="request-test")

    assert len(prepared) == 1
    assert prepared[0]["_lawReferenceCoverage"] == "full"
    assert "第十三項の予備電源要件" in rag.build_references_block(prepared)
    assert result == original
    assert client.get_object.call_count == 1
    assert client.get_object.call_args.kwargs["ExpectedBucketOwner"] == "123456789012"
    citations, documents = rag.extract_citations({"retrievalResults": [], "_lawSelectedResults": prepared}, mode="law")
    assert len(citations) == len(documents) == 1
    assert documents[0]["referenceCoverage"] == "full"
    assert documents[0]["sourceUri"].startswith("https://laws.e-gov.go.jp/")
    log = capsys.readouterr().out
    assert "request-test" in log and "fullDocuments" in log
    assert body not in log and "検索断片" not in log


@pytest.mark.parametrize("body, reason", [
    ("法" * 11000, "byte_limit"),
    ("法" * 8001, "character_limit"),
    ("", "empty_source"),
], ids=["byte-limit", "character-limit", "empty-source"])
def test_law_full_text_size_and_empty_fallback(rag, monkeypatch, body, reason):
    _configure_law_full_text(rag, monkeypatch, body)
    prepared = rag.prepare_law_references([_law_unit_result(rag)])
    assert prepared[0]["_lawReferenceCoverage"] == "partial"
    assert prepared[0]["_lawReferenceReason"] == reason
    assert prepared[0]["_lawReferenceText"] == "検索断片"


@pytest.mark.parametrize("error", [
    ClientError({"Error": {"Code": "AccessDenied", "Message": "secret-error"}}, "GetObject"),
    ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject"),
    ReadTimeoutError(endpoint_url="https://example.invalid"),
])
def test_law_full_text_read_errors_remain_partial(rag, monkeypatch, error, capsys):
    client = _configure_law_full_text(rag, monkeypatch)
    client.get_object.side_effect = error
    prepared = rag.prepare_law_references([_law_unit_result(rag)])
    assert prepared[0]["_lawReferenceReason"] == "read_error"
    assert prepared[0]["_lawReferenceCoverage"] == "partial"
    assert "secret-error" not in capsys.readouterr().out


@pytest.mark.parametrize("uri", [
    "s3://other-bucket/kb/egov/123/123_20260101_ABC/main/00001.txt",
    "https://law-bucket.s3.ap-northeast-1.amazonaws.com/kb/egov/123/123_20260101_ABC/main/00001.txt",
    "s3://law-bucket/raw/egov/123.xml",
    "s3://law-bucket/kb/egov/123/../main/00001.txt",
    "s3://law-bucket/kb/egov/999/999_20260101_ABC/main/00001.txt",
    "s3://law-bucket/kb/egov/123/123_20260101_ABC/main/00001.txt?token=bad",
    "s3://law-bucket/kb/egov/123/123_20260101_ABC/main/00001.txt#bad",
    "s3://[invalid",
])
def test_law_full_text_rejects_untrusted_uri_without_read(rag, monkeypatch, uri):
    client = _configure_law_full_text(rag, monkeypatch)
    result = _law_unit_result(rag)
    result["metadata"][rag.KB_PROFILE.source_uri_key] = uri
    prepared = rag.prepare_law_references([result])
    client.get_object.assert_not_called()
    assert prepared[0]["_lawReferenceReason"] == "invalid_uri"


def test_law_full_text_deadline_and_dev_gate(rag, monkeypatch):
    client = _configure_law_full_text(rag, monkeypatch)
    prepared = rag.prepare_law_references([_law_unit_result(rag)], request_deadline=0)
    assert prepared[0]["_lawReferenceReason"] == "time_budget"
    monkeypatch.setattr(rag, "ENVIRONMENT", "prd")
    prepared = rag.prepare_law_references([_law_unit_result(rag)])
    assert prepared[0]["_lawReferenceReason"] == "not_configured"
    client.get_object.assert_not_called()


def test_law_full_text_document_and_total_budgets(rag, monkeypatch):
    client = _configure_law_full_text(rag, monkeypatch, "全文")
    results = [_law_unit_result(rag, index) for index in range(1, 9)]
    prepared = rag.prepare_law_references(results)
    assert client.get_object.call_count == 6
    assert [result["_lawReferenceCoverage"] for result in prepared] == ["full"] * 6 + ["partial"] * 2
    assert prepared[-1]["_lawReferenceReason"] == "document_limit"

    monkeypatch.setattr(rag, "LAW_REFERENCE_MAX_TOTAL_CHARS", 10)
    client.get_object.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "GetObject")
    prepared = rag.prepare_law_references([_law_unit_result(rag, index, "断片本文です") for index in range(1, 9)])
    assert sum(len(result["_lawReferenceText"]) for result in prepared) <= 10
    citations, documents = rag.extract_citations({"_lawSelectedResults": prepared}, mode="law")
    assert len(citations) == len(documents) == len(prepared)
    assert len(prepared) < 8


def test_law_full_text_invalid_utf8_closes_stream(rag, monkeypatch):
    client = _configure_law_full_text(rag, monkeypatch)
    stream = io.BytesIO(b"\xff")
    client.get_object.side_effect = None
    client.get_object.return_value = {"ContentLength": 1, "Body": stream}
    prepared = rag.prepare_law_references([_law_unit_result(rag)])
    assert stream.closed
    assert prepared[0]["_lawReferenceReason"] == "read_error"


def test_law_citations_preserve_article_fragment_and_xml_title(rag):
    source_url = "https://laws.e-gov.go.jp/law/325CO0000000338/20251201_507CO0000000377#Mp-Ch_5_4-Se_2-At_129_13_3"
    result = {
        "score": 0.99,
        "metadata": {
            "law_id": "325CO0000000338",
            "law_title": "建築基準法施行令",
            "law_number": "昭和二十五年政令第三百三十八号",
            "effective_date": "2025-12-01",
            "provision_type": "main",
            "provision_reference": "第百二十九条の十三の三",
            "source_url": source_url,
        },
    }

    citations, documents = rag.extract_law_citations([result])

    assert citations == ["昭和二十五年政令第三百三十八号 第百二十九条の十三の三"]
    assert documents[0]["sourceUri"] == source_url
    assert documents[0]["lawCitation"]["sourceUrl"] == source_url
    assert documents[0]["lawCitation"]["provisionReference"] == "第百二十九条の十三の三"


def test_law_results_reject_legacy_aggregate_keys(rag):
    metadata = {
        "source_type": "law",
        "status": "current",
        "document_granularity": "provision_unit",
        "x-amz-bedrock-kb-source-uri": "s3://bucket/kb/egov/123/version/main/00001.txt",
    }
    assert rag.is_current_law_article_result({"metadata": metadata})
    legacy_metadata = {
        **metadata,
        "x-amz-bedrock-kb-source-uri": "s3://bucket/kb/egov/123/version.main.txt",
    }
    assert not rag.is_current_law_article_result({"metadata": legacy_metadata})
    assert not rag.is_current_law_article_result({"metadata": {
        **metadata,
        "status": "superseded",
    }})
    assert not rag.is_current_law_article_result({
        "metadata": {key: value for key, value in metadata.items() if key != "document_granularity"}
    })


def test_law_retrieval_uses_managed_search_and_law_kb_only(rag, monkeypatch):
    calls = []
    expected_response = {"retrievalResults": []}

    def retrieve(**kwargs):
        calls.append(kwargs)
        return expected_response

    monkeypatch.setattr(rag, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag, "LAW_KNOWLEDGE_BASE_ID", "ABCDEFGHIJ")
    monkeypatch.setattr(rag.bedrock_agent, "retrieve", retrieve)

    response = rag.query_law_knowledge_base("建築基準法の昇降機規定")

    assert response is expected_response
    assert calls[0]["knowledgeBaseId"] == "ABCDEFGHIJ"
    assert calls[0]["retrievalConfiguration"] == {
        "managedSearchConfiguration": {
            "numberOfResults": 30,
            "filter": rag.build_law_kb_filter(),
            "rerankingModelType": "NONE",
        }
    }
    model = get_session().get_service_model("bedrock-agent-runtime")
    validate_parameters(calls[0], model.operation_model("Retrieve").input_shape)


def test_law_lambda_bundles_pinned_aws_sdk(rag):
    requirements = Path(rag.__file__).with_name("requirements.txt").read_text().splitlines()
    assert any(line.startswith("boto3==") for line in requirements)
    assert any(line.startswith("botocore==") for line in requirements)


@pytest.mark.parametrize("source_prefix", [
    "s3://bucket",
    "https://bucket.s3.ap-northeast-1.amazonaws.com",
])
def test_law_retrieval_normalizes_managed_metadata_and_rejects_aggregates(rag, monkeypatch, source_prefix):
    metadata = {
        "source_type": "law",
        "status": "current",
        "document_granularity": "provision_unit",
        "_source_uri": f"{source_prefix}/kb/egov/123/version/main/00001.txt",
        "_chunk_id": "managed-chunk-1",
    }
    article = {"metadata": metadata}
    aggregate = {"metadata": {**metadata, "_source_uri": f"{source_prefix}/kb/egov/123/version.main.txt"}}
    monkeypatch.setattr(rag, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag, "LAW_KNOWLEDGE_BASE_ID", "ABCDEFGHIJ")
    monkeypatch.setattr(rag.bedrock_agent, "retrieve", lambda **kwargs: {
        "retrievalResults": [article, aggregate]
    })

    response = rag.query_law_knowledge_base("労働基準法")

    assert response["retrievalResults"] == [article]
    assert article["metadata"][rag.KB_PROFILE.source_uri_key] == "s3://bucket/kb/egov/123/version/main/00001.txt"
    assert article["metadata"][rag.KB_PROFILE.chunk_id_key] == "managed-chunk-1"


def test_law_mode_is_rejected_when_feature_gate_is_off(rag, monkeypatch):
    monkeypatch.setattr(rag, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag, "LAW_RAG_ENABLED", "false")
    monkeypatch.setattr(rag, "LAW_KNOWLEDGE_BASE_ID", "ABCDEFGHIJ")
    event = {
        "httpMethod": "POST",
        "body": '{"mode":"law","query":"建築基準法の昇降機規定"}',
        "requestContext": {
            "authorizer": {"claims": {"sub": "verified-user"}}
        },
    }

    response = rag.lambda_handler(event, None)

    assert response["statusCode"] == 403


def test_law_mode_rejects_existing_normal_session(rag, monkeypatch):
    monkeypatch.setattr(rag, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag, "LAW_KNOWLEDGE_BASE_ID", "ABCDEFGHIJ")
    monkeypatch.setattr(rag, "owns_session", lambda session_id, user_id: True)
    monkeypatch.setattr(rag, "get_session_rag_mode", lambda session_id: "normal")
    monkeypatch.setattr(
        rag.bedrock_agent, "retrieve",
        lambda **kwargs: pytest.fail("mode-mismatched session must not retrieve"),
    )
    event = {
        "httpMethod": "POST",
        "body": '{"sessionId":"normal-session","mode":"law","query":"建築基準法"}',
        "requestContext": {
            "authorizer": {"claims": {"sub": "verified-user"}}
        },
    }

    response = rag.lambda_handler(event, None)

    assert response["statusCode"] == 409
    assert json.loads(response["body"])["error"] == "SessionModeMismatch"


def test_law_handler_uses_only_law_kb_and_returns_egov_citation(rag, monkeypatch):
    saved_messages = []
    retrieval_result = {
        "score": 0.92,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://law-bucket/kb/egov/123/2025/main/00001.txt",
            "source_type": "law",
            "source_url": "https://laws.e-gov.go.jp/law/123",
            "document_granularity": "provision_unit",
            "law_id": "123",
            "law_title": "建築基準法",
            "law_number": "昭和二十五年法律第二百一号",
            "effective_date": "2025-06-01",
            "provision_type": "main",
            "provision_reference": "第1条",
        },
        "content": {"text": "法令本文"},
    }

    monkeypatch.setattr(rag, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag, "LAW_KNOWLEDGE_BASE_ID", "ABCDEFGHIJ")
    monkeypatch.setattr(rag, "get_chat_history", lambda *args, **kwargs: [])
    monkeypatch.setattr(rag, "query_law_knowledge_base", lambda query: {
        "retrievalResults": [retrieval_result]
    })
    monkeypatch.setattr(
        rag, "retrieve_for_normal_query",
        lambda *args, **kwargs: pytest.fail("law mode must not query the normal KB"),
    )
    monkeypatch.setattr(
        rag, "generate_response_with_claude",
        lambda query, results, history, mode, **kwargs: "法令本文から確認できる内容です。",
    )
    monkeypatch.setattr(rag, "enqueue_session_title", lambda *args: None)
    monkeypatch.setattr(
        rag,
        "save_message_to_dynamodb",
        lambda **kwargs: saved_messages.append(copy.deepcopy(kwargs)) or f"message-{len(saved_messages)}",
    )
    event = {
        "httpMethod": "POST",
        "body": '{"mode":"law","query":"建築基準法の規定"}',
        "requestContext": {
            "authorizer": {"claims": {"sub": "verified-user"}}
        },
    }

    response = rag.lambda_handler(event, None)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert response_body["pageCandidates"] == []
    assert response_body["sourceDocuments"][0]["sourceUri"] == "https://laws.e-gov.go.jp/law/123"
    assert response_body["sourceDocuments"][0]["lawCitation"]["provisionReference"] == "第1条"
    assert [message["rag_mode"] for message in saved_messages] == ["law", "law"]
    assert saved_messages[1]["source_documents"][0]["relevance"] == rag.Decimal("0.92")


def test_law_citations_link_only_to_egov_and_include_provision_metadata(rag):
    result = {
        "score": 0.82,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://private-law-bucket/kb/egov/abc.txt",
            "source_url": "https://laws.e-gov.go.jp/law/123",
            "law_id": "123",
            "law_title": "建築基準法",
            "law_number": "昭和二十五年法律第二百一号",
            "effective_date": "2025-06-01",
            "provision_type": "main",
            "provision_reference": "第1条",
        },
        "content": {"text": "法令本文"},
    }

    citations, source_documents = rag.extract_law_citations([result])

    assert citations == ["昭和二十五年法律第二百一号 第1条"]
    assert source_documents[0]["sourceUri"] == "https://laws.e-gov.go.jp/law/123"
    assert source_documents[0]["lawCitation"]["provisionReference"] == "第1条"
    assert "s3://" not in str(source_documents)
    result["metadata"]["source_url"] = "https://example.com/law/123"
    assert rag.extract_law_citations([result]) == ([], [])


def test_law_reference_context_omits_internal_s3_uri(rag):
    context = rag.build_references_block([{
        "score": 0.9,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://private-law-bucket/kb/egov/abc.txt",
            "source_type": "law",
            "law_id": "123",
            "law_title": "建築基準法",
            "law_number": "昭和二十五年法律第二百一号",
            "effective_date": "2025-06-01",
            "provision_type": "main",
            "provision_reference": "第1条",
        },
        "content": {"text": "法令本文"},
    }])

    assert "建築基準法" in context
    assert "第1条" in context
    assert "2025-06-01" in context
    assert "s3://" not in context


def test_unknown_mode_is_rejected(rag):
    event = {
        "httpMethod": "POST",
        "body": '{"mode":"unknown","query":"質問"}',
        "requestContext": {
            "authorizer": {"claims": {"sub": "verified-user"}}
        },
    }

    response = rag.lambda_handler(event, None)

    assert response["statusCode"] == 400


def test_get_chat_history_filters_sessions_by_rag_mode(rag, monkeypatch):
    class FakeChatLogsTable:
        def query(self, **kwargs):
            return {"Items": [
                {"role": "assistant", "ragMode": "law", "content": "law answer", "timestamp": "4"},
                {"role": "user", "ragMode": "law", "content": "law question", "timestamp": "3"},
                {"role": "assistant", "content": "old answer", "timestamp": "2"},
                {"role": "user", "content": "old question", "timestamp": "1"},
            ]}

    monkeypatch.setattr(rag, "chatlogs_table", FakeChatLogsTable())

    history = rag.get_chat_history("session-1", mode="law")

    assert [message["content"] for message in history] == ["law question", "law answer"]


def test_caller_identity_comes_only_from_verified_claims(rag):
    event = {
        "requestContext": {"authorizer": {"claims": {"sub": "verified-user"}}},
        "body": '{"userId":"spoofed-user"}',
    }

    assert rag.get_caller_id(event) == "verified-user"
