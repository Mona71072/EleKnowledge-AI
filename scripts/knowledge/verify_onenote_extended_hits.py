#!/usr/bin/env python3
"""Re-verify extended OneNote hits; drop prefix-only false positives."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTS = ROOT / "knowledge" / "source-snapshots" / "首都工_不具合情報共有リスト_初期スナップショット.md"
ON = ROOT / "knowledge" / "source-snapshots" / "onenote"
EXTENDED = ROOT / "knowledge" / "registry" / "lists-onenote-extended-hits.jsonl"
TITLE = ROOT / "knowledge" / "registry" / "lists-onenote-title-hits.jsonl"
VERIFIED = ROOT / "knowledge" / "registry" / "lists-onenote-extended-verified.jsonl"
REJECTED = ROOT / "knowledge" / "registry" / "lists-onenote-extended-rejected.jsonl"


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s.replace("（", "(").replace("）", ")"))


def list_titles() -> dict[str, str]:
    text = LISTS.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for m in re.finditer(r"^## Lists item ID (\d+): (.+)$", text, re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def title_hit_oids() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for line in TITLE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        lid = row["list_item_id"]
        out.setdefault(lid, set())
        for h in row.get("hits", []):
            out[lid].add(h["onenote_id"])
    return out


def body_for_file(fname: str) -> str:
    path = ON / fname
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text.split("## OneNote content", 1)[-1] if "## OneNote content" in text else text


def verify_row(row: dict, titles: dict[str, str], title_oids: dict[str, set[str]]) -> tuple[bool, str]:
    lid = row["list_item_id"]
    oid = row["onenote_id"]
    if oid in title_oids.get(lid, set()):
        return True, "title_hit_same_oid"
    title = titles.get(lid, "")
    if title.startswith("（情報管理"):
        return False, "info_mgmt_withheld"
    body = body_for_file(row["file"])
    if not body:
        return False, "missing_snapshot"
    pats = [
        rf"\bID{lid}\b",
        rf"[（(]ID{lid}[）)]",
        rf"Lists item ID {lid}",
        rf"§{lid}\b",
    ]
    if any(re.search(p, body, re.I) for p in pats):
        return True, "list_id_in_body"
    nt = norm(title)
    if len(nt) >= 10 and nt in norm(body):
        return True, "full_title_in_body"
    # ①/② 等の枝番違いは prefix 一致だけでは通さない
    if re.search(r"[①②③④⑤]$", title):
        base = norm(re.sub(r"[①②③④⑤]$", "", title.strip()))
        if base and base in norm(body) and norm(title) not in norm(body):
            return False, "list_suffix_mismatch"
    # stricter than discover: require 20+ char prefix OR 70% of title length
    need = max(20, int(len(nt) * 0.7))
    seg = nt[: min(len(nt), need)]
    if len(seg) >= 12 and seg in norm(body):
        return True, "long_prefix_in_body"
    return False, f"prefix_only_{row.get('match', '')}"


def main() -> None:
    titles = list_titles()
    title_oids = title_hit_oids()
    verified: list[dict] = []
    rejected: list[dict] = []
    for line in EXTENDED.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        ok, reason = verify_row(row, titles, title_oids)
        row["verify_status"] = "pass" if ok else "fail"
        row["verify_reason"] = reason
        if ok:
            verified.append(row)
        else:
            rejected.append(row)
    VERIFIED.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in verified),
        encoding="utf-8",
    )
    REJECTED.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rejected),
        encoding="utf-8",
    )
    EXTENDED.write_text(
        "".join(
            json.dumps({k: v for k, v in r.items() if k not in ("verify_status", "verify_reason")}, ensure_ascii=False)
            + "\n"
            for r in verified
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"verified": len(verified), "rejected": len(rejected), "extended_now": len(verified)},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
