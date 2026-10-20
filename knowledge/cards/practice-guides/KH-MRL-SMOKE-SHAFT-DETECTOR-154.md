---
knowledge_id: KH-MRL-SMOKE-SHAFT-DETECTOR-154
kind: practice_guide
status: draft
card_version: 1
title: "遮煙現場 — 昇降路内煙感知器の要否"
symptoms:
  - "遮煙"
  - "煙感知器"
  - "シャフト"
  - "竪穴"
  - "警戒区域"
  - "自火報"
model_scope:
  lists_model_label:
    - "MRL機種"
  machine_room:
    - "MRL"
  observed_on: []
  may_apply_to:
    - "全階遮煙・竪穴防火区画現場"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "154"
  - ref_type: law_rag
    law_title: "建築基準法"
    law_id: "325AC0000000201_20260527_508AC0000000023"
    retrieval: "mode=law"
    law_rag_status: current
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

# 遮煙現場 — 昇降路内煙感知器の要否

## 使う場面・対象条件

**遮煙乗場ドア** 現場で、技評・据付要領と **昇降路内の煙感知器** の有無が食い違うとき（Lists 154）。Lists **Model=MRL機種** — 遮煙・竪穴区画は機種横断の話が多い。

## 症状・現象

- 遮煙適用なのに **シャフト内に煙感知器が無い**（Lists）。
- 据付要領の「遮煙階ロビーに感知器」と **昇降路設置** を混同。

## ソース要約

### Lists（154）

- 据付要領「遮煙ドア採用階ロビーに火災/煙感知器」→ **火災管制運転** 用（着床前乗場火災対策。認定の **20 秒閉鎖** 条件）。
- **全階遮煙＋竪穴防火区画** でも、**建築条文で「昇降路に必ず1台」** ではない（Lists）。
- **自火報（消防法）** 対象建物 → **警戒区域** ごとに感知器。**竪穴は縦方向の別区域** — 消防法上 **1 種煙感知器**（火災感知器不可）。
- **自火報義務が無い** → 昇降路への遮煙用煙感知器 **設置義務なし**（Lists 整理）。
- **大臣認定書** に「昇降路に煙感知器」とは **書いていない**（Lists Notes）。

## 統合した回答・ノウハウ

テーマまとめ: [LAW-FREQUENT-THEMES.md §B-1](../../registry/LAW-FREQUENT-THEMES.md#b-1-遮煙ドア大臣認定シール)

**ロビー感知器（火災管制）** と **自火報の竪穴区域** と **認定書** は別レイヤ。技評だけ見てシャフト内必須と決め打ちしない。

## 調査・確認手順

1. 遮煙認定・全階遮煙か（**346** / **227**）。
2. 建物の **自火報** 要否・警戒区域図。
3. 据付要領 4 項（火災管制）の意図か、消防設備かを切り分け。
4. 必要なら消防設計・ **154** Notes の URL 資料（未承認リンクは Lists 参照のみ）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **154** | シャフト内煙感知器 |
| [227](./KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) | 火災管制＋MELD |
| [KH-SMOKE-DOOR-MELD-227](./KH-SMOKE-DOOR-MELD-227.md) | 同一 §227 — **BBUK/123** |
| [346](./KH-ALL-SMOKE-DOOR-SEAL-346.md) | 大臣認定シール |

## KB確認に基づく追記

（該当 KB なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §154 |
| 法令 RAG | 建築基準法、消防法・令・規則（frontmatter） |

## 未確認事項

- 個別建築確認・消防同意の例外。
