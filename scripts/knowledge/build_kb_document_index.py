#!/usr/bin/env python3
"""Build machine-readable KB catalog index from docs/kb-metadata-catalog-*.md."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
OUT = ROOT / "knowledge" / "registry" / "kb-document-index.jsonl"

ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|")
AS_OF_RE = re.compile(r"取得日:\*\*\s*(\d{4}-\d{2}-\d{2})")


def find_catalog_md() -> Path:
    dated = sorted(DOCS.glob("kb-metadata-catalog-*.md"), reverse=True)
    if dated:
        return dated[0]
    legacy = DOCS / "kb-metadata-catalog-2026-08-26.md"
    if legacy.exists():
        return legacy
    sys.exit("docs/kb-metadata-catalog-*.md not found")


def catalog_as_of(text: str) -> str:
    m = AS_OF_RE.search(text)
    return m.group(1) if m else "unknown"


def stem(filename: str) -> str:
    name = filename
    if name.lower().endswith(".pdf"):
        name = name[:-4]
    return name.strip()


def main() -> None:
    catalog_path = find_catalog_md()
    text = catalog_path.read_text(encoding="utf-8")
    as_of = catalog_as_of(text)
    category = "unknown"
    rows: list[dict] = []

    for line in text.splitlines():
        if line.startswith("### "):
            category = line.removeprefix("### ").split("（", 1)[0].strip()
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        filename, model_type, tags, note = (x.strip() for x in m.groups())
        if filename in ("filename", "file_path"):
            continue
        file_stem = stem(filename)
        rows.append(
            {
                "filename": filename,
                "file_stem": file_stem,
                "category": category,
                "model_type": model_type.replace("—", "").strip() or None,
                "tags": tags.replace("—", "").strip() or None,
                "catalog_source": str(catalog_path.relative_to(ROOT)),
                "catalog_as_of": as_of,
                "unindexed_note": note if "未索引" in note else None,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({"catalog": catalog_path.name, "as_of": as_of, "entries": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
