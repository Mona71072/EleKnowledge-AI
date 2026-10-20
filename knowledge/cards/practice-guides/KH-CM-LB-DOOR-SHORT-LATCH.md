---

knowledge_id: KH-CM-LB-DOOR-SHORT-LATCH
kind: practice_guide
status: draft
card_version: 2
title: "CM-LB 戸短検出（ラッチあり）の注意"
symptoms:
  - "CM-LB"
  - "戸短検出"
  - "ラッチ"
  - "VFGLB-K"
  - "TI-1415"
model_scope:
  lists_model_label: []
  product_lines:
    - "Nexcube"
  machine_room:
    - "MR"
  model_abbreviations:
    - "CM-LB"
  control_methods:
    - "VFGLB-K"
  door_families: []
  door_types:
    - "CM-LB戸短検出（ラッチあり）"
  observed_on: []
  may_apply_to:
    - "CM-LB 戸短検出機能適用現場"
  excludes: []
source_refs:
  - ref_type: onenote_page
    onenote_id: "464e56cb-6668-4326-9c71-c89a3cb8c0dd:1"
    page_role: content
  - ref_type: kb_document
    document_number: "TI-1415"
    kb_verify_status: not_reviewed
    locator: ""
    summary_from_kb: ""
---
# CM-LB 戸短検出（ラッチあり）の注意

## 使う場面・対象条件

**機種 CM-LB** + **door_types: CM-LB 戸短（ラッチあり）**（**制御 VFGLB-K**）。LV5K/LV6K **戸型コード** とは別軸。戸短検出の適用・検査・保守を扱うとき。Vault **`技術メモ【ELV】３/モード/戸短検出機能の適用拡大（CM-LB）`** 写し（draft `catalog-elv3-cm-lb-door-short-detection-reference`）に基づく。

## 症状・現象

（Lists 単独事例に紐づけず）戸短・ラッチ状態の **誤判断リスク** を防ぐ参照カード。

## ソース要約

### OneNote（`464e56cb-…:1`）

- 原文注記: **「CM-LBはラッチありのため注意！！！！（～25/3E）」**
- **「25/3E」** の意味・現行性は本文のみでは未確定（draft 転記）。
- 埋め込み画像2点・TI-1415 PDF はスナップショット **未同梱・未閲覧**。

### Lists

- 本テーマ専用 list 節は Wave7 時点で未紐付（VFGLB 戸短 list 419 は別制御）。

## 統合した回答・ノウハウ

CM-LB の戸短検出は **ラッチあり** 仕様の注意が Vault/OneNote に明示されている。VFGLB 系の戸短解除手順を **そのまま CM-LB に適用しない**。TI-1415 と現行承認仕様を `content_reviewed` 後に手順化する。現時点では **判断材料にしない**（draft 安全警告どおり）。

## 調査・確認手順

1. 対象が CM-LB（VFGLB-K）か catalog で確認。
2. 戸短検出のラッチ状態を VFGLB 現場と混同していないか。
3. TI-1415・技連通知の現行版を KB 確認（未実施）。
4. 不明時は lists 419（VFGLB）手順を転用しない。

## 関連事例と条件の違い

| 制御 | 戸短 |
| --- | --- |
| **VFGLB-K**（CM-LB） | ラッチあり注意（本カード） |
| **VFGLB**（list 419） | 解除方法の注意（別 list） |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | — |
| OneNote | `464e56cb-6668-4326-9c71-c89a3cb8c0dd:1` |
| KB | TI-1415 |

## 未確認事項

- 25/3E の意味、画像・PDF 本文。
