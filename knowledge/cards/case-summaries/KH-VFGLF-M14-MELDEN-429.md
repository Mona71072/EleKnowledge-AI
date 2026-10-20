---
knowledge_id: KH-VFGLF-M14-MELDEN-429
kind: case_summary
status: draft
card_version: 1
title: "M14 ピンアサイン — 345 MCB(MP) 遮断"
symptoms:
  - "345"
  - "M14"
  - "MELDEN"
  - "MPスイッチ"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "高速調整後 MON 345"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "429"
---

# M14 ピンアサイン — 345 MCB(MP) 遮断

## 使う場面・対象条件

**VFGLF** **高速調整後** **345 MCB(MP) 遮断検出**（Lists 429）。

## 症状・現象

- MON=1/0 で **345**（Lists）。

## ソース要約

### Lists（429）

- **原因**: **M14（MP 側）1-3pin 接続** — 正は **2-3pin** → **MELDEN** 未取込。
- **調査**: RPC A9=0V、RHY A2=48V、**RHY B3=0V** → M14 確認。**2-3 短絡** でエラー消去。
- 図 **YE317C142**。菱技 3201 MELDEN 監視説明（Lists Notes）。

### OneNote

- なし。

## 統合した回答・ノウハウ

**132**（RHY 64D）と **429**（M14 MP）は **RHY 経路** で接続 — 345 は **MP 接点** 専用。

## 調査・確認手順

1. 345 意味（C 資料 SW_MELDEN_DETECTED）。
2. RPC/RHY 電圧。
3. **M14 ジャック 2-3** 図面照合。
4. 配線是正（Lists progress — 1pin 切断→2pin 追加例）。

## 未確認事項

- なし。
