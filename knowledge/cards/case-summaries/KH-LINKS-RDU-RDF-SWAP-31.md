---
knowledge_id: KH-LINKS-RDU-RDF-SWAP-31
kind: case_summary
status: draft
card_version: 1
title: "LINKs — RDU/RDF と DRU/DRF 誤結（UP 不入）"
symptoms:
  - "UP信号"
  - "事前チェック"
  - "RDU"
  - "RDF"
  - "WOS"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "31"
---

# LINKs — RDU/RDF と DRU/DRF 誤結（UP 不入）

## 使う場面・対象条件

**AXIEZ-LINKS** **制御盤事前チェック** で **DN のみ・UP 不入**（WOS/ETP）（Lists 31）。

## 症状・現象

- SET1/0=7/1 で **特記エラーなし**（Lists）。
- **420-SSU 導通** — WOS 治具正常（Lists progress）。

## ソース要約

### Lists（31）

- **原因**: **RDU/RDF 短絡コネクタ誤結** — 誤: RDU→**DRU**、RDF→**DRF**（Lists）。
- **正**: RDU/RDF は **R1 基板**、DRU/DRF は **制御盤下部**（Lists Notes）。
- 是正後 UP/DN・安全回路・短絡運転良好（Lists）。

## 統合した回答・ノウハウ

[345 WOS DL/DP](../practice-guides/KH-LINKS-WOS-DLDP-345.md)・[87 RHQ](./KH-LINKS-RHQ-CONNECTOR-87.md) と同系 **短絡コネクタ名取違え** — UP のみ死ぬとき **RDU/RDF↔DRU/DRF** を Lists 上確認。

## 調査・確認手順

1. DN/UP 片側のみ → **UL/USL 短絡コネクタ**（Lists progress 順）。
2. **R1 上 RDU/RDF** vs **盤下 DRU/DRF** 挿入先。
3. WOS **420-SSU** 導通（治具切り分け）。
4. P1/R1 交換前に **結線再確認**（Lists progress）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **31** | RDU/RDF 逆 |
| [87](./KH-LINKS-RHQ-CONNECTOR-87.md) | RHQ 忘れ |
| [345](../practice-guides/KH-LINKS-WOS-DLDP-345.md) | WOS コネクタ |

## KB確認に基づく追記

（KB2AA1001 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §31 |

## 未確認事項

- KB2AA1001 現行版。
