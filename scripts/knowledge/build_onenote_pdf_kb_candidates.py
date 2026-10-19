#!/usr/bin/env python3
"""Extract C-/TI-/EA- document hints from OneNote catalog outgoing titles → candidate ledger."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "knowledge" / "registry" / "onenote-page-catalog.jsonl"
OUT = ROOT / "knowledge" / "registry" / "onenote-pdf-kb-candidates.jsonl"

DOC_RE = re.compile(
    r"(C-\d+[-\w.]+(?:-J|-U\d+\.\d+-J)?|TI-\d+|EA-\d+[-\w.]+|SUE-\d+[-\w.]*)",
    re.I,
)


def main() -> None:
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        oid = rec["onenote_id"]
        snap = rec.get("snapshot_file", "")
        for title in rec.get("outgoing_titles_sample") or []:
            for m in DOC_RE.finditer(title):
                doc = m.group(1).upper().replace("_", "-")
                key = (oid, doc)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "onenote_id": oid,
                        "snapshot_file": snap,
                        "document_number_hint": doc,
                        "source_title_sample": title[:120],
                        "kb_verify_status": "pending",
                        "note": "catalog outgoing only — resolve via build_kb_document_index / KB-REF-WORKFLOW",
                    }
                )
    OUT.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )
    print(json.dumps({"candidates": len(rows), "out": str(OUT.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
