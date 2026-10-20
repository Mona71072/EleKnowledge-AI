---
knowledge_id: KH-VFGLB-UP1-SPRING-177
kind: case_summary
status: draft
card_version: 1
title: "最上階起動不能 — UP1 バネ外れと SETS 40"
symptoms:
  - "最上階"
  - "起動不能"
  - "UP1"
  - "SETS"
  - "62D"
  - "64E"
  - "64F"
  - "VFGLB"
model_scope:
  lists_model_label:
    - "VFGLB"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLB"
  observed_on:
    - "VFGLB"
  may_apply_to:
    - "高速出し後、最上階だけ自動で止まる"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "177"
---

# 最上階起動不能 — UP1 バネ外れと SETS 40

## 使う場面・対象条件

**VFGLB** **高速出し後**、**最上階着床後だけ** 自動運転が進まない（他階・手動は OK）。

## 症状・現象

- P1: **62D, 64E, 64F** — SETS **40 かご位置異常**（Lists）

## ソース要約

### Lists（177）

- **原因**: **基準位置 SW UP1 バネ外れ** → ON 故障。
- **注意**: 取付位置 **「OK」** は **位置確認のみ** — **ON/OFF 判定まではしない**（Lists）。
- **progress**: 情報管理 **保留**（識別情報）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

SETS/群管理エラーで **最上階限定** なら **UP1 機械** を Lists 177 どおり。[187 エンコーダ/KUN](./KH-MRL-SETS-ENCODER-DIR-187.md)（**9999**）とは別。

## 調査・確認手順

1. 最上階限定か確認。
2. P1 / SETS エラー（62D 系、40）。
3. **UP1 バネ・ON/OFF**（取付 OK 表示だけ信用しない）。
4. バネ復帰後試運転。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **177** | **UP1 バネ** |
| [187](./KH-MRL-SETS-ENCODER-DIR-187.md) | SETS **9999** エンコーダ |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §177 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- progress **保留**。
