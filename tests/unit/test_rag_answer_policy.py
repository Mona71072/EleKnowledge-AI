"""Parity tests for the extracted answer-context policy module.

移行期間限定のテスト: app.py が answer_policy を import するよう配線された時点で
new == legacy は恒真（自明に成立）になるため、配線 PR で本ファイルを
モジュール単体の振る舞いテストへ書き換える（または削除する）こと。
"""
import pytest


@pytest.fixture(scope="module")
def modules(rag_app, load_rag_module):
    return rag_app, load_rag_module("rag_answer_new", "answer_policy.py")


def test_policy_constants_match_existing_behavior(modules):
    legacy, new = modules
    assert new.MAX_IMAGE_BLOCKS == legacy.MAX_IMAGE_BLOCKS


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
