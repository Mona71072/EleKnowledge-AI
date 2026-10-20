#!/usr/bin/env python3
"""Add onenote_page source_refs from lists-onenote-title-hits.jsonl when missing."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
HITS = ROOT / "knowledge" / "registry" / "lists-onenote-title-hits.jsonl"

NONE_BLOCK = re.compile(
    r"(### OneNote\s*\n\s*\n)- タイトル一致索引なし。\s*\n",
    re.M,
)


def load_hits() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in HITS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["list_item_id"]] = row
    return out


def primary_list_id(fm: str) -> str | None:
    m = re.search(
        r"ref_type:\s*lists_item\s*\n\s*list_item_id:\s*[\"']?(\d+)",
        fm,
    )
    return m.group(1) if m else None


def has_onenote(fm: str) -> bool:
    return "ref_type: onenote_page" in fm or "ref_type: onenote" in fm


def main() -> None:
    import sys

    apply = "--apply" in sys.argv
    hits = load_hits()
    updated = 0
    candidates: list[dict] = []
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        fm = text[3:end]
        body = text[end + 4 :]
        lid = primary_list_id(fm)
        if not lid or lid not in hits or has_onenote(fm):
            continue
        h = hits[lid]["hits"][0]
        oid = h["onenote_id"]
        snap = h["file"]
        kid = re.search(r"^knowledge_id:\s*(\S+)", fm, re.M)
        candidates.append(
            {
                "list_item_id": lid,
                "knowledge_id": kid.group(1) if kid else "",
                "onenote_id": oid,
                "source": "title_hit",
                "snapshot_file": snap,
            }
        )
        if not apply:
            continue
        note = f"Lists タイトル一致 — snapshot `{snap}`（本文未転載）"
        ref_block = (
            f"  - ref_type: onenote_page\n"
            f"    onenote_id: \"{oid}\"\n"
            f"    note: \"{note}\"\n"
        )
        if "source_refs:" not in fm:
            continue
        fm_new = fm.rstrip() + "\n" + ref_block
        onenote_body = (
            f"- **onenote_id**: `{oid}` — Lists §{lid} タイトル一致（`{snap}`）。"
            " 本文はスナップショット参照・未転載。\n\n"
        )
        if NONE_BLOCK.search(body):
            body = NONE_BLOCK.sub(r"\1" + onenote_body, body, count=1)
        elif "### OneNote" not in body:
            # insert after ### Lists block (first occurrence under ソース要約)
            m = re.search(r"(## ソース要約\s*\n.*?### Lists.*?\n(?:.*?\n)*?)(\n## )", body, re.S)
            if m:
                insert = m.group(1) + "\n### OneNote\n\n" + onenote_body + m.group(2)
                body = body[: m.start()] + insert + body[m.end() :]
            else:
                continue
        else:
            # OneNote section exists but not なし — skip body
            pass
        path.write_text(f"---\n{fm_new.rstrip()}\n---\n{body.lstrip(chr(10))}", encoding="utf-8")
        updated += 1
    out = ROOT / "knowledge" / "registry" / "onenote-attach-candidates-title.jsonl"
    if candidates:
        out.write_text(
            "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in candidates),
            encoding="utf-8",
        )
    print(json.dumps({"updated": updated, "candidates": len(candidates), "apply": apply}, ensure_ascii=False))


if __name__ == "__main__":
    main()
