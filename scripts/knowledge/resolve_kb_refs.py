#!/usr/bin/env python3
"""Resolve document_number refs against kb-document-index.jsonl."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "knowledge" / "registry" / "kb-document-index.jsonl"
CARDS = ROOT / "knowledge" / "cards"
OUT = ROOT / "knowledge" / "registry" / "kb-ref-resolution.jsonl"
REPORT = ROOT / "knowledge" / "validation" / "kb-ref-status-wave1-2.md"

CATALOG_MD = "docs/kb-metadata-catalog-2026-08-26.md"

DOC_ALIASES = {
    "S-EL-323": ["S-EL-323", "S-EL-323.1", "S-EL・323"],
    "S-EL・323": ["S-EL-323", "S-EL-323.1", "S-EL・323"],
}

# Lists 通称 → カタログ上の図番（2026-08-26 実測一覧で filename 存在を確認済み）
LIST_LABEL_TO_CATALOG_STEM = {
    "VFGLF据付調整資料抜粋_シーケンス表示": "C-7-C3900-J-E",
}

# Lists 資料番号がカタログに無いときの関連 KB（要 content_reviewed）
RELATED_IN_CATALOG = {
    "S-1-Z06.1": [
        {
            "document_number": "TI-1371",
            "kb_filename": "TI-1371.pdf",
            "kb_category": "テクニカルインフォメーション",
            "note": "BSER-CP・長周期振動（Lists S-1-Z06.1 の代替探索候補）",
        }
    ],
}


def normalize_ref(raw: str) -> str:
    s = raw.strip().strip('"').replace("・", "-")
    s = re.sub(r"\s+", "", s)
    return s


def stem(filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return filename[:-4]
    return filename


class IndexEntry(NamedTuple):
    filename: str
    file_stem: str
    category: str
    model_type: str | None
    catalog_as_of: str


def load_index() -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        entries.append(
            IndexEntry(
                filename=row["filename"],
                file_stem=row["file_stem"],
                category=row.get("category") or "",
                model_type=row.get("model_type"),
                catalog_as_of=row.get("catalog_as_of") or "unknown",
            )
        )
    return entries


def resolve_one(ref: str, entries: list[IndexEntry]) -> dict:
    variants = [normalize_ref(ref)] + [normalize_ref(v) for v in DOC_ALIASES.get(ref, [])]
    seen: set[str] = set()
    variants = [v for v in variants if not (v in seen or seen.add(v))]

    for variant in variants:
        exact_pdf = variant if variant.lower().endswith(".pdf") else f"{variant}.pdf"
        for e in entries:
            if e.filename == exact_pdf or e.file_stem == variant:
                return {
                    "document_number": ref,
                    "kb_verify_status": "catalog_matched",
                    "match_kind": "exact",
                    "kb_filename": e.filename,
                    "kb_category": e.category,
                    "model_type": e.model_type,
                    "catalog_as_of": e.catalog_as_of,
                }

    mapped = LIST_LABEL_TO_CATALOG_STEM.get(ref)
    if mapped:
        inner = resolve_one(mapped, entries)
        if inner.get("kb_verify_status") == "catalog_matched":
            inner["document_number"] = ref
            inner["match_kind"] = "list_label_map"
            inner["catalog_stem"] = mapped
            return inner

    prefix_hits: list[IndexEntry] = []
    for variant in variants:
        if not re.match(r"^[A-Z0-9][A-Z0-9.-]{2,}$", variant):
            continue
        for e in entries:
            if e.file_stem.startswith(variant):
                prefix_hits.append(e)
    if len(prefix_hits) == 1:
        e = prefix_hits[0]
        return {
            "document_number": ref,
            "kb_verify_status": "catalog_matched",
            "match_kind": "prefix",
            "kb_filename": e.filename,
            "kb_category": e.category,
            "model_type": e.model_type,
            "catalog_as_of": e.catalog_as_of,
        }
    if len(prefix_hits) > 1:
        return {
            "document_number": ref,
            "kb_verify_status": "catalog_ambiguous",
            "match_kind": "prefix",
            "candidates": [e.filename for e in prefix_hits[:8]],
            "catalog_as_of": prefix_hits[0].catalog_as_of,
        }

    row = {
        "document_number": ref,
        "kb_verify_status": "not_in_catalog",
        "match_kind": "none",
        "catalog_as_of": entries[0].catalog_as_of if entries else "unknown",
        "catalog_source": CATALOG_MD,
    }
    related = RELATED_IN_CATALOG.get(ref)
    if related:
        row["related_in_catalog"] = related
    return row


def collect_refs() -> list[tuple[str, str]]:
    """Return (knowledge_id, document_number) from card frontmatter."""
    pairs: list[tuple[str, str]] = []
    for path in sorted(CARDS.rglob("*.md")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = text[3:end] if end != -1 else ""
        kid_m = re.search(r"^knowledge_id:\s*(\S+)", fm, re.M)
        if not kid_m:
            continue
        kid = kid_m.group(1)
        in_kb = False
        for line in fm.splitlines():
            if re.match(r"\s*-\s*ref_type:\s*kb_document\b", line):
                in_kb = True
                continue
            if in_kb and re.match(r"\s*-\s*ref_type:\s*\w+", line):
                in_kb = False
            if in_kb:
                m = re.match(r'\s*document_number:\s*["\']?([^"\']+)', line)
                if m:
                    pairs.append((kid, m.group(1).strip()))
    return pairs


def main() -> None:
    if not INDEX.exists():
        raise SystemExit("Run build_kb_document_index.py first")

    entries = load_index()
    rows: list[dict] = []
    for kid, doc in collect_refs():
        row = resolve_one(doc, entries)
        row["knowledge_id"] = kid
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    as_of = entries[0].catalog_as_of if entries else "?"
    lines = [
        "# Wave1/2 KB 資料番号 — カタログ突合",
        "",
        "> 正本: **`docs/kb-metadata-catalog-2026-08-26.md`**（S3 実測 **3,745** 件。C資料 729 / TI 308 / 据付基準 121 等）",
        "> 本文確認前の **filename 突合** のみ。`content_reviewed` は PDF 確認後。",
        f"> 機械可読: `registry/kb-document-index.jsonl`（catalog_as_of: {as_of}）",
        "",
        "| knowledge_id | document_number | 状態 | KB filename | category |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        fn = r.get("kb_filename") or ("候補: " + ", ".join(r.get("candidates", [])) if r.get("candidates") else "—")
        if r.get("catalog_stem"):
            fn = f"{fn}（図番 `{r['catalog_stem']}`）"
        lines.append(
            f"| {r['knowledge_id']} | {r['document_number']} | {r['kb_verify_status']} | {fn} | {r.get('kb_category') or '—'} |"
        )
    related_rows = [r for r in rows if r.get("related_in_catalog")]
    if related_rows:
        lines.extend(["", "## カタログ未収載だが関連 PDF あり（Lists 番号の探索候補）", ""])
        for r in related_rows:
            for rel in r["related_in_catalog"]:
                lines.append(
                    f"- **{r['knowledge_id']}** / Lists `{r['document_number']}` → `{rel['kb_filename']}`（{rel['note']}）"
                )
    absent = [r for r in rows if r["kb_verify_status"] == "not_in_catalog" and not r.get("related_in_catalog")]
    if absent:
        lines.extend(
            [
                "",
                "## カタログに filename 無し（2026-08-26 時点）",
                "",
                "以下は `kb-metadata-catalog-2026-08-26.md` 全件および旧 TSV を **図番文字列で検索** しても該当 PDF 名が無い。",
                "",
            ]
        )
        for r in absent:
            lines.append(f"- `{r['document_number']}`（{r['knowledge_id']}）")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"resolved": len(rows), "report": str(REPORT.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
