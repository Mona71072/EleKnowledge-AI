---
knowledge_id: KH-ALL-FMS-CAM-SKEW-330
kind: practice_guide
status: draft
card_version: 1
title: "FMS 完了しない — 終点カム BG 斜め取付"
symptoms:
  - "FMS"
  - "UHS"
  - "A43"
  - "SET1/0"
  - "7/A"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "330"
---

# FMS 完了しない — 終点カム BG 斜め取付

## 使う場面・対象条件

**スロー FMS** で **UHS 停止・書込未完了**、**A43 セレクタずれ**（Lists 330）。

## 症状・現象

- **寸法不良・機械**（Lists）。

## ソース要約

### Lists（330）

- **原因**: **終点 SW カム** が **BG 方向に斜め**。
- **progress**: SET1/0=**7/A** で下部 DL 付近 **「E」** — カム倒れで **DL 時 DSR OFF** → 是正で FMS 完了。
- **Notes**: FMS 不完了の多くは **着床プレート or 終点 SW** — **7/9**（着床）、**7/A**（終点）読取を活用。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[380 S21](../case-summaries/KH-VFGLF-S21-B2-PIN-380.md) は **SETS 配線** — **330** は **カム機械**。

## 調査・確認手順

1. SET1/0 **7/9**・**7/A**（Lists Notes）。
2. 終点 **カム垂直**・DSR 随動。
3. 着床プレート（Lists Notes 多発原因）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **330** | **カム斜め** |
| [380](../case-summaries/KH-VFGLF-S21-B2-PIN-380.md) | **SETS** S21 |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §330 |

## 未確認事項

- なし。
