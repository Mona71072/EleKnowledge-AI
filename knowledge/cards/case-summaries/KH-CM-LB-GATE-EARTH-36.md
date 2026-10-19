---
knowledge_id: KH-CM-LB-GATE-EARTH-36
kind: case_summary
status: draft
card_version: 1
title: "CM-LB — ゲート SW G3/EARTH 取違えと D41"
symptoms:
  - "D41"
  - "41DG"
  - "R1"
  - "KCA-1102B"
  - "CM-LB"
  - "本スロー"
model_scope:
  lists_model_label:
    - "CM-LB"
  machine_room:
    - "MR"
  control_methods:
    - "VFGLB-K"
  model_abbreviations:
    - "CM-LB"
  observed_on:
    - "CM-LB"
  may_apply_to:
    - "本スロー切替で D41 不点灯・R1 焼損疑い"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "36"
---

# CM-LB — ゲート SW G3/EARTH 取違えと D41

## 使う場面・対象条件

**CM-LB** **本スロー切替** で **D41 不点灯** → R1 焼損交換しても改善せず（Lists 36）。

## 症状・現象

- D41-420 短絡投入で **R1（KCA-1102B）焼損**（Lists — 実因は配線）。

## ソース要約

### Lists（36）

- **原因**: **ゲート SW → かご上 ST ターミナル** — 図 **G3**、現地 **EARTH**。
- **是正後**: メガ 60MΩ、**41DG 点灯**、本スロー良好。

### OneNote

- なし。

## 統合した回答・ノウハウ

R1 不良疑い **前** に **かご上 ST 後結線**（Lists progress）。**172**（RDK）とは別。

## 調査・確認手順

1. ゲート SW 配線 **G3 vs EARTH**。
2. D41-420 短絡試験は **配線確認後**。
3. メガ・41DG。

## 未確認事項

- なし。
