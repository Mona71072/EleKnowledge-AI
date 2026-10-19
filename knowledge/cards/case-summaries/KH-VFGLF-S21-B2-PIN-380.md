---
knowledge_id: KH-VFGLF-S21-B2-PIN-380
kind: case_summary
status: draft
card_version: 1
title: "S21 B2 ピン抜け — 842 と SETS 下降不良"
symptoms:
  - "S21"
  - "842"
  - "SETS"
  - "1DSD"
  - "終点スイッチ"
  - "VFGLF"
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
    - "最上→最下で各階停止・842"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "380"
---

# S21 B2 ピン抜け — 842 と SETS 下降不良

## 使う場面・対象条件

**VFGLF** **自動 DOWN** で **各階停止**（UP は可）。**842 終点スイッチ順序違反**（Lists 380）。

## 症状・現象

- スロー不能、MON3/3 リミット **6F 超で E**、SETS 行程表示異常（Lists progress）。

## ソース要約

### Lists（380）

- **原因**: **S21 コネクタ B2 ピン抜け**（1DSD/SETS 系）。
- **Notes**: 1DSD 抜けでも走行するが **下降不良+スロー不可**。SETS 行程表示・UP2/DN2/UP1/DN1 共有（Lists）。

### OneNote

- なし。

## 統合した回答・ノウハウ

**187**（9999 エンコーダ）/ **113**（レゾルバ基板）と **842+S21** を分ける。

## 調査・確認手順

1. 842 確認。
2. **S21 B2** 嵌合。
3. SETS 行程・1DSD 結線。
4. DOWN/UP 非対称再試験。

## 未確認事項

- なし。
