---
knowledge_id: KH-CM-MA-POLE-CORRECT-ENC-234
kind: case_summary
status: draft
card_version: 1
title: "CM-MA — 空回し磁極補正が止まらない（ENC/GND接触）"
symptoms:
  - "磁極補正"
  - "空回し"
  - "ENC1"
  - "GOV"
model_scope:
  lists_model_label: ["CM-MA"]
source_refs:
  - ref_type: lists_item
    list_item_id: "234"
  - ref_type: kb_document
    document_number: "IN-EL-08-111"
    kb_verify_status: pending
---

# CM-MA — 空回し磁極補正が止まらない（ENC/GND接触）

## 使う場面・対象条件

**空回し** で **磁極補正** が **停止しない**（Lists 234）。

## 症状・現象

- Lists **症状** は情報管理 **保留**。

## ソース要約

### Lists（234）

- **progress**: PT.11A **ENC1** と **GOV** ターミナル・線色確認 → **U,V,W / R0,S0,T0 接地・対地** 確認後 **磁極補正再実施** で解消 — **接触不良** 疑い。
- **Notes / 症状**: 保留。
- **Referenced**: IN-EL-08-111（**最新版** 確認 — Lists Notes）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[53 M1 焼損](./KH-CM-MA-M1-CARD-BURN-53.md)・[46 相順](../case-summaries/KH-ME-CH-PHASE-89M-46.md) — **234** は **巻上端子/GND** 系。

## 調査・確認手順

1. IN-EL-08-111 **最新版**（Lists）。
2. **ENC1 / GOV** ターミナル対応（Lists progress）。
3. **対地電圧** 後 **磁極補正** 再実行。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **234** | **磁極補正** |
| [53](./KH-CM-MA-M1-CARD-BURN-53.md) | **空回し前 M1** |

## KB確認に基づく追記

（IN-EL-08-111 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §234 |

## 未確認事項

- 症状・Notes — 情報管理保留。
