#!/usr/bin/env python3
"""For index/hybrid/empty page_role refs, simplify ### OneNote to navigation-only."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
CATALOG = ROOT / "knowledge" / "registry" / "onenote-page-catalog.jsonl"

NAV_ONLY = re.compile(
    r"(### OneNote\s*\n\s*\n)(.*?)(?=\n## )",
    re.S,
)

NEIGHBOR_BLOCK = re.compile(
    r"\n\*\*同(?: OneNote ページ|页)の別(?:タイトル)?索引\*\*.*?(?=\n## )",
    re.S,
)


def catalog_roles() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["onenote_id"]] = row["page_role"]
    return out


def parse_refs(fm: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for block in re.split(r"\n\s*-\s*ref_type:\s*onenote_page\s*\n", fm):
        if "onenote_id:" not in block:
            continue
        oid_m = re.search(r'onenote_id:\s*"([^"]+)"', block)
        role_m = re.search(r"page_role:\s*(\w+)", block)
        if oid_m:
            refs.append((oid_m.group(1), role_m.group(1) if role_m else ""))
    return refs


def main() -> None:
    cat = catalog_roles()
    updated = 0
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = text[3:end]
        body = text[end + 4 :]
        index_oids = [
            oid
            for oid, role in parse_refs(fm)
            if role in ("index", "empty", "hybrid") or cat.get(oid) in ("index", "hybrid", "empty_or_attachment_only")
        ]
        if not index_oids and not NEIGHBOR_BLOCK.search(body):
            continue
        new_body = NEIGHBOR_BLOCK.sub("\n", body)
        m = NAV_ONLY.search(new_body)
        if m and index_oids:
            oid = index_oids[0]
            snap = ""
            for line in CATALOG.read_text(encoding="utf-8").splitlines():
                if line.strip() and json.loads(line)["onenote_id"] == oid:
                    snap = json.loads(line)["snapshot_file"]
                    break
            inner = (
                f"- **索引頁** `{oid}`（`{snap}`）— **navigation のみ**。"
                " 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。\n\n"
            )
            new_body = NAV_ONLY.sub(r"\1" + inner, new_body, count=1)
        if new_body != body:
            path.write_text(f"---\n{fm.rstrip()}\n---\n{new_body.lstrip(chr(10))}", encoding="utf-8")
            updated += 1
    print(json.dumps({"updated": updated}, ensure_ascii=False))


if __name__ == "__main__":
    main()
