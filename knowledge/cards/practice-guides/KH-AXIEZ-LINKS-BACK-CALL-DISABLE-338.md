---
knowledge_id: KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338
kind: practice_guide
status: draft
card_version: 1
title: "AXIEZ-LINKs 背後呼び登録無効（CID-S / CID-SA）"
symptoms:
  - "背後呼び"
  - "AXIEZ-LINKs"
  - "CID-S"
  - "CID-SA"
  - "群管理"
  - "呼び"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  door_families: []
  door_types: []
  model_abbreviations: []
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "5.7インチ CID-S 適用 LINKs"
    - "10.1インチ CID-SA 適用 LINKs"
  excludes: []
  scope_note: "群管理・呼び仕様（door 軸外）"
source_refs:
  - ref_type: lists_item
    list_item_id: "338"
---

# AXIEZ-LINKs 背後呼び登録無効（CID-S / CID-SA）

## 使う場面・対象条件

**制御 AXIEZ-LINKS** で **背後呼び登録無効**が効かない／効く条件の確認（Lists 338、豆知識）。

**door_families / door_types とは無関係** — 群管理・乗場 UI 仕様。

## 症状・現象

- 背後呼び登録無効機能が **効いていない** 現場がある（Lists）

## ソース要約

### Lists（338）

- **5.7インチ液晶 CID-S** → 背後呼び登録無効 **適用されない**。
- **10.1インチ CID-SA** → 背後呼び登録無効 **適用される**。
- **背後の定義（Notes）**: 運転方向と反対側で、自かごより後ろの階（例: 2階・UP 持ち → 1階が背後）。

## 統合した回答・ノウハウ

LINKs で背後呼び無効の有無を疑うとき、まず **CID-S vs CID-SA** を確認する（Lists 338）。VFGLF ラベルだけでは判断できない。

## 調査・確認手順

1. 乗場液晶が **CID-S（5.7）** か **CID-SA（10.1）** かを確認。
2. 338 の適用表どおり期待動作を設定。
3. 「背後」階の定義を Lists Notes で確認。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **338** | 背後呼び無効 × 液晶サイズ |
| **99** | かご内 **行先階予約** 表示 |
| [371 給電](../case-summaries/KH-MR-GROUP-PANEL-POWER-371.md) / [92 パニック](../case-summaries/KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) / [269 CR](../case-summaries/KH-ALL-CR-SECURITY-FLOOR-DISPLAY-269.md) | 群管理・呼び |
| [422 GS3](../case-summaries/KH-GS3-PART-NO-SCU20-422.md) / [384 3car](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | SCU / 多 car |

## KB確認に基づく追記

（該当 C 資料 Lists 未記載）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §338 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 現行仕様で CID 型式が追加・変更されていないか（Lists 2024 記載のみ）。
