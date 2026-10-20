"""Bounded, fail-closed retrieval over the explicitly approved Markdown index."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "lambda/rag/rag-function/knowhow_retrieval.py"


def _module():
    spec = importlib.util.spec_from_file_location("knowhow_retrieval_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _card(**overrides):
    body = "## 症状\nかごが走行中に振動する。\n\n## 原因\n取付条件を確認する。\n\n## 対策\n締結状態を確認する。"
    card = {
        "knowledgeId": "KH-AX-001",
        "cardVersion": 2,
        "sha256": hashlib.sha256(body.encode()).hexdigest(),
        "title": "かご走行中の振動",
        "status": "draft",
        "usage": "navigation_only",
        "body": body,
        "searchTerms": ["振動", "走行中", "かご"],
        "sourceRefs": [{"type": "lists_item", "id": "123"}],
        "modelScope": {"modelType": ["AXIEZ"]},
    }
    card.update(overrides)
    return card


def _index(*cards):
    return {
        "schemaVersion": 1,
        "indexVersion": "sha256:" + "a" * 64,
        "generatedAt": "2026-10-20T00:00:00Z",
        "cards": list(cards),
    }


def test_search_returns_relevant_markdown_as_navigation_only_even_when_draft():
    module = _module()

    result = module.search_index(_index(_card()), "かごが走行中に振動")

    assert result["status"] == "matched"
    assert result["indexVersion"] == "sha256:" + "a" * 64
    assert len(result["matches"]) == 1
    match = result["matches"][0]
    assert match["knowledgeId"] == "KH-AX-001"
    assert match["status"] == "draft"
    assert match["usage"] == "navigation_only"
    assert "## 症状" in match["body"] and "## 対策" in match["body"]


def test_search_does_not_match_only_on_common_single_character():
    module = _module()

    result = module.search_index(_index(_card()), "の")

    assert result["status"] == "not_found"
    assert result["matches"] == []


@pytest.mark.parametrize(
    "card_change",
    [
        {"status": "retired"},
        {"usage": "answer_authority"},
        {"knowledgeId": "../outside"},
        {"sha256": "bad-hash"},
        {"sourceRefs": [{"type": "arbitrary_url", "url": "https://example.test"}]},
    ],
)
def test_invalid_card_rejects_entire_index(card_change):
    module = _module()

    with pytest.raises(ValueError):
        module.validate_index(_index(_card(**card_change)))


def test_duplicate_json_keys_are_rejected():
    module = _module()
    duplicate_key_json = (
        '{"schemaVersion":1,"indexVersion":"sha256:' + "a" * 64
        + '","generatedAt":"2026-10-20T00:00:00Z","cards":[],"cards":[]}'
    )

    with pytest.raises(ValueError):
        module.parse_index(duplicate_key_json)


def test_index_size_is_bounded_at_eight_mib():
    module = _module()

    with pytest.raises(ValueError):
        module.parse_index(" " * (8 * 1024 * 1024 + 1))
