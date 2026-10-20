---
knowledge_id: KH-KM-LD-MED-HARNESS-E35-261
kind: case_summary
status: draft
card_version: 1
title: "KM-LD — MED ハーネス違いで E35/E36/E45"
symptoms:
  - "E35"
  - "E36"
  - "E45"
  - "U-CAN"
  - "MED-2"
model_scope:
  lists_model_label: ["KM-LD"]
source_refs:
  - ref_type: lists_item
    list_item_id: "261"
---

# KM-LD — MED ハーネス違いで E35/E36/E45

## 使う場面・対象条件

**WOS→本スロー後** **E35/E36/E45** — **CPU リセット直後のみ短時間可**（Lists 261）。

## 症状・現象

- **乗場 PT** は継続可（Lists）。
- **MED-2 用 ST ハーネス** vs 現地 **MED-2.1**（Lists）。

## ソース要約

### Lists（261）

- **L10/L20 AC100V** が **停電灯 DC16V** へ **混触** → **CS 損傷（R600 等）**、**CAN 拒否 S/W**（Lists）。
- **対策**: CS・停電灯交換（Lists）。
- **Notes**: 通信エラーでも **地絡/混触** を疑う（Lists）。

## 統合した回答・ノウハウ

[266 MED 版差](../practice-guides/KH-MRL-HEALTH-AIR-MED-VERSION-266.md)・[282 照度](../practice-guides/KH-ALL-CABIN-ILLUMINANCE-62LX-282.md)（停電灯）— 本件は **ハーネス群番**。[46](../case-summaries/KH-ME-CH-PHASE-89M-46.md) も E35/E45 例示。

## 調査・確認手順

1. **MED 版** vs **かご上 ST ハーネス**。
2. **U-CAN** 電圧・終端・ピン（Lists progress）。
3. **CS/DC** 基板電圧・421 等。
4. **挟み込み/コタ**（Lists Notes 類似）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **261** | MED 混触 |
| [266](../practice-guides/KH-MRL-HEALTH-AIR-MED-VERSION-266.md) | 版違い |
| [46](../case-summaries/KH-ME-CH-PHASE-89M-46.md) | E35 例 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §261 |

## 未確認事項

- MED-2/2.1 ハーネス品番対照。
