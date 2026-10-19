#!/usr/bin/env python3
"""Prefix same-directory card links with ./ for consistency."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
LINK = re.compile(r"\]\((KH-[^)]+\.md)\)")


def main() -> None:
    n = 0
    files = 0
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")

        def sub(m: re.Match[str]) -> str:
            nonlocal n
            fn = m.group(1)
            if (path.parent / fn).is_file():
                n += 1
                return f"](./{fn})"
            for subdir in ("case-summaries", "practice-guides"):
                alt = path.parent.parent / subdir / fn
                if alt.is_file() and path.parent.name != subdir:
                    n += 1
                    return f"](../{subdir}/{fn})"
            return m.group(0)

        new = LINK.sub(sub, text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            files += 1
    print(json.dumps({"files": files, "fixes": n}, ensure_ascii=False))


if __name__ == "__main__":
    main()
