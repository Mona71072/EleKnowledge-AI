---
knowledge_id: KH-VFGLF-RESOLVER-BOARD-113
kind: case_summary
status: draft
card_version: 1
title: "レゾルバ基板 KCZ-990C — 93F 空回し不能"
symptoms:
  - "レゾルバ"
  - "KCZ-990C"
  - "93F"
  - "空回し"
  - "VFGLF"
  - "巻上機"
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
    - "巻上機空回し不能・93F"
  excludes: []
  scope_note: "411 は巻上レゾルバ線断線。113 は基板不良。duplicate primary: case-elv-vfglf-resolver-board-free-run-unavailable-id113"
source_refs:
  - ref_type: lists_item
    list_item_id: "113"
---

# レゾルバ基板 KCZ-990C — 93F 空回し不能

## 使う場面・対象条件

**VFGLF（MRL）** で **巻上機空回し不能**。**411** は **レゾルバ線断線**、**113** は **KCZ-990C 基板不良**。

## 症状・現象

- **空回し不能**
- 小分類 **93F**（SET1/0=7/1 で確認、Lists）

## ソース要約

### Lists（113）

- **配線・導通・コネクタ**（レゾルバ–P1）問題なし。
- **対応**: MEBS トラブルシュート参照 **レゾルバ基板交換** → 良好。
- **原因**: **KCZ-990C 不良** — 不具合品は **LED 全点灯**、交換品は **半分程度点灯**（Notes、個数未確認）。
- **参照**: VFGLF-J トラブルシュート 00602014–16（ST_AEER）、C-7-C3900 小分類 93F。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

93F 空回しは **配線→基板**。**411 断線** と **113 基板** は Lists 上別 record（duplicate の **elv-temporary-slow-issues** 索引にしない）。

## 調査・確認手順

1. SET1/0=7/1 で **93F** 確認（Lists）。
2. 制御盤～レゾルバ **配線・導通・コネクタ**。
3. 基板 **LED 点灯パターン**（Notes 参考）。
4. **KCZ-990C 交換**（MEBS マニュアル — KB 未レビュー）。
5. 断線疑いは **411** カードへ。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **113** | **基板** 93F |
| [411](./KH-VFGLF-HOIST-RESOLVER-WIRE-411.md) | **レゾルバ線** 断線 |
| [392](./KH-VFGLF-BRAKE-SW-392.md) | 本スロー **`:156`** 索引（別論点） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §113 |
| OneNote | なし |
| KB | C-7-C3900、VFGLF-J TS（pending） |

## 未確認事項

- 93F と ST_AEER の現行ソフト対応（Lists 注記どおり）。
