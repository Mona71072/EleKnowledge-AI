#!/usr/bin/env python3
"""Classify OneNote snapshot pages by role (index/content/cross_topic/empty)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ON = ROOT / "knowledge" / "source-snapshots" / "onenote"
OUT = ROOT / "knowledge" / "registry" / "onenote-page-catalog.jsonl"
SUMMARY = ROOT / "knowledge" / "registry" / "onenote-page-catalog-summary.json"

LINK_LINE = re.compile(r"\[([^\]]+)\]\(\[URL omitted")
HEADING = re.compile(r"^【[^】]+】")


def classify(body: str) -> tuple[str, str]:
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if not lines or len(body.strip()) < 15:
        return "empty_or_attachment_only", "minimal_body"
    link_lines = sum(1 for ln in lines if LINK_LINE.search(ln) or "URL omitted" in ln)
    non_link = [ln for ln in lines if not LINK_LINE.search(ln) and "URL omitted" not in ln]
    attachment_only = body.count("attachment reference omitted") >= 1 and len(non_link) <= 2
    if attachment_only:
        return "empty_or_attachment_only", "attachment_only"
    if link_lines >= 3 and link_lines >= max(1, len(lines) * 0.45):
        if len(non_link) >= 2 and any(len(x) > 40 for x in non_link):
            return "hybrid", "index_plus_body"
        return "index", "link_list"
    if any(HEADING.match(ln) for ln in lines) and link_lines >= 1:
        return "cross_topic", "sectioned_notes"
    if len(body) > 1200:
        return "content", "long_body"
    return "content", "short_body"


def outgoing_titles(body: str) -> list[str]:
    return [m.group(1).strip() for m in LINK_LINE.finditer(body)]


def main() -> None:
    rows: list[dict] = []
    counts: dict[str, int] = {}
    for path in sorted(ON.glob("onenote-*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        oid_m = re.search(r'^onenote_id:\s*"([^"]+)"', text, re.M)
        oid = oid_m.group(1) if oid_m else ""
        resolved = "source_links_resolved: true" in text[:800]
        body = text.split("## OneNote content", 1)[-1] if "## OneNote content" in text else text
        role, reason = classify(body)
        rows.append(
            {
                "onenote_id": oid,
                "snapshot_file": path.name,
                "page_role": role,
                "classify_reason": reason,
                "source_links_resolved": resolved,
                "body_chars": len(body.strip()),
                "outgoing_link_count": len(outgoing_titles(body)),
                "outgoing_titles_sample": outgoing_titles(body)[:8],
            }
        )
        counts[role] = counts.get(role, 0) + 1

    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    SUMMARY.write_text(
        json.dumps({"pages": len(rows), "by_role": counts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"pages": len(rows), "by_role": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
