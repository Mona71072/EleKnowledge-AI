---
knowledge_id: KH-VFGR-DIRECT-COMM-B3B7-354
kind: case_summary
status: draft
card_version: 1
title: "VFGR 直伝通信未確立 — B3/B7 テレコ（ドアSW・点検SW）"
symptoms:
  - "VFGR"
  - "直伝通信"
  - "ドアSW"
  - "点検SW"
  - "CPD"
  - "LHS-509C"
  - "B3"
  - "B7"
model_scope:
  lists_model_label: ["VFGR"]
  control_methods: ["VFGR"]
  product_lines: ["MELCITY"]
  door_families: []
  door_types: []
  observed_on: ["VFGR"]
  may_apply_to: ["かご内調整・ドアカット・点検SW・CPD が同時におかしい VFGR"]
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "354"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:136"
  - ref_type: kb_document
    document_number: "YE601D403"
    kb_verify_status: pending
---

# VFGR 直伝通信未確立 — B3/B7 テレコ（ドアSW・点検SW）

## 使う場面・対象条件

**制御 VFGR** 高速調整時、**かご内調整反映なし** + **点検SW** + **ドアSW（カット不可）** + **CPD** が同時不調（Lists 354）。

## 症状・現象

- P1 操作は可、点検 SW 不可、停電灯なし
- ドア SW 无效、CPD-K 鳴らず（インターホンは可）

## ソース要約

### Lists（354）

- **原因**: かご釦 CPU **LHS-509C** の **B3 と B7 コネクタがテレコ** — DO/DI **直伝通信** 不通。
- **対応**: コネクタ復旧で一括解消。
- **Notes**: ②③④は **かご内調整基板経由** のため、複合時は基板結線/交換も検討。
- **図**: YE601D403、YE602C556、YE602B764G01G03。

## 統合した回答・ノウハウ

VFGR で **ドアSW+点検+CPD** がまとめて死ぬとき **B3/B7 テレコ** を先に見る（354）。戸型軸ではない。

## 調査・確認手順

1. 症状が 354 Notes の複合パターンか確認。
2. LHS-509C **B3/B7** 嵌合・ピン。
3. 直伝 DO/DI ライン。
4. 必要ならかご内調整基板・配線図どおり再確認。

## 関連事例と条件の違い

| list | 機種 |
| --- | --- |
| **354** | VFGR 直伝 |
| **438** | 操作盤 **B3** 経路（VFGLF/MRL） |
| [403](./KH-VFGLF-DOR-DOB-403.md) | ドア SW **D14/釦CPU** 系 |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §354 |
| OneNote | a8c15103…:136 |
| KB | YE601D403 等 |

## 未確認事項

- KB 図面現行版。
