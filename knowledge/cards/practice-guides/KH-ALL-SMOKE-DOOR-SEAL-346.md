---
knowledge_id: KH-ALL-SMOKE-DOOR-SEAL-346
kind: practice_guide
status: draft
card_version: 1
title: "遮煙ドア認定シール — 大臣認定番号と金/銀"
symptoms:
  - "遮煙ドア"
  - "認定シール"
  - "大臣認定"
  - "CO"
  - "2S"
  - "2CO"
  - "特定防火設備"
model_scope:
  lists_model_label: ["全エレ機種"]
  door_families: []
  door_types: []
  observed_on: []
  may_apply_to:
    - "戸閉方式 CO/2S/2CO 等で認定番号が異なる現場"
  excludes: []
  scope_note: "door_types は戸閉方式表記。LV/KV 品目名とは別に確認"
source_refs:
  - ref_type: lists_item
    list_item_id: "346"
  - ref_type: onenote_page
    onenote_id: "057444fa-309a-4170-bbef-998c0015e5f7:113"
  - ref_type: kb_document
    document_number: "S-31-50.1"
    kb_verify_status: pending
  - ref_type: law_rag
    law_title: "建築基準法"
    law_id: "325AC0000000201_20260527_508AC0000000023"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "建築基準法施行令"
    law_id: "325CO0000000338_20251201_507CO0000000377"
    retrieval: "mode=law"
    law_rag_status: current
  - ref_type: law_rag
    law_title: "建築基準法施行規則"
    law_id: "325M50004000040_20260401_508M60000800022"
    retrieval: "mode=law"
    law_rag_status: current
---

# 遮煙ドア認定シール — 大臣認定番号と金/銀

## 使う場面・対象条件

**遮煙乗場ドア**の **大臣認定番号・シール色**（金/銀）の違いを確認するとき（Lists 346）。**Lists Model=全エレ** — 実際は **戸閉方式・防火区分** で変わる。

## 症状・現象

- 認定番号の違いが周知されていない（Lists）
- 同一番号で金/銀シール混在の疑問

## ソース要約

### Lists（346）

- **番号**: **戸閉方式（CO, 2S, 2CO 等）** + 三方枠/乗場戸仕様で分岐。
- **色**: **特定防火設備＝金** / **防火設備＝銀**。
- **Notes**: 窓付→防火、CAS-1046 (1)/(2) 等。非常用エレ昇降路は **特定防火（窓無）**（129条の13の2）— Lists 豆知識。
- **参照**: 三菱 EL **遮煙乗場ドア S-31-50.1**。

## 統合した回答・ノウハウ

テーマまとめ: [LAW-FREQUENT-THEMES.md §B-1](../../registry/LAW-FREQUENT-THEMES.md#b-1-遮煙ドア大臣認定シール)

**door_types**（CO/2S 等）と **金/銀シール**（特定防火 vs 防火）を **S-31-50.1** で確認。遮煙＋**227**（火災管制・MELD）・**154**（煙感知器義務の整理）も同節参照。LV5K 戸型（432）とは軸が異なる。

## 調査・確認手順

1. 戸閉方式（CO/2S/2CO…）を品目表で確認。
2. 特定防火 vs 防火（窓有無）。
3. S-31-50.1 で大臣認定番号対照。
4. シール色（金/銀）と一致するか目視。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **346** | 大臣認定番号・金/銀シール |
| [227](./KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) | 遮煙時 **火災管制＋MELD** 必須 |
| **154** | シャフト内煙感知器（自火報・警戒区域） |
| [432](./KH-LV5K-LV6K-CLT-432.md) | LV 戸型 CLT（別軸） |

## KB確認に基づく追記

（S-31-50.1 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §346（§227・§154 関連） |
| OneNote | 057444fa…:113 等 |
| 法令 RAG | 建築基準法・令・規則（frontmatter 3件） |
| KB | S-31-50.1 |

## 未確認事項

- 現行 CAS 番号体系の更新（Lists 2024）。
