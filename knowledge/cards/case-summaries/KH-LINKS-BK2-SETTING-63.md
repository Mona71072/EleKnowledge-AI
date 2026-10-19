---
knowledge_id: KH-LINKS-BK2-SETTING-63
kind: case_summary
status: draft
card_version: 1
title: "LINKs — BK2 設定不良で B・K 表示・不走"
symptoms:
  - "B・K"
  - "BK接点"
  - "ブレーキ開放"
  - "ETP"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "63"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:156"
  - ref_type: kb_document
    document_number: "C-4-A90"
    kb_verify_status: pending
---

# LINKs — BK2 設定不良で B・K 表示・不走

## 使う場面・対象条件

**AXIEZ-LINKS** 引継後 **かご不走**、乗場インジ **「B・K・↓」**、**ブレーキ開放のみ可**（Lists 63）。

## 症状・現象

- ETP UP/DN で戸は閉まるが **不走**（Lists）。
- **BK2** のみ UP/DN 時 **導通なし**（Lists progress）。

## ソース要約

### Lists（63）

- **原因**: **BK2 接点設定不良** — **C-4-A90** 基準で調整→正常（Lists）。
- **Notes**: 手動束不可時は **ブレーキ開放** — 空振り時 DN 不能リスク → **他原因潰し**＋**乗場オモリ準備**（Lists）。
- **progress**: QB1 一時疑い（接触不良）、BK1/BK2 比較（Lists）。

### OneNote 詳細

- 索引 `a8c15103-95f4-4d08-897a-403d412bffb5:156` — 本文未取得（タイトル hit のみ）。

## 統合した回答・ノウハウ

**81** と同系 BK 設定。**BK2 のみ** UP/DN 時不良は Lists 上の典型切り分け。

## 調査・確認手順

1. インジ **B・K** 表示。
2. ブレーキ開放 vs UP/DN **コイル電圧** 比較（Lists progress）。
3. **BK1/BK2 SW** 導通。
4. C-4-A90 設定（pending）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **63** | BK2 |
| **81** | BK2 設定（別事例） |
| **82** | QB1 逆接 |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（C-4-A90 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §63 |
| OneNote | `a8c15103-95f4-4d08-897a-403d412bffb5:156` |
| KB | C-4-A90（pending） |

## 未確認事項

- OneNote 本文・手順詳細。
