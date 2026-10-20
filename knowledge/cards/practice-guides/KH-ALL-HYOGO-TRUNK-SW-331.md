---
knowledge_id: KH-ALL-HYOGO-TRUNK-SW-331
kind: practice_guide
status: draft
card_version: 1
title: "兵庫県条例 — トランク扉スイッチと DKO-TR"
symptoms:
  - "兵庫県条例"
  - "HYOG"
  - "DKO-TR"
  - "トランク扉"
  - "専用運転"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "HYOG と DKO-TR が品目で重複する現場"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "331"
---

# 兵庫県条例 — トランク扉スイッチと DKO-TR

## 使う場面・対象条件

品目で **HYOG（兵庫県条例）** と **DKO-TR（トランク戸開延長）** が両方付くとき、**トランク扉スイッチ** が要否か（Lists 331）。**法令 RAG 対象外**（自治体条例）。

## 症状・現象

- トランク扉 SW と DKO-TR が **重複** しているように見える（Lists）。

## ソース要約

### Lists（331）

- トランク扉 SW → **30 秒戸開延長**（DKO-TR 相当）。
- **HYOG** あり → かご COP に **キースイッチ**、**専用運転**で戸開維持可 → **DKO-TR 機能は実質不要** → **トランク扉 SW 不要**（Lists）。
- 社内整理: **S-1-B120(3)**、**JEAS-A514C**（専用運転方式）— 条例本文はカードに転記しない。

## 統合した回答・ノウハウ

テーマまとめ: [LAW-FREQUENT-THEMES.md §E](../../registry/LAW-FREQUENT-THEMES.md#e-条例都道府県53法令外)

**品目の HYOG/DKO-TR 組合せ** と **JEAS/S 資料** で判断。条例の適用要件は **設計・規格** に確認。

## 調査・確認手順

1. 品目表の HYOG・DKO-TR。
2. S-1-B120 / JEAS-A514C（Lists 331 Notes）。
3. 現地キー **専用運転** の有無。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **331** | 兵庫条例・トランク SW |
| **144** | A/B/C 工事区分（別軸） |

## KB確認に基づく追記

（S-1-B120 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §331 |
| 条例 | **53法令外** — 自治体条例・JEAS（索引のみ） |

## 未確認事項

- 他府県条例の同型仕様。
