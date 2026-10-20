---
knowledge_id: KH-ESC-SVFC-PHOTO-STANDBY-103
kind: case_summary
status: draft
card_version: 1
title: "SVFC ポスト式光電ずれ — 停止待機に移行しない"
symptoms:
  - "SVFC"
  - "光電センサー"
  - "停止待機"
  - "ポスト式"
  - "エスカレーター"
model_scope:
  lists_model_label: ["SVFC"]
  product_lines: ["escalator"]
  control_methods: ["SVFC"]
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on: ["SVFC"]
  may_apply_to: ["u形/SVFC 自動運転の停止待機確認"]
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "103"
  - ref_type: kb_document
    document_number: "C-60-631-VF30.4-J"
    kb_verify_status: pending
---

# SVFC ポスト式光電ずれ — 停止待機に移行しない

## 使う場面・対象条件

**product: エスカレーター**、**制御 SVFC**。自動運転で **停止待機に入らない**（Lists 103）。エレ door 軸とは無関係。

## 症状・現象

- 所定時間経過しても停止待機なし（Lists）
- progress **情報管理保留**

## ソース要約

### Lists（103）

- **原因**: **上部右ポスト受光センサ光軸ずれ**。
- **対応**: 受光角度調整。
- **資料**: C-60-631-VF30.4-J。

## 統合した回答・ノウハウ

エスカ停止待機不全は **ポスト光電** を先に調整（103）。301（低速待機）と関連得るが **別 list**。

## 調査・確認手順

1. 停止待機条件・時間を C 資料で確認。
2. ポスト式光電 **上下/左右** 光軸。
3. 調整後再試験。

## 関連事例と条件の違い

| ID | テーマ |
| --- | --- |
| **103** | 光電→停止待機 |
| **427** | 周波数→運転不能 |

## KB確認に基づく追記

（VF30.4 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §103 |
| KB | C-60-631-VF30.4-J |

## 未確認事項

- progress 原文保留。
