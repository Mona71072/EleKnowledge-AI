---
knowledge_id: KH-VFGLF-HOIST-RESOLVER-WIRE-411
kind: case_summary
status: draft
card_version: 1
title: "巻上機レゾルバ配線断線で空回し不能"
symptoms:
  - "空回し"
  - "レゾルバ"
  - "巻上機"
  - "VFGLF"
  - "ブレーキ"
model_scope:
  lists_model_label: ["VFGLF"]
  product_lines: ["AXIEZ-LINKs"]
  control_methods: ["VFGLF"]
  guide_systems: []
  door_families: []
  door_types: []
  observed_on: ["VFGLF"]
  may_apply_to: ["空回し1発目で停止後 UP/DN 無反応"]
  excludes: ["439 ドア駆動レゾルバ 328"]
source_refs:
  - ref_type: lists_item
    list_item_id: "411"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:154"
---

# 巻上機レゾルバ配線断線で空回し不能

## 使う場面・対象条件

**制御 VFGLF**。**空回し** 不可 — 1発目でブレーキ音後停止、以降 UP/DN 無反応（Lists 411）。

## 症状・現象

- 制御盤事前確認済みでも初回のみ動作
- 巻上機レゾルバ～上部配線 **断線**（Lists）

## ソース要約

### Lists（411）

- **切り分け**: 電源三相・BK SW・**レゾルバ導通** — 巻上機内～上部で **導通不良**。
- **対応**: アンプ処理暫定→配線交換予定。
- **Notes**: 同相/欠相/逆相の見方（電気屋確認推奨）。

## 統合した回答・ノウハウ

空回し即死は **巻上レゾルバ配線**（411）。**439** は **ドア駆動 328** で別系統。

## 調査・確認手順

1. 初回のみ動くか記録。
2. R/S/T、BK SW（Lists progress）。
3. **レゾルバ～巻上機上部** 導通。
4. 断線箇所 repair/交換。

## 関連事例と条件の違い

| list | 系統 |
| --- | --- |
| **411** | 巻上レゾルバ **線** |
| [113](./KH-VFGLF-RESOLVER-BOARD-113.md) | **KCZ-990C 基板** 93F（duplicate primary） |
| **439** | ドア 328 |

## KB確認に基づく追記

（なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §411 |
| OneNote | a8c15103…:154 |

## 未確認事項

- 配線交換後の最終記録（Lists 予定）。
