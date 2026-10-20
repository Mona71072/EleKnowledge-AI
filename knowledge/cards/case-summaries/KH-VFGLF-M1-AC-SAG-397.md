---
knowledge_id: KH-VFGLF-M1-AC-SAG-397
kind: case_summary
status: draft
card_version: 1
title: "M1 カード — AC 低下 312 と急停止"
symptoms:
  - "M1"
  - "312"
  - "AC電源低下"
  - "急停止"
  - "IPU"
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
    - "DOWN 中急停止・アラーム 312・盤面無表示"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "397"
---

# M1 カード — AC 低下 312 と急停止

## 使う場面・対象条件

**VFGLF** 工事使用中 **DOWN 急停止** → 最寄階着床後 **復帰**、盤 **無エラー**、メンテコン **312 AC 低下**（Lists 397）。

## 症状・現象

- 5 階付近等で急停止（Lists 例）。

## ソース要約

### Lists（397）

- 客先電源・仮設容量除外後 **M1 交換** → 改善。不発 **はんだクラック**（ASHO30325）。
- **Notes**: M1 単体可だが **IPU 交換推奨**（取外し P-6-S900.01-B **2-6** 放電）。コンデンサ **誤結線** 過去例 — 結線確認。

### OneNote

- なし。

## 統合した回答・ノウハウ

**101**（MELD±→M1 焼损）とは **別経路** — **397** は **運転中 312**。

## 調査・確認手順

1. アラーム履歴 **312**。
2. 客先/本設電圧。
3. **M1 / IPU** 交換（放電手順）。
4. 不発 FB。

## 正式資料

| 種別 | 参照 |
| --- | --- |
| Lists | §397 |
| KB | P-6-S900.01-B（pending） |

## 未確認事項

- なし。
