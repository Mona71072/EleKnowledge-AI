---
knowledge_id: KH-VFGLF-SSC-JGS-CR1-197
kind: case_summary
status: draft
card_version: 1
title: "SSC 不良 — JGS 経由で CR1 トリップ"
symptoms:
  - "SSC"
  - "CR1"
  - "JGS"
  - "DSPW"
  - "420"
  - "本スロー"
model_scope:
  lists_model_label: ["VFGLB・VFGLF"]
  machine_room: ["MRL"]
  control_methods: ["VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "197"
  - ref_type: kb_document
    document_number: "YE312C847"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "YE315C379"
    kb_verify_status: pending
---

# SSC 不良 — JGS 経由で CR1 トリップ

## 使う場面・対象条件

**VFGLB/VFGLF** **本スロー後 CR1 トリップ**、**制御ライン絶縁 0Ω**（Lists 197・↓低）。

## 症状・現象

- **CR1 トリップ**（Lists）。

## ソース要約

### Lists（197）

- **切分**: **420 不良** 疑い → **JGS 抜き** で CR1 止まる → **DSPW リレー SSC 不良**（Lists）。
- **SSC 確認**: ダイオードモード **OL**（Lists Notes 要旨）。
- **対策**: **SSC 交換**（Lists progress）。
- YE312C847 / YE315C379（Lists — pending）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[226 R03/420](../case-summaries/KH-VFGLF-R03-PIT-WIRE-226.md) は **幹線損傷** — **197** は **SSC 部品**。[180 #5→R1](./KH-ALL-CONDUCTOR-5-DIODE-R1-180.md) も **SSC/R1**。Lists Notes の **ダイオードテスタ手順** は索引のみ。

## 調査・確認手順

1. 本スロー後 **CR1**。
2. **絶縁抵抗 0Ω** ライン切分。
3. **JGS** 抜き CR1。
4. **DSPW SSC** ダイオードモード（Lists Notes）。
5. 図 YE312C847 / YE315C379（pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **197** | SSC・JGS |
| [226](./KH-VFGLF-R03-PIT-WIRE-226.md) | R03 420 |

## KB確認に基づく追記

（YE312C847 / YE315C379 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §197 |
| KB | YE312C847 / YE315C379（pending） |

## 未確認事項

- VFGLB 限定部品か（Lists Model 両方）。
