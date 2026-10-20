---
knowledge_id: KH-VFGH-FE-FIRE-RELAY-102
kind: case_summary
status: draft
card_version: 1
title: "FE1S/FE2S 接触不良 — 506 と自動運転不能"
symptoms:
  - "消防リレー"
  - "FE1S"
  - "FE2S"
  - "506"
  - "一次二次消防"
  - "VFGH"
model_scope:
  lists_model_label:
    - "VFGH"
  machine_room:
    - "MR"
  control_methods:
    - "VFGH"
  observed_on:
    - "VFGH"
  may_apply_to:
    - "自動運転不能・506 接点故障"
  excludes: []
  scope_note: "症状欄保留。progress にエラー列挙あり"
source_refs:
  - ref_type: lists_item
    list_item_id: "102"
---

# FE1S/FE2S 接触不良 — 506 と自動運転不能

## 使う場面・対象条件

**VFGH** で **自動運転不能**、群管理/各台エラーに **506（一次・二次消防リレー監視接点故障）** があるとき。

## 症状・現象

- **Reported symptoms**: 情報管理 **保留**
- エラー例: MON E/0 で **302,304,306,308,506**、MON 1/0 で **64E,64F,A41,A51**（Lists）

## ソース要約

### Lists（102）

- **原因**: 制御盤 **FE1S/FE2S リレー接触不良**。
- **対応**: リレー **抜き差し** → 自動運転可（progress）。
- **506** 検出 → FE1S/FE2S 疑い（progress）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

消防系 **506** は **FE1S/FE2S 接触** を Lists 102 どおり先に見る。詳細症状は保留解除まで §102 全文。

## 調査・確認手順

1. 各台/群管理エラー **506** の有無。
2. 関連 **302–308 / 64E,A41 等**（Lists 記載例）。
3. 制御盤 **FE1S/FE2S** 抜き差し・交換。
4. 自動運転復帰確認。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **102** | **FE1S/FE2S** |
| [227](../practice-guides/KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) | 遮煙 **火災管制** 要件 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §102 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- Reported symptoms **保留**。
