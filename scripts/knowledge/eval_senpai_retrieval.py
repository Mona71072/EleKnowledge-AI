#!/usr/bin/env python3
"""Run the Senpai knowhow retrieval eval cases against a local index file.

Report only: prints a PASS/FAIL line per case and totals per category.
Card bodies are never printed, only knowledgeIds. The exit code is always 0
because the case set is still a draft.

Usage:
    python scripts/knowledge/eval_senpai_retrieval.py --index <path> [--cases <path>]
    python scripts/knowledge/eval_senpai_retrieval.py --from-cards <repo_root> [--cases <path>]

``--from-cards`` runs ``build-senpai-index.mjs check <repo_root> --eval-index <tmp>`` so the
eval uses the real build output (never a hand-made index), then deletes the temporary,
unapproved index. Cards that fail the build check are listed and left out of the eval.
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_PATH = REPO_ROOT / "lambda" / "rag" / "rag-function" / "knowhow_retrieval.py"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "knowledge" / "build-senpai-index.mjs"
DEFAULT_CASES = REPO_ROOT / "tests" / "fixtures" / "knowledge" / "senpai-eval-cases.json"
MAX_MATCHES = 3


def load_retrieval(path: Path) -> ModuleType:
    """Load knowhow_retrieval.py from its file path without touching sys.path."""
    spec = importlib.util.spec_from_file_location("knowhow_retrieval_eval", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_case(retrieval: ModuleType, index: dict, case: dict) -> tuple[dict, list[str]]:
    """Run one case; return the search result and any setup notes."""
    kwargs: dict = {}
    notes: list[str] = []
    if case.get("modelType"):
        if "model_type" in inspect.signature(retrieval.search_index).parameters:
            kwargs["model_type"] = case["modelType"]
        else:
            notes.append("search_index が model_type 未対応のため絞り込みなしで実行")
    return retrieval.search_index(index, case["query"], **kwargs), notes


def evaluate(case: dict, result: dict, notes: list[str]) -> tuple[list[str], list[str]]:
    """Return (failure reasons, returned knowledgeIds) for one case."""
    reasons = list(notes)
    ids = [card["knowledgeId"] for card in result["matches"]]
    expect = case["expect"]
    if len(ids) > MAX_MATCHES:
        reasons.append(f"返却件数 {len(ids)} が上限 {MAX_MATCHES} を超える")
    if expect["status"] != "any" and result["status"] != expect["status"]:
        reasons.append(f"status={result['status']} (期待 {expect['status']})")
    for knowledge_id in expect["mustInclude"]:
        if knowledge_id not in ids:
            reasons.append(f"必須 {knowledge_id} が未検出")
    for knowledge_id in expect["mustNotInclude"]:
        if knowledge_id in ids:
            reasons.append(f"除外すべき {knowledge_id} が検出された")
    return reasons, ids


def build_eval_index(cards_root: Path, index_path: Path) -> None:
    """Run the real build ``check`` and write a local-only eval index (raises on setup failure)."""
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("node が見つかりません")
    completed = subprocess.run(
        [node, str(BUILD_SCRIPT), "check", str(cards_root), "--eval-index", str(index_path)],
        capture_output=True, text=True, check=False,
    )
    sys.stdout.write(completed.stdout)
    if not index_path.exists():
        raise RuntimeError(f"評価用索引を作れませんでした: {completed.stderr.strip()[:300]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Senpai knowhow retrieval eval report (read-only).")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--index", type=Path, help="private index JSON (read only)")
    source.add_argument("--from-cards", type=Path, metavar="REPO_ROOT",
                        help="build a temporary index from knowledge/cards via the real build check, then delete it")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="eval case JSON")
    args = parser.parse_args(argv)
    if args.from_cards is not None:
        work_dir = Path(tempfile.mkdtemp(prefix="senpai-eval-"))
        try:
            index_path = work_dir / "index.json"
            try:
                build_eval_index(args.from_cards, index_path)
            except (OSError, RuntimeError) as exc:
                print(f"読み込みに失敗: {type(exc).__name__}: {exc}", file=sys.stderr)
                return 0
            args.index = index_path
            return _run(args)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
    return _run(args)


def _run(args: argparse.Namespace) -> int:
    try:
        retrieval = load_retrieval(RETRIEVAL_PATH)
        index = retrieval.parse_index(args.index.read_bytes())
        cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"読み込みに失敗: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0

    print(f"index={args.index.name} indexVersion={index['indexVersion'][:23]}... cards={len(index['cards'])}")
    print(f"{'ID':<8}{'CATEGORY':<24}{'RESULT':<7}{'STATUS':<11}MATCHES")
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    failures: list[str] = []
    for case in cases:
        try:
            result, notes = run_case(retrieval, index, case)
            reasons, ids = evaluate(case, result, notes)
            status = result["status"]
        except Exception as exc:  # one broken case must not stop the report
            reasons, ids, status = [f"例外: {type(exc).__name__}"], [], "-"
        passed = not reasons
        totals[case["category"]][0] += 1 if passed else 0
        totals[case["category"]][1] += 1
        verdict = "PASS" if passed else "FAIL"
        print(f"{case['id']:<8}{case['category']:<24}{verdict:<7}{status:<11}{','.join(ids) or '-'}")
        failures.extend(f"{case['id']}: {reason}" for reason in reasons)

    print("\nカテゴリ別:")
    for category in sorted(totals):
        passed_count, total = totals[category]
        print(f"  {category:<24}{passed_count}/{total}")
    total_pass = sum(value[0] for value in totals.values())
    total_all = sum(value[1] for value in totals.values())
    print(f"合計: {total_pass}/{total_all} PASS")
    if failures:
        print("\nFAIL 理由:")
        for line in failures:
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
