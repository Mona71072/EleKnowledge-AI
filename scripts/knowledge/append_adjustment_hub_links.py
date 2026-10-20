#!/usr/bin/env python3
"""Append adjustment hub row to ## 関連事例 tables (Wave 68, idempotent)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
L2C = ROOT / "knowledge" / "registry" / "list-item-to-card.jsonl"

HUB_REL_CASE = "../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md"
HUB_REL_PRACTICE = "./KH-ALL-INSTALL-TEST-ADJUST-HUB.md"
HUB_SNIPPET = "KH-ALL-INSTALL-TEST-ADJUST-HUB"

CASE_LIDS = [
    "433",
    "392",
    "63",
    "81",
    "430",
    "176",
    "87",
    "139",
    "388",
    "184",
    "383",
    "55",
    "342",
    "414",
    "381",
    "107",
    "171",
]

PRACTICE_KIDS = [
    "KH-LV5K-LV6K-CLT-432",
    "KH-VFGH-SHORT-LANDING-LIMIT-428",
    "KH-VFGLF-INSTALL-FLAG-361",
    "KH-AXIEZ-INSTALL-FLAG-85",
    "KH-PIT-TRAP-POSITION-394",
    "KH-LINKS-HOIST-WALL-GAP-29",
    "KH-ALL-TECHSPEC-BRAKE-TORQUE-133",
    "KH-VFEL-DZ-PLATE-SHORT-RUN-182",
    "KH-VFGLB-DOOR-SHORT-RELEASE-419",
    "KH-CM-LB-DOOR-SHORT-LATCH",
    "KH-VFGLF-DOOR-SHORT-CHECK-160",
]


def card_path_for_lid(lid: str) -> Path | None:
    for line in L2C.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["list_item_id"] == lid:
            return ROOT / "knowledge" / "cards" / row["card_path"]
    return None


def card_path_for_kid(kid: str) -> Path | None:
    for sub in ("case-summaries", "practice-guides"):
        for p in (CARDS / sub).glob("*.md"):
            if p.stem == kid:
                return p
    return None


def append_hub_row(text: str, hub_link: str) -> str:
    if HUB_SNIPPET in text:
        return text
    row = f"| [据付・試験・調整ハブ]({hub_link}) | 設定・寸法・本スロー **横断入口** |\n"
    m = re.search(r"(## 関連事例と条件の違い\n\n(?:\|.+\n)+)", text)
    if not m:
        m = re.search(r"(## 関連事例\n\n(?:\|.+\n)+)", text)
    if not m:
        return text
    block = m.group(1)
    if "調整・試験（入口）" in block:
        return text
    new_block = block.rstrip() + "\n" + row
    return text.replace(block, new_block, 1)


def main() -> None:
    import sys

    apply = "--apply" in sys.argv
    touched: list[str] = []
    for lid in CASE_LIDS:
        path = card_path_for_lid(lid)
        if not path or not path.is_file():
            print("missing lid", lid)
            continue
        new = append_hub_row(path.read_text(encoding="utf-8"), HUB_REL_CASE)
        if new != path.read_text(encoding="utf-8"):
            touched.append(str(path.relative_to(ROOT)))
            if apply:
                path.write_text(new, encoding="utf-8")
    for kid in PRACTICE_KIDS:
        path = card_path_for_kid(kid)
        if not path:
            print("missing kid", kid)
            continue
        old = path.read_text(encoding="utf-8")
        new = append_hub_row(old, HUB_REL_PRACTICE)
        if new != old:
            touched.append(str(path.relative_to(ROOT)))
            if apply:
                path.write_text(new, encoding="utf-8")
    print({"touched": len(touched), "apply": apply, "files": touched[:20]})


if __name__ == "__main__":
    main()
