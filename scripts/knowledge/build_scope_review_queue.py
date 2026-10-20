#!/usr/bin/env python3
"""Generate the scope review queue for Senpai model-filter verification.

The Senpai model filter only excludes cards whose applicability scope a person has
verified (``model_scope.scope_status: verified``). This script lists every card that
is still unverified, ordered by how much a human check matters, so reviewers can
correct the scope and mark it verified.

Reads ``knowledge/cards/**/*.md`` only (no network) and writes a deterministic
Markdown file; re-running without card changes produces identical output.

Field reports from 先輩チャット「結果を残す」 close the loop: ``--field-reports`` takes an
exported JSON of report candidates (no AWS calls here), stores a counts-only aggregate
(``queues/scope-review/field-reports.json``: card IDs, versions, reaction counts per model,
latest date; never report text or people) and puts cards that field reports contradict
first, in section P0. Later runs without the option reuse the committed aggregate.

Usage:
    python scripts/knowledge/build_scope_review_queue.py [--field-reports export.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
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
FIELD_REPORT_AGGREGATE = Path("queues") / "scope-review" / "field-reports.json"
COMMAND = "python scripts/knowledge/build_scope_review_queue.py"
CARD_DIRS = ("case-summaries", "practice-guides")
PRODUCT_KEYS = ("product_lines", "model_abbreviations", "lists_model_label", "observed_on")
BROAD_FIELDS = ("may_apply_to", "scope_note", "lists_model_label")
BROAD_PATTERN = re.compile(r"全エレ|全機種|全エス|共通|一般")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)

# SYNC: must equal REACTIONS / REVIEW_STATES in lambda/rag/senpai-field-report/field_report_vocab.py
# and frontend/src/lib/knowledge-senpai-field-report.mjs (tests/unit/test_senpai_field_report_sync.py).
FIELD_REPORT_REACTIONS = ("matched", "not_matched", "unsure")
FIELD_REPORT_REVIEW_STATES = ("unconfirmed", "awaiting_review", "reflected", "held_or_rejected")
# Only reports nobody has handled yet reorder the queue.
OPEN_REVIEW_STATES = frozenset({"unconfirmed", "awaiting_review"})
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})T")

DUPLICATE_TITLE = "重複の疑い（同じ Lists 番号）"
DUPLICATE_ACTION = "内容が同じなら統合する。役割が違うなら、片方に関連を明記して役割を分ける"

PRIORITY_TITLES = {
    "P0": "P0 現場の報告で確認が必要（当てはまらなかった／カードと違う機種で報告）",
    "P1": "P1 矛盾の疑い（機種名があるのに適用範囲が広いと読める）",
    "P2": "P2 機種を名指し・未検証（検証すれば機種フィルタで除外対象になる）",
    "P3": "P3 制御方式・略称のみ・未検証",
    "P4": "P4 汎用ラベル／空（対応不要の情報）",
}
ACTIONS = {
    "P0": "報告の内容（担当者用の書き出し）と原文を照合し、model_scope と本文の条件を直す。検証済みでも見直す",
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
class CardInfo:
    """Every readable card, verified or not, for joining field reports."""

    title: str
    link: str
    section: str
    scope: dict


@dataclass(frozen=True)
class DuplicateGroup:
    """Cards that cite the same Lists item, so they compete for search slots."""

    list_item_id: str
    knowledge_ids: tuple[str, ...]
    shared_onenote_ids: tuple[str, ...]


@dataclass(frozen=True)
class Inventory:
    """Result of scanning the cards: queue rows, verified count, unreadable cards."""

    rows: tuple[Row, ...]
    verified: int
    unreadable: tuple[str, ...]
    cards: dict


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
    cards: dict[str, CardInfo] = {}
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
        knowledge_id = str(data.get("knowledge_id") or path.stem)
        title = str(data.get("title") or "")
        link = "../../" + path.relative_to(root).as_posix()
        if scope.get("scope_status") == "verified":
            verified += 1
            cards[knowledge_id] = CardInfo(title, link, "検証済み", scope)
            continue
        priority, signal = _classify(scope, retrieval)
        cards[knowledge_id] = CardInfo(title, link, priority, scope)
        rows.append(Row(
            priority=priority,
            knowledge_id=knowledge_id,
            title=title,
            link=link,
            product_lines=_as_list(scope.get("product_lines")),
            lists_model_label=_as_list(scope.get("lists_model_label")),
            control_methods=_as_list(scope.get("control_methods")),
            signal=signal,
        ))
    return Inventory(
        tuple(sorted(rows, key=lambda r: (r.priority, r.knowledge_id))), verified, tuple(unreadable), cards,
    )


def _refs(data: dict, ref_type: str, key: str) -> set[str]:
    refs = data.get("source_refs")
    if not isinstance(refs, list):
        return set()
    return {
        str(ref[key]).strip() for ref in refs
        if isinstance(ref, dict) and ref.get("ref_type") == ref_type and str(ref.get(key) or "").strip()
    }


def duplicate_groups(root: Path = KNOWLEDGE_ROOT) -> tuple[DuplicateGroup, ...]:
    """Group cards (verified or not) that share a ``lists_item`` ``list_item_id``.

    Ordered by Lists number (numeric when possible), members by knowledge ID."""
    by_item: dict[str, list[tuple[str, set[str]]]] = {}
    for path in _card_paths(root):
        try:
            data = _read_card(path)
        except (ValueError, yaml.YAMLError, OSError):
            continue
        knowledge_id = str(data.get("knowledge_id") or path.stem)
        onenote = _refs(data, "onenote_page", "onenote_id")
        for item in _refs(data, "lists_item", "list_item_id"):
            by_item.setdefault(item, []).append((knowledge_id, onenote))
    groups = []
    for item, members in by_item.items():
        if len(members) < 2:
            continue
        members.sort(key=lambda member: member[0])
        shared = sorted({
            onenote for _, ids in members for onenote in ids
            if sum(onenote in other for _, other in members) >= 2
        })
        groups.append(DuplicateGroup(item, tuple(kid for kid, _ in members), tuple(shared)))
    return tuple(sorted(groups, key=lambda g: (not g.list_item_id.isdigit(),
                                               int(g.list_item_id) if g.list_item_id.isdigit() else 0,
                                               g.list_item_id)))


def collect_rows(root: Path = KNOWLEDGE_ROOT) -> tuple[Row, ...]:
    """Return the queue rows for unverified cards, ordered by priority then ID."""
    return scan(root).rows


def load_field_report_export(path: Path) -> list:
    """Read an exported JSON of field reports: a list, or ``{"items": [...]}``."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    if isinstance(data, list):
        return data
    raise ValueError("field report export must be a list or an object with items")


