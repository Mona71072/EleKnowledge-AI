#!/usr/bin/env python3
"""Apply audited OneNote links: navigation-only and verified title hits."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
WAVE = ROOT / "knowledge" / "registry" / "onenote-wave61-63-audit.jsonl"
CATALOG = ROOT / "knowledge" / "registry" / "onenote-page-catalog.jsonl"

NONE_ON = re.compile(
    r"(### OneNote\s*\n\s*\n)(- スナップショット照合:.*?|- タイトル一致索引なし.*?)\s*\n",
    re.S,
)
NO_HIT = re.compile(
    r"- スナップショット照合: Lists §\d+ の \*\*タイトル一致・ID 索引未検出\*\*[^\n]*\n",
)


def load_catalog() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["onenote_id"]] = row
    return out


def card_path(row: dict) -> Path | None:
    cp = row.get("card_path", "")
    if not cp:
        return None
    if cp.startswith("knowledge/"):
        return ROOT / cp
    return CARDS.parent / cp if (CARDS.parent / cp).is_file() else CARDS / cp.replace("knowledge/cards/", "")


def has_oid(fm: str, oid: str) -> bool:
    return f'onenote_id: "{oid}"' in fm


def primary_list_id(fm: str) -> str | None:
    m = re.search(
        r"ref_type:\s*lists_item\s*\n\s*list_item_id:\s*[\"']?(\d+)",
        fm,
    )
    return m.group(1) if m else None


def nav_body(oid: str, snap: str, role: str) -> str:
    label = "索引頁" if role in ("index", "cross_topic", "hybrid") else "OneNote"
    return (
        f"- **{label}** `{oid}`（`{snap}`）— **navigation のみ**。"
        " 他テーマタイトルはカード本文に載せない。詳細はスナップショット参照。\n\n"
    )


def apply_row(path: Path, row: dict, cat: dict[str, dict]) -> bool:
    oid = row["onenote_id"]
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    fm = text[3:end]
    body = text[end + 4 :]
    if has_oid(fm, oid):
        return False
    snap = row.get("snapshot_file") or row.get("catalog_file") or cat.get(oid, {}).get("snapshot_file", "")
    role = row.get("page_role") or cat.get(oid, {}).get("page_role", "index")
    note = (
        f"監査適用 ({row.get('attach_source', 'wave')}) — `{snap}`（navigation）"
    )
    fm = fm.rstrip() + (
        f"\n  - ref_type: onenote_page\n"
        f'    onenote_id: "{oid}"\n'
        f"    page_role: {role if role != 'cross_cutting' else 'cross_topic'}\n"
        f'    note: "{note}"\n'
    )
    inner = nav_body(oid, snap, role)
    if "### OneNote" in body:
        body = NO_HIT.sub("", body)
        body = NONE_ON.sub(r"\1" + inner, body, count=1)
        if inner.strip() not in body and re.search(r"### OneNote\s*\n\s*\n", body):
            body = re.sub(
                r"(### OneNote\s*\n\s*\n)",
                r"\1" + inner,
                body,
                count=1,
            )
    else:
        ins = re.search(r"(## ソース要約\s*\n.*?### Lists.*?\n(?:.*?\n)*?)(\n## )", body, re.S)
        if ins:
            body = (
                body[: ins.start()]
                + ins.group(1)
                + "\n### OneNote\n\n"
                + inner
                + ins.group(2)
                + body[ins.end() :]
            )
    path.write_text(f"---\n{fm.rstrip()}\n---\n{body.lstrip(chr(10))}", encoding="utf-8")
    return True


def main() -> None:
    import sys

    apply = "--apply" in sys.argv
    cat = load_catalog()
    actions = sys.argv[1:] if len(sys.argv) > 1 else []
    allow = {"navigation_only", "cross_link_or_theme_card"}
    if "--navigation-only" in actions:
        allow = {"navigation_only"}
    rows = [json.loads(l) for l in WAVE.read_text(encoding="utf-8").splitlines() if l.strip()]
    todo = [
        r
        for r in rows
        if not r.get("on_card")
        and r.get("recommended_action") in allow
        and r.get("page_role") in ("index", "cross_topic", "hybrid", "cross_cutting", "")
    ]
    # cross_topic index pages: still navigation only on list cards
    updated = 0
    skipped = 0
    for row in todo:
        path = card_path(row)
        if not path or not path.is_file():
            skipped += 1
            continue
        role = row.get("page_role") or cat.get(row["onenote_id"], {}).get("page_role", "")
        if role == "content":
            skipped += 1
            continue
        if not apply:
            continue
        if apply_row(path, row, cat):
            updated += 1
    print(
        json.dumps(
            {"eligible": len(todo), "updated": updated, "skipped": skipped, "apply": apply},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
