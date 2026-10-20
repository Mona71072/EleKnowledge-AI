"""Regression tests for Lists ID reconciliation."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "knowledge" / "build_reconcile_ledger.py"


def _load_module():
    import sys

    spec = importlib.util.spec_from_file_location("build_reconcile_ledger", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_explicit_list_id_in_evidence_title():
    mod = _load_module()
    text = """---
record_id: x
evidence_sources:
  - source_id: "evidence-list-foo-id345"
    title: "リスト項目（ID345）"
---
body
"""
    ids = mod.list_ids_from_draft(Path("x.md"), text, include_source_id_suffix=False)
    assert ids == {"345"}


def test_training_suffix_not_matched_primary():
    mod = _load_module()
    text = """---
evidence_sources:
  - source_id: "evidence-training-m-series-2025-1"
    title: "研修1"
---
"""
    ids = mod.list_ids_from_draft(Path("x.md"), text, include_source_id_suffix=False)
    assert ids == set()


def test_extended_requires_list_marker_in_source_id():
    mod = _load_module()
    text = """---
evidence_sources:
  - source_id: "evidence-training-m-series-2025-1"
---
"""
    assert mod.list_ids_from_draft(Path("x.md"), text, include_source_id_suffix=True) == set()

    text2 = """---
evidence_sources:
  - source_id: "evidence-list-hall-indicator-drawing-number-232"
---
"""
    assert mod.list_ids_from_draft(Path("x.md"), text2, include_source_id_suffix=True) == {"232"}


def test_nexiez_doc_suffix_not_extended_match():
    mod = _load_module()
    text = """---
evidence_sources:
  - source_id: "evidence-nexiez-vfglf-door-operator-wiring-4"
---
"""
    assert mod.list_ids_from_draft(Path("x.md"), text, include_source_id_suffix=True) == set()