def _report_reactions(report) -> list | None:
    if not isinstance(report, dict) or report.get("reviewState") not in FIELD_REPORT_REVIEW_STATES:
        return None
    reactions = report.get("cardReactions")
    if not isinstance(reactions, list):
        return None
    valid = []
    for entry in reactions:
        if (isinstance(entry, dict) and isinstance(entry.get("knowledgeId"), str)
                and ID_PATTERN.match(entry["knowledgeId"]) and type(entry.get("cardVersion")) is int
                and entry.get("reaction") in FIELD_REPORT_REACTIONS):
            valid.append(entry)
    return valid


def _report_model(report: dict) -> str:
    model = report.get("modelType") or report.get("turnModelType") or ""
    return model if isinstance(model, str) and len(model) <= 50 else ""


def aggregate_field_reports(reports: list) -> dict:
    """Counts-only aggregate per card. Report text, people and conversation IDs are dropped."""
    cards: dict[str, dict] = {}
    counted = skipped = 0
    for report in reports:
        reactions = _report_reactions(report)
        if reactions is None or report["reviewState"] not in OPEN_REVIEW_STATES:
            skipped += 1
            continue
        counted += 1
        model = _report_model(report)
        found = DATE_PATTERN.match(str(report.get("createdAt") or ""))
        for entry in reactions:
            card = cards.setdefault(entry["knowledgeId"], {"versions": set(), "reactions": {}, "latestReportDate": ""})
            card["versions"].add(entry["cardVersion"])
            counts = card["reactions"].setdefault(model, dict.fromkeys(FIELD_REPORT_REACTIONS, 0))
            counts[entry["reaction"]] += 1
            if found and found.group(1) > card["latestReportDate"]:
                card["latestReportDate"] = found.group(1)
    return {
        "counted": counted,
        "skipped": skipped,
        "cards": {
            knowledge_id: {
                "versions": sorted(card["versions"]),
                "reactions": {key: card["reactions"][key] for key in sorted(card["reactions"])},
                "latestReportDate": card["latestReportDate"],
            }
            for knowledge_id, card in sorted(cards.items())
        },
    }


