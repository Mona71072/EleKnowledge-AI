---
knowledge_id: KH-VFGLF-KEIAIN-HARNESS-PINCH-382
kind: case_summary
status: draft
card_version: 1
title: "VFGLF — 気配り配線挟み込みで +12V 切・U-CAN 不能"
symptoms:
  - "気配り"
  - "TX1"
  - "E34"
  - "421"
  - "U-CAN"
model_scope:
  lists_model_label: ["VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "382"
---

# VFGLF — 気配り配線挟み込みで +12V 切・U-CAN 不能

## 使う場面・対象条件

**本スロー後** **カゴ上/内運転不可**、**ETP は可**（Lists 382）。

## 症状・現象

- E34–E46、DC **421**（Lists）。

## ソース要約

### Lists（382）

- **+12 V 欠** → 基板が **安全カット** & **CAN 拒否**。
- **TX1 抜き** で復帰手がかり — **操作盤パネル縫い** **挟み込み地絡**。
- **Notes**: 直流電源 **過電流保護** — 遮断 **30 s 以上** 後再投入（Lists progress）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[249 DC 保護リセット](../practice-guides/KH-ALL-DC-SUPPLY-PROTECT-RESET-249.md) — **383** も **電源系** だが **仮設電圧**。

## 調査・確認手順

1. PC22 **UCAH/UCAL**（Lists ①）。
2. カゴ上 **+12 V**・コネクタ **抜き差し**（気配り TX1）。
3. **パネル縫い** 配線確認。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **382** | **気配り地絡** |
| [424](./KH-ALL-KEIAI-RX1-PINCH-424.md) | **RX1** 損傷 |
| [407](./KH-ALL-KEIAIN-DOOR-WIRING-407.md) | **戸系配線**（TX2 挟み） |
| [249](../practice-guides/KH-ALL-DC-SUPPLY-PROTECT-RESET-249.md) | **DC 保護** |
| [307](./KH-MRL-POWER-CABLE-IR-307.md) | **IR** |
| [383](./KH-ALL-WELDER-LOW-VOLT-DN-383.md) | 仮設 **電圧**（U-CAN 似た症状） |
| [414](./KH-VFGLF-LINE-LED-GROUND-414.md) | **421** ライン LED |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §382 |

## 未確認事項

- なし。
