#!/usr/bin/env python3
"""Attach onenote_page refs from linked drafts (list-item-to-record) when card lacks OneNote."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
DRAFTS = ROOT / "knowledge" / "drafts"
L2R = ROOT / "knowledge" / "registry" / "list-item-to-record.jsonl"
OUT = ROOT / "knowledge" / "registry" / "lists-onenote-draft-hits.jsonl"


def load_l2r() -> dict[str, list[dict]]:
    by: dict[str, list[dict]] = defaultdict(list)
    for line in L2R.read_text(encoding="utf-8").splitlines():
        if line.strip():
            by[json.loads(line)["list_item_id"]].append(json.loads(line))
    return by


def onenote_from_draft(record_id: str, path_hint: str) -> list[tuple[str, str]]:
    candidates: list[Path] = []
    if path_hint:
        candidates.append(DRAFTS / path_hint)
    candidates.append(DRAFTS / f"{record_id}.md")
    for p in DRAFTS.rglob("*.md"):
        if record_id in p.stem or (path_hint and path_hint in p.name):
            candidates.append(p)
    oids: list[tuple[str, str]] = []
    seen: set[str] = set()
    for p in candidates:
        if not p.is_file():
            continue
        key = str(p.resolve())
        if key in seen:
            continue
        seen.add(key)
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'onenote_id:\s*["\']([^"\']+)["\']', text):
            oid = m.group(1).strip()
            if oid:
                oids.append((oid, p.name))
    return oids


def primary_list_id(fm: str) -> str | None:
    m = re.search(
        r"ref_type:\s*lists_item\s*\n\s*list_item_id:\s*[\"']?(\d+)",
        fm,
    )
    return m.group(1) if m else None


def has_onenote(fm: str) -> bool:
    return "ref_type: onenote_page" in fm


def main() -> None:
    import sys

    apply = "--apply" in sys.argv
    by_lid = load_l2r()
    rows: list[dict] = []
    updated = 0
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---") or "索引未検出" not in text:
            continue
        end = text.find("\n---", 3)
        fm = text[3:end]
        body = text[end + 4 :]
        if has_onenote(fm):
            continue
        lid = primary_list_id(fm)
        if not lid:
            continue
        pick: tuple[str, str, str] | None = None
        for rec in by_lid.get(lid, []):
            oids = onenote_from_draft(rec["record_id"], rec.get("path", ""))
            if oids:
                pick = (oids[0][0], oids[0][1], rec["record_id"])
                break
        if not pick:
            continue
        oid, draft_name, record_id = pick
        kid_m = re.search(r"knowledge_id:\s*(\S+)", fm)
        rows.append(
            {
                "list_item_id": lid,
                "knowledge_id": kid_m.group(1) if kid_m else "",
                "onenote_id": oid,
                "draft": draft_name,
                "record_id": record_id,
                "source": "draft_hit",
            }
        )
        if not apply:
            continue
        note = f"draft 索引 — `{draft_name}` / record `{record_id}`（本文未転載）"
        fm = fm.rstrip() + (
            f"\n  - ref_type: onenote_page\n"
            f'    onenote_id: "{oid}"\n'
            f'    note: "{note}"\n'
        )
        # §3 OneNote: replace 未検出 line
        on_body = (
            f"- **onenote_id**: `{oid}` — {note}\n\n"
        )
        body = re.sub(
            r"(### OneNote\s*\n\s*\n)- スナップショット照合:.*?。\s*\n",
            r"\1" + on_body,
            body,
            count=1,
            flags=re.S,
        )
        path.write_text(f"---\n{fm.rstrip()}\n---\n{body.lstrip(chr(10))}", encoding="utf-8")
        updated += 1

    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"updated": updated, "candidates": len(rows), "apply": apply, "out": str(OUT.relative_to(ROOT))},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
