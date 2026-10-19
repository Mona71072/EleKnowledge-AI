#!/usr/bin/env python3
"""Repair YAML frontmatter when closing --- was merged into the last field line."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"


def main() -> None:
    fixed = 0
    for p in sorted(CARDS.rglob("*.md")):
        if p.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        if re.match(r"---\n.*?\n---\n", text, re.S):
            continue
        new = re.sub(
            r"^(---\n.*?)([\"'].*?[\"'])---(\n\n# )",
            r"\1\2\n---\3",
            text,
            count=1,
            flags=re.S,
        )
        if new == text:
            new = re.sub(
                r"^(---\n.*?)(\S)---(\n\n# )",
                r"\1\2\n---\3",
                text,
                count=1,
                flags=re.S,
            )
        if new != text:
            p.write_text(new, encoding="utf-8")
            fixed += 1
    print(json.dumps({"fixed": fixed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
