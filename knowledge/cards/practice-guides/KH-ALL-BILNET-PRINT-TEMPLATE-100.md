---
knowledge_id: KH-ALL-BILNET-PRINT-TEMPLATE-100
kind: practice_guide
status: draft
card_version: 1
title: "BILNET — 雛形の印刷範囲設定"
symptoms:
  - "BILNET"
  - "雛形"
  - "印刷"
  - "不発"
  - "品目表"
model_scope:
  lists_model_label: []
  observed_on: []
  may_apply_to:
    - "BILNET 印刷が1ページに収まらない"
  excludes: []
  scope_note: "Lists Model 空欄 — 事務・帳票横断"
source_refs:
  - ref_type: lists_item
    list_item_id: "100"
---

# BILNET — 雛形の印刷範囲設定

## 使う場面・対象条件

**BILNET** から **不発・帳票** 等を印刷し **1 ページに収まらない** とき（Lists 100）。

## 症状・現象

- 印刷レイアウトはがし（Lists — 豆知識）。

## ソース要約

### Lists（100）

- **C:\BILNET2\PRINT\HINA** — 不発 **UQAL0101**、稲電回答 **UQAL0201**、検査成績 **AKA06101** / 継紙 **AKA06801**・**AKA06901**、品目表 **AAC01001** / 改定 **AAE01001**、手配依頼 **UJBL0701** / 控 **UJBL0G01**（Lists）。
- **C:\BILUSR\PEUSR\HINA** — エスカ安全対策品 **KENSA_S_ANZEN.XLSX**（Lists）。
- **雛形の印刷範囲設定** を変更（Lists cause）。

### OneNote

- なし。

## 統合した回答・ノウハウ

現場エレ故障手順ではない — **378**（METREP 9稲）等の事務フローと併用。

## 調査・確認手順

1. 対象帳票の **HINA ファイル名**（Lists 一覧）。
2. 雛形 **印刷範囲** 設定変更。
3. エスカ帳票は **BILUSR** 側（Lists）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **100** | **BILNET 雛形** |
| **378** | **METREP 9稲** |

## KB確認に基づく追記

（Lists のみ — ローカルパス）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §100 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- BILNET 版によるパス差 — Lists 2022 共有。