def write_field_report_aggregate(reports: list, root: Path = KNOWLEDGE_ROOT) -> Path:
    """Store the counts-only aggregate next to the queue (deterministic JSON)."""
    path = root / FIELD_REPORT_AGGREGATE
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(aggregate_field_reports(reports), ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")
    return path


def _read_aggregate(root: Path) -> dict | None:
    path = root / FIELD_REPORT_AGGREGATE
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) and isinstance(data.get("cards"), dict) else None


def _other_model(scope: dict, model: str, retrieval: ModuleType) -> bool:
    """True when every recognized product value of the card names a product other than ``model``."""
    if model not in retrieval.MODEL_ALIASES:
        return False
    kinds = {
        retrieval._classify_model_value(value, model)
        for key in PRODUCT_KEYS for value in _as_list(scope.get(key))
    } - {"unknown"}
    return kinds == {"conflicting"}


@dataclass(frozen=True)
class FieldRow:
    """One card with open field reports."""

    knowledge_id: str
    card: CardInfo | None
    totals: dict
    other_model: int
    models: tuple[str, ...]
    latest: str

    @property
    def needs_review(self) -> bool:
        return self.totals["not_matched"] > 0 or self.other_model > 0

    @property
    def sort_key(self) -> tuple:
        return (-self.totals["not_matched"], -self.other_model, -sum(self.totals.values()), self.knowledge_id)


def _field_rows(aggregate: dict, cards: dict, retrieval: ModuleType) -> list[FieldRow]:
    rows = []
    for knowledge_id, entry in aggregate["cards"].items():
        card = cards.get(knowledge_id)
        totals = dict.fromkeys(FIELD_REPORT_REACTIONS, 0)
        other = 0
        for model, counts in (entry.get("reactions") or {}).items():
            reports = 0
            for reaction in FIELD_REPORT_REACTIONS:
                totals[reaction] += int(counts.get(reaction, 0))
                reports += int(counts.get(reaction, 0))
            if card is not None and _other_model(card.scope, model, retrieval):
                other += reports
        models = tuple(sorted(model for model in entry.get("reactions") or {} if model))
        rows.append(FieldRow(knowledge_id, card, totals, other, models, str(entry.get("latestReportDate") or "")))
    return sorted(rows, key=lambda row: row.sort_key)


