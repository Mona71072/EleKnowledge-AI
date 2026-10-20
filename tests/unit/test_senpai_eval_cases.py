"""Structural checks for the Senpai knowhow retrieval eval case draft.

These tests do not call the retrieval function or the network. They only
verify that the case file is well formed and that every referenced
knowledgeId is a real card ID in knowledge/cards.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = REPO_ROOT / "tests" / "fixtures" / "knowledge" / "senpai-eval-cases.json"
CARDS_ROOT = REPO_ROOT / "knowledge" / "cards"

ALLOWED_CATEGORIES = {
    "markdown_sufficient",
    "needs_kb",
    "no_markdown",
    "condition_mismatch",
    "conflict",
    "stale_or_unauthorized",
    "search_limit",
    "excludes_not_boost",
    "model_filter",
}
ALLOWED_MODEL_TYPES = {
    "AXIEZ",
    "AXIEZ-LINKs",
    "NEXCUBE",
    "メルシティ",
    "メルワイド",
    "エスカレーター",
}
ALLOWED_STATUS = {"matched", "not_found", "any"}
REQUIRED_CASE_KEYS = {"id", "category", "query", "expect", "rationale"}
ID_PATTERN = re.compile(r"^SE-\d{3}$")
KNOWLEDGE_ID_LINE = re.compile(r"^knowledge_id:\s*(\S+)\s*$", re.MULTILINE)


def _load_cases() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _card_ids() -> set[str]:
    ids: set[str] = set()
    for path in CARDS_ROOT.glob("*/*.md"):
        text = path.read_text(encoding="utf-8")
        frontmatter = text.split("---\n", 2)[1] if text.startswith("---\n") else ""
        match = KNOWLEDGE_ID_LINE.search(frontmatter)
        if match:
            ids.add(match.group(1))
    return ids


@pytest.fixture(scope="module")
def data() -> dict:
    return _load_cases()


@pytest.fixture(scope="module")
def card_ids() -> set[str]:
    return _card_ids()


def test_top_level_structure(data: dict) -> None:
    assert data["schemaVersion"] == 1
    assert data["purpose"] == "senpai-knowhow-retrieval-eval-draft"
    assert data["status"] == "draft"
    assert isinstance(data["notes"], str) and data["notes"].strip()
    assert isinstance(data["cases"], list) and data["cases"]


def test_each_case_has_required_keys_and_valid_values(data: dict) -> None:
    for case in data["cases"]:
        assert REQUIRED_CASE_KEYS <= set(case), case.get("id")
        assert ID_PATTERN.match(case["id"]), case["id"]
        assert case["category"] in ALLOWED_CATEGORIES, case["id"]
        assert isinstance(case["query"], str) and case["query"].strip(), case["id"]
        assert isinstance(case["rationale"], str) and case["rationale"].strip(), case["id"]
        assert "modelType" not in case or case["modelType"] in ALLOWED_MODEL_TYPES, case["id"]


def test_expect_block_is_well_formed(data: dict) -> None:
    for case in data["cases"]:
        expect = case["expect"]
        assert set(expect) == {"mustInclude", "mustNotInclude", "status"}, case["id"]
        for key in ("mustInclude", "mustNotInclude"):
            assert isinstance(expect[key], list), f"{case['id']} {key}"
            assert all(isinstance(item, str) for item in expect[key]), f"{case['id']} {key}"
        assert expect["status"] in ALLOWED_STATUS, case["id"]
        overlap = set(expect["mustInclude"]) & set(expect["mustNotInclude"])
        assert not overlap, f"{case['id']} overlap: {sorted(overlap)}"


def test_case_ids_are_unique(data: dict) -> None:
    ids = [case["id"] for case in data["cases"]]
    assert len(ids) == len(set(ids))


def test_referenced_knowledge_ids_exist_as_cards(data: dict, card_ids: set[str]) -> None:
    missing = []
    for case in data["cases"]:
        for key in ("mustInclude", "mustNotInclude"):
            for knowledge_id in case["expect"][key]:
                if knowledge_id not in card_ids:
                    missing.append((case["id"], knowledge_id))
    assert not missing, f"unknown knowledgeIds: {missing}"


def test_every_category_is_covered(data: dict) -> None:
    covered = {case["category"] for case in data["cases"]}
    assert covered == ALLOWED_CATEGORIES, sorted(ALLOWED_CATEGORIES - covered)


def test_model_filter_cases_set_model_type(data: dict) -> None:
    for case in data["cases"]:
        if case["category"] == "model_filter":
            assert "modelType" in case, case["id"]
