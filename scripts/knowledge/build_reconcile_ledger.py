#!/usr/bin/env python3
"""Build source-to-draft ID reconciliation artifacts (read-only inputs)."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "knowledge" / "drafts"
LISTS_SNAPSHOT = ROOT / "knowledge" / "source-snapshots" / "首都工_不具合情報共有リスト_初期スナップショット.md"
ONENOTE_DIR = ROOT / "knowledge" / "source-snapshots" / "onenote"
OUT_DIR = ROOT / "knowledge" / "source-snapshots"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end]
    body = text[end + 4 :]
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line or line.startswith(" ") or line.startswith("-"):
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def frontmatter_text(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def evidence_sources_blob(text: str) -> str:
    fm = frontmatter_text(text)
    if not fm:
        return ""
    lines = fm.splitlines()
    out: list[str] = []
    in_block = False
    for line in lines:
        if line.startswith("evidence_sources:"):
            in_block = True
            out.append(line)
            continue
        if in_block:
            if re.match(r"^[A-Za-z_]+:", line):
                break
            out.append(line)
    return "\n".join(out)


def list_ids_from_draft(path: Path, text: str, *, include_source_id_suffix: bool) -> set[str]:
    """Match list item IDs only (not error codes in narrative body)."""
    ids: set[str] = set()
    for m in re.finditer(r"(?<![0-9])ID(\d{1,5})(?![0-9])", path.name):
        ids.add(m.group(1))
    evidence = evidence_sources_blob(text)
    for m in re.finditer(r"[（(]ID(\d{1,5})[）)]", evidence):
        ids.add(m.group(1))
    for m in re.finditer(r"list_item_id:\s*[`\"']?(\d{1,5})", evidence, re.I):
        ids.add(m.group(1))
    if include_source_id_suffix:
        for m in re.finditer(r'source_id:\s*"[^"]*[-_](\d{1,5})"', evidence):
            ids.add(m.group(1))
    return ids


def build_list_id_map(*, include_source_id_suffix: bool) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = defaultdict(list)
    for path in DRAFTS.glob("*.md"):
        if path.name.startswith("IMPORT"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, _ = parse_frontmatter(text)
        record_id = fm.get("record_id") or path.stem
        for lid in list_ids_from_draft(path, text, include_source_id_suffix=include_source_id_suffix):
            mapping[lid].append(record_id)
    return mapping


def onenote_id_from_draft(text: str) -> str | None:
    fm, _ = parse_frontmatter(text)
    oid = fm.get("onenote_id", "").strip()
    return oid.lower() if oid else None


@dataclass
class ListItem:
    list_item_id: str
    title: str
    model: str
    importance: str
    reported_status: str


def parse_lists_snapshot(path: Path) -> list[ListItem]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"\n## Lists item ID ", text)
    items: list[ListItem] = []
    for part in parts[1:]:
        lines = part.splitlines()
        head = lines[0]
        m = re.match(r"(\d+):\s*(.*)", head)
        if not m:
            continue
        item = ListItem(
            list_item_id=m.group(1),
            title=m.group(2).strip(),
            model="",
            importance="",
            reported_status="",
        )
        for line in lines[1:]:
            if line.startswith("## "):
                break
            if line.startswith("- ") and ":" in line:
                key, val = line[2:].split(":", 1)
                key = key.strip()
                val = val.strip().strip("`")
                if key == "Model":
                    item.model = val
                elif key == "Reported importance":
                    item.importance = val
                elif key == "Reported status":
                    item.reported_status = val
        items.append(item)
    return items


def onenote_body_emptyish(body: str) -> bool:
    lines = [
        ln.strip()
        for ln in body.splitlines()
        if ln.strip() and not ln.startswith(">") and ln.strip() != "## OneNote content"
    ]
    placeholder_prefixes = (
        "[OneNote attachment reference omitted",
        "OneNote reference (unresolved",
        "◆OneNote reference (unresolved",
    )
    substantive_lines: list[str] = []
    placeholder_chars = 0
    total_non_ws = 0
    for ln in lines:
        if ln == "\\n":
            continue
        if any(ln.startswith(p) for p in placeholder_prefixes):
            placeholder_chars += len(re.sub(r"\s+", "", ln))
            continue
        cleaned = re.sub(r"\s+", "", ln)
        total_non_ws += len(cleaned)
        substantive_lines.append(cleaned)
    substantive = "".join(substantive_lines)
    total_non_ws += placeholder_chars
    if len(substantive) <= 15:
        return True
    if total_non_ws > 0 and placeholder_chars / total_non_ws >= 0.55 and len(substantive) < 80:
        return True
    return False


def parse_onenote_pages() -> list[tuple[str, bool]]:
    pages: list[tuple[str, bool]] = []
    for path in sorted(ONENOTE_DIR.glob("onenote-*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(text)
        oid = fm.get("onenote_id", "").strip().lower()
        if not oid:
            continue
        pages.append((oid, onenote_body_emptyish(body)))
    return pages


def theme_bucket(title: str) -> str:
    rules = [
        ("door", r"ドア|CLT|OLT|カプラ|戸"),
        ("group_call", r"群管理|呼び|割当|乗場"),
        ("power", r"電源|電圧|トランス|受電|E-stop|E-STOP"),
        ("display", r"インジ|表示|液晶|7SEG"),
        ("comm", r"通信|伝送|CAN|SCU|I-CAN"),
        ("safety", r"非常|UCMP|安全|緩衝|遮煙"),
        ("clock_sets", r"時計|SETS|時刻"),
        ("install_dim", r"据付|寸法|芯|レベル|ピット"),
    ]
    for name, pat in rules:
        if re.search(pat, title):
            return name
    return "other"


def classify_lists(
    list_items: list[ListItem], list_id_to_records: dict[str, list[str]]
) -> tuple[list[dict], list[dict], list[dict]]:
    matched_lists: list[dict] = []
    unmatched_lists: list[dict] = []
    duplicate_list_matches: list[dict] = []
    for item in list_items:
        records = sorted(set(list_id_to_records.get(item.list_item_id, [])))
        if len(records) > 1:
            duplicate_list_matches.append(
                {
                    "list_item_id": item.list_item_id,
                    "record_ids": records,
                    "title": item.title,
                }
            )
        if records:
            matched_lists.append(
                {
                    "list_item_id": item.list_item_id,
                    "record_id": records[0],
                    "record_ids": records,
                    "title": item.title,
                    "model": item.model,
                    "importance": item.importance,
                }
            )
        else:
            unmatched_lists.append(
                {
                    "list_item_id": item.list_item_id,
                    "title": item.title,
                    "model": item.model,
                    "importance": item.importance,
                    "reported_status": item.reported_status,
                    "theme_bucket": theme_bucket(item.title),
                }
            )
    return matched_lists, unmatched_lists, duplicate_list_matches


def main() -> None:
    draft_paths = [p for p in DRAFTS.glob("*.md") if not p.name.startswith("IMPORT")]
    list_id_to_records = build_list_id_map(include_source_id_suffix=True)
    list_id_to_records_primary = build_list_id_map(include_source_id_suffix=False)
    onenote_to_records: dict[str, list[str]] = defaultdict(list)

    for path in draft_paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, _ = parse_frontmatter(text)
        record_id = fm.get("record_id") or path.stem
        oid = onenote_id_from_draft(text)
        if oid:
            onenote_to_records[oid].append(record_id)

    list_items = parse_lists_snapshot(LISTS_SNAPSHOT)
    onenote_pages = parse_onenote_pages()

    matched_lists, unmatched_lists, duplicate_list_matches = classify_lists(
        list_items, list_id_to_records_primary
    )
    matched_ext, unmatched_ext, duplicate_ext = classify_lists(list_items, list_id_to_records)

    onenote_ids = {oid for oid, _ in onenote_pages}
    draft_onenote_ids = set(onenote_to_records.keys())
    matched_onenote = onenote_ids & draft_onenote_ids
    unmatched_onenote = sorted(onenote_ids - draft_onenote_ids)
    emptyish = sum(1 for _, e in onenote_pages if e)

    high_unmatched = [
        u
        for u in unmatched_lists
        if u["importance"] in ("↑高", "重要")
    ]

    theme_counts = Counter(u["theme_bucket"] for u in unmatched_lists)

    # machine-readable exports
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "reconcile-lists-matched.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["list_item_id", "record_id", "record_ids", "title", "model", "importance"])
        for row in sorted(matched_lists, key=lambda r: int(r["list_item_id"])):
            w.writerow(
                [
                    row["list_item_id"],
                    row["record_id"],
                    "|".join(row["record_ids"]),
                    row["title"],
                    row["model"],
                    row["importance"],
                ]
            )

    with (OUT_DIR / "reconcile-lists-matched-extended.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["list_item_id", "record_id", "record_ids", "title", "model", "importance"])
        for row in sorted(matched_ext, key=lambda r: int(r["list_item_id"])):
            w.writerow(
                [
                    row["list_item_id"],
                    row["record_id"],
                    "|".join(row["record_ids"]),
                    row["title"],
                    row["model"],
                    row["importance"],
                ]
            )

    with (OUT_DIR / "reconcile-lists-unmatched-extended.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["list_item_id", "title", "model", "importance", "reported_status", "theme_bucket"])
        for row in sorted(unmatched_ext, key=lambda r: int(r["list_item_id"])):
            w.writerow(
                [
                    row["list_item_id"],
                    row["title"],
                    row["model"],
                    row["importance"],
                    row["reported_status"],
                    row["theme_bucket"],
                ]
            )

    with (OUT_DIR / "reconcile-lists-unmatched.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["list_item_id", "title", "model", "importance", "reported_status", "theme_bucket"])
        for row in sorted(unmatched_lists, key=lambda r: int(r["list_item_id"])):
            w.writerow(
                [
                    row["list_item_id"],
                    row["title"],
                    row["model"],
                    row["importance"],
                    row["reported_status"],
                    row["theme_bucket"],
                ]
            )

    with (OUT_DIR / "reconcile-onenote-unmatched-ids.txt").open("w", encoding="utf-8") as f:
        for oid in unmatched_onenote:
            f.write(oid + "\n")

    summary = {
        "generated_on": date.today().isoformat(),
        "lists": {
            "total": len(list_items),
            "matched_primary": len(matched_lists),
            "unmatched_primary": len(unmatched_lists),
            "duplicate_matches_primary": len(duplicate_list_matches),
            "matched_extended_with_source_id_suffix": len(matched_ext),
            "unmatched_extended_with_source_id_suffix": len(unmatched_ext),
            "duplicate_matches_extended": len(duplicate_ext),
        },
        "onenote": {
            "total_pages": len(onenote_pages),
            "matched": len(matched_onenote),
            "unmatched": len(unmatched_onenote),
            "emptyish_pages": emptyish,
        },
        "drafts_scanned": len(draft_paths),
        "high_importance_unmatched_lists": len(high_unmatched),
        "unmatched_theme_buckets": dict(theme_counts),
        "duplicate_list_matches": duplicate_list_matches[:20],
    }
    (OUT_DIR / "reconcile-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    md = render_markdown(summary, high_unmatched, theme_counts, duplicate_list_matches)
    (OUT_DIR / "RECONCILE.md").write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def render_markdown(
    summary: dict,
    high_unmatched: list[dict],
    theme_counts: Counter,
    duplicate_list_matches: list[dict],
) -> str:
    today = summary["generated_on"]
    ls = summary["lists"]
    on = summary["onenote"]
    lp = ls
    lines = [
        "---",
        'snapshot_type: "source_reconciliation_ledger"',
        f'generated_on: "{today}"',
        "review_status: unreviewed",
        "publication_status: not_published",
        "cloud_approval: not_reviewed",
        "---",
        "",
        "# 出典と整備済み下書きの突き合わせ台帳",
        "",
        "> ID の一致だけを記録する。症状・原因の正誤判定、承認、RAG 公開は含まない。",
        "> 正本の運用境界は [knowledge-markdown-foundation.md](../../docs/features/development/knowledge-markdown-foundation.md) と develop 上の [design-2026-10-01-knowhow-flywheel.md](https://github.com/yukiworkspace/EleKnowledge-AI/blob/develop/docs/design-2026-10-01-knowhow-flywheel.md)（段階A）を参照。",
        "",
        "## 突き合わせの意味",
        "",
        "- **一致**: 同じ `list_item_id` または `onenote_id` が、既存の `knowledge/drafts/` にすでに紐づいている。新規事例カードは作らない。",
        "- **未整備**: スナップショット上の ID が、下書き側に見つからない。体系化候補として人がテーマを選ぶ。",
        "- **本文比較はしない**: ファイル名・frontmatter・根拠題名の ID のみ。",
        "",
        "## 件数サマリ",
        "",
        "| 対象 | 総数 | 一致 | 未整備 | 備考 |",
        "| --- | ---: | ---: | ---: | --- |",
        f"| Lists（推奨: ファイル名 + evidence の ID） | {lp['total']} | {lp['matched_primary']} | {lp['unmatched_primary']} | 重複一致 {lp['duplicate_matches_primary']} 件 |",
        f"| Lists（拡張: + source_id 末尾） | {lp['total']} | {lp['matched_extended_with_source_id_suffix']} | {lp['unmatched_extended_with_source_id_suffix']} | 重複 {lp['duplicate_matches_extended']} 件・要確認 |",
        f"| OneNote ページ | {on['total_pages']} | {on['matched']} | {on['unmatched']} | 添付中心で実質空 {on['emptyish_pages']} 件 |",
        f"| 下書き走査 | {summary['drafts_scanned']} | — | — | IMPORT-* を除く |",
        "",
        "## Lists の一致ルール",
        "",
        "各 `list_item_id` について、次のいずれかで下書きを探した。",
        "",
        "1. ファイル名の `ID{番号}` / `_ID{番号}`",
        "2. frontmatter の `evidence_sources` 題名中の `(ID{番号})` / `（ID{番号}）`（本文のエラーコードは対象外）",
        "3. `evidence_sources` 内の `source_id` 末尾 `-{番号}` / `_{番号}`（拡張行。推奨行は 1–2 のみ）",
        "",
        "機械可読な一覧:",
        "",
        "- 一致（推奨）: [reconcile-lists-matched.tsv](./reconcile-lists-matched.tsv)",
        "- 未整備（推奨）: [reconcile-lists-unmatched.tsv](./reconcile-lists-unmatched.tsv)",
        "- 一致 / 未整備（拡張）: [reconcile-lists-matched-extended.tsv](./reconcile-lists-matched-extended.tsv) / [reconcile-lists-unmatched-extended.tsv](./reconcile-lists-unmatched-extended.tsv)",
        "",
        "## OneNote の一致ルール",
        "",
        "ページ frontmatter の `onenote_id` と、下書き frontmatter の `onenote_id` を小文字化して完全一致。",
        "",
        "- 未一致 ID 一覧: [reconcile-onenote-unmatched-ids.txt](./reconcile-onenote-unmatched-ids.txt)",
        "",
        "## 未整備 Lists のテーマ分布（参考）",
        "",
        "| theme_bucket | 件数 |",
        "| --- | ---: |",
    ]
    for name, count in theme_counts.most_common():
        lines.append(f"| `{name}` | {count} |")

    lines.extend(
        [
            "",
            "## 優先してテーマ候補にしたい未整備（重要度 高 / 重要）",
            "",
            f"件数: **{len(high_unmatched)}**（原因・対策の断定はしていない）",
            "",
            "| list_item_id | Model | 重要度 | タイトル（スナップショット） | theme_bucket |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in sorted(high_unmatched, key=lambda r: int(r["list_item_id"]), reverse=True):
        title = row["title"].replace("|", "\\|")[:80]
        lines.append(
            f"| {row['list_item_id']} | {row['model'] or '—'} | {row['importance']} | {title} | `{row['theme_bucket']}` |"
        )

    if duplicate_list_matches:
        lines.extend(
            [
                "",
                "## 同一 list_item_id が複数下書きに付いた例（要確認）",
                "",
                "ID 一致だけではどちらを正とするか決めない。担当者が確認する。",
                "",
                "| list_item_id | record_ids | タイトル |",
                "| --- | --- | --- |",
            ]
        )
        for row in duplicate_list_matches[:15]:
            title = row["title"].replace("|", "\\|")[:60]
            lines.append(
                f"| {row['list_item_id']} | `{', '.join(row['record_ids'])}` | {title} |"
            )

    lines.extend(
        [
            "",
            "## この台帳の範囲外",
            "",
            "- 新しい Markdown 本文の生成",
            "- 承認・公開・Bedrock KB への取り込み",
            "- OneNote / Lists への書き戻し",
            "",
            "次のステップ: 上記テーマ候補から **少数テーマ** を人が選び、選んだ ID だけ体系化（差分案）に進む。",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
