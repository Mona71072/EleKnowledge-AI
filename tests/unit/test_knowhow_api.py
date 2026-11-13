"""The Markdown retrieval extension is opt-in and admin-gated at the API boundary."""
import hashlib
import json
import types

import pytest


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


@pytest.mark.parametrize("groups", ["user", "keyman", "users,keyman"])
def test_non_admin_is_rejected_before_session_or_history_reads(rag_app, monkeypatch, groups):
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
        _event({"query": "かごの振動", "includeKnowhow": True}, groups=groups),
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
        assert body["knowhow"]["searchTerms"] == ([] if clarify else ["C-6-R56.1", "TI-1335.pdf"])
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


def test_markdown_search_reuses_the_conversation_rewrite_once(rag_app, monkeypatch):
    captured = _configure_successful_pipeline(rag_app, monkeypatch)
    rewrites = []

    def rewrite(query, *_args, **_kwargs):
        rewrites.append(query)
        return "かごの走行中振動"

    monkeypatch.setattr(rag_app, "maybe_rewrite_search_query", rewrite)
    response = rag_app.handle_rag_request(
        _event({"query": "それについて教えて", "includeKnowhow": True}), None, 0
    )
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["knowhow"]["status"] == "matched"
    assert len(rewrites) == 1
    assert "かごの走行中振動" in captured["search_query"]


def test_kb_hints_never_truncate_a_composed_question_or_its_exclusion(rag_app, monkeypatch):
    captured = _configure_successful_pipeline(rag_app, monkeypatch)
    composed = "かごの走行中振動。" + "あ" * 1980 + "対象外の設備には適用しない"
    monkeypatch.setattr(rag_app, "compose_search_query", lambda *_args: composed)
    response = rag_app.handle_rag_request(
        _event({"query": "対象外です", "includeKnowhow": True}), None, 0
    )
    assert response["statusCode"] == 200
    assert captured["search_query"] == composed
    assert json.loads(response["body"])["knowhow"]["searchTerms"] == []


def test_private_markdown_index_cannot_use_the_document_download_route(rag_app, monkeypatch):
    monkeypatch.setattr(rag_app, "DOCUMENTS_BUCKET", "shared-documents")
    monkeypatch.setattr(rag_app, "KNOWHOW_INDEX_BUCKET", "shared-documents")
    monkeypatch.setattr(rag_app, "KNOWHOW_INDEX_KEY", "private-senpai/index.json")
    assert not rag_app.is_allowed_document_uri("s3://shared-documents/private-senpai/index.json")
    assert rag_app.is_allowed_document_uri("s3://shared-documents/ordinary.pdf")


def test_index_bucket_must_be_separate_from_ordinary_document_buckets(rag_app, monkeypatch):
    _configure_successful_pipeline(rag_app, monkeypatch)
    monkeypatch.setattr(rag_app, "DOCUMENTS_BUCKET", "private-bucket")
    response = rag_app.handle_rag_request(
        _event({"query": "かごの走行中振動", "includeKnowhow": True}), None, 0
    )
    assert response["statusCode"] == 503


VERIFIED_SCOPE = {
    "scope_status": "verified",
    "scope_verified_by": "reviewer",
    "scope_verified_at": "2026-10-20",
}


def _two_product_index(other_scope=None):
    index = _index()
    other = dict(index["cards"][0])
    other.update(
        knowledgeId="KH-SYN-ESC",
        sourceRefs=[{"ref_type": "kb_document", "document_number": "E-1-ESC", "kb_filename": "ESC-1.pdf"}],
        modelScope={"product_lines": ["escalator"], **(VERIFIED_SCOPE if other_scope is None else other_scope)},
    )
    return {**index, "cards": [index["cards"][0], other]}


def _matched_ids(response):
    return [m["knowledgeId"] for m in json.loads(response["body"])["knowhow"]["matches"]]


