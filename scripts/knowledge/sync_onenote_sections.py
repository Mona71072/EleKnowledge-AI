#!/usr/bin/env python3
"""Sync ### OneNote from frontmatter; optional extended ID/title hits."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
LISTS = ROOT / "knowledge" / "source-snapshots" / "首都工_不具合情報共有リスト_初期スナップショット.md"
ON = ROOT / "knowledge" / "source-snapshots" / "onenote"
EXTENDED_OUT = ROOT / "knowledge" / "registry" / "lists-onenote-extended-hits.jsonl"

ONENOTE_BLOCK = re.compile(
    r"(### OneNote\s*\n\s*\n)(.*?)(?=\n## )",
    re.S,
)


def parse_onenote_refs(fm: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for m in re.finditer(
        r"ref_type: onenote_page\s*\n\s*onenote_id:\s*\"([^\"]+)\""
        r"(?:\s*\n\s*note:\s*\"([^\"]*)\")?",
        fm,
    ):
        refs.append((m.group(1), m.group(2) or ""))
    return refs


def primary_list_id(fm: str) -> str | None:
    m = re.search(
        r"ref_type:\s*lists_item\s*\n\s*list_item_id:\s*[\"']?(\d+)",
        fm,
    )
    return m.group(1) if m else None


def list_titles() -> dict[str, str]:
    text = LISTS.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for m in re.finditer(r"^## Lists item ID (\d+): (.+)$", text, re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def load_pages() -> list[tuple[str, str, str]]:
    pages: list[tuple[str, str, str]] = []
    for path in ON.glob("onenote-*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        oid_m = re.search(r'^onenote_id:\s*"([^"]+)"', text, re.M)
        oid = oid_m.group(1) if oid_m else ""
        body = text.split("## OneNote content", 1)[-1] if "## OneNote content" in text else text
        pages.append((path.name, oid, body))
    return pages


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s.replace("（", "(").replace("）", ")"))


def discover_extended(
    need_lids: set[str], titles: dict[str, str], pages: list[tuple[str, str, str]]
) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for lid in need_lids:
        if lid in found:
            continue
        pats = [
            rf"\bID{lid}\b",
            rf"[（(]ID{lid}[）)]",
            rf"list_item_id[`'\":\s]+{lid}",
        ]
        for fname, oid, body in pages:
            if any(re.search(p, body, re.I) for p in pats):
                found[lid] = {
                    "list_item_id": lid,
                    "match": "list_id_in_body",
                    "file": fname,
                    "onenote_id": oid,
                }
                break
        if lid in found:
            continue
        title = titles.get(lid, "")
        if not title or title.startswith("（情報管理"):
            continue
        for n in (16, 12, 8):
            seg = norm(title)[:n]
            if len(seg) < 6:
                break
            for fname, oid, body in pages:
                if seg in norm(body):
                    found[lid] = {
                        "list_item_id": lid,
                        "match": f"title_prefix_{n}",
                        "file": fname,
                        "onenote_id": oid,
                    }
                    break
            if lid in found:
                break
    return found


def render_onenote_body(refs: list[tuple[str, str]], lid: str | None, *, no_hit: bool) -> str:
    lines: list[str] = []
    for oid, note in refs:
        if note:
            lines.append(f"- **onenote_id**: `{oid}` — {note}")
        else:
            lines.append(f"- **onenote_id**: `{oid}` — frontmatter 索引（本文未転載）。")
    if no_hit and not refs:
        lines.append(
            f"- スナップショット照合: Lists §{lid or '?'} の **タイトル一致・ID 索引未検出**"
            "（Lists のみ。OneNote 追探索は別途）。"
        )
    return "\n".join(lines) + "\n\n"


def add_ref_to_fm(fm: str, oid: str, note: str) -> str:
    if oid in fm:
        return fm
    block = (
        f"  - ref_type: onenote_page\n"
        f'    onenote_id: "{oid}"\n'
        f'    note: "{note}"\n'
    )
    return fm.rstrip() + "\n" + block


def main() -> None:
    import sys

    apply = "--apply" in sys.argv
    titles = list_titles()
    pages = load_pages()
    need: set[str] = set()
    paths_by_lid: dict[str, Path] = {}

    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = text[3:end]
        lid = primary_list_id(fm)
        if not lid:
            continue
        if not parse_onenote_refs(fm):
            need.add(lid)
            paths_by_lid[lid] = path

    extended = discover_extended(need, titles, pages)
    EXTENDED_OUT.parent.mkdir(parents=True, exist_ok=True)
    EXTENDED_OUT.write_text(
        "".join(json.dumps(v, ensure_ascii=False) + "\n" for v in extended.values()),
        encoding="utf-8",
    )

    stats = {"extended_added": 0, "synced": 0, "no_hit_text": 0}
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = text[3:end]
        body = text[end + 4 :]
        lid = primary_list_id(fm)

        if apply and lid and lid in extended and not parse_onenote_refs(fm):
            hit = extended[lid]
            note = (
                f"拡張索引 ({hit['match']}) — `{hit['file']}`（本文未転載）"
            )
            fm = add_ref_to_fm(fm, hit["onenote_id"], note)
            stats["extended_added"] += 1

        refs = parse_onenote_refs(fm)
        no_hit = bool(lid and lid in need and lid not in extended and not refs)
        if lid and lid in extended:
            no_hit = False

        m = ONENOTE_BLOCK.search(body)
        if not m and "### OneNote" not in body:
            if refs or no_hit:
                ins = re.search(r"(## ソース要約\s*\n.*?### Lists.*?\n(?:.*?\n)*?)(\n## )", body, re.S)
                if ins:
                    block = render_onenote_body(refs, lid, no_hit=no_hit)
                    body = (
                        body[: ins.start()]
                        + ins.group(1)
                        + "\n### OneNote\n\n"
                        + block
                        + ins.group(2)
                        + body[ins.end() :]
                    )
                    stats["synced"] += 1
            continue

        if m or "### OneNote" in body:
            new_inner = render_onenote_body(refs, lid, no_hit=no_hit)
            if m:
                body = ONENOTE_BLOCK.sub(r"\1" + new_inner, body, count=1)
            if no_hit:
                stats["no_hit_text"] += 1
            elif refs:
                stats["synced"] += 1

        if not apply:
            continue
        new_text = f"---\n{fm.rstrip()}\n---\n{body.lstrip(chr(10))}"
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")

    print(json.dumps({**stats, "apply": apply}, ensure_ascii=False))


if __name__ == "__main__":
    main()
