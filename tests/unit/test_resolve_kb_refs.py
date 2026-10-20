"""Unit tests for KB document_number resolution."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "resolve_kb_refs",
    ROOT / "scripts" / "knowledge" / "resolve_kb_refs.py",
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


def test_normalize_ref():
    assert mod.normalize_ref("S-EL・323") == "S-EL-323"


def test_resolve_exact_ti():
    entries = [
        mod.IndexEntry("TI-1335.pdf", "TI-1335", "テクニカルインフォメーション", "AXIEZ-LINKs", "2026-08-26")
    ]
    r = mod.resolve_one("TI-1335", entries)
    assert r["kb_verify_status"] == "catalog_matched"
    assert r["kb_filename"] == "TI-1335.pdf"


def test_resolve_not_in_catalog():
    entries = [
        mod.IndexEntry("TI-1335.pdf", "TI-1335", "C資料", None, "2026-08-26"),
    ]
    r = mod.resolve_one("C-6-R56.1", entries)
    assert r["kb_verify_status"] == "not_in_catalog"
