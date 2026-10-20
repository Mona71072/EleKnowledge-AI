"""Structure check for the senpai research end-to-end eval draft (no network).

Validates tests/fixtures/knowledge/senpai-research-eval.json against the layer/kind
enums, model keys, and the knowledge ids that exist in knowledge/cards.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/knowledge/senpai-research-eval.json"
CARDS_DIR = ROOT / "knowledge/cards"

LAYERS = {
    "simple_lookup",
    "cross_source",
    "ambiguous_model",
    "vague_or_colloquial",
    "compound",
    "no_evidence",
    "injection",
    "clarify_needed",
}
KINDS = {"answer", "clarify", "not_found", "any"}
MODEL_TYPES = {"AXIEZ", "AXIEZ-LINKs", "NEXCUBE", "メルシティ", "メルワイド", "エスカレーター"}
CASE_ID_RE = re.compile(r"^SR-\d{3}$")
KNOWLEDGE_ID_RE = re.compile(r"^knowledge_id:\s*(\S+)\s*$", re.MULTILINE)
CASE_KEYS = {"id", "layer", "question", "expect", "checks", "rationale"}
EXPECT_KEYS = {
    "kind",
    "lawRelevant",
    "knowhowShouldInclude",
    "knowhowShouldNotUseAsAuthority",
    "mustMentionModel",
    "mustNotAttributeTo",
    "techDocsHint",
}


def _load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _card_knowledge_ids() -> set[str]:
    ids: set[str] = set()
    for path in CARDS_DIR.rglob("*.md"):
        head = path.read_text(encoding="utf-8")[:2000]
        match = KNOWLEDGE_ID_RE.search(head)
        if match:
            ids.add(match.group(1))
    return ids


@pytest.fixture(scope="module")
def data() -> dict:
    return _load()


@pytest.fixture(scope="module")
def cases(data: dict) -> list[dict]:
    return data["cases"]


def test_top_level_structure(data: dict) -> None:
    assert data["schemaVersion"] == 1
    assert data["purpose"] == "senpai-research-e2e-eval-draft"
    assert data["status"] == "draft"
    assert isinstance(data["notes"], str) and data["notes"].strip()
    assert isinstance(data["cases"], list) and data["cases"]


def test_case_fields_and_types(cases: list[dict]) -> None:
    for case in cases:
        assert CASE_KEYS <= set(case), case.get("id")
        assert set(case) <= CASE_KEYS | {"modelType"}, case["id"]
        assert CASE_ID_RE.match(case["id"]), case["id"]
        assert isinstance(case["question"], str) and case["question"].strip(), case["id"]
        assert isinstance(case["rationale"], str) and case["rationale"].strip(), case["id"]

        checks = case["checks"]
        assert isinstance(checks, list) and 1 <= len(checks) <= 3, case["id"]
        assert all(isinstance(c, str) and c.strip() for c in checks), case["id"]

        expect = case["expect"]
        assert set(expect) == EXPECT_KEYS, case["id"]


def test_ids_are_unique(cases: list[dict]) -> None:
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))


def test_layers_are_allowed_and_each_has_at_least_two(cases: list[dict]) -> None:
    counts = Counter(case["layer"] for case in cases)
    assert set(counts) <= LAYERS
    for layer in LAYERS:
        assert counts[layer] >= 2, f"layer {layer} has {counts[layer]} cases"


def test_model_type_values_are_valid(cases: list[dict]) -> None:
    for case in cases:
        if "modelType" in case:
            assert case["modelType"] in MODEL_TYPES, case["id"]


def test_expect_values_are_valid(cases: list[dict]) -> None:
    for case in cases:
        expect = case["expect"]
        cid = case["id"]
        assert expect["kind"] in KINDS, cid
        assert expect["lawRelevant"] in (True, False, None), cid
        assert expect["knowhowShouldNotUseAsAuthority"] is True, cid
        assert expect["mustMentionModel"] is None or expect["mustMentionModel"] in MODEL_TYPES, cid
        assert isinstance(expect["mustNotAttributeTo"], list), cid
        assert set(expect["mustNotAttributeTo"]) <= MODEL_TYPES, cid
        assert isinstance(expect["knowhowShouldInclude"], list), cid
        assert isinstance(expect["techDocsHint"], list), cid
        assert all(isinstance(h, str) and h.strip() for h in expect["techDocsHint"]), cid


def test_knowhow_ids_exist_in_cards(cases: list[dict]) -> None:
    known = _card_knowledge_ids()
    assert known, "no knowledge_id found under knowledge/cards"
    missing = [
        (case["id"], kid)
        for case in cases
        for kid in case["expect"]["knowhowShouldInclude"]
        if kid not in known
    ]
    assert missing == []


def test_knowhow_ids_are_strings(cases: list[dict]) -> None:
    for case in cases:
        assert all(isinstance(k, str) and k.startswith("KH-") for k in case["expect"]["knowhowShouldInclude"]), case["id"]
