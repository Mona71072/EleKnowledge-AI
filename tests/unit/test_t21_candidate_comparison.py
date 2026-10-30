from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/eval/compare_t21_candidate_strategies.py"
SPEC = importlib.util.spec_from_file_location("t21_candidate_comparison", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
COMPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARE)
FIXTURE = Path(__file__).resolve().parents[1] / "eval/fixtures/t21_synthetic_candidates_v1.json"


def test_t21_strategies_share_a_fixed_synthetic_pool_and_limit() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    report = COMPARE.compare(data)
    policies = report["policies"]
    assert report["candidateRows"] == 21
    assert report["uniqueEvidenceGroups"] == 20
    assert report["sameCandidatePool"] is True
    assert report["externalCalls"] == 0
    assert all(row["candidateLimit"] == 10 and row["selectedCount"] <= 10 for row in policies.values())

    assert policies["A_global_score"]["goldRetained"] == []
    assert policies["B_per_lane_quota"]["goldRetained"] == ["SYN-GOLD-B@p1"]
    assert policies["B_per_lane_quota"]["goldMissed"] == ["SYN-GOLD-A@p11"]
    assert policies["C_dedupe_then_global"] == policies["A_global_score"]
    assert policies["D_equipment_and_version_filter"]["goldRetained"] == [
        "SYN-GOLD-A@p11", "SYN-GOLD-B@p1"
    ]
    assert policies["E_fixed_rerank_scores"]["goldRetained"] == ["SYN-GOLD-B@p1"]


def test_candidate_fixture_rejects_non_synthetic_sources() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["source"] = "production"
    assert "source=synthetic" in COMPARE.validate_fixture(data)
