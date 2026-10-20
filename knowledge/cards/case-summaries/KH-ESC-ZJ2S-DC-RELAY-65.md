---
knowledge_id: KH-ESC-ZJ2S-DC-RELAY-65
kind: case_summary
status: draft
card_version: 1
title: "ZJ2S DC1/DC2 リレー嵌合不良 — E.0.0"
symptoms:
  - "ZJ2S"
  - "DC1"
  - "DC2"
  - "E.0.0"
  - "安全回路"
  - "エスカレーター"
model_scope:
  lists_model_label: ["ZJ2S"]
  product_lines: ["escalator"]
  model_abbreviations: ["ZJ2S"]
  observed_on: ["ZJ2S"]
  may_apply_to: ["監視盤結線後に突然運転不能"]
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "65"
---

# ZJ2S DC1/DC2 リレー嵌合不良 — E.0.0

## 使う場面・対象条件

**エスカ ZJ2S**。**E.0.0**、安全回路遮断、**DC1/DC2 リレー** 疑い（Lists 65）。前日まで運転可・監視盤作業後停止。

## 症状・現象

- E.0.0 のみ、安全 SW A 接点情報なし（Lists）
- ドット2点灯（添付参照・未同梱）

## ソース要約

### Lists（65）

- **原因**: **DC1/DC2 リレーが完全嵌合せず**（DC1 外れかかり）。
- **対応**: DC1 正しく取付 → 運転可。
- **切り分け**: ターミナル 24V、YS139B214 安全回路、投入時リレー動作目視。

## 統合した回答・ノウハウ

ZJ2S E.0.0 は **DC1/DC2 物理嵌合** を先（65）。427 周波数系とエラーコードで分岐。

## 調査・確認手順

1. E.0.0 表示確認。
2. 安全回路 24V（Lists）。
3. 電源投入時 **DC1/DC2** の入り。
4. リレー再嵌合・YS139B214 参照。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **65** | DC リレー |
| **136** | ZJ2 溶接 |

## KB確認に基づく追記

（YS139B214 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §65 |
| KB | YS139B214（Lists 添付名） |

## 未確認事項

- 添付詳細未同梱。
