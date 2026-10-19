---
knowledge_id: KH-ALL-MAINTECON-P1-USB-88
kind: practice_guide
status: draft
card_version: 1
title: "メンテコン — P1 未認識（FWR トグル・USB COM）"
symptoms:
  - "メンテコン"
  - "P1"
  - "PP10"
  - "FWR"
  - "USB"
  - "COM"
model_scope:
  lists_model_label: []
  observed_on: []
  may_apply_to:
    - "メンテコンが P1 を認識しない"
  excludes: []
  scope_note: "Lists Model 空欄 — 横断手順"
source_refs:
  - ref_type: lists_item
    list_item_id: "88"
---

# メンテコン — P1 未認識（FWR トグル・USB COM）

## 使う場面・対象条件

**メンテコン** を **P1 / PP10** に接続して **P1 未認識**（Lists 88、Lists Model 空）。

## 症状・現象

- 接続後認識しない（Lists）。

## ソース要約

### Lists（88）

- **トグル SW が FWR 側** でないか確認。
- **USB ポート COM1** 設定（添付参照）。
- **追記**: デバイスマネージャで USB シリアルに **!** — **Intel AMT SOL が COM1** なら **COM3** 等へ変更（Lists）。

### OneNote

- なし。

## 統合した回答・ノウハウ

**325**（エス P2 FWR）/ **88**（メンテコン FWR）— 同名でも **機種別**。P1 未認識は **FWR + COM** を先に Lists 88。

## 調査・確認手順

1. P1 トグル **中立**（FWR でない）。
2. メンテコン USB **COM** 設定。
3. デバイスマネージャ **SOL COM 競合**。

## 関連事例と条件の違い

| list | 層 |
| --- | --- |
| **88** | **PC–P1** |
| **325** | エス **P2 FWR** |

## KB確認に基づく追記

（添付手順 — KB 未照合）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §88 |
| OneNote | なし |
| KB | Lists 添付（pending） |

## 未確認事項

- 添付画像/手順ファイル未同梱。
