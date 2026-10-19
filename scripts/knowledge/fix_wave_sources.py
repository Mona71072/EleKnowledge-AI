#!/usr/bin/env python3
"""Normalize Wave1/2 drafts: list_item_id, titles without ID, rename files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "knowledge" / "drafts"

WAVE = [
    (
        "ELV_VFGLF_I-CAN未接続_乗場バックアップ不可_ID417事例.md",
        "ELV_VFGLF_I-CAN未接続_乗場バックアップ不可事例.md",
        "417",
        "VFGLFで乗場バックアップができない",
        "I-CAN未接続により乗場バックアップできない",
    ),
    (
        "ELV_AXIEZ-LINKS_照明安定化電源地絡_ID398事例.md",
        "ELV_AXIEZ-LINKS_照明安定化電源地絡事例.md",
        "398",
        "AXIEZ-LINKS かごの撓みで照明電源が地絡する",
        "カゴが撓むことで照明安定化電源が地絡する件",
    ),
    (
        "ELV_LINKs_WOS工法切替_DLDPコネクタ_ID345知見.md",
        "ELV_LINKs_WOS工法切替_DLDPコネクタ知見.md",
        "345",
        "GAWからWOSへの切替でDL・DPコネクタが無い",
        "LINKsでWOS工法に切り替える際にDL,DPコネクタが制御盤側に無い",
    ),
    (
        "ELV_VFGLF_ブレーキスイッチ本スロー不能_ID392事例.md",
        "ELV_VFGLF_ブレーキスイッチ本スロー不能事例.md",
        "392",
        "VFGLF 本スロー時ブレーキSW設定不良による運転不能",
        "ブレーキスイッチ設定不良で本スロー時カゴ運転不能の件",
    ),
    (
        "ELV_ピットタラップ取付位置_ID394事例.md",
        "ELV_ピットタラップ取付位置事例.md",
        "394",
        "ピットタラップ取付位置と800mm基準の整理",
        "ピットタラップの取付位置について",
    ),
    (
        "ELV_VFGH_長周期振動感知器短絡ジャンパ_ID416知見.md",
        "ELV_VFGH_長周期振動感知器短絡ジャンパ知見.md",
        "416",
        "長周期振動感知器の短絡ジャンパとBSER/BSER-CP",
        "長周期振動感知器の短絡ジャンパについて",
    ),
]


def patch_content(text: str, list_id: str, title: str, list_title: str) -> str:
    text = re.sub(r"^title: .*$", f'title: "{title}"', text, count=1, flags=re.M)
    if not re.search(r"^list_item_id:", text, re.M):
        text = re.sub(
            r"(^record_id:.*\n)",
            rf"\1list_item_id: \"{list_id}\"\n",
            text,
            count=1,
            flags=re.M,
        )
    else:
        text = re.sub(r'^list_item_id: .*$', f'list_item_id: "{list_id}"', text, flags=re.M)

    def clean_evidence_title(m: re.Match) -> str:
        line = m.group(0)
        line = re.sub(r"[（(]ID\d+[）)]", "", line)
        if "首都工" in line and list_title not in line:
            line = re.sub(
                r'(title: "首都工・不具合情報共有リスト: )([^"]*)(")',
                rf'\1{list_title}\3',
                line,
            )
        return line

    text = re.sub(r'^\s+title: "首都工[^"]*"', clean_evidence_title, text, flags=re.M)
    # H1
    text = re.sub(r"^# .+\n", f"# {title}\n", text, count=1, flags=re.M)
    text = re.sub(r"（ID\d+）|\(ID\d+\)", "", text)
    text = re.sub(r"Lists ID\d+", "共有リスト上の記録", text)
    text = re.sub(r"リスト ID\d+", "共有リスト上の記録", text)
    text = re.sub(r"ID\d+ は", "共有リスト上の記録は", text)
    return text


def main() -> None:
    for old_name, new_name, lid, title, list_title in WAVE:
        old = DRAFTS / old_name
        new = DRAFTS / new_name
        if not old.exists() and new.exists():
            path = new
        elif old.exists():
            path = old
        else:
            print("skip missing", old_name)
            continue
        text = path.read_text(encoding="utf-8")
        text = patch_content(text, lid, title, list_title)
        if path != new:
            new.write_text(text, encoding="utf-8")
            old.unlink()
        else:
            new.write_text(text, encoding="utf-8")
        print("ok", new_name, lid)


if __name__ == "__main__":
    main()
