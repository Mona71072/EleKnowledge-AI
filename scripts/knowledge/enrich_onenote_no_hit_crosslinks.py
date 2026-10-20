#!/usr/bin/env python3
"""Add theme cluster cross-links to ### OneNote for Lists-without-OneNote cards."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "knowledge" / "cards"

NO_HIT = re.compile(
    r"(### OneNote\s*\n\s*\n)(- スナップショット照合:.*?索引未検出.*?\n|- タイトル一致索引なし.*?\n)",
    re.S,
)

CLUSTERS: list[tuple[re.Pattern[str], list[str]]] = [
    (
        re.compile(r"エレコール|SCU-20|SCU20|elecall", re.I),
        [
            "[SCU 接続試験](../practice-guides/KH-SCU20-CONN-TEST-228.md)",
            "[SCU 書換](../practice-guides/KH-SCU20-FLASH-REWRITE-233.md)",
            "[GS3 通信](../case-summaries/KH-VFGLF-SCU20-GS3-149.md)",
        ],
    ),
    (
        re.compile(r"エレナビ|ELSGW|DOAS|MELSAFETY|フラッパ", re.I),
        [
            "[エレナビ索引](../practice-guides/KH-ELENAVI-ISSUES-INDEX-336.md)",
            "[ELSGW PuTTY/IP](../practice-guides/KH-ELENAVI-ELSGW-PUTTY-NET-415.md)",
            "[工事 DOAS](../case-summaries/KH-VFGH-DOAS-CONSTRUCTION-373.md)",
        ],
    ),
    (
        re.compile(r"群管理|2C-2BC|3car|GS3|バンク", re.I),
        [
            "[3台 2C-2BC](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md)",
            "[群管理盤給電](../case-summaries/KH-MR-GROUP-PANEL-POWER-371.md)",
            "[配線セーブ索引](../practice-guides/KH-VFGLF-GROUP-WIRING-SAVE-MODE-253.md)",
        ],
    ),
    (
        re.compile(r"気配り|RX1|KEIAI|2C-2BC", re.I),
        [
            "[DOB 403](../case-summaries/KH-VFGLF-DOR-DOB-403.md)",
            "[HMS 408](../case-summaries/KH-VFGH-KEIAIN-HMS-DOOR-408.md)",
            "[RX1 424](../case-summaries/KH-ALL-KEIAI-RX1-PINCH-424.md)",
        ],
    ),
    (
        re.compile(r"SVFC|エスカ|escalator|product_lines:\s*\n\s*- \"escalator\"", re.I),
        [
            "[u形索引](../practice-guides/KH-ESC-U-MODEL-CATALOG.md)",
            "[チェーン隙間](../case-summaries/KH-ESC-SVFC-STEP-CHAIN-GAP-326.md)",
            "[Bセンサ 301](../case-summaries/KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301.md)",
        ],
    ),
    (
        re.compile(r"遮煙|大臣認定|火災管制|MELD.*戸閉", re.I),
        [
            "[遮煙 MELD 227](../practice-guides/KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md)",
            "[シール 346](../practice-guides/KH-ALL-SMOKE-DOOR-SEAL-346.md)",
            "[煙感知 154](../practice-guides/KH-MRL-SMOKE-SHAFT-SENSOR-154.md)",
        ],
    ),
    (
        re.compile(r"LV5K|LV6K|CLT|ドア型|door_types", re.I),
        [
            "[CLT 432](../practice-guides/KH-LV5K-LV6K-CLT-432.md)",
            "[戸異音 433](../case-summaries/KH-LV5K-2S-DOOR-NOISE-433.md)",
            "[DOB 403](../case-summaries/KH-VFGLF-DOR-DOB-403.md)",
        ],
    ),
    (
        re.compile(r"LINKs|AXIEZ-LINK", re.I),
        [
            "[WOS DL/DP](../practice-guides/KH-LINKS-WOS-DLDP-345.md)",
            "[戸駆動 434](../case-summaries/KH-AXIEZ-LINKS-DOOR-DRIVE-31-434.md)",
            "[PSL 55](../case-summaries/KH-LINKS-PSL-PIN-55.md)",
        ],
    ),
    (
        re.compile(r"Putty|PuTTY", re.I),
        [
            "[インストール 130](../practice-guides/KH-ELECALL-PUTTY-INSTALL-130.md)",
            "[管理者 119](../practice-guides/KH-ELECALL-PUTTY-LOG-ADMIN-119.md)",
        ],
    ),
    (
        re.compile(r"ER運転|DL-A|DOT-A|深ピット", re.I),
        [
            "[ER 動作点 379](../case-summaries/KH-VFGH-ER-OPERATION-DL-A-379.md)",
            "[追加 DL/DOT 348](../practice-guides/KH-MR-ER-EXTRA-DL-DOT-348.md)",
        ],
    ),
]


def cluster_links(blob: str, card_path: Path) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    self_name = card_path.stem
    for pat, cluster in CLUSTERS:
        if pat.search(blob):
            for ln in cluster:
                if self_name in ln:
                    continue
                if ln not in seen:
                    seen.add(ln)
                    links.append(ln)
    return links[:4]


def rel_prefix(card_path: Path) -> str:
    if "case-summaries" in card_path.as_posix():
        return "../practice-guides/"
    return "./"


def fix_cluster_paths(links: list[str], card_path: Path) -> list[str]:
    """Adjust relative paths when target is in same directory."""
    same_dir = "case-summaries" in card_path.as_posix()
    out: list[str] = []
    for ln in links:
        if same_dir and "../case-summaries/" in ln:
            ln = ln.replace("../case-summaries/", "./")
        elif (not same_dir) and ln.startswith("[") and "/case-summaries/" in ln and not ln.startswith("../"):
            pass
        out.append(ln)
    return out


def main() -> None:
    import sys

    apply = "--apply" in sys.argv
    updated = 0
    for path in sorted(CARDS.rglob("*.md")):
        if path.name in ("INDEX.md", "TEMPLATE.md", "_SOURCE-LEGEND.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if "ref_type: onenote_page" in text:
            continue
        m = NO_HIT.search(text)
        if not m:
            continue
        blob = text
        links = fix_cluster_paths(cluster_links(blob, path), path)
        if not links:
            links = [
                "[Lists 索引](../cards/INDEX.md) — OneNote タイトル未一致（全件 grep 2026-10-19）"
            ]
            if "practice-guides" in path.as_posix():
                links[0] = links[0].replace("../cards/", "../")
        block = (
            "- Lists — **OneNote スナップショットにタイトル一致なし**（`scan_onenote_title_residuals.py` 0 件）。\n"
            "- **関連クラスタ（カード相互リンク）**: "
            + " / ".join(links)
            + "\n"
        )
        new_text = NO_HIT.sub(r"\1" + block, text, count=1)
        if new_text != text and apply:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
    print({"updated": updated, "apply": apply})


if __name__ == "__main__":
    main()
