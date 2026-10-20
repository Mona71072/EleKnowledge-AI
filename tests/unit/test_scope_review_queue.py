"""Tests for the scope review queue generator (synthetic cards only, no network)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "knowledge" / "build_scope_review_queue.py"


def _module():
    spec = importlib.util.spec_from_file_location("build_scope_review_queue_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def _write_card(root: Path, knowledge_id: str, scope_yaml: str, *, title: str = "合成カード") -> None:
    directory = root / "cards" / "practice-guides"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{knowledge_id}.md").write_text(
        f"---\nknowledge_id: {knowledge_id}\nkind: practice_guide\nstatus: draft\n"
        f"title: \"{title}\"\nmodel_scope:\n{scope_yaml}\n---\n\n# body\n",
        encoding="utf-8",
    )


@pytest.fixture
def cards_root(tmp_path):
    root = tmp_path / "knowledge"
    _write_card(root, "KH-P1", '  product_lines: ["AXIEZ"]\n  scope_note: "全エレ機種で共通"')
    _write_card(root, "KH-P1B", '  product_lines: ["Nexcube"]\n  lists_model_label: ["全エレ機種"]')
    _write_card(root, "KH-P2", '  product_lines: ["AXIEZ-LINKs"]')
    _write_card(root, "KH-P3", '  control_methods: ["VFGH"]\n  model_abbreviations: ["VFGH"]')
    _write_card(root, "KH-P4", '  lists_model_label: ["全エレ機種"]')
    _write_card(root, "KH-P4E", "  product_lines: []")
    _write_card(
        root, "KH-DONE",
        '  product_lines: ["AXIEZ"]\n  scope_status: verified\n'
        '  scope_verified_by: reviewer\n  scope_verified_at: "2026-10-20"',
    )
    return root


def _priorities(module, root):
    return {row.knowledge_id: row.priority for row in module.collect_rows(root)}


def test_cards_are_assigned_to_priorities(cards_root):
    assert _priorities(_module(), cards_root) == {
        "KH-P1": "P1", "KH-P1B": "P1", "KH-P2": "P2", "KH-P3": "P3", "KH-P4": "P4", "KH-P4E": "P4",
    }


def test_verified_cards_are_not_queued_but_counted(cards_root):
    module = _module()
    assert "KH-DONE" not in _priorities(module, cards_root)
    assert module.render_queue(cards_root).count("検証済み") >= 1


def test_render_is_deterministic_and_groups_by_priority(cards_root):
    module = _module()
    first = module.render_queue(cards_root)
    assert first == module.render_queue(cards_root)
    assert first.index("## P1") < first.index("## P2") < first.index("## P3") < first.index("## P4")
    assert "scope_status: verified" in first
    assert "build_scope_review_queue.py" in first
    assert "機種フィルタ対象外" in first
    assert "[KH-P1](../../cards/practice-guides/KH-P1.md)" in first


def test_p4_lists_no_per_card_table_rows_for_generic_cards(cards_root):
    section = _module().render_queue(cards_root).split("## P4", 1)[1]
    assert "KH-P4E" in section and "KH-P4](" not in section


def test_main_writes_queue_file(cards_root, tmp_path):
    module = _module()
    out = tmp_path / "queues" / "scope-review" / "QUEUE.md"

    assert module.main(["--knowledge-root", str(cards_root), "--output", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == module.render_queue(cards_root)


def test_unparseable_card_is_reported_not_fatal(cards_root):
    (cards_root / "cards" / "practice-guides" / "KH-BAD.md").write_text("---\n: [\n---\n", encoding="utf-8")

    assert "KH-BAD" in _module().render_queue(cards_root)
