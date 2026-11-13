"""Cross-language contract: vocab lists and the real built index must agree everywhere.

The same lists live in the Lambda (Python), the index builder and the frontend
validator (JavaScript). These tests fail when one copy drifts, and they run the
Lambda against an index produced by the real build code instead of a hand-made one.
"""
from __future__ import annotations

import hashlib
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
# MODEL_ALIASES・汎用ラベルは語彙ファイルから生成し、build-senpai-index.mjs と画面が import する。
BUILD_VOCAB = ROOT / "scripts/knowledge/vocabulary.generated.mjs"
FRONTEND_VOCAB = ROOT / "frontend/src/data/kb-model-types.generated.mjs"
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


def _js_block(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"const {name} = (?:Object\.freeze\()?\{{(.*?)\n?\}}\)?;", text, re.DOTALL)
    assert match, f"{name} not found in {path.name}"
    return match.group(1)


def _js_string_map(path: Path, name: str) -> dict[str, str]:
    return dict(re.findall(r"(\w+): '([^']+)'", _js_block(path, name)))


def _js_alias_map(path: Path, name: str) -> dict[str, set[str]]:
    return {key: set(re.findall(r"'([^']+)'", values))
            for key, values in re.findall(r"'([^']+)': (?:Object\.freeze\()?\[([^\]]*)\]", _js_block(path, name))}


def _js_string(path: Path, name: str) -> str:
    match = re.search(rf"const {name} = '([^']*)';", path.read_text(encoding="utf-8"))
    assert match, f"{name} not found in {path.name}"
    return match.group(1)


def _js_regex_source(path: Path, name: str) -> str:
    match = re.search(rf"const {name} = /(.*?)/u;", path.read_text(encoding="utf-8"))
    assert match, f"{name} not found in {path.name}"
    return match.group(1)


def test_source_types_and_identity_keys_match_across_lambda_builder_and_frontend():
    lambda_module = _retrieval()
    assert set(lambda_module.SOURCE_TYPES) == _js_set(BUILD_SCRIPT, "SOURCE_REF_TYPES")
    assert dict(lambda_module.SOURCE_ID_KEYS) == _js_string_map(BUILD_SCRIPT, "SOURCE_ID_KEYS")
    assert dict(lambda_module.SOURCE_ID_KEYS) == _js_string_map(FRONTEND_LIB, "KNOWHOW_SOURCE_IDS")
    assert set(lambda_module.KNOWHOW_ORIGINS) == _js_set(BUILD_SCRIPT, "KNOWHOW_ORIGINS")
    assert set(lambda_module.KNOWHOW_ORIGINS) == _js_set(FRONTEND_LIB, "KNOWHOW_ORIGINS")


def test_scope_status_values_and_date_pattern_match_between_lambda_and_builder():
    lambda_module = _retrieval()
    assert set(lambda_module.SCOPE_STATUSES) == _js_set(BUILD_SCRIPT, "SCOPE_STATUSES")
    assert lambda_module.SCOPE_DATE_PATTERN.pattern == _js_regex_source(BUILD_SCRIPT, "SCOPE_DATE")


def test_model_aliases_and_generic_labels_match_between_lambda_and_builder():
    lambda_module = _retrieval()
    assert {key: set(values) for key, values in lambda_module.MODEL_ALIASES.items()} == _js_alias_map(BUILD_VOCAB, "MODEL_ALIASES")
    assert lambda_module.GENERIC_ELEVATOR_LABEL == _js_string(BUILD_VOCAB, "GENERIC_ELEVATOR_LABEL")
    assert lambda_module.GENERIC_ESCALATOR_LABEL == _js_string(BUILD_VOCAB, "GENERIC_ESCALATOR_LABEL")
    build_text = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "from './vocabulary.generated.mjs'" in build_text
    assert "const MODEL_ALIASES" not in build_text
    assert set(lambda_module.MODEL_CLASSIFY_KEYS) == _js_set(BUILD_SCRIPT, "MODEL_CLASSIFY_KEYS")


def test_committed_card_version_ledger_matches_every_card_file():
    """Independent of node: a body edit without a card_version bump and ledger regeneration fails here too."""
    ledger = ROOT / "knowledge/registry/card-versions.jsonl"
    assert ledger.exists(), "run: node scripts/knowledge/build-senpai-index.mjs ledger ."
    entries = {}
    for line in ledger.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        assert list(item) == ["knowledgeId", "cardVersion", "sha256"]
        assert item["knowledgeId"] not in entries
        entries[item["knowledgeId"]] = item
    cards = {}
    for path in sorted((ROOT / "knowledge/cards").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        front = text.split("---", 2)[1]
        card_id = re.search(r"^knowledge_id:\s*(\S+)", front, re.MULTILINE).group(1).strip("\"'")
        version = int(re.search(r"^card_version:\s*(\d+)", front, re.MULTILINE).group(1))
        content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        cards[card_id] = (version, hashlib.sha256(content).hexdigest())
    assert set(entries) == set(cards), "ledger and cards differ; run: node scripts/knowledge/build-senpai-index.mjs ledger ."
    for card_id, (version, sha) in cards.items():
        assert (entries[card_id]["cardVersion"], entries[card_id]["sha256"]) == (version, sha), (
            f"{card_id}: bump card_version, then regenerate the ledger")


@pytest.fixture(scope="module")
def retrieval():
    return _retrieval()


@pytest.fixture(scope="module")
def index(retrieval):
    return retrieval.parse_index(FIXTURE.read_bytes())


def _ids(result):
    return [card["knowledgeId"] for card in result["matches"]]


def test_lambda_accepts_the_really_built_fixture(index):
    assert {c["knowledgeId"] for c in index["cards"]} == {"KH-SYN-POSITIVE", "KH-SYN-CONFLICT", "KH-SYN-UNVERIFIED", "KH-SYN-DUPTERMS"}


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


def test_fixture_search_terms_have_no_duplicates(index):
    for card in index["cards"]:
        assert len(card["searchTerms"]) == len(set(card["searchTerms"])), card["knowledgeId"]
    dup = next(card for card in index["cards"] if card["knowledgeId"] == "KH-SYN-DUPTERMS")
    assert dup["searchTerms"].count("qxdupterm") == 1


def test_model_fit_values_and_products_match_between_lambda_and_frontend():
    lambda_module = _retrieval()
    assert set(lambda_module.MODEL_FIT_VALUES) == _js_set(FRONTEND_LIB, "KNOWHOW_MODEL_FITS")
    keys = re.search(r"export const KB_MODEL_KEYS = Object\.freeze\(\[(.*?)\]\);", FRONTEND_VOCAB.read_text(encoding="utf-8"))
    assert keys, "KB_MODEL_KEYS not found"
    assert set(lambda_module.MODEL_ALIASES) == set(re.findall(r"'([^']+)'", keys.group(1)))
    assert "const KNOWHOW_MODEL_PRODUCTS = new Set(KB_MODEL_KEYS);" in FRONTEND_LIB.read_text(encoding="utf-8")
