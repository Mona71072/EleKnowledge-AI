#!/usr/bin/env python3
"""Match Lists snapshot titles against OneNote snapshot page bodies."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTS = ROOT / "knowledge" / "source-snapshots" / "首都工_不具合情報共有リスト_初期スナップショット.md"
ONENOTE = ROOT / "knowledge" / "source-snapshots" / "onenote"
OUT = ROOT / "knowledge" / "registry" / "lists-onenote-title-hits.jsonl"


def list_items() -> list[tuple[str, str]]:
    text = LISTS.read_text(encoding="utf-8")
    items: list[tuple[str, str]] = []
    current_id = ""
    for line in text.splitlines():
        m = re.match(r"^## Lists item ID (\d+): (.+)$", line)
        if m:
            current_id, title = m.group(1), m.group(2).strip()
            items.append((current_id, title))
    return items


def onenote_pages() -> list[tuple[str, str, str]]:
    pages: list[tuple[str, str, str]] = []
    for path in ONENOTE.glob("onenote-*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = re.search(r'^onenote_id:\s*"([^"]+)"', text, re.M)
        oid = fm.group(1) if fm else ""
        body = text.split("## OneNote content", 1)[-1] if "## OneNote content" in text else text
        pages.append((path.name, oid, body))
    return pages


def main() -> None:
    pages = onenote_pages()
    rows: list[dict] = []
    for lid, title in list_items():
        if "情報管理確認まで保留" in title and title.startswith("（"):
            continue
        hits = []
        for fname, oid, body in pages:
            if title in body or title.replace(" ", "") in body.replace(" ", ""):
                hits.append({"file": fname, "onenote_id": oid})
        if hits:
            rows.append({"list_item_id": lid, "title": title, "hits": hits})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"list_items_with_onenote_hit": len(rows), "out": str(OUT.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
