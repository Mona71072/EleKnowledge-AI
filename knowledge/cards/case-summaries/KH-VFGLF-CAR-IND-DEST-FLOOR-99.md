---
knowledge_id: KH-VFGLF-CAR-IND-DEST-FLOOR-99
kind: case_summary
status: draft
card_version: 1
title: "階床 S/W 変更後もかご内行先階予約表示が変わらない（LHC-1132）"
symptoms:
  - "行先階予約"
  - "LHC-1132"
  - "ロータリースイッチ"
  - "FL1"
  - "階床表示"
  - "VFGLF"
  - "LINKs"
model_scope:
  lists_model_label:
    - "VFGLF"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  door_families: []
  door_types: []
  model_abbreviations: []
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "LINKs かご内インジ LHC-1132 系で M2/R 階等非標準階床"
  excludes: []
  scope_note: "群管理・表示（door 外）"
source_refs:
  - ref_type: lists_item
    list_item_id: "99"
  - ref_type: kb_document
    document_number: "C-32-A303.1-J"
    kb_verify_status: pending
---

# 階床 S/W 変更後もかご内行先階予約表示が変わらない（LHC-1132）

## 使う場面・対象条件

**制御 VFGLF（LINKs）**。制御盤 S/W で **乗場・かご内インジの階床表示**を変えたが、**かご内行先階予約表示（LINKs）** だけ旧表示のまま（Lists 99）。

## 症状・現象

- 行先階予約表示が階床変更に追随しない
- 制御盤 S/W 書換のみ実施（Lists Notes — 指示外作業リスク）

## ソース要約

### Lists（99）

- **原因**: 行先階変更には **かご内インジ基板 LHC-1132x** の **ロータリースイッチ FL1（最下階床名）** 変更が必要（**C-32-A303.1-J**）。
- **対応例**: FL1 を **D（B1FL）→ 1（1FL）** に変更。
- **Notes**: 改造要領にロータリ設定が無い場合は不発・改造提案で **行先階予約変更も記載** を依頼（Lists）。

## 統合した回答・ノウハウ

LINKs の **行先階予約**は制御盤階床 S/W だけでは変わらない。**LHC-1132 FL1** と **C-32-A303.1-J** をセットで確認（Lists 99）。

## 調査・確認手順

1. 階床変更範囲（M2/R 等）を確認。
2. 制御盤 S/W 変更に加え **LHC-1132 FL1** を C 資料どおり設定。
3. 改造要領に記載があるか確認；無ければ Lists Notes のエスカレーション方針。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **99** | 行先階予約 / FL1 |
| **338** | 背後呼び無効 |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §99 |
| OneNote | なし |
| KB | C-32-A303.1-J |

## 未確認事項

- LHC-1132 派生型番の差（Lists は 1132x 表記）。
