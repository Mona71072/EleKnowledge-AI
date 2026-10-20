---

knowledge_id: KH-MRL-CAR-PANEL-B3-SW-438
kind: case_summary
status: draft
card_version: 1
title: "操作盤フロント/リア取違え — 平常-独立・ドア-切 SW 无效"
symptoms:
  - "開戸内スイッチ"
  - "平常-独立"
  - "ドア-切"
  - "ボタンCPU"
  - "B3"
  - "MRL"
  - "テレコ"
model_scope:
  lists_model_label: ["MRL機種"]
  machine_room: ["MRL"]
  door_families: []
  door_types: []
  observed_on: []
  may_apply_to: ["操作盤側面型・フロント/リア二面操作盤"]
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "438"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:161"
    page_role: index
  - ref_type: kb_document
    document_number: "C-6-S1200.1"
    kb_verify_status: pending
---
# 操作盤フロント/リア取違え — 平常-独立・ドア-切 SW 无效

## 使う場面・対象条件

**MRL**・**操作盤側面型**。高速出し時 **「平常-独立」「ドア-切」** のみ无效、他 SW は正常（Lists 438）。

## 症状・現象

- 独立設定でも全自動になる、ドア切でも DZ 内自動開
- 照明/ファン/点検/休止/自動-手動は正常

## ソース要約

### Lists（438）

- **原因**: **フロント/リア操作盤パネルがテレコ** — リア側に **ボタンCPU B3 への配線なし**。
- **機序**: 「平常-独立」「ドア-切」だけ **ボタンCPU B3→かご上 ST 伝送**。他 SW は ST 直結。
- **対応**: フロント/リア操作盤を **正しい向きに振替** 解消。
- **調査**: 伝送 620/DI/DO 良好、SW 導通良好、**B3 未接続** を発見。

### OneNote（`a8c15103-95f4-4d08-897a-403d412bffb5:161`）

- **不具合共有リスト索引** — 本件タイトル「開戸内スイッチの一部が動作しない」へのリンクのみ（**navigation**）。手順・原因は **Lists 438** が正。

## 統合した回答・ノウハウ

**2系統 SW だけ死ぬ** → **B3 経由 SW** と **操作盤 F/R 取付** を疑う（438）。354（VFGR B3/B7 テレコ）と配線構造が似る。

## 調査・確認手順

1. 无效 SW が B3 経由か（Lists 機序）。
2. フロント/リア パネル向き・テレコ。
3. ボタン CPU **B3** 配線有無（リア/フロント）。
4. C-6-S1200.1 信号経路。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **438** | MRL B3/F-R |
| **354** | VFGR B3/B7 |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §438 |
| OneNote | a8c15103…:161 |
| KB | C-6-S1200.1 |

## 未確認事項

- 具体機種略称・door_types（Lists MRL のみ）。
