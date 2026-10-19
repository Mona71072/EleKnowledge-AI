---
knowledge_id: KH-LINKS-ENTRANCE-RELEASE-44
kind: case_summary
status: draft
card_version: 1
title: "LINKs — エントランス解除・パラメータ"
symptoms:
  - "エントランス解除"
  - "NSRE1"
  - "品目599"
  - "乗場呼び"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
  control_methods: ["LINKS"]
source_refs:
  - ref_type: lists_item
    list_item_id: "44"
---

# LINKs — エントランス解除・パラメータ

## 使う場面・対象条件

**AXIEZ-LINKS** **エントランス解除** が **品目599 未指定で結線不明**／**解除操作しても乗場呼び自動登録しない**（Lists 44）。

## 症状・現象

- NSRE1＋420/210 短絡試験でも **乗場呼び自動登録せず**（Lists progress）。

## ソース要約

### Lists（44）

- **原因**: **エントランス解除パラメータ未設定** → **S/W 書換**；解除接点 **48V 設計** → **添付参考の現地改造**（Lists）。
- 品目 **599 YA317C610** 参照（Lists）。
- 不発 **ASHO29309**（Lists）。

## 統合した回答・ノウハウ

24V 外部機器と **48V 設計** のミスマッチ — Lists 上は **S/W＋改造**。**NS 一時解除** [KH-LINKS-NS-TEMP-RELEASE-BLINK-315](./practice-guides/KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) 等とは別系。

## 調査・確認手順

1. 品目 **599** 結線図（KB pending）。
2. **パラメータ**（S/W 書換前後）。
3. 接点 **電圧等级**（48V vs 24V）。
4. NSRE1・420/210 試験結果（Lists progress）。

## 関連事例と条件の違い

| テーマ | 備考 |
| --- | --- |
| **44** | エントランス解除 |
| [315](../practice-guides/KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) | NS 一時解除点滅 |
| [110](./KH-VFGLB-TOUCHLESS-PHANTOM-CALL-110.md) | タッチレス誤呼び |

## KB確認に基づく追記

（YA317C610 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §44 |

## 未確認事項

- 添付改造図・ASHO29309 本文。
