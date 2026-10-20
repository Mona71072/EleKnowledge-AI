#!/usr/bin/env python3
"""Generate the scope review queue for Senpai model-filter verification.

The Senpai model filter only excludes cards whose applicability scope a person has
verified (``model_scope.scope_status: verified``). This script lists every card that
is still unverified, ordered by how much a human check matters, so reviewers can
correct the scope and mark it verified.

Reads ``knowledge/cards/**/*.md`` only (no network) and writes a deterministic
Markdown file; re-running without card changes produces identical output.

Usage:
    python scripts/knowledge/build_scope_review_queue.py
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
RETRIEVAL_PATH = REPO_ROOT / "lambda" / "rag" / "rag-function" / "knowhow_retrieval.py"
DEFAULT_OUTPUT = KNOWLEDGE_ROOT / "queues" / "scope-review" / "QUEUE.md"
COMMAND = "python scripts/knowledge/build_scope_review_queue.py"
CARD_DIRS = ("case-summaries", "practice-guides")
PRODUCT_KEYS = ("product_lines", "model_abbreviations", "lists_model_label", "observed_on")
BROAD_FIELDS = ("may_apply_to", "scope_note", "lists_model_label")
BROAD_PATTERN = re.compile(r"全エレ|全機種|全エス|共通|一般")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)

PRIORITY_TITLES = {
    "P1": "P1 矛盾の疑い（機種名があるのに適用範囲が広いと読める）",
    "P2": "P2 機種を名指し・未検証（検証すれば機種フィルタで除外対象になる）",
    "P3": "P3 制御方式・略称のみ・未検証",
    "P4": "P4 汎用ラベル／空（対応不要の情報）",
}
ACTIONS = {
    "P1": "適用範囲を確認する。全機種対応なら product_lines / lists_model_label を全エレ機種へ直し、特定機種のみなら may_apply_to / scope_note を直して、検証済みにする",
    "P2": "product_lines が正しければ検証済みにする（以後、他機種を選んだときに除外される）",
    "P3": "機種フィルタ対象外。全機種対応なら lists_model_label を全エレ機種へ",
}


@dataclass(frozen=True)
class Row:
    """One unverified card awaiting a scope review."""

    priority: str
    knowledge_id: str
    title: str
    link: str
    product_lines: tuple[str, ...]
    lists_model_label: tuple[str, ...]
    control_methods: tuple[str, ...]
    signal: str


@dataclass(frozen=True)
class Inventory:
    """Result of scanning the cards: queue rows, verified count, unreadable cards."""

    rows: tuple[Row, ...]
    verified: int
    unreadable: tuple[str, ...]


def load_retrieval(path: Path = RETRIEVAL_PATH) -> ModuleType:
    """Load knowhow_retrieval.py by path so product classification has one source."""
    spec = importlib.util.spec_from_file_location("knowhow_retrieval_scope_queue", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _as_list(value) -> tuple[str, ...]:
    if value is None or value == "":
        return ()
    items = value if isinstance(value, list) else [value]
    return tuple(str(item) for item in items if str(item).strip())


def _read_card(path: Path) -> dict:
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError("frontmatter is missing")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def _value_kinds(scope: dict, retrieval: ModuleType) -> tuple[bool, bool, bool]:
    """Return (specific_elevator, specific_escalator, generic_label) for recognized values."""
    escalator = set(retrieval.MODEL_ALIASES[retrieval.ESCALATOR_KEY])
    elevator = set().union(*retrieval.MODEL_ALIASES.values()) - escalator
    generic = {
        retrieval.normalize_model_label(retrieval.GENERIC_ELEVATOR_LABEL),
        retrieval.normalize_model_label(retrieval.GENERIC_ESCALATOR_LABEL),
    }
    labels = {
        retrieval.normalize_model_label(value)
        for key in PRODUCT_KEYS for value in _as_list(scope.get(key))
    }
    return bool(labels & elevator), bool(labels & escalator), bool(labels & generic)


def _broad_signals(scope: dict) -> list[str]:
    signals = []
    for field in BROAD_FIELDS:
        for value in _as_list(scope.get(field)):
            found = BROAD_PATTERN.search(value)
            if found:
                signals.append(f"{field} に「{found.group(0)}」")
                break
    return signals


def _classify(scope: dict, retrieval: ModuleType) -> tuple[str, str]:
    elevator, escalator, generic = _value_kinds(scope, retrieval)
    broad = _broad_signals(scope)
    if elevator and broad:
        return "P1", "エレベーター機種名あり、かつ " + "・".join(broad)
    if elevator or escalator:
        return "P2", "機種名あり（" + "・".join(_as_list(scope.get("product_lines"))) + "）"
    if generic:
        return "P4", "汎用ラベル（全エレ機種 等）"
    if any(_as_list(scope.get(key)) for key in (*PRODUCT_KEYS, "control_methods")):
        return "P3", "制御方式・略称のみ"
    return "P4", "適用範囲が空"


def _card_paths(root: Path) -> list[Path]:
    paths = [p for name in CARD_DIRS for p in (root / "cards" / name).glob("*.md")]
    return sorted(paths, key=lambda p: (p.stem, str(p)))


def scan(root: Path = KNOWLEDGE_ROOT) -> Inventory:
    """Scan card files and return the unverified rows plus counts."""
    retrieval = load_retrieval()
    rows: list[Row] = []
    unreadable: list[str] = []
    verified = 0
    for path in _card_paths(root):
        try:
            data = _read_card(path)
        except (ValueError, yaml.YAMLError, OSError):
            unreadable.append(path.stem)
            continue
        scope = data.get("model_scope") or {}
        if not isinstance(scope, dict):
            unreadable.append(path.stem)
            continue
        if scope.get("scope_status") == "verified":
            verified += 1
            continue
        priority, signal = _classify(scope, retrieval)
        rows.append(Row(
            priority=priority,
            knowledge_id=str(data.get("knowledge_id") or path.stem),
            title=str(data.get("title") or ""),
            link="../../" + path.relative_to(root).as_posix(),
            product_lines=_as_list(scope.get("product_lines")),
            lists_model_label=_as_list(scope.get("lists_model_label")),
            control_methods=_as_list(scope.get("control_methods")),
            signal=signal,
        ))
    return Inventory(tuple(sorted(rows, key=lambda r: (r.priority, r.knowledge_id))), verified, tuple(unreadable))


def collect_rows(root: Path = KNOWLEDGE_ROOT) -> tuple[Row, ...]:
    """Return the queue rows for unverified cards, ordered by priority then ID."""
    return scan(root).rows


def _cell(values) -> str:
    text = "、".join(values) if not isinstance(values, str) else values
    return (text or "—").replace("|", "\\|").replace("\n", " ")


def _table(rows: list[Row], priority: str) -> list[str]:
    lines = [
        "| カード | タイトル | product_lines | lists_model_label | control_methods | 理由 | 推奨対応 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| [{row.knowledge_id}]({row.link}) | {_cell(row.title)} | {_cell(row.product_lines)} "
            f"| {_cell(row.lists_model_label)} | {_cell(row.control_methods)} | {_cell(row.signal)} "
            f"| {ACTIONS[priority]} |"
        )
    return lines


def _generic_section(rows: list[Row]) -> list[str]:
    generic = [r.knowledge_id for r in rows if r.signal.startswith("汎用")]
    empty = [r.knowledge_id for r in rows if not r.signal.startswith("汎用")]
    return [
        "対応不要（全機種向けまたは未記載）。個別の確認行は出さず ID のみ列挙する。",
        "",
        f"- 汎用ラベル（{len(generic)} 件）: {', '.join(generic) or 'なし'}",
        f"- 適用範囲が空（{len(empty)} 件）: {', '.join(empty) or 'なし'}",
    ]


def render_queue(root: Path = KNOWLEDGE_ROOT) -> str:
    """Render the full queue Markdown deterministically."""
    inventory = scan(root)
    counts = Counter(row.priority for row in inventory.rows)
    lines = [
        "# scope-review queue",
        "",
        "> 自動生成ファイルです。直接編集せず、次のコマンドで再生成します。",
        ">",
        f"> `{COMMAND}`",
        "",
        "Senpai の機種フィルタ（UI「機種（任意）」）は、**人が適用範囲を確認したカード**"
        "（`scope_status: verified`）だけを除外対象にします。Lists の機種欄は信頼できないため、"
        "未検証のカードは除外されません。このキューは未検証カードを確認の優先度順に並べたものです。",
        "",
        "## 訂正の手順",
        "",
        "1. 一覧のカードを開き、Lists・OneNote・KB の原文で実際の適用範囲を確認する。",
        "2. `model_scope` を正しい内容に直す（例: VFGH と書かれていても全エレベーターに当てはまるなら"
        " `lists_model_label: [\"全エレ機種\"]` にし、機種名のみの `product_lines` を外す）。",
        "3. 確認できたら `model_scope` に次の 3 行を足す（`verified` は確認者と確認日が必須。欠けるとビルドが失敗する）。",
        "",
        "```yaml",
        "model_scope:",
        "  scope_status: verified",
        "  scope_verified_by: <確認した人の名前>",
        "  scope_verified_at: YYYY-MM-DD",
        "```",
        "",
        "詳細は [CONTRACT.md](../../CONTRACT.md) と "
        "[APPLICABILITY-TAXONOMY.md](../../registry/APPLICABILITY-TAXONOMY.md) を参照。",
        "",
        "## 件数",
        "",
        "| 区分 | 件数 |",
        "| --- | ---: |",
    ]
    for key in ("P1", "P2", "P3", "P4"):
        lines.append(f"| {PRIORITY_TITLES[key]} | {counts[key]} |")
    lines += [
        f"| 検証済み（キュー対象外） | {inventory.verified} |",
        f"| 読み込み不可 | {len(inventory.unreadable)} |",
        "",
    ]
    for key in ("P1", "P2", "P3", "P4"):
        rows = [r for r in inventory.rows if r.priority == key]
        lines += [f"## {PRIORITY_TITLES[key]}（{len(rows)} 件）", ""]
        lines += _generic_section(rows) if key == "P4" else (_table(rows, key) if rows else ["（なし）"])
        lines.append("")
    if inventory.unreadable:
        lines += [
            "## 読み込み不可のカード", "",
            "frontmatter を読めなかったカード。先に修復する。", "",
            *[f"- {name}" for name in inventory.unreadable], "",
        ]
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate the scope review queue.")
    parser.add_argument("--knowledge-root", type=Path, default=KNOWLEDGE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    text = render_queue(args.knowledge_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
