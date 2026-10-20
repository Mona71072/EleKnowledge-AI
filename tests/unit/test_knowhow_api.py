"""The Markdown retrieval extension is opt-in and admin-gated at the API boundary."""
import json


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
