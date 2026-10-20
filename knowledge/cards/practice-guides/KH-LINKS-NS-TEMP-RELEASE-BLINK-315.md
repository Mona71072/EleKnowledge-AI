---
knowledge_id: KH-LINKS-NS-TEMP-RELEASE-BLINK-315
kind: practice_guide
status: draft
card_version: 1
title: "NS 一時解除 — ボタン点滅（22/2 生産以降）"
symptoms:
  - "NS一時解除"
  - "ボタン点滅"
  - "AXIEZ-LINKs"
  - "S-6-D12"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "22年2月生産以降で点滅しない仕様変更後、客先が点滅希望"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "315"
  - ref_type: kb_document
    document_number: "S-6-D12"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-8-S436"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-8-S451"
    kb_verify_status: pending
---

# NS 一時解除 — ボタン点滅（22/2 生産以降）

## 使う場面・対象条件

**product: AXIEZ-LINKs**（Lists Model **AXIEZ-LINKS**）。**NS 一時解除** 時の **乗場ボタン点滅**（Lists 315）。

## 症状・現象

- **22/2 生産以降**、一時解除時 **点滅しない** 仕様変更（Lists）。
- 客先から **点滅させたい** 依頼。

## ソース要約

### Lists（315）

- C 資料上は **点滅への変更不可** 記載があるが、**客先依頼時は条件付きで変更可能**（Lists）。
- 参照: **S-6-D12**、C-8-S436、C-8-S451（Lists Notes）。

### OneNote

- なし。

## 統合した回答・ノウハウ

仕様変更＝不具合ではない。**客先合意 + S-6-D12 条件** で設計・設定変更の可否を確認（KB pending）。**予約タイマー RSW** は [292](./KH-ALL-RESERVE-TIMER-RSW-292.md)（C-8-S436 共通）。

## 調査・確認手順

1. 生産時期（22/2 以降か）。
2. 客先要件（点滅要否）。
3. **S-6-D12** / C-8 系（pending）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **315** | **NS 点滅** |
| **338** | **背後呼び** CID |

## KB確認に基づく追記

（S-6-D12 / C-8-S436 / C-8-S451 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §315 |
| OneNote | なし |
| KB | S-6-D12、C-8-S436、C-8-S451 |

## 未確認事項

- 条件付き変更の具体手順 — KB 本文未レビュー。
