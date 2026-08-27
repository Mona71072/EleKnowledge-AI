"""Parity tests for the extracted answer-context policy module."""
import importlib.util
import os
import sys

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")
RAG_DIR = os.path.normpath(os.path.join(BASE, "lambda/rag/rag-function"))


def _load(name: str, filename: str):
    path = os.path.join(RAG_DIR, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def modules():
    os.environ.setdefault("CHATLOGS_TABLE", "test-chatlogs")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    if RAG_DIR not in sys.path:
        sys.path.insert(0, RAG_DIR)
    return _load("rag_answer_legacy", "app.py"), _load("rag_answer_new", "answer_policy.py")


def _result(uri="s3://bucket/C-123.pdf", score=0.82, text="火災管制の解除条件"):
    return {
        "score": score,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": uri,
            "title": "火災管制",
            "category": "C資料",
            "model_type": "AXIEZ",
        },
        "content": {"text": text},
    }


def test_question_text_matches_existing_behavior(modules):
    legacy, new = modules
    cases = [
        ("火災管制は？", None),
        ("かご", "異音がする\nかご"),
        ("", "検索文"),
    ]
    for query, search_query in cases:
        assert new.build_question_text_for_claude(query, search_query) == legacy.build_question_text_for_claude(
            query, search_query
        )


def test_references_block_matches_existing_behavior(modules):
    legacy, new = modules
    results = [_result()]
    assert new.build_references_block(results) == legacy.build_references_block(results)


def test_references_block_matches_for_image_chunk(modules):
    legacy, new = modules
    image = {
        "score": 0.75,
        "metadata": {
            "x-amz-bedrock-kb-source-uri": "s3://bucket/drawing.pdf",
            "category": "据付場用図",
            "model_type": "AXIEZ",
        },
        "content": {"type": "IMAGE", "byteContent": "data:image/png;base64,XYZ"},
    }
    assert new.build_references_block([image]) == legacy.build_references_block([image])


def test_claude_messages_first_turn_matches_existing_behavior(modules):
    legacy, new = modules
    results = [_result()]
    assert new.build_claude_messages("火災管制は？", results) == legacy.build_claude_messages(
        "火災管制は？", results
    )


def test_claude_messages_history_matches_existing_behavior(modules):
    legacy, new = modules
    history = [
        {"role": "assistant", "content": "古い回答"},
        {"role": "user", "content": "前の質問"},
        {"role": "assistant", "content": "前の回答"},
    ]
    results = [_result()]
    assert new.build_claude_messages(
        "追記",
        results,
        chat_history=history,
        search_query="前の質問\n追記",
    ) == legacy.build_claude_messages(
        "追記",
        results,
        chat_history=history,
        search_query="前の質問\n追記",
    )


def test_append_message_merging_matches_existing_behavior(modules):
    legacy, new = modules
    legacy_messages = []
    new_messages = []
    for role, content in [("user", "a"), ("user", "b"), ("assistant", "c")]:
        legacy.append_claude_message(legacy_messages, role, content)
        new.append_claude_message(new_messages, role, content)
    assert new_messages == legacy_messages
