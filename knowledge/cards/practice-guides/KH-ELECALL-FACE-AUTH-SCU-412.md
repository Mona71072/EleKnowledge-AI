---

knowledge_id: KH-ELECALL-FACE-AUTH-SCU-412
kind: practice_guide
status: draft
card_version: 1
title: "エレコール — 顔認証複数台の SCU RS-422 ポート"
symptoms:
  - "顔認証"
  - "SCU"
  - "RS-422"
  - "2RDB"
  - "3RDB"
  - "制御装置ID"
  - "エレコール"
model_scope:
  lists_model_label:
    - "エレコール"
  observed_on: []
  may_apply_to:
    - "顔認証デバイス複数・SCU 接続先不明"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "412"
  - ref_type: kb_document
    document_number: "C-7-C3343.1"
    kb_verify_status: pending
  - ref_type: onenote_page
    onenote_id: "2dbb1e7c-e6c4-4b52-87b1-9e8896eaa58b:1"
    page_role: cross_cutting
    note: "Lists タイトル一致 — snapshot `onenote-758605d7c606a475a4eeb209.md`（本文未転載）"
---
# エレコール — 顔認証複数台の SCU RS-422 ポート

## 使う場面・対象条件

**エレコール** **顔認証デバイス複数** — **SCU 上の RS-422 接続先**（Lists 412）。CR とは **1 装置＝1 制御装置** 扱い。

## 症状・現象

- 複数顔認証の **SCU ポート** が分からない（Lists）。
- 基本: **ポート1=HA**、**ポート2=CR 通信**（Lists）。

## ソース要約

### Lists（412）

- **IDS**: 制御装置 ID **(1)** → **ポート2: 2RDB～**、**(2)** → **ポート3: 3RDB～**。
- **暫定** — 最終は据付図記載予定（Lists Notes）。
- **ゲート番号** 両方 01 でも可 — SCU は **2RDB/3RDB で 01/02 相当** に区別（Lists）。

### OneNote

- **onenote_id**: `2dbb1e7c-e6c4-4b52-87b1-9e8896eaa58b:1` — Lists タイトル一致 — snapshot `onenote-758605d7c606a475a4eeb209.md`（本文未転載）


## 統合した回答・ノウハウ

**143**（ゲート番号）/ **412**（**物理ポート**）を併用。**149**（SCU-20 通信）は別 list。

## 調査・確認手順

1. IDS **制御装置 ID (1)(2)**。
2. SCU **2RDB / 3RDB** 結線。
3. 据付図確定後は図面優先（Lists 暫定注記）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **412** | 顔認証 **ポート** |
| [143](../case-summaries/KH-ELECALL-GATE-NO-INTERCOM-143.md) | インターホン **ゲート** |

## KB確認に基づく追記

（C-7-C3343.1 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §412 |
| OneNote | なし |
| KB | C-7-C3343.1 |

## 未確認事項

- IDS 本文未レビュー — Lists 要約のみ。
