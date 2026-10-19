---
knowledge_id: KH-ESC-ZJ-SAFL-HGS-52
kind: case_summary
status: draft
card_version: 1
title: "ZJ ESC — SD_SAFL と HGS-R コネクタ"
symptoms:
  - "SD_SAFL"
  - "安全回路"
  - "ブザーチェッカー"
  - "HGS-R"
model_scope:
  lists_model_label: ["ZJ型ESC"]
  may_apply_to: ["エスカレーター ZJ"]
source_refs:
  - ref_type: lists_item
    list_item_id: "52"
  - ref_type: lists_item
    list_item_id: "285"
---

# ZJ ESC — SD_SAFL と HGS-R コネクタ

## 使う場面・対象条件

**ZJ 型 ESC** **突然運転不可**、盤上 **A 接点不一致**（Lists **52**＝**285** 同型記述）。

## 症状・現象

- 安全 SW 点検中 **ブザー常鳴**（Lists）。
- エラー **SD_SAFL**（メンテコン「現状確認」）（Lists progress）。

## ソース要約

### Lists（52 / 285）

- **切り分け**: **29 ライン（B 接点側）順次短絡** → **下部 HGS-R のみ短絡でブザー停止**（Lists）。
- **対応**: 当該 **コネクタ抜き差し** で正常 — ピン異常なし（Lists）。
- **285 Notes**: **7SEG の A 接点だけ** では SW 特定できない場合 — **B 接点（29 回路）** で SAFL 確認（Lists）。

## 統合した回答・ノウハウ

A 接点表示と **SAFL リアルタイム** がズレる — **白 MC＋現状確認**（Lists）。

## 調査・確認手順

1. メンテコン **SD_SAFL** 確認。
2. **29 ライン** 短絡順。
3. **HGS-R** コネクタ抜き差し。
4. ブザーチェッカー作業手順の再現条件。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **52 / 285** | HGS-R・29 短絡 |
| **65** | DC1/DC2 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §52、§285 |

## 未確認事項

- SD_SAFL の正式定義（KB）。
