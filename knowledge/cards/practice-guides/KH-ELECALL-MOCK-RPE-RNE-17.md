---
knowledge_id: KH-ELECALL-MOCK-RPE-RNE-17
kind: practice_guide
status: draft
card_version: 1
title: "エレコール — 模擬試験と RPE/RNE テレコ"
symptoms:
  - "模擬試験"
  - "RSW3"
  - "RPE"
  - "RNE"
  - "7SEG"
model_scope:
  lists_model_label: ["エレコール"]
source_refs:
  - ref_type: lists_item
    list_item_id: "17"
  - ref_type: kb_document
    document_number: "C-7-C3300.1700"
    kb_verify_status: pending
---

# エレコール — 模擬試験と RPE/RNE テレコ

## 使う場面・対象条件

**模擬照合で 7SEG「1」** だが **エレコール未動作**（Lists 17）。

## 症状・現象

- RSW3=C 模擬、**盤は反応・エレコール不動**（Lists）。

## ソース要約

### Lists（17）

- **原因**: 管理盤ツナギ **RPE/RNE テレコ** — 振替で模擬 OK（Lists）。
- **Notes**: テレコでも **エラー不出** → **物理結線・SW 忘れ** 優先（Lists）。

## 統合した回答・ノウハウ

HA 論点 [26](./case-summaries/KH-ELECALL-HA-SECOM-26.md) の前に **伝送線テレコ** を Lists 順で潰す。

## 調査・確認手順

1. エレコール盤・制御盤 **エラー**。
2. ゲート/棟番 **照合条件**（Lists progress）。
3. SCU **メモリ**（Lists progress）。
4. **RPE/RNE** 導通（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **17** | RPE/RNE |
| [26](../case-summaries/KH-ELECALL-HA-SECOM-26.md) | HA パラメータ |
| [130](./KH-ELECALL-PUTTY-INSTALL-130.md) | 接続ツール |

## KB確認に基づく追記

（C-7-C3300.1700 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §17 |
| KB | C-7-C3300.1700（pending） |

## 未確認事項

- ツナギ箱線色の現行図。
