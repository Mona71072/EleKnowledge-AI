#!/usr/bin/env python3
"""Set page_role on card onenote_page refs from onenote-page-catalog.jsonl."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
CATALOG = ROOT / "knowledge" / "registry" / "onenote-page-catalog.jsonl"

ROLE_MAP = {
    "index": "index",
    "hybrid": "hybrid",
    "content": "body",
    "cross_topic": "cross_cutting",
    "empty_or_attachment_only": "empty",
}


def load_catalog() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["onenote_id"]] = ROLE_MAP.get(row["page_role"], row["page_role"])
    return out


def main() -> None:
    catalog = load_catalog()
    updated = 0
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---") or "ref_type: onenote_page" not in text:
            continue
        end = text.find("\n---", 3)
        fm = text[3:end]
        body = text[end + 4 :]
        new_fm = fm
        changed = False
        for oid, role in catalog.items():
            if f'onenote_id: "{oid}"' not in new_fm:
                continue
            if re.search(rf'onenote_id:\s*"{re.escape(oid)}"[^\n]*\n(?:\s*page_role:)', new_fm):
                continue
            new_fm = re.sub(
                rf'(onenote_id:\s*"{re.escape(oid)}"\s*\n)',
                rf'\1    page_role: {role}\n',
                new_fm,
                count=1,
            )
            changed = True
        if changed:
            path.write_text(f"---\n{new_fm.rstrip()}\n---\n{body.lstrip(chr(10))}", encoding="utf-8")
            updated += 1
    print(json.dumps({"updated": updated}, ensure_ascii=False))


if __name__ == "__main__":
    main()
