---
knowledge_id: KH-LV5K-LV6K-CAP-COVER-BAND-435
kind: practice_guide
status: draft
card_version: 1
title: "LV5K/LV6K かごドア カプラカバー入口の結束バンド"
symptoms:
  - "LV5K"
  - "LV6K"
  - "カプラカバー"
  - "結束バンド"
  - "MBS"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  door_families: []
  door_types:
    - "LV5K"
    - "LV6K"
  model_abbreviations: []
  observed_on:
    - "LV5K"
    - "LV6K"
  may_apply_to:
    - "ケーブルベアと MBS をジョイントするカプラカバー付き LV かごドア"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "435"
  - ref_type: onenote_page
    onenote_id: "057444fa-309a-4170-bbef-998c0015e5f7:120"
  - ref_type: kb_document
    document_number: "C-18-A9-491.1-J"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "IN-EL-12-107-12"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "IN-EL-12-104-43"
    kb_verify_status: pending
---

# LV5K/LV6K かごドア カプラカバー入口の結束バンド

## 使う場面・対象条件

**door_types: LV5K / LV6K** かごドア。**Lists Model=VFGLF**。

引渡し・保守点検で **カプラカバー入口に結束バンドが無い**、または MBS/配線まわりの防滴・固定確認時（Lists 435）。

## 症状・現象

- カプラカバー入口の結束バンド未取付（ビル側指摘）
- カプラカバーはケーブルベア–MBS ジョイントの **防滴**、結束バンドは **カバー固定**（Lists）

## ソース要約

### Lists（435）

- **原因**: 結束バンド使用忘れ。
- **依頼**: 結束バンドでカプラカバーを **必ず固定**。
- **対応済**: 結束バンドで固定（Lists）。
- **資料**: IN-EL-12-107-12、IN-EL-12-104-43、C-18-A9-491.1-J。

### OneNote（057444fa…:120）

- 不具合リスト索引に 435 リンク。
- チェック例: **カプラカバー入口に結束バンドがあるか**（MBS 配線・SDE 設定良好と併記）。

## 統合した回答・ノウハウ

LV5K/LV6K かごドアでは **カプラカバー入口の結束バンド** を欠落させない。制御が VFGLF でも **戸型 LV** で判断する。

## 調査・確認手順

1. 戸型 LV5K/LV6K を確認。
2. カプラカバー入口の **結束バンド有無** を目視。
3. 無ければ Lists 435 どおり結束バンドで固定。
4. MBS 配線・SDE（OneNote 同页チェック項目）を必要に応じ確認。

## 関連事例と条件の違い

| テーマ | カード |
| --- | --- |
| 結束バンド | **435** |
| CLT/OLT | [432](./KH-LV5K-LV6K-CLT-432.md) |
| G寸法異音 | **433** |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §435 |
| OneNote | 057444fa…:120 |
| KB | C-18-A9-491.1-J、IN-EL-12-107-12、IN-EL-12-104-43 |

## 未確認事項

- IN/C 資料の現行版と取付位置の詳細（KB 未レビュー）。
