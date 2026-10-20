"""The Markdown retrieval extension is opt-in and admin-gated at the API boundary."""
import json
import hashlib


def _event(body, *, groups="admin"):
    return {
        "httpMethod": "POST",
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user", "cognito:groups": groups}
            }
        },
        "body": json.dumps(body),
    }


def test_non_admin_is_rejected_before_session_or_history_reads(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", True, raising=False)
    monkeypatch.setattr(
        rag_app,
        "owns_session",
        lambda *_args: (_ for _ in ()).throw(AssertionError("session checked before gate")),
    )
    monkeypatch.setattr(
        rag_app,
        "get_chat_history",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("history read before gate")),
    )

    response = rag_app.handle_rag_request(
        _event({"query": "かごの振動", "includeKnowhow": True}, groups="user"),
        None,
        0,
    )

    assert response["statusCode"] == 403
    assert json.loads(response["body"])["error"] == "FeatureUnavailable"


def test_non_dev_environment_is_rejected_before_index_access(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "prod")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", True, raising=False)
    monkeypatch.setattr(
        rag_app,
        "get_chat_history",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("history read before gate")),
    )

    response = rag_app.handle_rag_request(
        _event({"query": "かごの振動", "includeKnowhow": True}), None, 0
    )

    assert response["statusCode"] == 403


def test_include_knowhow_requires_json_boolean(rag_app):
    response = rag_app.handle_rag_request(
        _event({"query": "かごの振動", "includeKnowhow": "true"}), None, 0
    )

    assert response["statusCode"] == 400


