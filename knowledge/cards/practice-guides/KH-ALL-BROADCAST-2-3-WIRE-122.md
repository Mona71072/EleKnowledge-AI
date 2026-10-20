---
knowledge_id: KH-ALL-BROADCAST-2-3-WIRE-122
kind: practice_guide
status: draft
card_version: 1
title: "一般/非常放送 — 2 線式・3 線式と BGM 操作盤"
symptoms:
  - "2線式"
  - "3線式"
  - "非常放送"
  - "BGM"
  - "アッテネータ"
  - "操作盤"
  - "消防法"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "技評の 2/3 線式と操作盤 SW の関係が不明"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "122"
  - ref_type: law_rag
    law_title: "消防法"
    law_id: "323AC1000000186_20250601_504AC0000000068"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "消防法施行令"
    law_id: "336CO0000000037_20251001_507CO0000000085"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "消防法施行規則"
    law_id: "336M50000008006_20260626_508M60000008081"
    retrieval: "mode=law"
    law_rag_status: current
---

# 一般/非常放送 — 2 線式・3 線式と BGM 操作盤

## 使う場面・対象条件

**放送配線** の **2 線式/3 線式** と **BGM 操作盤内 SW** の関係（Lists 122）— [179](./KH-ALL-BGM-EMERG-WIRING-179.md)（芯数ミス）と併読。

## 症状・現象

- 2/3 線式と **操作盤 SW 有無** の関係が分からない（Lists）

## ソース要約

### Lists（122）

- **2 線式**: 同一信号線で放送。**3 線式**: 信号線別々。
- **消防法（非常放送）**: **音量調整機器（BGM 操作盤 SW＋アッテネータ）を設ける場合は 3 線式**。
- → 非常放送必要で **2 線式** なら **BGM 操作盤内 SW 不可**。三菱はアッテネータ推奨 → 2 線式では **アッテネータ取外し** が必要な場合あり。
- **Notes**: 11 階以上・地下 3 階以上は非常放送設備義務等（消防法施工例）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

テーマまとめ: [LAW-FREQUENT-THEMES.md §C](../../registry/LAW-FREQUENT-THEMES.md#c-消防法放送自火報)

- **2 線**＝同一信号線 / **3 線**＝信号分離。非常放送で **BGM 操作盤 SW＋アッテネータ** なら **3 線必須** — 2 線時は SW 不可（アッテネータ外しが必要な場合あり）。
- 11 階以上・地下 3 階以上は非常放送義務（Lists Notes・施工例）。
- [179](./KH-ALL-BGM-EMERG-WIRING-179.md) = 芯数取違えの別事例。

## 調査・確認手順

1. 非常放送設備の要否（Lists Notes 建物条件）。
2. 2 線式か 3 線式か（設計・機械室配線）。
3. BGM 操作盤 SW / アッテネータの有無と整合。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **122** | **2/3 線式** 定義 |
| [179](./KH-ALL-BGM-EMERG-WIRING-179.md) | **芯数** ミス |
| [363](./KH-VFGLF-BGM-WIRING-363.md) | **ATN 無** BGM |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §122 |
| OneNote | なし |
| 法令 RAG | 消防法・令・規則（frontmatter 3件） |
| KB | 消防法施工例（URL 未承認） |

## 未確認事項

- 現行技評との逐条突合未了。
