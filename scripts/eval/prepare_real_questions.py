#!/usr/bin/env python3
"""Prepare anonymized, stratified real-question candidates for human review.

The input CSV is sensitive and must remain outside Git. Only anonymized
questions and non-identifying outcome labels are written to output files.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import defaultdict
from pathlib import Path

DEFAULT_QUOTAS = {
    "thumbs_down": 4,
    "not_found": 4,
    "ordinary_answered": 5,
    "clarify_followup": 3,
    "model_specified": 2,
    "model_unspecified": 2,
}

REDACTIONS = (
    ("email", re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"), "○○メール"),
    ("phone", re.compile(r"(?<!\d)(?:\+81[- ]?(?:0\d{1,4}|[1-9]\d{1,3})|0\d{1,4})[- ]?\d{1,4}[- ]?\d{3,4}(?!\d)"), "○○電話番号"),
    ("work_order", re.compile(r"(?i)(?:工事|作業|案件|注文)(?:番号|No\.?|№)\s*[:：#]?\s*[A-Z0-9][A-Z0-9-]{3,}"), "○○工事番号"),
    ("address", re.compile(r"(?:〒?\s*\d{3}-?\d{4}\s*)?(?:東京都|北海道|(?:大阪|京都)府|[一-龥]{2,3}県)[^\s、。]{2,30}(?:市|区|町|村)[^\s、。]{0,30}"), "○○住所"),
    ("company", re.compile(r"(?:株式会社|有限会社|合同会社|㈱|㈲)[^\s、。のがはにを]{1,20}|[^\s、。のがはにを]{1,20}(?:株式会社|有限会社|合同会社)"), "○○会社"),
    ("site", re.compile(r"[^\s、。]{1,30}(?:現場|ビル|マンション|病院|工場|駅|ホテル)"), "○○現場"),
    ("person", re.compile(r"(?:担当者|作業員|お客様|氏名)\s*[:：]?\s*[一-龥々]{2,5}(?:\s*[一-龥々]{1,5})?"), "○○人名"),
    ("person_honorific", re.compile(r"[一-龥々]{2,5}(?:さん|様)"), "○○人名"),
)


def anonymize(text: str) -> tuple[str, list[str]]:
    """Replace recognizable personal/business identifiers, preserving RAG terms."""
    result = text or ""
    found: list[str] = []
    for label, pattern, replacement in REDACTIONS:
        result, count = pattern.subn(replacement, result)
        if count:
            found.append(label)
    return result, found


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "はい"}


def classify(row: dict[str, str]) -> str:
    if row.get("feedback", "").lower() == "bad":
        return "thumbs_down"
    if row.get("response_type", "").lower() == "not_found":
        return "not_found"
    if _truthy(row.get("preceded_by_clarify")):
        return "clarify_followup"
    if row.get("response_type", "").lower() == "pages":
        return "ordinary_answered"
    if row.get("model_type", "").strip():
        return "model_specified"
    return "model_unspecified"


def _proportional_quotas(target: int) -> dict[str, int]:
    total_quota = sum(DEFAULT_QUOTAS.values())
    scaled = {stratum: target * quota for stratum, quota in DEFAULT_QUOTAS.items()}
    quotas = {stratum: value // total_quota for stratum, value in scaled.items()}
    remainders = {stratum: value % total_quota for stratum, value in scaled.items()}
    remaining = target - sum(quotas.values())
    ranked_strata = sorted(DEFAULT_QUOTAS, key=remainders.get, reverse=True)
    for stratum in ranked_strata[:remaining]:
        quotas[stratum] += 1
    return quotas


def stratified_sample(rows: list[dict[str, str]], target: int = 20,
                      seed: int = 20260929) -> list[tuple[dict[str, str], str]]:
    """Sample without replacement from exclusive, documented primary strata."""
    quotas = _proportional_quotas(target)
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("question", "").strip():
            buckets[classify(row)].append(row)
    rng = random.Random(seed)
    selected: list[tuple[dict[str, str], str]] = []
    leftovers: list[tuple[dict[str, str], str]] = []
    for stratum, quota in quotas.items():
        bucket = list(buckets[stratum])
        rng.shuffle(bucket)
        selected.extend((row, stratum) for row in bucket[:quota])
        leftovers.extend((row, stratum) for row in bucket[quota:])
    rng.shuffle(leftovers)
    selected.extend(leftovers[:max(0, target - len(selected))])
    return selected[:target]


def _tags(row: dict[str, str], stratum: str, redactions: list[str]) -> list[str]:
    tags = ["実利用", stratum]
    if row.get("model_type", "").strip():
        tags.append("機種指定あり")
    else:
        tags.append("機種指定なし")
    if _truthy(row.get("preceded_by_clarify")):
        tags.append("聞き返し後の追記")
    if redactions:
        tags.append("匿名化確認")
    return tags


def _validate_output_path(path: Path) -> None:
    """Keep repository-local generated files inside the ignored output directory."""
    repo_root = Path(__file__).resolve().parents[2]
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(repo_root)
    except ValueError:
        return
    if len(relative.parts) < 2 or relative.parts[0] != ".eval-real-questions":
        raise ValueError(
            f"Repository-local output must be under .eval-real-questions/: {path}"
        )


def write_outputs(rows: list[dict[str, str]], review_path: Path,
                  jsonl_path: Path, target: int = 20, seed: int = 20260929) -> int:
    _validate_output_path(review_path)
    _validate_output_path(jsonl_path)
    sampled = stratified_sample(rows, target=target, seed=seed)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with review_path.open("w", encoding="utf-8-sig", newline="") as csv_file, \
            jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        fields = ["id", "question_anonymized", "stratum", "response_type",
                  "feedback", "feedback_reason", "document_opened", "model_type",
                  "previous_user_question_anonymized",
                  "previous_assistant_content_anonymized", "redaction_candidates",
                  "human_review", "expected_documents",
                  "expected_pages", "expected_gate"]
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for index, (row, stratum) in enumerate(sampled, start=25):
            question, redactions = anonymize(row.get("question", ""))
            item_id = f"G2-{index:03d}"
            prior_user, prior_user_redactions = anonymize(
                row.get("previous_user_question", "")
            )
            prior_assistant, prior_assistant_redactions = anonymize(
                row.get("previous_assistant_content", "")
            )
            all_redactions = list(dict.fromkeys(
                redactions + prior_user_redactions + prior_assistant_redactions
            ))
            writer.writerow({
                "id": item_id,
                "question_anonymized": question,
                "stratum": stratum,
                "response_type": row.get("response_type", ""),
                "feedback": row.get("feedback", ""),
                "feedback_reason": row.get("feedback_reason", ""),
                "document_opened": row.get("document_opened", ""),
                "model_type": row.get("model_type", "").strip(),
                "previous_user_question_anonymized": prior_user,
                "previous_assistant_content_anonymized": prior_assistant,
                "redaction_candidates": ",".join(all_redactions),
                "human_review": "pending",
                "expected_documents": "",
                "expected_pages": "",
                "expected_gate": "",
            })
            tags = _tags(row, stratum, all_redactions)
            chat_history = []
            if prior_user.strip() and prior_assistant.strip():
                chat_history = [
                    {"role": "user", "content": prior_user},
                    {"role": "assistant", "content": prior_assistant},
                ]
            draft = {
                "id": item_id,
                "query": question,
                "filters": ({"modelType": row.get("model_type", "").strip()}
                            if row.get("model_type", "").strip() else {}),
                "chat_history": chat_history,
                "expected_documents": [],
                "expected_pages": [],
                "expected_gate": "",
                "tags": tags,
                "notes": "出典: 実利用（匿名化・人確認待ち）",
                "skip": True,
            }
            jsonl_file.write(json.dumps(draft, ensure_ascii=False) + "\n")
    return len(sampled)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path, help="Athena export CSV; keep outside Git")
    parser.add_argument("--review-csv", type=Path, required=True)
    parser.add_argument("--draft-jsonl", type=Path, required=True)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260929)
    args = parser.parse_args()
    if args.count <= 0:
        parser.error("--count must be positive")
    with args.input_csv.open(encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    count = write_outputs(rows, args.review_csv, args.draft_jsonl,
                          target=args.count, seed=args.seed)
    print(f"Prepared {count} anonymized candidates. Review and approve before Git use.")


if __name__ == "__main__":
    main()
