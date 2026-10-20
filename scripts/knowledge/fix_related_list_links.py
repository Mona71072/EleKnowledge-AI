#!/usr/bin/env python3
"""Linkify | **NNN** | in card tables using list-item-to-card.jsonl."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
REGISTRY = ROOT / "knowledge" / "registry" / "list-item-to-card.jsonl"

# duplicate primary: prefer this card_path
PREFER: dict[str, str] = {
    "227": "practice-guides/KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md",
    "154": "practice-guides/KH-MRL-SMOKE-SHAFT-SENSOR-154.md",
}

ROW = re.compile(r"(\|\s)\*\*(\d{1,3})\*\*(\s*\|)")


def load_index() -> dict[str, list[dict]]:
    by_id: dict[str, list[dict]] = defaultdict(list)
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if line.strip():
            by_id[json.loads(line)["list_item_id"]].append(json.loads(line))
    return by_id


def pick_path(lid: str, rows: list[dict]) -> str | None:
    if lid in PREFER:
        return PREFER[lid]
    for r in rows:
        if r["knowledge_id"].endswith(f"-{lid}"):
            return r["card_path"]
    return rows[0]["card_path"] if rows else None


def rel_href(from_file: Path, card_path: str) -> str:
    target = CARDS / card_path
    rel = Path(os_relpath(target, from_file.parent))
    return rel.as_posix()


def os_relpath(target: Path, start: Path) -> str:
    import os

    return os.path.relpath(target, start)


def frontmatter_kid(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else ""
    m = re.search(r"^knowledge_id:\s*(\S+)", fm, re.M)
    return m.group(1) if m else ""


def process_file(path: Path, by_id: dict[str, list[dict]]) -> tuple[str, int]:
    text = path.read_text(encoding="utf-8")
    kid = frontmatter_kid(text)
    n = 0

    def sub(m: re.Match[str]) -> str:
        nonlocal n
        lid = m.group(2)
        if lid not in by_id:
            return m.group(0)
        if kid.endswith(f"-{lid}"):
            return m.group(0)
        card_path = pick_path(lid, by_id[lid])
        if not card_path:
            return m.group(0)
        href = rel_href(path, card_path)
        # already linked on this line
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        line = text[line_start:line_end if line_end != -1 else None]
        if "](." in line or f"]({href}" in line:
            return m.group(0)
        n += 1
        return f"{m.group(1)}[{lid}]({href}){m.group(3)}"

    new = ROW.sub(sub, text)
    return new, n


def main() -> None:
    by_id = load_index()
    total = 0
    files = 0
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        new, n = process_file(path, by_id)
        if n:
            path.write_text(new, encoding="utf-8")
            total += n
            files += 1
    print(json.dumps({"files": files, "replacements": total}, ensure_ascii=False))


if __name__ == "__main__":
    main()
