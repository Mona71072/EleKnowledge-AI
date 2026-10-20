"""eval_senpai_retrieval.py --from-cards builds a temporary index from raw cards, evaluates, and deletes it."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/knowledge/eval_senpai_retrieval.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/knowledge/synthetic/contract-root"

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None or not (ROOT / "frontend/node_modules/yaml").exists(),
    reason="needs node and frontend dependencies (npm ci)",
)


def _module():
    spec = importlib.util.spec_from_file_location("eval_senpai_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _cases(path: Path) -> Path:
    path.write_text(json.dumps({"cases": [
        {"id": "T-1", "category": "synthetic", "query": "qxpositive",
         "expect": {"status": "matched", "mustInclude": ["KH-SYN-POSITIVE"], "mustNotInclude": []}},
        {"id": "T-2", "category": "synthetic", "query": "qxexcl",
         "expect": {"status": "not_found", "mustInclude": [], "mustNotInclude": []}},
    ]}), encoding="utf-8")
    return path


def test_from_cards_evaluates_real_build_output_and_removes_the_temp_index(tmp_path, monkeypatch, capsys):
    module = _module()
    created: list[Path] = []
    real_mkdtemp = tempfile.mkdtemp

    def recording_mkdtemp(*args, **kwargs):
        path = Path(real_mkdtemp(*args, **kwargs))
        created.append(path)
        return str(path)

    monkeypatch.setattr(tempfile, "mkdtemp", recording_mkdtemp)
    code = module.main(["--from-cards", str(FIXTURE_ROOT), "--cases", str(_cases(tmp_path / "cases.json"))])
    out = capsys.readouterr().out
    assert code == 0
    assert "T-1" in out and "PASS" in out and "合計: 2/2 PASS" in out
    assert created and all(not path.exists() for path in created)


def test_index_and_from_cards_are_mutually_exclusive(tmp_path, capsys):
    module = _module()
    with pytest.raises(SystemExit):
        module.main(["--from-cards", str(FIXTURE_ROOT), "--index", str(tmp_path / "x.json")])
    with pytest.raises(SystemExit):
        module.main([])


def test_from_cards_reports_check_failures_but_still_cleans_up(tmp_path, monkeypatch, capsys):
    module = _module()
    root = tmp_path / "repo"
    shutil.copytree(FIXTURE_ROOT, root)
    bad = root / "knowledge/cards/practice-guides/KH-SYN-BAD.md"
    bad.write_text("---\nknowledge_id: KH-SYN-BAD\nstatus: draft\ncard_version: 1\ntitle: bad\n"
                   "source_refs:\n  - ref_type: lists_item\n    bogus: 1\n    list_item_id: X\n---\nbody\n",
                   encoding="utf-8")
    code = module.main(["--from-cards", str(root), "--cases", str(_cases(tmp_path / "cases.json"))])
    captured = capsys.readouterr()
    assert code == 0
    assert "KH-SYN-BAD" in captured.out + captured.err
    assert "合計: 2/2 PASS" in captured.out
