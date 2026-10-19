---
knowledge_id: KH-VFGH-SAI2200C-EMERG-IND-152
kind: practice_guide
status: draft
card_version: 1
title: "SAI2200C バンク内非常用エレの乗場インジ点灯"
symptoms:
  - "SAI2200C"
  - "非常用エレ"
  - "乗場インジ"
  - "ホールランタン"
  - "FL0"
  - "FL1"
  - "VFGH"
model_scope:
  lists_model_label:
    - "VFGH"
  control_methods:
    - "VFGH"
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on:
    - "VFGH"
  may_apply_to:
    - "即時予報付 SAI2200C・バンク内非常用エレ"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "152"
  - ref_type: onenote_page
    onenote_id: "f387bd9f-2ae5-4eb5-80db-909992d0ec42:1"
---

# SAI2200C バンク内非常用エレの乗場インジ点灯

## 使う場面・対象条件

**制御 VFGH**。**SAI2200C（即時予報付）** で **バンク内非常用エレの乗場インジ** が通常時 **点灯しない** — 問題か？（Lists 152）。

Lists **原因欄は情報管理保留**。判断は **Notes** 主。

## 症状・現象

- 通常運行時インジ不点灯（非常用エレ）
- 作業員からの問合せ（Lists）

## ソース要約

### Lists（152）

- **Notes**:
  - 仕様により **通常運転でも点灯** する場合あり — 仕様確認必須。
  - **1CAR 非常用**: 階床灯・方向灯は通常/非常とも表示。
  - SAI2200C + バンク内非常用: **通常時インジ点灯しない** が仕様得るが、**FL0/FL1 をホールランタン有** にすると **方向灯のみ点灯** — 誤設定注意。

### OneNote（f387bd9f…:1）

- 152 タイトル hit。

## 統合した回答・ノウハウ

不点灯＝不良と決めず **SAI2200C・1CAR/バンク内非常・FL0/FL1** を Sets で確認（Lists Notes）。

## 調査・確認手順

1. 監視 **SAI2200C** 即時予報付か。
2. 非常用が **1CAR** か **バンク内** か。
3. **FL0/FL1** ホールランタン設定（方向灯のみ点灯パターン）。
4. 仕様書/設計で **通常時点灯** の有無を確認。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **152** | 非常用 **インジ点灯仕様** |
| **147** | ホールランタン **配線挟み** |

## KB確認に基づく追記

（未実施 — 原因欄保留）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §152（Notes 主） |
| OneNote | f387bd9f…:1 |
| KB | なし |

## 未確認事項

- Lists 原因・response 原文（情報管理保留）。
