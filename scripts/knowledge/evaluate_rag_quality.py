#!/usr/bin/env python3
"""Score manually judged RAG run records against a versioned, synthetic gold set.

This evaluator does not call a model or retrieve data. Human/SME judgments are
required for relevance, support, citation validity, and scope correctness.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "tests/fixtures/knowledge/rag-quality-eval-v1.json"
DEFAULT_RESULTS = ROOT / "tests/fixtures/knowledge/rag-quality-baseline-not-run.json"
EXPECTED_DECISIONS = {"answer", "hold", "clarify"}


def validate_cases(cases: Any) -> str | None:
    if not isinstance(cases, list) or not cases:
        return "cases must be a non-empty array"
    seen: set[str] = set()
    required_case = {"id", "category", "question", "premises", "expected", "majorFailure"}
    required_expected = {"decision", "lawRelevant", "answer", "evidence", "forbiddenEvidence", "checks"}
    required_evidence = {"documentId", "version", "equipment", "part", "sourceKind"}
    for case in cases:
        if not isinstance(case, dict) or not required_case <= set(case):
            return "every case needs id/category/question/premises/expected/majorFailure"
        if not isinstance(case["id"], str) or not case["id"].strip() or case["id"] in seen:
            return f"case id is blank or duplicated: {case.get('id')!r}"
        seen.add(case["id"])
        if not all(isinstance(case[field], str) and case[field].strip() for field in ("category", "question", "majorFailure")):
            return f"{case['id']}: category, question, and majorFailure must be non-empty strings"
        if not isinstance(case["premises"], list) or not all(isinstance(x, str) for x in case["premises"]):
            return f"{case['id']}: premises must be an array of strings"
        expected = case["expected"]
        if not isinstance(expected, dict) or not required_expected <= set(expected):
            return f"{case['id']}: expected block is incomplete"
        if expected["decision"] not in EXPECTED_DECISIONS or type(expected["lawRelevant"]) is not bool:
            return f"{case['id']}: expected decision/lawRelevant is invalid"
        if not isinstance(expected["evidence"], list) or not isinstance(expected["forbiddenEvidence"], list):
            return f"{case['id']}: evidence and forbiddenEvidence must be arrays"
        for evidence in expected["evidence"]:
            if not isinstance(evidence, dict) or not required_evidence <= set(evidence):
                return f"{case['id']}: evidence metadata is incomplete"
        for forbidden in expected["forbiddenEvidence"]:
            if not isinstance(forbidden, dict) or not {"documentId", "reason"} <= set(forbidden) or set(forbidden) - {"documentId", "reason", "version", "equipment", "part"}:
                return f"{case['id']}: forbidden evidence needs documentId and reason"
        if not isinstance(expected["checks"], list) or not expected["checks"]:
            return f"{case['id']}: expected checks must be a non-empty array"
    return None


def _metric(numerator: int, denominator: int) -> dict[str, int | float | None]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": (numerator / denominator) if denominator else None,
    }


def _score(cases: list[dict], results: list[dict], k: int, *, include_categories: bool = True) -> dict:
    result_by_id = {item["caseId"]: item for item in results}
    search = defaultdict(int)
    answer = defaultdict(int)
    per_category: dict[str, list[dict]] = defaultdict(list)
    counts = defaultdict(int)
    for case in cases:
        result = result_by_id.get(case["id"])
        if result is None:
            continue
        counts["evaluated_cases"] += 1
        per_category[case["category"]].append(case)
        expected = case["expected"]
        retrieved = result["retrieved"]
        retrieved_by_id: dict[str, list[dict]] = defaultdict(list)
        for row in retrieved:
            retrieved_by_id[row["documentId"]].append(row)
        forbidden_rows = expected["forbiddenEvidence"]
        gold = expected["evidence"]
        for evidence in gold:
            matching_id = retrieved_by_id.get(evidence["documentId"], [])
            search["gold_total"] += 1
            matching_gold = [
                row for row in matching_id
                if all(row.get(field) == evidence[field] for field in ("version", "equipment", "part", "sourceKind"))
            ]
            if matching_gold:
                search["gold_found"] += 1
                if min(x["rank"] for x in matching_gold) <= k:
                    search["top_k_found"] += 1
                search["metadata_match"] += 1
        for row in retrieved:
            search["retrieved_total"] += 1
            wrong_gold_metadata = any(
                row["documentId"] == evidence["documentId"]
                and any(row.get(field) != evidence[field] for field in ("version", "equipment", "part", "sourceKind"))
                for evidence in gold
            )
            is_forbidden = any(
                row["documentId"] == forbidden["documentId"]
                and all(row.get(field) == forbidden[field] for field in ("version", "equipment", "part") if field in forbidden)
                for forbidden in forbidden_rows
            )
            if not row.get("relevant", False) or not row.get("authorized", False) or is_forbidden or wrong_gold_metadata:
                search["contaminated"] += 1

        decision = result["decision"]
        retrieved_ids = {item["documentId"] for item in retrieved}
        answer["decision_total"] += 1
        if decision == expected["decision"]:
            answer["decision_correct"] += 1
        if expected["decision"] == "hold":
            answer["hold_total"] += 1
            if decision == "hold":
                answer["hold_correct"] += 1
        case_law_confusion = bool(result.get("lawConfusion", False))
        for claim in result["claims"]:
            if claim.get("factual", False):
                answer["factual_claims"] += 1
                if claim.get("supported", False):
                    answer["supported_claims"] += 1
                else:
                    answer["unsupported_claims"] += 1
                valid_citations = [c for c in claim["citations"] if c.get("validSupport", False) and c["documentId"] in retrieved_ids]
                if not valid_citations:
                    answer["citation_omissions"] += 1
            for citation in claim["citations"]:
                answer["citation_total"] += 1
                if citation.get("validSupport", False) and citation["documentId"] in retrieved_ids:
                    answer["citation_valid"] += 1
            if expected["lawRelevant"] and claim.get("lawClaim", False):
                if any(c.get("sourceKind") != "legal" for c in claim["citations"]):
                    case_law_confusion = True
        if expected["lawRelevant"]:
            answer["law_case_total"] += 1
            answer["law_confusion"] += int(case_law_confusion)

    category_report = {}
    case_report = []
    if include_categories:
        for category, category_cases in sorted(per_category.items()):
            category_results = [result_by_id[c["id"]] for c in category_cases]
            sub = _score(category_cases, category_results, k, include_categories=False)
            category_report[category] = {
                "evaluatedCases": sub["evaluated_cases"],
                "decisionAccuracy": sub["answer"]["decision_accuracy"],
                "goldEvidenceRecall": sub["search"]["gold_evidence_recall"],
                "unsupportedFactualClaimRate": sub["answer"]["unsupported_factual_claim_rate"],
            }
        for case in cases:
            result = result_by_id.get(case["id"])
            if result is None:
                continue
            retrieved = result["retrieved"]
            expected_evidence = case["expected"]["evidence"]
            forbidden_rows = case["expected"]["forbiddenEvidence"]
            case_report.append({
                "id": case["id"],
                "category": case["category"],
                "expectedDecision": case["expected"]["decision"],
                "actualDecision": result["decision"],
                "decisionCorrect": case["expected"]["decision"] == result["decision"],
                "goldEvidenceFound": sum(
                    any(
                        row["documentId"] == item["documentId"]
                        and all(row.get(field) == item[field] for field in ("version", "equipment", "part", "sourceKind"))
                        for row in retrieved
                    )
                    for item in expected_evidence
                ),
                "goldEvidenceTotal": len(expected_evidence),
                "goldEvidenceInTopK": sum(
                    any(
                        row["documentId"] == item["documentId"]
                        and row["rank"] <= k
                        and all(row.get(field) == item[field] for field in ("version", "equipment", "part", "sourceKind"))
                        for row in retrieved
                    )
                    for item in expected_evidence
                ),
                "forbiddenEvidenceReturned": sorted({
                    row["documentId"] + (f"@{row['version']}" if row.get("version") else "")
                    for row in retrieved
                    for forbidden in forbidden_rows
                    if row["documentId"] == forbidden["documentId"]
                    and all(row.get(field) == forbidden[field] for field in ("version", "equipment", "part") if field in forbidden)
                }),
                "unsupportedFactualClaims": sum(bool(c.get("factual")) and not bool(c.get("supported")) for c in result["claims"]),
            })
    return {
        "case_count": len(cases),
        "evaluated_cases": counts["evaluated_cases"],
        "search": {
            "gold_evidence_recall": _metric(search["gold_found"], search["gold_total"]),
            "top_k_evidence_recall": _metric(search["top_k_found"], search["gold_total"]),
            "version_equipment_part_match": _metric(search["metadata_match"], search["gold_total"]),
            "irrelevant_or_unauthorized_rate": _metric(search["contaminated"], search["retrieved_total"]),
        },
        "answer": {
            "decision_accuracy": _metric(answer["decision_correct"], answer["decision_total"]),
            "correct_abstention": _metric(answer["hold_correct"], answer["hold_total"]),
            "claim_support_rate": _metric(answer["supported_claims"], answer["factual_claims"]),
            "citation_precision": _metric(answer["citation_valid"], answer["citation_total"]),
            "citation_omission_rate": _metric(answer["citation_omissions"], answer["factual_claims"]),
            "unsupported_factual_claim_rate": _metric(answer["unsupported_claims"], answer["factual_claims"]),
            "law_technical_confusion": _metric(answer["law_confusion"], answer["law_case_total"]),
        },
        "categories": category_report if include_categories else {},
        "cases": case_report if include_categories else [],
        "grader": "case-set gold is authored; retrieved relevance, claim support, and citation judgments must be supplied by a human/SME",
        "k": k,
    }


def evaluate(cases: list[dict], results: list[dict], k: int = 5, *, allow_empty: bool = False) -> dict:
    error = validate_cases(cases)
    if error:
        raise ValueError(error)
    if k < 1:
        raise ValueError("k must be at least 1")
    if not isinstance(results, list):
        raise ValueError("results must be an array")
    if not results and not allow_empty:
        raise ValueError("no run results; pass --allow-empty only for a declared not-run baseline")
    by_id: dict[str, dict] = {}
    allowed_result = {"caseId", "decision", "retrieved", "claims", "lawConfusion"}
    allowed_retrieval = {"documentId", "version", "equipment", "part", "sourceKind", "rank", "relevant", "authorized"}
    for row in results:
        if not isinstance(row, dict) or set(row) - allowed_result or not {"caseId", "decision", "retrieved", "claims"} <= set(row):
            raise ValueError("result rows require caseId/decision/retrieved/claims and no extra fields")
        if row["caseId"] not in {case["id"] for case in cases} or row["caseId"] in by_id:
            raise ValueError(f"unknown or duplicate result caseId: {row['caseId']}")
        if row["decision"] not in EXPECTED_DECISIONS or not isinstance(row["retrieved"], list) or not isinstance(row["claims"], list):
            raise ValueError(f"{row['caseId']}: result decision/retrieved/claims invalid")
        for item in row["retrieved"]:
            if not isinstance(item, dict) or set(item) - allowed_retrieval or not allowed_retrieval <= set(item):
                raise ValueError(f"{row['caseId']}: retrieved rows need complete metadata and human relevance/authorization labels")
            if type(item["rank"]) is not int or item["rank"] < 1 or type(item["relevant"]) is not bool or type(item["authorized"]) is not bool:
                raise ValueError(f"{row['caseId']}: rank/relevance/authorization label invalid")
        for claim in row["claims"]:
            if not isinstance(claim, dict) or not {"factual", "supported", "lawClaim", "citations"} <= set(claim):
                raise ValueError(f"{row['caseId']}: claim needs factual/support/lawClaim/citations judgments")
            if not all(type(claim[field]) is bool for field in ("factual", "supported", "lawClaim")) or not isinstance(claim["citations"], list):
                raise ValueError(f"{row['caseId']}: claim judgment types invalid")
            if any(not isinstance(c, dict) or not {"documentId", "sourceKind", "validSupport"} <= set(c) or type(c["validSupport"]) is not bool for c in claim["citations"]):
                raise ValueError(f"{row['caseId']}: citations need documentId/sourceKind/validSupport")
        by_id[row["caseId"]] = row
    if results and set(by_id) != {case["id"] for case in cases}:
        missing = sorted({case["id"] for case in cases} - set(by_id))
        raise ValueError(f"run must include every case; missing: {','.join(missing)}")
    return _score(cases, results, k)


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score a human-judged EleKnowledge RAG run (offline; no model calls).")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--allow-empty", action="store_true", help="emit N/A rates only for an explicitly not-run baseline")
    parser.add_argument("--json-out", type=Path, help="optional local report output path")
    args = parser.parse_args(argv)
    try:
        case_data = _load(args.cases)
        result_data = _load(args.results)
        if result_data.get("schemaVersion") != 1 or not isinstance(result_data.get("run"), dict) or not isinstance(result_data.get("results"), list):
            raise ValueError("results file must have schemaVersion=1, run metadata, and results array")
        run = result_data["run"]
        if not {"source", "headSha", "evaluatedAt", "grader", "notes"} <= set(run):
            raise ValueError("run metadata must include source/headSha/evaluatedAt/grader/notes")
        if run["source"] == "not-run" and result_data["results"]:
            raise ValueError("source=not-run must not contain scored outputs")
        report = evaluate(case_data["cases"], result_data["results"], args.k, allow_empty=args.allow_empty)
        report["run"] = run
        report["caseSetVersion"] = case_data.get("datasetVersion")
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.json_out:
            args.json_out.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (KeyError, TypeError, ValueError) as exc:
        print(f"評価できません: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
