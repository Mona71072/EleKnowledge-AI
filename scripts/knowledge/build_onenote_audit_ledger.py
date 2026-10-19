#!/usr/bin/env python3
"""Build card↔OneNote audit ledger and Wave 61–63 auto-link inventory."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
REGISTRY = ROOT / "knowledge" / "registry"
OUT = REGISTRY / "onenote-card-audit.jsonl"
WAVE_OUT = REGISTRY / "onenote-wave61-63-audit.jsonl"
SUMMARY = REGISTRY / "onenote-card-audit-summary.json"


def frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def body_after_fm(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text[end + 4 :] if end != -1 else ""


def parse_onenote_refs(fm: str) -> list[dict]:
    refs: list[dict] = []
    blocks = re.split(r"\n\s*-\s*ref_type:\s*onenote_page\s*\n", fm)
    for block in blocks[1:]:
        oid_m = re.search(r'onenote_id:\s*"([^"]+)"', block)
        if not oid_m:
            continue
        role_m = re.search(r"page_role:\s*(\w+)", block)
        note_m = re.search(r'note:\s*"((?:[^"\\]|\\.)*)"', block)
        refs.append(
            {
                "onenote_id": oid_m.group(1),
                "page_role": role_m.group(1) if role_m else "",
                "note": note_m.group(1) if note_m else "",
            }
        )
    return refs


def parse_body_onenote_ids(body: str) -> list[str]:
    ids: set[str] = set()
    for m in re.finditer(
        r"[`\"]?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:\d+)[`\"]?",
        body,
        re.I,
    ):
        ids.add(m.group(1))
    return sorted(ids)


def infer_source(note: str, body_snip: str = "") -> str:
    blob = note + body_snip
    if "Lists タイトル一致" in blob or "タイトル一致" in blob:
        return "title_hit"
    if "拡張索引" in blob or "title_prefix" in blob or "list_id_in_body" in blob:
        return "extended_hit"
    if "draft 索引" in blob:
        return "draft_hit"
    if note:
        return "manual_or_other"
    if "索引" in body_snip or "navigation" in body_snip:
        return "title_hit_or_index"
    return "unknown"


def load_page_catalog() -> dict[str, dict]:
    path = REGISTRY / "onenote-page-catalog.jsonl"
    if not path.is_file():
        return {}
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["onenote_id"]] = row
    return out


def load_list_to_card() -> dict[str, dict]:
    path = REGISTRY / "list-item-to-card.jsonl"
    out: dict[str, dict] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            lid = row["list_item_id"]
            if lid not in out:
                out[lid] = row
    return out


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def card_on_card_refs() -> dict[tuple[str, str], dict]:
    """(knowledge_id, onenote_id) -> row fragment from cards."""
    attached: dict[tuple[str, str], dict] = {}
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text)
        body = body_after_fm(text)
        kid_m = re.search(r"^knowledge_id:\s*(\S+)", fm, re.M)
        kid = kid_m.group(1) if kid_m else ""
        lid = primary_list_id(fm)
        fm_ids = {r["onenote_id"] for r in parse_onenote_refs(fm)}
        on_section = ""
        m = re.search(r"### OneNote[^\n]*\n(.*?)(?=\n## |\Z)", body, re.S)
        if m:
            on_section = m.group(1)[:500]
        for ref in parse_onenote_refs(fm):
            attached[(kid, ref["onenote_id"])] = {
                "on_card": True,
                "in_frontmatter": True,
                "card_path": path.relative_to(ROOT).as_posix(),
                "list_item_id": lid,
                "note": ref["note"],
                "page_role_fm": ref["page_role"],
                "body_snip": on_section,
            }
        for oid in parse_body_onenote_ids(body):
            if oid in fm_ids:
                continue
            key = (kid, oid)
            if key not in attached:
                attached[key] = {
                    "on_card": True,
                    "in_frontmatter": False,
                    "card_path": path.relative_to(ROOT).as_posix(),
                    "list_item_id": lid,
                    "note": "",
                    "page_role_fm": "",
                    "body_snip": on_section,
                }
    return attached


def primary_list_id(fm: str) -> str:
    m = re.search(
        r"ref_type:\s*lists_item\s*\n\s*list_item_id:\s*[\"']?(\d+)",
        fm,
    )
    return m.group(1) if m else ""


def _recommend(role: str, src: str, cat: dict) -> str:
    role = role or cat.get("page_role", "")
    if role in ("index", "hybrid") and src in ("title_hit", "extended_hit", "title_hit_or_index"):
        return "navigation_only"
    if role == "empty_or_attachment_only":
        return "remove_ref"
    if src == "extended_hit":
        return "manual_verify_prefix"
    if role == "content" or cat.get("page_role") == "content":
        return "curate_summary"
    if role == "cross_topic":
        return "cross_link_or_theme_card"
    return "review"


def build_wave_rows(
    attached: dict[tuple[str, str], dict],
    catalog: dict[str, dict],
    l2c: dict[str, dict],
) -> list[dict]:
    wave: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    def add(
        *,
        list_item_id: str,
        onenote_id: str,
        attach_source: str,
        wave_id: str,
        extra: dict | None = None,
    ) -> None:
        key = (list_item_id, onenote_id, attach_source)
        if key in seen:
            return
        seen.add(key)
        card = l2c.get(list_item_id, {})
        kid = card.get("knowledge_id", "")
        att = attached.get((kid, onenote_id), {})
        cat = catalog.get(onenote_id, {})
        role = att.get("page_role_fm") or cat.get("page_role", "")
        src = attach_source
        row = {
            "wave": wave_id,
            "list_item_id": list_item_id,
            "knowledge_id": kid,
            "card_path": att.get("card_path") or card.get("card_path", ""),
            "onenote_id": onenote_id,
            "attach_source": src,
            "on_card": bool(att.get("on_card")),
            "in_frontmatter": bool(att.get("in_frontmatter")),
            "page_role": role,
            "catalog_file": cat.get("snapshot_file", ""),
            "recommended_action": _recommend(role, src, cat),
            **(extra or {}),
        }
        wave.append(row)

    for row in load_jsonl(REGISTRY / "lists-onenote-title-hits.jsonl"):
        lid = row["list_item_id"]
        for h in row.get("hits", [])[:1]:
            add(
                list_item_id=lid,
                onenote_id=h["onenote_id"],
                attach_source="title_hit",
                wave_id="61",
                extra={"snapshot_file": h.get("file", "")},
            )

    for row in load_jsonl(REGISTRY / "lists-onenote-extended-hits.jsonl"):
        add(
            list_item_id=row["list_item_id"],
            onenote_id=row["onenote_id"],
            attach_source="extended_hit",
            wave_id="62",
            extra={"match": row.get("match", ""), "snapshot_file": row.get("file", "")},
        )

    for row in load_jsonl(REGISTRY / "lists-onenote-draft-hits.jsonl"):
        add(
            list_item_id=row.get("list_item_id", ""),
            onenote_id=row["onenote_id"],
            attach_source="draft_hit",
            wave_id="63",
            extra={"draft": row.get("draft", ""), "record_id": row.get("record_id", "")},
        )

    for row in load_jsonl(REGISTRY / "onenote-attach-candidates-title.jsonl"):
        add(
            list_item_id=row.get("list_item_id", ""),
            onenote_id=row["onenote_id"],
            attach_source="title_hit",
            wave_id="61_candidate",
            extra={"snapshot_file": row.get("snapshot_file", ""), "pending_apply": True},
        )

    return wave


def main() -> None:
    catalog = load_page_catalog()
    l2c = load_list_to_card()
    attached_map = card_on_card_refs()
    rows: list[dict] = []
    by_source: dict[str, int] = {}
    by_role: dict[str, int] = {}

    for (kid, oid), att in sorted(attached_map.items()):
        cat = catalog.get(oid, {})
        role = att.get("page_role_fm") or cat.get("page_role", "")
        src = infer_source(att.get("note", ""), att.get("body_snip", ""))
        row = {
            "knowledge_id": kid,
            "card_path": att["card_path"],
            "list_item_id": att.get("list_item_id", ""),
            "onenote_id": oid,
            "attach_source": src,
            "on_card": True,
            "in_frontmatter": att.get("in_frontmatter", False),
            "page_role": role,
            "note": att.get("note", ""),
            "catalog_file": cat.get("snapshot_file", ""),
            "recommended_action": _recommend(role, src, cat),
        }
        rows.append(row)
        by_source[src] = by_source.get(src, 0) + 1
        by_role[role or "unset"] = by_role.get(role or "unset", 0) + 1

    wave_rows = build_wave_rows(attached_map, catalog, l2c)

    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    WAVE_OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in wave_rows),
        encoding="utf-8",
    )

    wave_on_card = sum(1 for r in wave_rows if r.get("on_card"))
    SUMMARY.write_text(
        json.dumps(
            {
                "card_onenote_refs": len(rows),
                "unique_onenote_ids": len({r["onenote_id"] for r in rows}),
                "by_attach_source": by_source,
                "by_page_role": by_role,
                "wave61_63_links": len(wave_rows),
                "wave_on_card": wave_on_card,
                "wave_pending_candidate": sum(
                    1 for r in wave_rows if not r.get("on_card")
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "card_refs": len(rows),
                "wave_rows": len(wave_rows),
                "out": str(OUT.relative_to(ROOT)),
                "wave_out": str(WAVE_OUT.relative_to(ROOT)),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
