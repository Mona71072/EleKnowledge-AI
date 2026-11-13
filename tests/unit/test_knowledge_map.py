"""知識マップの生成（scripts/knowledge/build_knowledge_map.py）。設計: docs/design-2026-11-12-knowledge-map.md §4.5・§5 段階 1。"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/knowledge/build_knowledge_map.py"


@pytest.fixture(scope="module")
def km():
    spec = importlib.util.spec_from_file_location("build_knowledge_map_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def vocab():
    return json.loads((ROOT / "knowledge/registry/applicability-vocabulary.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def resolution():
    path = ROOT / "knowledge/registry/kb-ref-resolution.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _card(**extra):
    meta = {"knowledge_id": "KH-TEST-1", "card_version": 2, "kind": "case_summary", "title": "t",
            "model_scope": {"product_lines": ["AXIEZ"]}, "source_refs": []}
    meta.update(extra)
    return {meta["knowledge_id"]: meta}


def test_builds_from_repository_cards_deterministically(km, vocab, resolution):
    cards = km.read_cards(ROOT / "knowledge/cards")
    first = km.build(cards, vocab, resolution)
    second = km.build(copy.deepcopy(cards), vocab, resolution)
    assert first["sha256"] == second["sha256"]
    assert first["counts"]["cards"] == len(cards) > 0
    assert {"C1", "C2", "R1"} <= set(first["counts"]["edges"])
    node_ids = {n["id"] for n in first["nodes"]}
    item_targets = [e["to"] for e in first["edges"] if not e["to"].split(":", 1)[0] in ("kb", "lists", "onenote", "knowhow")]
    assert set(item_targets) <= node_ids


def test_card_edges_carry_card_version_and_qualifier(km, vocab, resolution):
    cards = _card(model_scope={"product_lines": ["AXIEZ"], "may_apply_to": ["NEXCUBE"], "excludes": ["自由記述"]},
                  source_refs=[{"ref_type": "lists_item", "list_item_id": "1"}])
    result = km.build(cards, vocab, resolution)
    c1 = [e for e in result["edges"] if e["type"] == "C1"]
    assert {(e["to"], e.get("qualifier")) for e in c1} == {
        ("product_line:AXIEZ", None), ("product_line:NEXCUBE", "may_apply")}
    card_edges = [e for e in result["edges"] if e["from"] == "card:KH-TEST-1"]
    assert card_edges and all(e["origin"] == {"knowledge_id": "KH-TEST-1", "card_version": 2} for e in card_edges)
    assert result["unresolved"] == {"C1.excludes": 1}


def test_law_reference_maps_to_versionless_law_id(km, vocab, resolution):
    law = vocab["items"]["laws"][0]
    old_version = law["current_folder"].split("_")[0] + "_20000101_000AC0000000000"
    result = km.build(_card(source_refs=[{"ref_type": "law_rag", "law_id": old_version}]), vocab, resolution)
    [edge] = [e for e in result["edges"] if e["type"] == "C2"]
    assert edge["to"] == law["id"] and edge["law_folder"] == old_version


@pytest.mark.parametrize("cards, message", [
    (_card(model_scope={"product_lines": ["存在しない機種"]}), "項目台帳に無い"),
    (_card(source_refs=[{"ref_type": "law_rag", "law_id": "999AC9999999999_20260101_x"}]), "法令の項目に無い"),
])
def test_unknown_values_fail(km, vocab, resolution, cards, message):
    with pytest.raises(km.KnowledgeMapError, match=message):
        km.build(cards, vocab, resolution)


def test_registry_relation_without_source_or_target_fails(km, vocab, resolution):
    broken = copy.deepcopy(vocab)
    entry = next(e for e in broken["axes"]["product_lines"] if e.get("relations"))
    entry["relations"][0]["target"] = "product_line:無い"
    with pytest.raises(km.KnowledgeMapError, match="存在しない ID"):
        km.build({}, broken, resolution)
    broken = copy.deepcopy(vocab)
    entry = next(e for e in broken["axes"]["product_lines"] if e.get("relations"))
    entry["relations"][0]["source"] = ""
    with pytest.raises(km.KnowledgeMapError, match="出典が無い"):
        km.build({}, broken, resolution)


def test_duplicate_card_ids_fail(km, tmp_path):
    for name in ("a.md", "b.md"):
        (tmp_path / name).write_text("---\nknowledge_id: KH-DUP\n---\n本文\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# 説明\n", encoding="utf-8")
    with pytest.raises(km.KnowledgeMapError, match="重複"):
        km.read_cards(tmp_path)
