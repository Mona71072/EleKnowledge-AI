---
knowledge_id: KH-VFGLF-LINE-LED-GROUND-414
kind: case_summary
status: draft
card_version: 1
title: "ライン LED 挟み込み地絡 — 421 U-CAN"
symptoms:
  - "421"
  - "伝送異常"
  - "U-CAN"
  - "ラインLED"
  - "G1"
  - "G2"
model_scope:
  lists_model_label:
    - "VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "本スロー後 421・かご上/内運転不可"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "414"
---

# ライン LED 挟み込み地絡 — 421 U-CAN

## 使う場面・対象条件

**VFGLF** **本スロー後** **421**（ドア駆動基板 **伝送異常**）、かご上/内 **運転不可**（Lists 414）。

## 症状・現象

- UCAH/UCAL **12V**（正常 ~2V）、かご上 ST **+5V=19V** 等異常（Lists progress）。

## ソース要約

### Lists（414）

- **原因**: **左奥ライン LED** 配線 **挟み込み地絡**（DL5 間接光・現地取付）。
- **切分**: G1/G2 浮かせで解消 — 照明 ON で再発。**B1 対地導通**。
- 取外し **C-30-E6.106-J**（Lists）。

### OneNote

- なし。

## 統合した回答・ノウハウ

**417**（I-CAN 乗場）と **414**（U-CAN 照明地絡）は **421 共用** でも層が異なる。[222 MMS 噛み](./KH-LINKS-UCAN-MMS-CABLE-222.md) は **-42-/PLG** 切り口。

## 調査・確認手順

1. 421 確認。
2. PC22/J1 **UCAH/UCAL**。
3. **G1/G2** 抜き差し、波動 SW 照明。
4. ライン LED コネクタ **対地導通**（B1）。

## 関連事例と条件の違い

| カード | 軸 |
| --- | --- |
| [417 I-CAN 乗場](./KH-VFGLF-ICAN-HALL-BACKUP-417.md) | 421 別層 |
| [222 MMS 噛み](./KH-LINKS-UCAN-MMS-CABLE-222.md) | -42-/PLG |
| [407 気配り戸](./KH-ALL-KEIAIN-DOOR-WIRING-407.md) | U-CAN 索引 |
| [392 本スロー BK](./KH-VFGLF-BRAKE-SW-392.md) | 同 OneNote **`:156`** 索引 |
| [382 TX1 挟み](./KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) | 気配り **12V** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 本スロー後 421 — **横断入口** |

## KB確認に基づく追記

（C-30-E6.106-J 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §414 |
| OneNote | —（392 索引 `:156` U-CAN 行参照） |
| KB | C-30-E6.106-J（pending） |

## 未確認事項

- なし。
