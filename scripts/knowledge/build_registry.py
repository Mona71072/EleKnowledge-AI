#!/usr/bin/env python3
"""Build knowledge registry artifacts from drafts and cards."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "knowledge" / "drafts"
CARDS = ROOT / "knowledge" / "cards"
SNAP_ONENOTE = ROOT / "knowledge" / "source-snapshots" / "onenote"
REGISTRY = ROOT / "knowledge" / "registry"
REPAIR_MANIFEST = ROOT / "knowledge" / "queues" / "repair" / "MANIFEST.md"


def frontmatter_block(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def parse_scalar(fm: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*[\"']?(.*?)[\"']?\s*$", fm, re.M)
    return m.group(1).strip("\"'") if m else ""


def yaml_loadable(text: str) -> bool:
    try:
        import yaml

        block = frontmatter_block(text)
        if not block:
            return False
        yaml.safe_load(block)
        return True
    except Exception:
        return False


def list_ids_from_draft(text: str) -> set[str]:
    fm = frontmatter_block(text)
    ids: set[str] = set()
    lid = parse_scalar(fm, "list_item_id")
    if lid:
        ids.add(lid)
    evidence = fm
    if "evidence_sources:" in fm:
        start = fm.index("evidence_sources:")
        rest = fm[start:]
        end = len(rest)
        for m in re.finditer(r"^[a-z_]+:", rest, re.M):
            if m.start() > 0:
                end = m.start()
                break
        evidence = rest[:end]
    for m in re.finditer(r"[（(]ID(\d{1,5})[）)]", evidence):
        ids.add(m.group(1))
    for m in re.finditer(r"list_item_id:\s*[\"']?(\d{1,5})", evidence, re.I):
        ids.add(m.group(1))
    return ids


def main() -> None:
    REGISTRY.mkdir(parents=True, exist_ok=True)
    REPAIR_MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    list_rows: list[dict] = []
    onenote_map: dict[str, list[str]] = defaultdict(list)
    repair_files: list[str] = []

    for path in sorted(DRAFTS.glob("*.md")):
        if path.name.startswith("IMPORT"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not yaml_loadable(text):
            repair_files.append(path.name)
            continue
        fm = frontmatter_block(text)
        record_id = parse_scalar(fm, "record_id") or path.stem
        oid = parse_scalar(fm, "onenote_id").lower()
        if oid:
            onenote_map[oid].append(record_id)
        for lid in sorted(list_ids_from_draft(text)):
            list_rows.append(
                {
                    "list_item_id": lid,
                    "record_id": record_id,
                    "path": path.name,
                    "source": "draft_evidence",
                }
            )

    # Merge preserved working-tree registry if present (top-level list_item_id from refactor)
    preserved = REGISTRY / "list-item-to-record.jsonl"
    if preserved.exists():
        seen = {(r["list_item_id"], r["record_id"]) for r in list_rows}
        for line in preserved.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = (row["list_item_id"], row["record_id"])
            if key not in seen:
                row["source"] = row.get("source", "preserved_working_tree")
                list_rows.append(row)
                seen.add(key)

    list_rows.sort(key=lambda r: (int(r["list_item_id"]), r["record_id"]))
    with (REGISTRY / "list-item-to-record.jsonl").open("w", encoding="utf-8") as f:
        for row in list_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    snap_ids: set[str] = set()
    for path in SNAP_ONENOTE.glob("onenote-*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter_block(text)
        oid = parse_scalar(fm, "onenote_id").lower()
        if oid:
            snap_ids.add(oid)

    multi_onenote = {k: v for k, v in onenote_map.items() if len(v) > 1}
    missing_snap = sorted(set(onenote_map.keys()) - snap_ids)

    card_links: list[dict] = []
    for path in sorted(CARDS.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter_block(text)
        kid = parse_scalar(fm, "knowledge_id")
        if not kid:
            continue
        # naive source_refs parse for record_id / list_item_id lines
        for m in re.finditer(r"record_id:\s*(\S+)", fm):
            card_links.append({"knowledge_id": kid, "ref_type": "draft_record", "record_id": m.group(1)})
        for m in re.finditer(r"list_item_id:\s*[\"']?(\d+)", fm):
            card_links.append({"knowledge_id": kid, "ref_type": "lists_item", "list_item_id": m.group(1)})
        for m in re.finditer(r'onenote_id:\s*["\']?([^"\']+)', fm):
            card_links.append({"knowledge_id": kid, "ref_type": "onenote_page", "onenote_id": m.group(1).strip()})
        for m in re.finditer(r'document_number:\s*["\']?([^"\']+)', fm):
            card_links.append(
                {"knowledge_id": kid, "ref_type": "kb_document", "document_number": m.group(1).strip()}
            )
        for m in re.finditer(r'law_id:\s*["\']?([^"\']+)', fm):
            card_links.append(
                {"knowledge_id": kid, "ref_type": "law_rag", "law_id": m.group(1).strip()}
            )

    (REGISTRY / "card-source-links.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in card_links),
        encoding="utf-8",
    )

    list_to_card: list[dict] = []
    for path in sorted(CARDS.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter_block(text)
        kid = parse_scalar(fm, "knowledge_id")
        if not kid:
            continue
        rel = path.relative_to(CARDS).as_posix()
        for m in re.finditer(r'list_item_id:\s*["\']?(\d+)', fm):
            list_to_card.append(
                {"list_item_id": m.group(1), "knowledge_id": kid, "card_path": rel}
            )
    list_to_card.sort(key=lambda r: (int(r["list_item_id"]), r["knowledge_id"]))
    with (REGISTRY / "list-item-to-card.jsonl").open("w", encoding="utf-8") as f:
        for row in list_to_card:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    index = {
        "onenote_id_to_record_ids": dict(sorted(onenote_map.items())),
        "onenote_one_to_many": multi_onenote,
        "draft_onenote_not_in_snapshot_count": len(missing_snap),
        "draft_onenote_not_in_snapshot_sample": missing_snap[:15],
    }
    (REGISTRY / "onenote-id-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    repair_lines = [
        "# repair queue",
        "",
        "frontmatter が YAML として読めない draft。照合・カード生成から除外。",
        "",
    ]
    for name in sorted(repair_files):
        repair_lines.append(f"- `{name}`")
    if not repair_files:
        repair_lines.append("- （なし）")
    REPAIR_MANIFEST.write_text("\n".join(repair_lines) + "\n", encoding="utf-8")
    print(json.dumps({"list_links": len(list_rows), "repair": len(repair_files), "cards": len(card_links)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