def test_model_type_filter_excludes_cards_scoped_only_to_another_product(rag_app, monkeypatch):
    captured = _configure_successful_pipeline(rag_app, monkeypatch)
    monkeypatch.setattr(rag_app, "load_index", lambda **_kwargs: _two_product_index())
    request = {"query": "かごの走行中振動", "includeKnowhow": True}

    unfiltered = rag_app.handle_rag_request(_event(request), None, 0)
    assert sorted(_matched_ids(unfiltered)) == ["KH-SYN-001", "KH-SYN-ESC"]

    filtered = rag_app.handle_rag_request(
        _event({**request, "filters": {"modelType": "AXIEZ"}}), None, 0
    )
    assert _matched_ids(filtered) == ["KH-SYN-001"]
    assert "E-1-ESC" not in captured["search_query"]
    assert "ESC-1.pdf" not in captured["search_query"]


def test_model_type_filter_keeps_unverified_cards(rag_app, monkeypatch):
    _configure_successful_pipeline(rag_app, monkeypatch)
    monkeypatch.setattr(
        rag_app, "load_index", lambda **_kwargs: _two_product_index({"product_lines": ["escalator"]})
    )

    response = rag_app.handle_rag_request(
        _event({"query": "かごの走行中振動", "includeKnowhow": True, "filters": {"modelType": "AXIEZ"}}), None, 0
    )

    assert sorted(_matched_ids(response)) == ["KH-SYN-001", "KH-SYN-ESC"]


def test_knowhow_model_vocabulary_covers_every_ui_model_filter(rag_app):
    retrieval = types.SimpleNamespace(**rag_app.search_index.__globals__)

    assert set(retrieval.MODEL_ALIASES) == set(rag_app.UI_MODEL_FILTERS)
    for key, targets in rag_app.UI_MODEL_FILTERS.items():
        for target in targets:
            assert retrieval.normalize_model_label(target) in retrieval.MODEL_ALIASES[key]


def _matches(response):
    return {m["knowledgeId"]: m for m in json.loads(response["body"])["knowhow"]["matches"]}


def test_model_fit_is_returned_only_when_a_model_filter_is_selected(rag_app, monkeypatch):
    _configure_successful_pipeline(rag_app, monkeypatch)
    monkeypatch.setattr(
        rag_app, "load_index", lambda **_kwargs: _two_product_index({"product_lines": ["escalator"]})
    )
    request = {"query": "かごの走行中振動", "includeKnowhow": True}

    plain = _matches(rag_app.handle_rag_request(_event(request), None, 0))
    assert all("modelFit" not in card and "modelFitProducts" not in card for card in plain.values())

    filtered = _matches(rag_app.handle_rag_request(
        _event({**request, "filters": {"modelType": "AXIEZ"}}), None, 0
    ))
    assert filtered["KH-SYN-ESC"]["modelFit"] == "other_product"
    assert filtered["KH-SYN-ESC"]["modelFitProducts"] == ["エスカレーター"]
    assert filtered["KH-SYN-001"]["modelFit"] in {"matched", "general", "unknown"}
    assert "modelFitProducts" not in filtered["KH-SYN-001"]


def test_model_named_in_the_question_is_applied_like_the_ui_filter(rag_app, monkeypatch):
    """2026-11-12 itai 決定: 先輩チャットで機種が未選択なら、質問に 1 機種の呼び名だけがあれば絞り込む。"""
    _configure_successful_pipeline(rag_app, monkeypatch)
    monkeypatch.setattr(rag_app, "load_index", lambda **_kwargs: _two_product_index())
    seen = {}
    monkeypatch.setattr(rag_app, "needs_clarify", lambda q, filters, history: (seen.update(filters=dict(filters)) or (False, [])))

    response = rag_app.handle_rag_request(_event({"query": "アクシーズのかごの走行中振動", "includeKnowhow": True}), None, 0)
    body = json.loads(response["body"])
    explicit = rag_app.handle_rag_request(_event({"query": "アクシーズのかごの走行中振動", "includeKnowhow": True,
                                                  "filters": {"modelType": "AXIEZ"}}), None, 0)
    assert _matched_ids(response) == _matched_ids(explicit)
    assert seen["filters"]["modelType"] == "AXIEZ"
    assert "質問の文言から機種を AXIEZ と判断して絞り込みました" in json.dumps(body, ensure_ascii=False)

    # UI selection wins; two models or none leave the request unfiltered.
    for query, filters, expected in (
        ("アクシーズのかごの走行中振動", {"modelType": "NEXCUBE"}, "NEXCUBE"),
        ("アクシーズとリンクスのかごの走行中振動", {}, None),
        ("かごの走行中振動", {}, None),
    ):
        seen.clear()
        rag_app.handle_rag_request(_event({"query": query, "includeKnowhow": True, "filters": filters}), None, 0)
        assert seen["filters"].get("modelType") == expected, query


