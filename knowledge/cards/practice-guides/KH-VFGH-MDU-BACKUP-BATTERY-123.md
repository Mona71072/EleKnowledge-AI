---
knowledge_id: KH-VFGH-MDU-BACKUP-BATTERY-123
kind: practice_guide
status: draft
card_version: 1
title: "MELD なし — 受電盤バックアップバッテリー"
symptoms:
  - "MELD"
  - "バックアップバッテリー"
  - "受電盤"
  - "B79"
  - "48V"
model_scope:
  lists_model_label: ["VFGH"]
  control_methods: ["VFGH"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "123"
---

# MELD なし — 受電盤バックアップバッテリー

## 使う場面・対象条件

**VFGH** で **MELD 無し** なのに **受電盤バッテリー** があり MELD 有と誤解される（Lists 123）。

## 症状・現象

- MELD 無し仕様なのにバッテリー搭載（Lists）。

## ソース要約

### Lists（123）

- 条件: **1P 盤 + MELD なし + 遮煙戸なし（BBUK なし）** → **受電盤バックアップ**（制御盤型により盤内へ移る場合あり）。
- **48V**: 停電時 **B79 のみ** バックアップ → P1 の ±5V/±12V → **RAM→Flash 転送**（買電遮断時）。乗場 IND 等は制御上点灯させない（Lists）。

## 統合した回答・ノウハウ

**MELD 戸閉保証用** ではない — **制御データ保持** 用。遮煙・**227** とは別論点。

## 調査・確認手順

1. MELD / BBUK / 遮煙戸の品目。
2. バッテリー位置（受電 vs 制御盤）。
3. Lists 添付資料。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **123** | 受電盤 BB |
| **132** | RHY / MELD 実動作 |
| [227](./KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) | 遮煙 MELD 必須 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §123 |

## 未確認事項

- 現行盤種別一覧。
