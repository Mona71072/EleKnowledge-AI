---
knowledge_id: KH-VFGLF-DOB-CPU-PORTABLE-105
kind: case_summary
status: draft
card_version: 1
title: "かご内戸開閉釦无效 — 釦CPU・60A・据付ポータブル（DOB/DCB）"
symptoms:
  - "戸開閉釦"
  - "DOB"
  - "DCB"
  - "釦CPU"
  - "60A"
  - "CID-PB05"
  - "VFGLF"
  - "64C"
model_scope:
  lists_model_label: ["VFGLF"]
  product_lines: ["AXIEZ-LINKs"]
  control_methods: ["VFGLF"]
  door_families: []
  door_types: []
  observed_on: ["VFGLF"]
  may_apply_to: ["かご内釦のみ失效・かご上ST釦は正常"]
  excludes: ["403 DOR-1280D 経路のみの切り分けで足りる場合"]
source_refs:
  - ref_type: lists_item
    list_item_id: "105"
  - ref_type: kb_document
    document_number: "C-6-S1300"
    kb_verify_status: pending
    locator: "P.11"
---

# かご内戸開閉釦无效 — 釦CPU・60A・据付ポータブル（DOB/DCB）

## 使う場面・対象条件

**制御 VFGLF**。自動時 **かご内戸開閉釦无效**、**かご上 ST 釦は正常**、**行先呼びは可**（Lists 105）。

**403（D14 DOR-1280D）** との差: 本件は **釦CPU A1 DOB/DCB 0V** + **据付ポータブル UP 故障→60A ON**。

## 症状・現象

- 独立/全自動で戸開閉釦不動（Lists）
- 64C（SETS 未調整）記載あり
- B4/B5 12V 良好、A1-3/A1-5 が 0V（Lists 測定）

## ソース要約

### Lists（105）

- **確定原因**: **据付用かご上ポータブル故障**（CID-PB05/PB02 常時導通）→ **60A ON** → 操作盤 **DOB/DCB 取込不可**。
- **対応**: 製品添付ポータブルに付替え解消。
- **稲電 H/W 確認**: DOR-128X A1A A3-B3 12V、J9 A1-B3 48V、60A 固着/誤通電切り分け（Notes 長文）。
- **progress**: 釦CPU/ST 基板交換では未解消 → ポータブル系が核心。

## 統合した回答・ノウハウ

かご内釦だけ死ぬとき **403 より先に** 釦CPU 電圧（C-6-S1300）と **AUTO 時 60A/据付ポータブル** を疑う（Lists 105）。

## 調査・確認手順

1. かご上 ST 釦 vs かご内釦の切り分け。
2. 釦CPU **A1 DOB/DCB**（Lists 表）。
3. **据付ポータブル** ↔ 製品ポータブル付替え試験。
4. DOR-128X A3-B3 / J9 / 60A（Lists Notes 稲電手順）。

## 関連事例と条件の違い

| list | 経路 |
| --- | --- |
| **105** | 釦CPU/60A/ポータブル |
| [403 D14/DOB](./KH-VFGLF-DOR-DOB-403.md) | **DOR-1280D** ST 釦 |
| [419 戸短](../practice-guides/KH-VFGLB-DOOR-SHORT-RELEASE-419.md) | ポータブル **戸短** |

## KB確認に基づく追記

（C-6-S1300 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §105 |
| KB | C-6-S1300 P.11 |

## 未確認事項

- 戸型（LV/KV）Lists 未記載。
