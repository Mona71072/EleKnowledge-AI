---
knowledge_id: KH-ALL-1D2G-PAD-REVERSED-324
kind: case_summary
status: draft
card_version: 1
title: "1D2G — 調整前戸開せず（PAD 取付 F/R 逆）"
symptoms:
  - "戸開しない"
  - "421"
  - "204021"
  - "PAD"
  - "D21"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "324"
  - ref_type: kb_document
    document_number: "C-18-D60.1-J"
    kb_verify_status: pending
---

# 1D2G — 調整前戸開せず（PAD 取付 F/R 逆）

## 使う場面・対象条件

**1D2G** **調整前** **戸閉はするが戸開しない**、**#D21 不点灯**、かご上 **421 CAN 異常**（Lists 324）。

## 症状・現象

- 全自動/独立/スローで **戸開指令なし**（Lists 症状詳細）。

## ソース要約

### Lists（324）

- **原因**: **かご上 PAD 本体** の **フロント/リア取付位置が逆**。
- **progress**: 伝送・基板交換等後、**PAD 位置是正** で解消。診断 **204021**（トラブルシュート参照）。
- **Notes**: エラー **3 桁**＝保守資料 **C-18-D60.1-J**、**2 桁**＝据付 **C-18-D60.2-J**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**421 CAN** を **配線だけ** で追わない — **PAD 物理向き** を [113 93F](../case-summaries/KH-VFGLF-RESOLVER-BOARD-93F-113.md) 系と同様 **取付** 視点で確認。

## 調査・確認手順

1. かご上 ST **421** / MON 伝送。
2. **PAD 取込順**（インジ表示）と **実取付 F/R**。
3. 204021 TS 手順（Lists Referenced）。
4. 是正後 **D21**・戸開指令。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **324** | **PAD 逆** |
| [403](./KH-VFGLF-DOR-DOB-403.md) | **DOB/DCB** 電圧 |
| [438](./KH-MRL-CAR-PANEL-B3-SW-438.md) | 操作盤 **B3** |

## KB確認に基づく追記

（C-18-D60.1-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §324 |
| KB | C-18-D60.1-J / D60.2-J（pending） |

## 未確認事項

- なし（Lists cause 確定）。
