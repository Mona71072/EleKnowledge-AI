---
knowledge_id: KH-MRL-BRAKE-WIRING-REVERSE-362
kind: case_summary
status: draft
card_version: 1
title: "MRL — 制御盤内ブレーキ結線逆で空回し不能"
symptoms:
  - "空回し"
  - "ブレーキ交互"
  - "QB1"
  - "YE317C123"
model_scope:
  lists_model_label: ["MRL機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "362"
---

# MRL — 制御盤内ブレーキ結線逆で空回し不能

## 使う場面・対象条件

**MRL** **空回し** 不可 — **左右ブレーキ交互**（Lists 362）。

## 症状・現象

- UP/DN 中 **片側ずつ** 開閉、シーブ **不回転**（Lists）。
- **ETP** ブレーキ開放では **両側開**（Lists）。

## ソース要約

### Lists（362）

- **原因**: 稲電 **内部結線** で **ブレーキ回路逆** — QB1 **QP7–QP8** がテレコ（YE317C123）。
- **対応**: 正規配線で **空回し良好**。

### OneNote

- スナップショット照合: Lists §362 の **タイトル一致・ID 索引未検出**（Lists のみ。OneNote 追探索は別途）。


## 統合した回答・ノウハウ

BK 系エラー調査の **盤内ファストン** 確認例 — [390](../practice-guides/KH-MRL-UCMP-SEISMIC-INDEX-390.md)（UCMP 索引・情報管理保留）。

## 調査・確認手順

1. Lists progress の **BK/BC 電圧・コネクタ** 確認。
2. 制御盤内 **QB1** QP7–QP8（YE317C123）。
3. ETP 開放で **両ブレーキ** 切分。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **362** | **盤内結線逆** |
| [390](../practice-guides/KH-MRL-UCMP-SEISMIC-INDEX-390.md) | **UCMP** 索引（BK 調査文脈） |
| [438](../practice-guides/KH-MRL-CAR-PANEL-B3-SW-438.md) | **BK1 SW** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §362 |
| KB | YE317C123（pending） |

## 未確認事項

- なし（Lists cause 確定）。
