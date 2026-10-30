#!/usr/bin/env python3
"""Compare candidate selection policies on a fixed synthetic retrieval pool.

Offline only: no AWS, Bedrock, model calls, document text, or production data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "tests/eval/fixtures/t21_synthetic_candidates_v1.json"
GROUP_FIELDS = ("documentId", "page")
REQUIRED_CANDIDATE_FIELDS = {
    "queryLane", "documentId", "page", "chunkId", "contentHash", "score",
    "rerankScore", "equipment", "version",
}


def validate_fixture(data: Any) -> str | None:
    if not isinstance(data, dict) or data.get("schemaVersion") != 1 or data.get("source") != "synthetic":
        return "fixture must declare schemaVersion=1 and source=synthetic"
    if not isinstance(data.get("candidateLimit"), int) or data["candidateLimit"] < 1:
        return "candidateLimit must be a positive integer"
    if not isinstance(data.get("goldEvidence"), list) or not data["goldEvidence"]:
        return "goldEvidence must be a non-empty array"
    if not isinstance(data.get("candidates"), list) or not data["candidates"]:
        return "candidates must be a non-empty array"
    for row in data["candidates"]:
        if not isinstance(row, dict) or not REQUIRED_CANDIDATE_FIELDS <= set(row):
            return "every candidate must contain lane, identity, scope, and fixed score fields"
        if not isinstance(row["page"], int) or not all(isinstance(row[k], (int, float)) for k in ("score", "rerankScore")):
            return "candidate page and scores must be numeric"
    return None


def _key(row: dict) -> tuple:
    return tuple(row[field] for field in GROUP_FIELDS)


def _groups(candidates: list[dict]) -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for row in candidates:
        key = _key(row)
        entry = grouped.get(key)
        if entry is None:
            entry = {
                "documentId": row["documentId"], "page": row["page"],
                "score": float(row["score"]), "rerankScore": float(row["rerankScore"]),
                "equipment": row["equipment"], "version": row["version"],
                "laneScores": {},
            }
            grouped[key] = entry
        entry["score"] = max(entry["score"], float(row["score"]))
        entry["rerankScore"] = max(entry["rerankScore"], float(row["rerankScore"]))
        entry["laneScores"][row["queryLane"]] = max(
            entry["laneScores"].get(row["queryLane"], float("-inf")), float(row["score"])
        )
    return list(grouped.values())


def _rank(groups: list[dict], field: str, limit: int) -> list[dict]:
    return sorted(groups, key=lambda item: (-item[field], item["documentId"], item["page"]))[:limit]


def _lane_quota(groups: list[dict], limit: int) -> list[dict]:
    lanes = sorted({max(group["laneScores"], key=group["laneScores"].get) for group in groups})
    base, remainder = divmod(limit, len(lanes))
    chosen: dict[tuple, dict] = {}
    for index, lane in enumerate(lanes):
        quota = base + int(index < remainder)
        lane_groups = [g for g in groups if max(g["laneScores"], key=g["laneScores"].get) == lane]
        for group in _rank(lane_groups, "score", quota):
            chosen[_key(group)] = group
    if len(chosen) < limit:
        for group in _rank(groups, "score", len(groups)):
            if len(chosen) >= limit:
                break
            chosen.setdefault(_key(group), group)
    return _rank(list(chosen.values()), "score", limit)


def _deduplicate_chunks(candidates: list[dict]) -> list[dict]:
    best: dict[tuple, dict] = {}
    for row in candidates:
        key = (row["documentId"], row["page"], row["chunkId"], row["contentHash"])
        if key not in best or row["score"] > best[key]["score"]:
            best[key] = row
    return list(best.values())


def _summarize(selected: list[dict], gold: list[dict], candidate_limit: int) -> dict:
    selected_keys = {_key(row) for row in selected}
    gold_keys = {(row["documentId"], row["page"]) for row in gold}
    retained = sorted(f"{doc}@p{page}" for doc, page in selected_keys & gold_keys)
    missed = sorted(f"{doc}@p{page}" for doc, page in gold_keys - selected_keys)
    return {
        "selectedCount": len(selected),
        "candidateLimit": candidate_limit,
        "goldRetained": retained,
        "goldMissed": missed,
        "goldRecall": {"numerator": len(retained), "denominator": len(gold_keys), "rate": len(retained) / len(gold_keys)},
        "selectedSyntheticIds": [f"{r['documentId']}@p{r['page']}" for r in selected],
    }


def compare(data: dict) -> dict:
    error = validate_fixture(data)
    if error:
        raise ValueError(error)
    candidates = data["candidates"]
    groups = _groups(candidates)
    limit = data["candidateLimit"]
    gold = data["goldEvidence"]

    policies = {
        "A_global_score": _rank(groups, "score", limit),
        "B_per_lane_quota": _lane_quota(groups, limit),
        # Current merge/context and citation assembly already dedupe identical chunks/pages.
        "C_dedupe_then_global": _rank(_groups(_deduplicate_chunks(candidates)), "score", limit),
        "D_equipment_and_version_filter": _rank([
            group for group in groups
            if group["equipment"] == data["requestedEquipment"]
            and group["version"] == data["requestedVersion"]
        ], "score", limit),
        # rerankScore is fixed in the fixture; this does not invoke a reranker.
        "E_fixed_rerank_scores": _rank(groups, "rerankScore", limit),
    }
    return {
        "source": data["source"],
        "questionId": data.get("questionId"),
        "candidateRows": len(candidates),
        "uniqueEvidenceGroups": len(groups),
        "candidateLimit": limit,
        "sameCandidatePool": True,
        "externalCalls": 0,
        "policies": {name: _summarize(selected, gold, limit) for name, selected in policies.items()},
        "interpretation": {
            "A": "Current final citation selection: global score order with document/page grouping.",
            "B": "Fixed per-query-lane quotas preserve one lane's gold evidence but displace another lane's gold evidence.",
            "C": "Chunk deduplication is already performed before citation ranking; no change from A for this pool.",
            "D": "Ideal synthetic equipment/version metadata filter; runtime metadata coverage and approval are unverified.",
            "E": "Uses precomputed synthetic rerank scores only; one gold item can be demoted below the same limit.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    data = json.loads(args.fixture.read_text(encoding="utf-8"))
    report = compare(data)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
