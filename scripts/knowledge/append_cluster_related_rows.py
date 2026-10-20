#!/usr/bin/env python3
"""Append missing cluster hub rows to ## 関連 sections (idempotent)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"
L2C = ROOT / "knowledge" / "registry" / "list-item-to-card.jsonl"

PATCHES: dict[str, list[tuple[str, str]]] = {
    "92": [
        (
            "228",
            "| 群管理・SCU | [338 背後呼び](../practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) / [228 SCU索引](../practice-guides/KH-SCU20-CONN-TEST-228.md) / [286 試験発報](../practice-guides/KH-ALL-GROUP-ALARM-TRIGGER-286.md) |",
        ),
        (
            "384",
            "| [384 3car 群管理](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) / [371 給電](./KH-MR-GROUP-PANEL-POWER-371.md) | **群管理** 横断 |",
        ),
    ],
    "269": [
        (
            "338",
            "| 群管理・呼び | [338 背後呼び](../practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) / [99 行先階](./KH-VFGLF-CAR-IND-DEST-FLOOR-99.md) / [371 群管理給電](./KH-MR-GROUP-PANEL-POWER-371.md) |",
        ),
        (
            "384",
            "| [384 3car](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) / [92 パニック](../case-summaries/KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | 群管理連動 |",
        ),
    ],
    "384": [
        ("422", "| [422](./KH-GS3-PART-NO-SCU20-422.md) | GS3 **LM2B** / SCU 通信 |"),
        ("171", "| [171](./KH-GROUP-ECAN-MAG-171.md) | 群管理 **E-CAN** |"),
        (
            "371",
            "| [371 群管理給電](./KH-MR-GROUP-PANEL-POWER-371.md) | 盤 **電源** |",
        ),
    ],
    "422": [
        ("384", "| [384](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 3car **2C-2BC** |"),
        ("371", "| [371](./KH-MR-GROUP-PANEL-POWER-371.md) | 群管理盤 **給電** |"),
        ("228", "| [228](../practice-guides/KH-SCU20-CONN-TEST-228.md) | SCU **索引** |"),
        (
            "233",
            "| [233](../practice-guides/KH-SCU20-FLASH-REWRITE-233.md) | SCU-20 **書換** |",
        ),
        (
            "149",
            "| [149](./KH-VFGLF-SCU20-GS3-149.md) | GS3 **B/5** 設定 |",
        ),
        (
            "hub",
            "| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |",
        ),
    ],
    "354": [
        ("403", "| [403](./KH-VFGLF-DOR-DOB-403.md) | ドア SW **D14/釦CPU** 系 |"),
    ],
    "361": [
        ("394", "| [394](../practice-guides/KH-PIT-TRAP-POSITION-394.md) | 据付 **ピット** 横断 |"),
    ],
    "403": [
        (
            "419",
            "| [419 戸短](../practice-guides/KH-VFGLB-DOOR-SHORT-RELEASE-419.md) / [CM-LB 戸短](../practice-guides/KH-CM-LB-DOOR-SHORT-LATCH.md) | 官検・試験 **戸短** |",
        ),
        (
            "432",
            "| [432 CLT](../practice-guides/KH-LV5K-LV6K-CLT-432.md) | **LV** 戸調整 |",
        ),
    ],
    "160": [
        (
            "419",
            "| [419 VFGLB 戸短解除](../practice-guides/KH-VFGLB-DOOR-SHORT-RELEASE-419.md) | 解除手順 |",
        ),
    ],
    "105": [
        (
            "403",
            "| [403 D14/DOB](../case-summaries/KH-VFGLF-DOR-DOB-403.md) | 釦 **DOB** 系 |",
        ),
        (
            "419",
            "| [419 戸短](../practice-guides/KH-VFGLB-DOOR-SHORT-RELEASE-419.md) | ポータブル **戸短** |",
        ),
    ],
    "371": [
        (
            "422",
            "| [422 GS3/SCU](./KH-GS3-PART-NO-SCU20-422.md) / [171 E-CAN](./KH-GROUP-ECAN-MAG-171.md) | 群管理盤 **通信** |",
        ),
        (
            "338",
            "| [338 背後呼び](../practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) / [92 パニック](./KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | **呼び** 系 |",
        ),
    ],
    "338": [
        (
            "371",
            "| [371 給電](../case-summaries/KH-MR-GROUP-PANEL-POWER-371.md) / [92 パニック](../case-summaries/KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) / [269 CR](../case-summaries/KH-ALL-CR-SECURITY-FLOOR-DISPLAY-269.md) | 群管理・呼び |",
        ),
        (
            "422",
            "| [422 GS3](../case-summaries/KH-GS3-PART-NO-SCU20-422.md) / [384 3car](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | SCU / 多 car |",
        ),
    ],
    "228": [
        (
            "422",
            "| [422 GS3](../case-summaries/KH-GS3-PART-NO-SCU20-422.md) / [384](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) / [338 背後呼び](./KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) | 群管理 **索引** |",
        ),
    ],
    "149": [
        ("384", "| [384 3car](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 群管理 **運転モード** |"),
    ],
    "167": [
        ("174", "| [174](./KH-VFGLB-MELD-BATTERY-174.md) / [101](./KH-IPU-MELD-BATTERY-POLARITY-101.md) | MELD **電源** |"),
    ],
    "132": [
        ("174", "| [174](./KH-VFGLB-MELD-BATTERY-174.md) | バッテリー **低電圧** |"),
    ],
    "113": [
        ("411", "| [411](./KH-VFGLF-HOIST-RESOLVER-WIRE-411.md) | **レゾルバ線** 断線 |"),
        ("392", "| [392](./KH-VFGLF-BRAKE-SW-392.md) | 本スロー **`:156`** 索引 |"),
    ],
    "382": [
        ("383", "| [383](./KH-ALL-WELDER-LOW-VOLT-DN-383.md) | 仮設 **電圧**（U-CAN 似た症状） |"),
        ("414", "| [414](./KH-VFGLF-LINE-LED-GROUND-414.md) | **421** ライン LED |"),
    ],
    "233": [
        (
            "hub",
            "| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |",
        ),
    ],
}


def card_path_for_lid(lid: str) -> Path | None:
    for line in L2C.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["list_item_id"] == lid:
            p = CARDS / row["card_path"].replace("case-summaries/", "").replace("practice-guides/", "")
            # card_path is relative to cards/
            p = ROOT / "knowledge" / "cards" / row["card_path"]
            return p if p.is_file() else None
    return None


def main() -> None:
    import sys

    apply = "--apply" in sys.argv
    updated = 0
    for lid, rows in PATCHES.items():
        path = card_path_for_lid(lid)
        if not path:
            print("missing", lid)
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for marker, row_line in rows:
            if marker in text and row_line.split("|")[1].strip()[:8] in text:
                continue
            if marker in text and f"| {marker}" in text:
                continue
            m = re.search(
                r"(## 関連[^\n]*\n\n(?:\|.+\n)+)",
                text,
            )
            if not m:
                continue
            block = m.group(1)
            if row_line in block:
                continue
            new_block = block.rstrip() + "\n" + row_line + "\n"
            text = text.replace(block, new_block, 1)
        if text != orig and apply:
            path.write_text(text, encoding="utf-8")
            updated += 1
    print({"updated": updated, "apply": apply})


if __name__ == "__main__":
    main()