def _field_section(aggregate: dict | None, cards: dict, retrieval: ModuleType) -> tuple[list[str], int]:
    if aggregate is None:
        return ["現場の報告はまだ集計されていません（`--field-reports <書き出しJSON>` で取り込む）。"], 0
    rows = _field_rows(aggregate, cards, retrieval)
    review = [row for row in rows if row.needs_review]
    lines = [
        f"先輩チャット「結果を残す」の未確認・確認待ちの報告 {aggregate.get('counted', 0)} 件から集計"
        "（件数のみ。報告の本文・投稿者は含めない）。報告は観測であり、確認済みの事実ではない。",
        "",
    ]
    if review:
        lines += [
            "| カード | タイトル | 通常の区分 | 当てはまらなかった | カードと違う機種 | 当てはまった | 分からない | 報告の機種 | 最新 | 推奨対応 |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
        for row in review:
            card = row.card
            name = f"[{row.knowledge_id}]({card.link})" if card else f"{row.knowledge_id}（カードが見つからない）"
            lines.append(
                f"| {name} | {_cell(card.title if card else '')} | {card.section if card else '—'} "
                f"| {row.totals['not_matched']} | {row.other_model} | {row.totals['matched']} "
                f"| {row.totals['unsure']} | {_cell(row.models)} | {row.latest or '—'} | {ACTIONS['P0']} |"
            )
    else:
        lines.append("（確認が必要な報告なし）")
    reference = [row for row in rows if not row.needs_review]
    if reference:
        lines += ["", "参考（当てはまった・分からないのみ）: " + ", ".join(
            f"{row.knowledge_id}（{sum(row.totals.values())} 件）" for row in reference
        )]
    return lines, len(review)


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


def _duplicate_section(groups: tuple[DuplicateGroup, ...], cards: dict) -> list[str]:
    if not groups:
        return ["（なし）"]
    lines = [
        "同じ Lists 番号を `source_refs` に持つカード。内容が近いと検索の枠を取り合う。"
        "検証済みカードも含む。OneNote ページも共通のグループは強い重複の疑い。",
        "",
        "| Lists 番号 | カード | タイトル | 共通の OneNote | 推奨対応 |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for group in groups:
        links = [f"[{kid}]({cards[kid].link})" if kid in cards else kid for kid in group.knowledge_ids]
        titles = [cards[kid].title if kid in cards else "" for kid in group.knowledge_ids]
        lines.append(
            f"| {group.list_item_id} | {'<br>'.join(links)} | {'<br>'.join(_cell(t) for t in titles)} "
            f"| {_cell(group.shared_onenote_ids)} | {DUPLICATE_ACTION} |"
        )
    return lines


def render_queue(root: Path = KNOWLEDGE_ROOT) -> str:
    """Render the full queue Markdown deterministically."""
    inventory = scan(root)
    counts = Counter(row.priority for row in inventory.rows)
    duplicates = duplicate_groups(root)
    field_lines, counts["P0"] = _field_section(_read_aggregate(root), inventory.cards, load_retrieval())
    lines = [
        "# scope-review queue",
        "",
        "> 自動生成ファイルです。直接編集せず、次のコマンドで再生成します。",
        ">",
        f"> `{COMMAND}`",
        "",
        "Senpai の機種フィルタ（UI「機種（任意）」）は、**人が適用範囲を確認したカード**"
        "（`scope_status: verified`）だけを除外対象にします。Lists の機種欄は信頼できないため、"
        "未検証のカードは除外されません。このキューは未検証カードを確認の優先度順に並べたものです。"
        "末尾の「重複の疑い（同じ Lists 番号）」は、適用範囲とは別に、同じ Lists 項目を根拠にした"
        "複数のカードを挙げ、統合か役割分けの判断材料にします。",
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
    for key in ("P0", "P1", "P2", "P3", "P4"):
        lines.append(f"| {PRIORITY_TITLES[key]} | {counts[key]} |")
    lines += [
        f"| {DUPLICATE_TITLE} | {len(duplicates)} |",
        f"| 検証済み（キュー対象外） | {inventory.verified} |",
        f"| 読み込み不可 | {len(inventory.unreadable)} |",
        "",
        f"## {PRIORITY_TITLES['P0']}（{counts['P0']} 件）",
        "",
        *field_lines,
        "",
    ]
    for key in ("P1", "P2", "P3", "P4"):
        rows = [r for r in inventory.rows if r.priority == key]
        lines += [f"## {PRIORITY_TITLES[key]}（{len(rows)} 件）", ""]
        lines += _generic_section(rows) if key == "P4" else (_table(rows, key) if rows else ["（なし）"])
        lines.append("")
    lines += [f"## {DUPLICATE_TITLE}（{len(duplicates)} グループ）", "",
              *_duplicate_section(duplicates, inventory.cards), ""]
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
    parser.add_argument("--field-reports", type=Path, default=None,
                        help="exported JSON of 先輩チャット field reports (stored as a counts-only aggregate)")
    args = parser.parse_args(argv)
    if args.field_reports is not None:
        written = write_field_report_aggregate(load_field_report_export(args.field_reports), args.knowledge_root)
        print(f"wrote {written}", file=sys.stderr)
    text = render_queue(args.knowledge_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