def test_model_in_the_question_is_not_applied_outside_the_senpai_chat(rag_app, monkeypatch):
    _configure_successful_pipeline(rag_app, monkeypatch)
    seen = {}
    monkeypatch.setattr(rag_app, "needs_clarify", lambda q, filters, history: (seen.update(filters=dict(filters)) or (False, [])))
    rag_app.handle_rag_request(_event({"query": "アクシーズのかごの走行中振動"}), None, 0)
    assert "modelType" not in seen["filters"]


def _knowhow_only(rag_app, monkeypatch, index=None):
    _configure_successful_pipeline(rag_app, monkeypatch)
    if index is not None:
        monkeypatch.setattr(rag_app, "load_index", lambda **_kwargs: index)
    calls = {"retrieve": 0, "generate": []}
    monkeypatch.setattr(rag_app, "retrieve_for_normal_query",
                        lambda *_a, **_k: calls.__setitem__("retrieve", calls["retrieve"] + 1) or {"retrievalResults": []})
    monkeypatch.setattr(rag_app, "needs_clarify", lambda *_a: (_ for _ in ()).throw(AssertionError("clarify gate used")))
    monkeypatch.setattr(rag_app, "invoke_generation",
                        lambda _client, _model, system, messages, **_k: calls["generate"].append((system, messages)) or ("ノウハウの整理", {}, "end_turn"))
    return calls


def test_knowhow_only_answers_from_cards_without_kb_search(rag_app, monkeypatch):
    """D16（設計 rag-two-modes §11.13）: 先輩チャットはノウハウだけで答え、技術KB・法令KBを検索しない。"""
    calls = _knowhow_only(rag_app, monkeypatch)
    response = rag_app.handle_rag_request(
        _event({"query": "かごの走行中振動", "includeKnowhow": True, "knowhowOnly": True}), None, 0)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200 and body["responseType"] == "pages"
    assert calls["retrieve"] == 0 and len(calls["generate"]) == 1
    system, messages = calls["generate"][0]
    assert "検証済みのノウハウカードだけ" in system
    final = messages[-1]["content"]
    assert "KH-SYN-001" in final[0]["text"] and "かごの走行中振動" in final[-1]["text"]
    assert body["content"].startswith("※ノウハウは現場の経験から整理した参考情報で、正規文書ではありません。")
    assert body["content"].endswith("ノウハウの整理")
    assert body["citations"] == [] and body["sourceDocuments"] == [] and body["knowhow"]["matches"]


def test_knowhow_only_without_a_match_does_not_call_the_model(rag_app, monkeypatch):
    calls = _knowhow_only(rag_app, monkeypatch)
    response = rag_app.handle_rag_request(
        _event({"query": "まったく関係のない質問ZZQQ", "includeKnowhow": True, "knowhowOnly": True}), None, 0)
    body = json.loads(response["body"])
    assert body["responseType"] == "not_found" and calls["generate"] == [] and calls["retrieve"] == 0
    assert "該当するノウハウはありません" in body["content"]


def test_knowhow_only_adds_the_safety_notice_in_code(rag_app, monkeypatch):
    _knowhow_only(rag_app, monkeypatch)
    response = rag_app.handle_rag_request(
        _event({"query": "かごの走行中振動のとき作業してもよいか", "includeKnowhow": True, "knowhowOnly": True}), None, 0)
    assert "安全・法令・作業可否に関わる内容は、ここでは断定しません" in json.loads(response["body"])["content"]


def test_knowhow_only_is_validated(rag_app, monkeypatch):
    _knowhow_only(rag_app, monkeypatch)
    for body in ({"query": "かご", "knowhowOnly": True}, {"query": "かご", "includeKnowhow": True, "knowhowOnly": "true"}):
        assert rag_app.handle_rag_request(_event(body), None, 0)["statusCode"] == 400
