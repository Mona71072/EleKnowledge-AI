from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/knowledge/evaluate_rag_quality.py"
SPEC = importlib.util.spec_from_file_location("rag_quality_eval", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)
CASE_FILE = Path(__file__).resolve().parents[1] / "fixtures/knowledge/rag-quality-eval-v1.json"


def _case(case_id: str, decision: str = "answer", *, law: bool = False) -> dict:
    return {
        "id": case_id,
        "category": "legal_and_technical" if law else "model_specific",
        "question": "synthetic question",
        "premises": [],
        "majorFailure": "synthetic severe failure",
        "expected": {
            "decision": decision,
            "lawRelevant": law,
            "answer": "synthetic expected response",
            "checks": ["citation_support"],
            "evidence": [{
                "documentId": "SYN-LEGAL-1" if law else "SYN-TECH-1",
                "version": "v2",
                "equipment": "SYN-LIFT-A",
                "part": "brake",
                "sourceKind": "legal" if law else "technical",
            }],
            "forbiddenEvidence": [{"documentId": "SYN-WRONG-MODEL", "version": "v1", "reason": "wrong model"}],
        },
    }


def test_metrics_use_explicit_denominators_and_detect_metadata_mismatch() -> None:
    case = _case("RQ-001")
    result = {
        "caseId": "RQ-001",
        "decision": "answer",
        "retrieved": [
            {"documentId": "SYN-TECH-1", "version": "v1", "equipment": "SYN-LIFT-B", "part": "brake", "sourceKind": "technical", "rank": 1, "relevant": True, "authorized": True},
            {"documentId": "SYN-WRONG-MODEL", "version": "v1", "equipment": "SYN-LIFT-B", "part": "brake", "sourceKind": "technical", "rank": 2, "relevant": False, "authorized": False},
        ],
        "claims": [{"factual": True, "supported": False, "lawClaim": False, "citations": [{"documentId": "SYN-TECH-1", "sourceKind": "technical", "validSupport": False}]}],
    }
    report = EVAL.evaluate([case], [result], k=1)
    # A matching document ID on a stale/wrong-model revision is not the gold evidence.
    assert report["search"]["gold_evidence_recall"] == {"numerator": 0, "denominator": 1, "rate": 0.0}
    assert report["search"]["top_k_evidence_recall"] == {"numerator": 0, "denominator": 1, "rate": 0.0}
    assert report["search"]["version_equipment_part_match"] == {"numerator": 0, "denominator": 1, "rate": 0.0}
    assert report["search"]["irrelevant_or_unauthorized_rate"] == {"numerator": 2, "denominator": 2, "rate": 1.0}
    assert report["answer"]["unsupported_factual_claim_rate"]["numerator"] == 1
    assert report["answer"]["citation_precision"]["rate"] == 0.0
    assert report["cases"][0]["forbiddenEvidenceReturned"] == ["SYN-WRONG-MODEL@v1"]


def test_expected_hold_and_law_source_confusion_are_separate() -> None:
    case = _case("RQ-002", decision="hold", law=True)
    result = {
        "caseId": "RQ-002",
        "decision": "answer",
        "retrieved": [{"documentId": "SYN-TECH-1", "version": "v2", "equipment": "SYN-LIFT-A", "part": "brake", "sourceKind": "technical", "rank": 1, "relevant": True, "authorized": True}],
        "claims": [{"factual": True, "supported": False, "lawClaim": True, "citations": [{"documentId": "SYN-TECH-1", "sourceKind": "technical", "validSupport": False}]}],
    }
    report = EVAL.evaluate([case], [result])
    assert report["answer"]["correct_abstention"] == {"numerator": 0, "denominator": 1, "rate": 0.0}
    assert report["answer"]["law_technical_confusion"]["numerator"] == 1


def test_empty_baseline_reports_unmeasured_metrics_not_zero_quality() -> None:
    report = EVAL.evaluate([_case("RQ-001")], [], allow_empty=True)
    assert report["evaluated_cases"] == 0
    assert report["search"]["gold_evidence_recall"] == {"numerator": 0, "denominator": 0, "rate": None}


def test_case_set_schema_rejects_missing_material_fields() -> None:
    error = EVAL.validate_cases([{"id": "RQ-001"}])
    assert error


def test_synthetic_case_set_has_30_cases_and_covers_six_requested_groups() -> None:
    cases = json.loads(CASE_FILE.read_text(encoding="utf-8"))["cases"]
    assert len(cases) == 30
    assert {case["category"] for case in cases} == {
        "model_specific",
        "fault_diagnosis",
        "procedure_limit",
        "legal_standard",
        "cross_source",
        "adversarial_or_insufficient",
    }
    assert set(Counter(case["category"] for case in cases).values()) == {5}
    assert EVAL.validate_cases(cases) is None
