---
knowledge_id: KH-MRL-HALL-IND-WRONG-BOARD-318
kind: case_summary
status: draft
card_version: 1
title: "乗場位置表示 — LHH-1230E で G14/G24 取違え"
symptoms:
  - "乗場位置表示"
  - "LHH-1230E"
  - "G14"
  - "G24"
  - "2のみ表示"
  - "MRL"
model_scope:
  lists_model_label:
    - "MRL機種"
  machine_room:
    - "MRL"
  observed_on: []
  may_apply_to:
    - "B2 等で表示が単一桁だけになる"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "318"
---

# 乗場位置表示 — LHH-1230E で G14/G24 取違え

## 使う場面・対象条件

**MRL** **乗場位置表示器** で **特定階だけ桁がおかしい**（例: B2 が **2 のみ**）。

## 症状・現象

- B2 **「2」だけ表示**（Lists）

## ソース要約

### Lists（318）

- **原因**: プリント **G14/G24 取違え** — **LHH-1230E** で **2 桁=G24、1 桁=G14**。品目 **G24 手配** だが現地 **G14 据付**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

表示異常は **S/W 以前に基板品番**。**318** は **93 LHH-32X**（別型）と混同しない。

## 調査・確認手順

1. ドア型名・ **LHH-1230E** 等の型式。
2. 品目表 **G24/G14** 手配。
3. 現地基板品番 vs 桁数要件。
4. 誤品交換。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **318** | **乗場** G14/G24 |
| **93** | **LHH-32X** 表示基板 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §318 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- なし。
