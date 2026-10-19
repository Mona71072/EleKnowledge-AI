---
knowledge_id: KH-KM-LD-SEISMIC-HARNESS-155
kind: case_summary
status: draft
card_version: 1
title: "変換ハーネス誤品 — 呼戻し中低ガル遠隔解除不可"
symptoms:
  - "低ガル"
  - "呼び戻し"
  - "地震官制"
  - "変換ハーネス"
  - "KM-LD"
model_scope:
  lists_model_label: ["KM-LD"]
  machine_room: ["MR"]
  control_methods: ["KM-LD"]
source_refs:
  - ref_type: lists_item
    list_item_id: "155"
---

# 変換ハーネス誤品 — 呼戻し中低ガル遠隔解除不可

## 使う場面・対象条件

**KM-LD** **呼び戻し運転中** **低ガル** → **監視盤解除 SW** でも **遠隔解除不可**（Lists 155・重要）。

## 症状・現象

- 地震官制 **解除側** 无效（Lists）。

## ソース要約

### Lists（155）

- **原因**: 高圧 16 極 **PS1 A列6** 未接続 — **群番指定誤り** 疑い（Lists）。
- **対策**: **低圧 PA05→PA06** 結線変更、YP 反映（Lists）。
- **Notes**: Q-3734 とは要因異なるが **省エネモード移行** 症状は同型（Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[157 MR 地震 SW](../practice-guides/KH-MR-SEISMIC-SW-ELEQUICK-157.md) — **155** は **ハーネス配線**。

## 調査・確認手順

1. **呼び戻し中** 低ガル再現条件。
2. 変換ハーネス **PA05/06**（Lists）。
3. 不発 **Q-3766** 系（Lists progress 要旨 — 詳細再掲しない）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **155** | ハーネス |
| [157](../practice-guides/KH-MR-SEISMIC-SW-ELEQUICK-157.md) | SW 設定 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §155 |

## 未確認事項

- Q-3734 との切り分け（Lists Notes のみ）。
