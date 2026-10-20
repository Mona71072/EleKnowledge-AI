---

knowledge_id: KH-ESC-U-MODEL-CATALOG
kind: practice_guide
status: draft
card_version: 1
title: "u形エスカレーター機種略称（索引）"
symptoms:
  - "エスカレーター"
  - "u形"
  - "S1UJ1"
  - "S6UJ1"
  - "SVFC"
  - "機種略称"
model_scope:
  lists_model_label: []
  product_lines:
    - "escalator"
  control_methods:
    - "SVFC"
  model_abbreviations:
    - "S1UJ1"
    - "S6UJ1"
  door_families: []
  door_types: []
  observed_on: []
  may_apply_to:
    - "エスカレーター u形 — エレの VFGH/VFGLB 軸に載せない"
  excludes:
    - "エレベーター door_types / 制御方式の混同"
  scope_note: "Vault catalog 写し。Lists 事例未紐付"
source_refs:
  - ref_type: onenote_page
    onenote_id: "6f5ba25b-61e7-445e-ab15-77b81a9664e5:81"
    page_role: content
  - ref_type: draft_record
    record_id: "catalog-escalator-u-models"
    note: "照合用。出典にしない"
---
# u形エスカレーター機種略称（索引）

## 使う場面・対象条件

**製品: エスカレーター（u形）**。工技先輩 AI が **エレ事例カード** と混同しないよう、**機種略称・制御 SVFC** を確認するとき。

**Lists / 不具合 list_item_id なし** — Vault/OneNote 索引カード。

## 症状・現象

（catalog — 不具合カードではない）

## ソース要約

### Vault 写し（catalog-escalator-u-models）

- **製品名**: u形エスカレーター。
- **機種略称例**: **S1UJ1 (S1000)**、**S6UJ1 (S600)**。
- **制御方式欄**: **SVFC**（structured_data）。
- **形名**: 原資料 **表4.2** 参照（本文未全文レビュー）。

### OneNote（6f5ba25b…:81）

- エス機種一覧页（draft source_path 一致）。

## 統合した回答・ノウハウ

エスカは **`product_line: escalator`** + **`model_abbreviations`**（S1UJ1 等）+ **SVFC** で索引。エレの **L型/K型 door** や **CM-MA** には載せない。

## 調査・確認手順

1. 対象が **エスカ/u形** かエレかを確定。
2. 機種略称を catalog/品目で確認。
3. 不具合 list があれば **ESC_** draft / 将来 Wave で case 化。

## 関連事例と条件の違い

| 領域 | 索引 |
| --- | --- |
| エスカ u形 | **本カード** |
| エレ CM-MA | 制御別 INDEX |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | なし |
| OneNote | 6f5ba25b…:81 |
| KB | 形名表4.2（未レビュー） |

## 未確認事項

- 全 u形バリエーションの網羅（draft 2機種例のみ）。
