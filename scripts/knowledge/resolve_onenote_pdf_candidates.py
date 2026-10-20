#!/usr/bin/env python3
"""Resolve onenote-pdf-kb-candidates.jsonl against kb-document-index (filename only, pending)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_kb_refs import load_index, resolve_one  # noqa: E402

CAND = ROOT / "knowledge" / "registry" / "onenote-pdf-kb-candidates.jsonl"
OUT = ROOT / "knowledge" / "registry" / "onenote-pdf-kb-candidates-resolved.jsonl"
REPORT = ROOT / "knowledge" / "validation" / "onenote-pdf-kb-candidate-status.md"


def main() -> None:
    if not CAND.is_file():
        raise SystemExit("Run build_onenote_pdf_kb_candidates.py first")
    entries = load_index()
    rows: list[dict] = []
    for line in CAND.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        hint = rec["document_number_hint"]
        res = resolve_one(hint, entries)
        rows.append({**rec, **{k: v for k, v in res.items() if k != "document_number"}})
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    matched = sum(1 for r in rows if r.get("kb_verify_status") == "catalog_matched")
    amb = sum(1 for r in rows if r.get("kb_verify_status") == "catalog_ambiguous")
    absent = sum(1 for r in rows if r.get("kb_verify_status") == "not_in_catalog")
    lines = [
        "# OneNote outgoing → KB カタログ突合（候補台帳）",
        "",
        "> **断定・手順追記禁止** — filename 突合のみ。正: `onenote-pdf-kb-candidates.jsonl`",
        f"> 出力: `registry/onenote-pdf-kb-candidates-resolved.jsonl` — matched **{matched}** / ambiguous **{amb}** / absent **{absent}** / total **{len(rows)}**",
        "",
        "| onenote_id | hint | status | kb_filename |",
        "| --- | --- | --- | --- |",
    ]
    for r in rows[:80]:
        fn = r.get("kb_filename") or ("; ".join(r.get("candidates", [])[:3]) if r.get("candidates") else "—")
        lines.append(
            f"| `{r['onenote_id'][-12:]}` | {r['document_number_hint']} | {r.get('kb_verify_status')} | {fn} |"
        )
    if len(rows) > 80:
        lines.append(f"| … | … | … | （他 {len(rows) - 80} 行は jsonl 参照） |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"total": len(rows), "matched": matched, "ambiguous": amb, "absent": absent}, ensure_ascii=False))


if __name__ == "__main__":
    main()
