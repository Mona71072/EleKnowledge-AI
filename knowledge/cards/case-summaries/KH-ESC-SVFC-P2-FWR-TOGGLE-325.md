---
knowledge_id: KH-ESC-SVFC-P2-FWR-TOGGLE-325
kind: case_summary
status: draft
card_version: 1
title: "SVFC P2 FWR トグル — E-1 001 / P1P2 通信"
symptoms:
  - "SVFC"
  - "FWR"
  - "P2"
  - "トグル"
  - "E-1 001"
  - "E-0 C13"
  - "E-2 C11"
model_scope:
  lists_model_label:
    - "SVFC"
  product_lines:
    - "escalator"
  control_methods:
    - "SVFC"
  observed_on:
    - "SVFC"
  may_apply_to:
    - "受電後ポータブル運転不可・P1P2 通信系エラー"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "325"
---

# SVFC P2 FWR トグル — E-1 001 / P1P2 通信

## 使う場面・対象条件

**SVFC** **受電後** ポータブル運転不可。**E-1 001 / E-0 C13 / E-2 C11**（Lists 325）。

## 症状・現象

- インバータ盤 **P2 基板トグル SW** が **FWR 側** 倒れ（Lists）。

## ソース要約

### Lists（325）

- **対応**: トグル **中立** → エラー解消・運転可。
- **Notes**: FWR 倒れの **確定原因不明** — 同エラー時は **確認推奨**。

### OneNote

- Lists §325 **タイトル一致なし**。エレ盤の R/M/MNT/FWR 記述（例: 秤調整メモ）は **P2 インバータ FWR 倒れ（325）と別系** — 混同しない。
- SVFC 横断索引: [KH-ESC-U-MODEL-CATALOG](../practice-guides/KH-ESC-U-MODEL-CATALOG.md)。


## 統合した回答・ノウハウ

**325** は **盤内 SW**、**298** は **JB UVW** — エラー近接時も配線/SW を分ける。

## 調査・確認手順

1. エラー 001 / C13 / C11。
2. **P2 トグル** 中立 vs FWR。
3. 必要なら **298** 動力相順。

## 関連事例と条件の違い

| list | 層 |
| --- | --- |
| **325** | **P2 SW** |
| [298](./KH-ESC-SVFC-UVW-WIRING-298.md) | **受電 JB** |
| [326](./KH-ESC-SVFC-STEP-CHAIN-GAP-326.md) | ステップ **チェーン隙間** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §325 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- FWR 倒れ原因（Lists）。
