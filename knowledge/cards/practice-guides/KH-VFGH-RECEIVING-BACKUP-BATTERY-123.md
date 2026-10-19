---
knowledge_id: KH-VFGH-RECEIVING-BACKUP-BATTERY-123
kind: practice_guide
status: draft
card_version: 1
title: "MELD なしでも受電盤バッテリー — B79・P1 RAM 退避"
symptoms:
  - "バックアップバッテリー"
  - "受電盤"
  - "MELDなし"
  - "B79"
  - "P1"
  - "VFGH"
  - "BBUK"
  - "48V"
model_scope:
  lists_model_label:
    - "VFGH"
  machine_room:
    - "MR"
  control_methods:
    - "VFGH"
  model_abbreviations: []
  observed_on:
    - "VFGH"
  may_apply_to:
    - "MELD 無し現場で受電盤にバッテリーがあり MELD と誤認される場合"
  excludes: []
  scope_note: "Nexcube 高速系 Lists 表記。制御盤型により盤内搭載に変わる旨あり"
source_refs:
  - ref_type: lists_item
    list_item_id: "123"
---

# MELD なしでも受電盤バッテリー — B79・P1 RAM 退避

## 使う場面・対象条件

**VFGH（MR 系 Lists）** で **MELD が無い** のに **受電盤にバッテリー** がある現場。据付者が MELD 有と誤解しやすい（Lists 123）。

## 症状・現象

- MELD なし仕様なのに **受電盤バッテリー** あり → **MELD 有と勘違い**（Lists）

## ソース要約

### Lists（123）

- **搭載条件（報告）**: 制御盤 **1P 盤** かつ **MELD なし** かつ **遮煙乗場ドアなし（戸閉保証 BBUK なし）** → 受電盤にバックアップバッテリー。**制御盤型** により盤内搭載に変わる。
- **用途**: 停電時 **B79 ラインのみ** バックアップ。**P1 カード +5V / ±12V** 供給 → 買電遮断時 **RAM 一部をフラッシュ ROM へ転送**。
- 電動機回路以外は回路的にはほぼバックアップ（乗場インジ等は制御上点灯させない）。詳細は Lists 添付資料参照。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**MELD 用バッテリー**（174 等）と **受電盤 48V バックアップ**（123）は用途が異なる。仕様表で **MELD / BBUK / 1P 盤** を確認してから盤を見に行く。

## 調査・確認手順

1. 品目・付加仕様で **MELD / 戸閉保証（BBUK）/ 遮煙乗場** の有無。
2. バッテリー位置（受電盤 vs 制御盤 vs MELD 盤）。
3. 停電時動作の疑いは **MELD 系**（132/174）と **B79/P1 退避**（123）で分岐。

## 関連事例と条件の違い

| テーマ | 例 |
| --- | --- |
| MELD 運転 | 132, 174, 167 |
| 受電盤 48V 退避 | **123** |
| 227 遮煙 | MELD または戸閉保証盤必須（別 list） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §123（添付資料） |
| OneNote | なし |
| KB | 未レビュー |

## 未確認事項

- 添付資料の KB 同定・content_review 前。
- 1P 盤定義と全 VFGH 現場への一般化（Lists 条件付き記載）。
