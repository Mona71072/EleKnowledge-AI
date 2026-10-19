---
knowledge_id: KH-KM-LD-PWFH-PHASE-54
kind: case_summary
status: draft
card_version: 1
title: "KM-LD — PWFH 逆相で回生スロー不可"
symptoms:
  - "PWFH"
  - "LFOH"
  - "欠相"
  - "逆相"
  - "15m/min"
model_scope:
  lists_model_label: ["KM-LD"]
source_refs:
  - ref_type: lists_item
    list_item_id: "54"
  - ref_type: kb_document
    document_number: "C-7-C3700"
    kb_verify_status: pending
---

# KM-LD — PWFH 逆相で回生スロー不可

## 使う場面・対象条件

**KM-LD** **WOS** で **回生 ON 時 15 m/min 不可**、**8 m/min のみ可** — **80** と同型症状、**本件は逆相**（Lists 54）。

## 症状・現象

- C1 **④PWFH、⑦LFOH**（Lists）。
- 回生コンバータ経路確認後も不可（Lists progress）。

## ソース要約

### Lists（54）

- **原因**: 客先 **R/T 相順誤り** — 分電 **二次 R/T 入替** → 回生付き運転可（Lists）。
- **progress**: NVA/NVB/NVC、PT.14 ピン、NVC 48V、C1 RSW 等 — 最終 **PWFH/LFOH LED 消灯** まで（Lists）。
- 参照 C-7-C3700、YE310C814（Lists — pending）。

## 統合した回答・ノウハウ

**80（CCP 未投入）** と切り分け: **PWFH/LFOH** → **相順・欠相** 優先（Lists）。

## 調査・確認手順

1. C1 **PWFH/LFOH** LED。
2. 客先 **相関・相順**（Lists progress 電圧例）。
3. 回生盤・CP14 電圧。
4. C-7-C3700 / PT.14（pending）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **54** | **逆相** |
| **80** | **CCP** |
| **46** | [ME-CH 89M](./KH-ME-CH-PHASE-89M-46.md) |

## KB確認に基づく追記

（C-7-C3700 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §54 |
| KB | C-7-C3700、YE310C814（pending） |

## 未確認事項

- 客先入替作業の安全手順（Lists 外）。
