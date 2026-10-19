---
knowledge_id: KH-ALL-PHOTO-POST-FOB-DISPLAY-296
kind: practice_guide
status: draft
card_version: 1
title: "光電ポスト — 自動運転時インジ（FOB/制御方式別）"
symptoms:
  - "光電ポスト"
  - "FOB"
  - "進入禁止"
model_scope:
  lists_model_label: ["トラベーター"]
  may_apply_to: ["クラスタA", "SVFB", "SVFC", "スパイラルESC", "J型モダニ"]
source_refs:
  - ref_type: lists_item
    list_item_id: "296"
---

# 光電ポスト — 自動運転時インジ（FOB/制御方式別）

## 使う場面・対象条件

**光電ポスト** に **自動運転状態が表示されない** 等、FOB とインジの関係確認（Lists 296）。

## 症状・現象

- FOB ON でコンタクタ → インジ回路閉じる例（Lists — 接続図参照）。

## ソース要約

### Lists（296）

- **クラスタ A**（トラベータ・スパイラル ESC・J 型モダニ）: **FOB OFF＝保守中** → 上下 **進入禁止**；FOB ON＝運転状態表示。
- **SVFB**（ZA/AV）: **ポータブル運転＝保守中** → 進入禁止。
- **SVFC**（ZJ/u 形）: **ポータブル運転＝保守中** → **消灯**（Lists）。

## 統合した回答・ノウハウ

[301 B センサ](../case-summaries/KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301.md) は **ESC 低速待機** — 本件は **光電ポスト表示条件**（横断豆知識）。

## 調査・確認手順

1. **制御方式**（A / SVFB / SVFC）。
2. **FOB** または **ポータブル** 状態。
3. 接続図の **FOB–コンタクタ–インジ**（Lists）。
4. 方式別期待表示（Lists 296）。

## 関連事例と条件の違い

| 区分 | 保守表示 |
| --- | --- |
| クラスタ A | FOB OFF → 進入禁止 |
| SVFB | ポータブル → 進入禁止 |
| SVFC | ポータブル → 消灯 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §296 |

## 未確認事項

- トラベータ専用図と ESC 図の混同防止。
