---
knowledge_id: KH-LINKS-CAR-TOP-G4-HAND-16
kind: case_summary
status: draft
card_version: 1
title: "LINKs — G4 誤挿でかご上 HAND スロー不可"
symptoms:
  - "41DG"
  - "かご上HAND"
  - "G4"
  - "手摺スイッチ"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "16"
---

# LINKs — G4 誤挿でかご上 HAND スロー不可

## 使う場面・対象条件

**AXIEZ-LINKS** **かご上 HAND** で **スロー不可**、**かご内 HAND/ETP ED は可**（Lists 16）。

## 症状・現象

- UP/DN 信号入るが **41DG 不点灯**（Lists）。

## ソース要約

### Lists（16）

- **原因**: **手摺 SW G4 コネクタ** を **ST 基板の別位置** に誤挿（Lists）。

## 統合した回答・ノウハウ

[27 本スロー G6](./KH-LINKS-BLOCKING-DEVICE-G6-27.md) と同系 **41DG 回路** — **コネクタ位置** 誤りが典型。

## 調査・確認手順

1. かご上 vs かご内 **HAND** 切り分け。
2. **G4** 挿入位置（図面どおりか）。
3. UP/DN と **41DG** 同時確認。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **16** | G4 |
| [27](./KH-LINKS-BLOCKING-DEVICE-G6-27.md) | G6 固定装置 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §16 |

## 未確認事項

- G4 正位置の C 図番。
