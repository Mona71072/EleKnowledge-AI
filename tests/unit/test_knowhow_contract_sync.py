"""Cross-language contract: vocab lists and the real built index must agree everywhere.

The same lists live in the Lambda (Python), the index builder and the frontend
validator (JavaScript). These tests fail when one copy drifts, and they run the
Lambda against an index produced by the real build code instead of a hand-made one.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL = ROOT / "lambda/rag/rag-function/knowhow_retrieval.py"
BUILD_SCRIPT = ROOT / "scripts/knowledge/build-senpai-index.mjs"
FRONTEND_LIB = ROOT / "frontend/src/lib/knowledge-research.mjs"
FIXTURE = ROOT / "tests/fixtures/knowledge/synthetic/built-index.json"
QUEUE_SCRIPT = ROOT / "scripts/knowledge/build_scope_review_queue.py"
QUEUE_FILE = ROOT / "knowledge/queues/scope-review/QUEUE.md"
REGEN = "npm --prefix frontend run knowledge:regen-contract-fixture"


def _retrieval():
    spec = importlib.util.spec_from_file_location("knowhow_retrieval_contract", RETRIEVAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _js_set(path: Path, name: str) -> set[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"const {name} = (?:Object\.freeze\()?new Set\(\[(.*?)\]\)", text, re.DOTALL)
    assert match, f"{name} not found in {path.name}"
    return set(re.findall(r"'([^']+)'", match.group(1)))


def test_model_scope_keys_match_across_lambda_builder_and_frontend():
    lambda_keys = set(_retrieval().MODEL_SCOPE_KEYS)
    assert lambda_keys == _js_set(BUILD_SCRIPT, "MODEL_SCOPE_KEYS")
    assert lambda_keys == _js_set(FRONTEND_LIB, "KNOWHOW_SCOPE_FIELDS")


def test_positive_scope_keys_match_between_lambda_and_builder():
    assert set(_retrieval().POSITIVE_SCOPE_KEYS) == _js_set(BUILD_SCRIPT, "POSITIVE_SCOPE_KEYS")


def test_source_ref_keys_match_between_lambda_builder_and_frontend():
    # Builder output keys = SOURCE_REF_KEYS (annotation keys are dropped before output).
    lambda_keys = set(_retrieval().SOURCE_REF_KEYS)
    assert lambda_keys == _js_set(BUILD_SCRIPT, "SOURCE_REF_KEYS")
    assert lambda_keys == _js_set(FRONTEND_LIB, "KNOWHOW_SOURCE_FIELDS")


def test_annotation_keys_never_overlap_output_keys():
    assert not _js_set(BUILD_SCRIPT, "SOURCE_REF_ANNOTATION_KEYS") & set(_retrieval().SOURCE_REF_KEYS)


def test_scope_verification_keys_match_between_lambda_and_builder():
    assert set(_retrieval().SCOPE_VERIFICATION_KEYS) == _js_set(BUILD_SCRIPT, "SCOPE_VERIFICATION_KEYS")


@pytest.fixture(scope="module")
def retrieval():
    return _retrieval()


@pytest.fixture(scope="module")
def index(retrieval):
    return retrieval.parse_index(FIXTURE.read_bytes())


def _ids(result):
    return [card["knowledgeId"] for card in result["matches"]]


def test_lambda_accepts_the_really_built_fixture(index):
    assert {c["knowledgeId"] for c in index["cards"]} == {"KH-SYN-POSITIVE", "KH-SYN-CONFLICT", "KH-SYN-UNVERIFIED"}


@pytest.mark.parametrize("term", ["qxexcl", "qxmay", "qxnote"])
def test_terms_only_in_excludes_may_apply_to_or_scope_note_do_not_surface_a_card(retrieval, index, term):
    result = retrieval.search_index(index, term)
    assert result["status"] == "not_found", (
        f"{term} surfaced a card; the builder or scorer let a non-positive scope field leak. "
        f"If the fixture is outdated run: {REGEN}"
    )


def test_positive_term_surfaces_the_card(retrieval, index):
    assert "KH-SYN-POSITIVE" in _ids(retrieval.search_index(index, "qxpositive"))


def test_verified_conflicting_card_is_dropped_by_model_filter_and_unverified_is_kept(retrieval, index):
    unfiltered = _ids(retrieval.search_index(index, "synthzeta"))
    assert {"KH-SYN-CONFLICT", "KH-SYN-UNVERIFIED"} <= set(unfiltered)
    filtered = _ids(retrieval.search_index(index, "synthzeta", model_type="AXIEZ"))
    assert "KH-SYN-CONFLICT" not in filtered
    assert "KH-SYN-UNVERIFIED" in filtered


def test_scope_review_queue_is_fresh(tmp_path):
    out = tmp_path / "QUEUE.md"
    subprocess.run([sys.executable, str(QUEUE_SCRIPT), "--output", str(out)], check=True,
                   capture_output=True, cwd=ROOT)
    assert out.read_bytes() == QUEUE_FILE.read_bytes(), (
        "knowledge/queues/scope-review/QUEUE.md is stale. Regenerate with: "
        "python scripts/knowledge/build_scope_review_queue.py"
    )
