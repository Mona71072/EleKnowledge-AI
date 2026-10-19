---
knowledge_id: KH-KM-LD-YBO-YBI-CONNECTOR-70
kind: case_summary
status: draft
card_version: 1
title: "KM-LD — YBO/YBI 誤結で戸閉遅延"
symptoms:
  - "強制戸閉"
  - "30秒"
  - "トランク戸開延長"
  - "YBO"
model_scope:
  lists_model_label: ["KM-LD"]
source_refs:
  - ref_type: lists_item
    list_item_id: "70"
  - ref_type: onenote_page
    onenote_id: "97d4ebd4-396d-4083-b8ca-0bf27391d4ea:1"
---

# KM-LD — YBO/YBI 誤結で戸閉遅延

## 使う場面・対象条件

**KM-LD** 全自動で **戸閉せず約30秒後強制戸閉**（Lists 70・重要）。

## 症状・現象

- 通常戸閉せず **強制戸閉待ち**（Lists）。

## ソース要約

### Lists（70）

- **原因**: かご上 ST **YBO コネクタが YBI に誤挿** → **トランク戸開延長** 動作（Lists）。
- **対応**: 結線是正（Lists）。
- **progress**: MBS LED・配線、MBS 無効試験、S/W 書換、ST 内結線（Lists）。

### OneNote 詳細

- `97d4ebd4-396d-4083-b8ca-0bf27391d4ea:1` — タイトル索引。詳細手順は未取得。

## 統合した回答・ノウハウ

戸閉タイマー異常は **ST 内コネクタ名（YBO/YBI）** を Lists 上優先確認。

## 調査・確認手順

1. 戸閉待ち時間（30s 前後）。
2. **YBO/YBI** 挿入先。
3. MBS・トランク延長機能の有無（Lists progress）。
4. OneNote 索引の関連リンク。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **70** | YBO/YBI |
| **105** | DOB/DCB |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §70 |
| OneNote | `97d4ebd4-396d-4083-b8ca-0bf27391d4ea:1` |

## 未確認事項

- トランク戸開延長の仕様正本（KB）。
