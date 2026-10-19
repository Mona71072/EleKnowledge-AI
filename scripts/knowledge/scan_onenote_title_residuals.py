#!/usr/bin/env python3
"""Find OneNote pages whose body contains full Lists title for cards still without ref."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTS = ROOT / "knowledge" / "source-snapshots" / "首都工_不具合情報共有リスト_初期スナップショット.md"
ON = ROOT / "knowledge" / "source-snapshots" / "onenote"
CARDS = ROOT / "knowledge" / "cards"
L2C = ROOT / "knowledge" / "registry" / "list-item-to-card.jsonl"
OUT = ROOT / "knowledge" / "registry" / "lists-onenote-residual-hits.jsonl"
KNOWN = ROOT / "knowledge" / "registry" / "lists-onenote-title-hits.jsonl"


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s.replace("（", "(").replace("）", ")"))


def list_titles() -> dict[str, str]:
    text = LISTS.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for m in re.finditer(r"^## Lists item ID (\d+): (.+)$", text, re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def load_pages() -> list[tuple[str, str, str]]:
    pages: list[tuple[str, str, str]] = []
    for path in ON.glob("onenote-*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        oid_m = re.search(r'^onenote_id:\s*"([^"]+)"', text, re.M)
        oid = oid_m.group(1) if oid_m else ""
        body = text.split("## OneNote content", 1)[-1] if "## OneNote content" in text else text
        pages.append((path.name, oid, body))
    return pages


def cards_without_onenote() -> set[str]:
    need: set[str] = set()
    for line in L2C.read_text(encoding="utf-8").splitlines():
        if line.strip():
            need.add(json.loads(line)["list_item_id"])
    for path in CARDS.rglob("*.md"):
        if path.name in ("INDEX.md", "TEMPLATE.md", "_SOURCE-LEGEND.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = text[3:end]
        m = re.search(r'list_item_id:\s*["\']?(\d+)', fm)
        if not m:
            continue
        lid = m.group(1)
        if "ref_type: onenote_page" in fm or "onenote_id" in text[end:]:
            need.discard(lid)
    return need


def already_known() -> set[str]:
    s: set[str] = set()
    if KNOWN.is_file():
        for line in KNOWN.read_text(encoding="utf-8").splitlines():
            if line.strip():
                s.add(json.loads(line)["list_item_id"])
    return s


def main() -> None:
    titles = list_titles()
    pages = load_pages()
    need = cards_without_onenote() - already_known()
    rows: list[dict] = []
    for lid in sorted(need, key=int):
        title = titles.get(lid, "")
        if not title or title.startswith("（情報管理"):
            continue
        nt = norm(title)
        if len(nt) < 8:
            continue
        hits: list[dict] = []
        for fname, oid, body in pages:
            nb = norm(body)
            if nt in nb:
                hits.append({"file": fname, "onenote_id": oid, "match": "full_title"})
                continue
            if len(nt) >= 12 and nt[:12] in nb and nt not in nb:
                continue  # skip weak prefix-only
        if hits:
            rows.append({"list_item_id": lid, "title": title, "hits": hits[:3]})
    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    print(json.dumps({"scanned_need": len(need), "new_hits": len(rows), "out": str(OUT.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