def test_law_mode_rejects_markdown_retrieval(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", True, raising=False)
    monkeypatch.setattr(rag_app, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(rag_app, "LAW_KNOWLEDGE_BASE_ID", "law-test")

    response = rag_app.handle_rag_request(
        _event({"query": "法令確認", "mode": "law", "includeKnowhow": True}),
        None,
        0,
    )

    assert response["statusCode"] == 400


def test_disabled_feature_is_rejected_before_history_read(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", False, raising=False)
    monkeypatch.setattr(
        rag_app,
        "get_chat_history",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("history read before gate")),
    )

    response = rag_app.handle_rag_request(
        _event({"query": "かごの振動", "includeKnowhow": True}), None, 0
    )

    assert response["statusCode"] == 403


def _index():
    body = "## 症状\nかごの走行中振動。\n## 原因\n取付条件。\n## 対策\n締結を確認。"
    return {
        "schemaVersion": 1,
        "indexVersion": "sha256:" + "a" * 64,
        "generatedAt": "2026-10-20T00:00:00Z",
        "cards": [{
            "knowledgeId": "KH-SYN-001",
            "cardVersion": 1,
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
            "title": "かご走行中の振動",
            "status": "draft",
            "usage": "navigation_only",
            "body": body,
            "searchTerms": ["かご", "走行中", "振動"],
            "sourceRefs": [{
                "ref_type": "kb_document",
                "document_number": "C-6-R56.1",
                "kb_filename": "TI-1335.pdf",
            }],
            "modelScope": {"model_abbreviations": ["AXIEZ"], "excludes": []},
        }],
    }


def _configure_successful_pipeline(rag_app, monkeypatch, *, weak=False, clarify=False):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", True, raising=False)
    monkeypatch.setattr(rag_app, "KNOWHOW_INDEX_BUCKET", "private-bucket", raising=False)
    monkeypatch.setattr(rag_app, "KNOWHOW_INDEX_KEY", "senpai/index.json", raising=False)
    monkeypatch.setattr(rag_app, "load_index", lambda **_kwargs: _index())
    monkeypatch.setattr(rag_app, "get_chat_history", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(rag_app.telemetry, "stamp_reformulation", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(rag_app, "generate_session_id", lambda: "session-synthetic")
    monkeypatch.setattr(rag_app, "_fallback_session_title", lambda _query: "synthetic")
    monkeypatch.setattr(rag_app, "enqueue_session_title", lambda *_args: None)
    monkeypatch.setattr(rag_app, "save_message_to_dynamodb", lambda **_kwargs: "message-synthetic")
    monkeypatch.setattr(rag_app, "needs_clarify", lambda *_args: (clarify, ["機種と発生条件"] if clarify else []))
    monkeypatch.setattr(rag_app, "maybe_rewrite_search_query", lambda query, *_args, **_kwargs: query)
    monkeypatch.setattr(rag_app, "normalize_query_text", lambda query: query)
    monkeypatch.setattr(rag_app, "expand_query_abbreviations", lambda query: query)
    monkeypatch.setattr(
        rag_app,
        "retrieve_for_normal_query",
        lambda *_args, **_kwargs: {"retrievalResults": [{
            "score": 0.9,
            "content": {"text": "KBの合成根拠"},
            "metadata": {"x-amz-bedrock-kb-source-uri": "s3://kb/doc.pdf"},
        }]},
    )
    monkeypatch.setattr(rag_app, "select_retrieval_results", lambda results, **_kwargs: results)
    monkeypatch.setattr(rag_app, "merge_retrieval_results", lambda first, second: first + second)
    monkeypatch.setattr(rag_app, "is_weak_retrieval", lambda *_args, **_kwargs: weak)
    monkeypatch.setattr(rag_app, "build_page_candidates", lambda *_args, **_kwargs: [])
    captured = {}

    def generate(_query, kb_results, _history, _mode, *, search_query=None, **_kwargs):
        captured["knowhow"] = kb_results.get("_knowhow")
        captured["search_query"] = search_query
        return "合成回答"

    monkeypatch.setattr(rag_app, "generate_response_with_claude", generate)
    monkeypatch.setattr(rag_app, "extract_citations", lambda *_args, **_kwargs: ([], []))
    return captured


def test_all_three_response_paths_return_markdown_retrieval_metadata(rag_app, monkeypatch):
    for weak, clarify, expected in (
        (False, True, "clarify"),
        (True, False, "not_found"),
        (False, False, "pages"),
    ):
        _configure_successful_pipeline(rag_app, monkeypatch, weak=weak, clarify=clarify)
        response = rag_app.handle_rag_request(
            _event({"query": "かごの走行中振動", "includeKnowhow": True}), None, 0
        )

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["responseType"] == expected
        assert body["knowhow"]["status"] == "matched"
        assert body["knowhow"]["matches"][0]["knowledgeId"] == "KH-SYN-001"
        assert body["knowhow"]["searchTerms"] == ["C-6-R56.1", "TI-1335.pdf"]
        monkeypatch.undo()


def test_matching_markdown_adds_only_typed_kb_hints_and_non_authoritative_context(rag_app, monkeypatch):
    captured = _configure_successful_pipeline(rag_app, monkeypatch)
    response = rag_app.handle_rag_request(
        _event({"query": "かごの走行中振動", "includeKnowhow": True}), None, 0
    )

    assert response["statusCode"] == 200
    assert "C-6-R56.1" in captured["search_query"]
    assert "TI-1335.pdf" in captured["search_query"]
    assert captured["knowhow"]["matches"][0]["usage"] == "navigation_only"
    assert "_score" not in captured["knowhow"]["matches"][0]


def test_missing_private_index_returns_503_before_bedrock(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(rag_app, "KNOWHOW_ENABLED", True, raising=False)
    monkeypatch.setattr(rag_app, "get_chat_history", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(rag_app.telemetry, "stamp_reformulation", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(rag_app, "load_index", lambda **_kwargs: (_ for _ in ()).throw(rag_app.KnowhowIndexError("index is unavailable")))
    monkeypatch.setattr(
        rag_app,
        "retrieve_for_normal_query",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("KB retrieval ran after index failure")),
    )
    monkeypatch.setattr(
        rag_app,
        "generate_response_with_claude",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("Bedrock ran after index failure")),
    )

    response = rag_app.handle_rag_request(
        _event({"query": "かごの走行中振動", "includeKnowhow": True}), None, 0
    )

    assert response["statusCode"] == 503
    assert json.loads(response["body"])["error"] == "KnowledgeUnavailable"
