---
knowledge_id: KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301
kind: case_summary
status: draft
card_version: 1
title: "エス B センサ — 低速待機に移行しない"
symptoms:
  - "低速待機"
  - "Bセンサー"
  - "SFVB"
  - "ロータリー"
  - "エスカレーター"
model_scope:
  lists_model_label:
    - "全エス機種"
  product_lines:
    - "escalator"
  observed_on: []
  may_apply_to:
    - "オート低速待機 ON でも低速待機しない"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "301"
---

# エス B センサ — 低速待機に移行しない

## 使う場面・対象条件

**全エス** 自動運転で **低速待機オート** 設定も **低速待機に入らない**（Lists 301）。

## 症状・現象

- **B センサ** 動作表示灯（赤）**常時消灯**、C センサは良好（Lists progress）。
- 稲電出荷時 **距離設定ボリウム最小**（Lists）。

## ソース要約

### Lists（301）

- **原因**: 上下 **B センサ距離設定不良**。
- **対応**: 距離ボリウム（ロータリー）**時計回り**で検出距離延長 → 正常。
- **Notes**: **SFVB** は 7seg でセンサ反応確認不可 → 調整後 **エンドキャップ正位置** + **センサ LED** で確認。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**103**（SVFC ポスト光電・停止待機）と **301**（B センサ・低速待機）は **別センサ軸**。

## 調査・確認手順

1. C vs B センサ表示（Lists progress）。
2. B **距離ボリウム** 調整。
3. SFVB: **LED** 確認（7seg 不可）。
4. 低速待機オート再試験。

## 関連事例と条件の違い

| list | センサ |
| --- | --- |
| **301** | **B** 低速待機 |
| **103** | **ポスト光電** 停止待機 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §301 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- なし。
