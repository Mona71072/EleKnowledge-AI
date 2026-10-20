#!/usr/bin/env python3
"""Build OneNote jump index: card → snapshot, and index pages → child content pages.

Answer lives on content / cross_topic pages. Index / hybrid pages are navigation.
Does not copy page titles (index transcription rule).
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HIERARCHY = ROOT / "knowledge" / "source-snapshots" / "onenote" / "HIERARCHY.json"
CATALOG = ROOT / "knowledge" / "registry" / "onenote-page-catalog.jsonl"
CARDS = ROOT / "knowledge" / "cards"
REGISTRY = ROOT / "knowledge" / "registry"
OUT_PAGES = REGISTRY / "onenote-jump-index.jsonl"
OUT_CARDS = REGISTRY / "card-onenote-jumps.jsonl"

ANSWER_ROLES = {"content", "cross_topic"}
NAV_ROLES = {"index", "hybrid", "empty_or_attachment_only"}
CHILD_CAP = 12


def load_catalog() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not CATALOG.is_file():
        return out
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        oid = str(row.get("onenote_id", "")).strip()
        if oid:
            out[oid] = row
    return out


def load_hierarchy() -> list[dict]:
    data = json.loads(HIERARCHY.read_text(encoding="utf-8"))
    return list(data.get("pages") or [])


def frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def cards_by_onenote() -> dict[str, list[dict]]:
    found: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(CARDS.rglob("*.md")):
        if path.name.startswith("_") or path.name in {"INDEX.md", "TEMPLATE.md", "README.md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter(text)
        kid_m = re.search(r"^knowledge_id:\s*(\S+)", fm, re.M)
        kid = kid_m.group(1) if kid_m else path.stem
        rel = path.relative_to(CARDS).as_posix()
        seen: set[str] = set()
        for m in re.finditer(r'onenote_id:\s*["\']?([^"\'\s]+)', fm):
            oid = m.group(1).strip()
            if oid in seen:
                continue
            seen.add(oid)
            found[oid].append({"knowledge_id": kid, "card_path": rel})
    return found


def content_children(children: list[str], catalog: dict[str, dict]) -> list[str]:
    return [
        c
        for c in children
        if (catalog.get(c) or {}).get("page_role") in ANSWER_ROLES
    ][:CHILD_CAP]


def answer_for(
    page: dict,
    children: list[str],
    catalog: dict[str, dict],
    cited_by_cards: bool,
) -> tuple[str, list[str]]:
    oid = page["onenote_id"]
    role = (catalog.get(oid) or {}).get("page_role") or "unknown"
    kids = content_children(children, catalog)
    if role in ANSWER_ROLES:
        return "read_this_page", [oid]
    if kids:
        return "navigate_to_child_content", kids
    if cited_by_cards:
        return "use_citing_cards", []
    if role in NAV_ROLES or role == "unknown":
        return "navigation_only", []
    return "navigation_only", []


def main() -> None:
    catalog = load_catalog()
    pages = load_hierarchy()
    by_parent: dict[str, list[str]] = defaultdict(list)
    page_by_id = {p["onenote_id"]: p for p in pages}
    for p in pages:
        parent = p.get("parent_onenote_id")
        if parent:
            by_parent[parent].append(p["onenote_id"])

    card_map = cards_by_onenote()
    page_rows: list[dict] = []
    modes = defaultdict(int)

    for p in pages:
        oid = p["onenote_id"]
        cat = catalog.get(oid) or {}
        children = by_parent.get(oid, [])
        cards = card_map.get(oid, [])
        mode, targets = answer_for(p, children, catalog, bool(cards))
        modes[mode] += 1
        kid_ids = content_children(children, catalog)
        page_rows.append(
            {
                "onenote_id": oid,
                "snapshot_file": cat.get("snapshot_file"),
                "page_role": cat.get("page_role"),
                "hierarchy_status": p.get("hierarchy_status"),
                "parent_onenote_id": p.get("parent_onenote_id"),
                "page_level": p.get("page_level"),
                "child_count": len(children),
                "child_content_pages": [
                    {
                        "onenote_id": c,
                        "snapshot_file": (catalog.get(c) or {}).get("snapshot_file"),
                        "page_role": (catalog.get(c) or {}).get("page_role"),
                    }
                    for c in kid_ids
                ],
                "answer_mode": mode,
                "answer_onenote_ids": targets,
                "cards": cards,
            }
        )

    page_rows.sort(key=lambda r: r["onenote_id"])
    OUT_PAGES.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in page_rows),
        encoding="utf-8",
    )

    by_card: dict[str, dict] = {}
    for row in page_rows:
        for card in row["cards"]:
            kid = card["knowledge_id"]
            slot = by_card.setdefault(
                kid,
                {"knowledge_id": kid, "card_path": card["card_path"], "jumps": []},
            )
            targets = []
            for tid in row["answer_onenote_ids"]:
                tcat = catalog.get(tid) or {}
                targets.append(
                    {
                        "onenote_id": tid,
                        "snapshot_file": tcat.get("snapshot_file"),
                        "page_role": tcat.get("page_role"),
                    }
                )
            slot["jumps"].append(
                {
                    "cited_onenote_id": row["onenote_id"],
                    "cited_page_role": row["page_role"],
                    "cited_snapshot_file": row["snapshot_file"],
                    "answer_mode": row["answer_mode"],
                    "answer_pages": targets,
                    "child_content_pages": row["child_content_pages"],
                    "same_page_cards": [
                        c["knowledge_id"] for c in row["cards"] if c["knowledge_id"] != kid
                    ],
                }
            )

    card_rows = [by_card[k] for k in sorted(by_card)]
    OUT_CARDS.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in card_rows),
        encoding="utf-8",
    )

    linked = sum(1 for r in page_rows if r["cards"])
    print(
        json.dumps(
            {
                "pages": len(page_rows),
                "cards_with_onenote": len(card_rows),
                "pages_cited_by_cards": linked,
                "answer_modes": dict(modes),
                "hierarchy_pages_missing_catalog": sum(1 for r in page_rows if not r["snapshot_file"]),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
