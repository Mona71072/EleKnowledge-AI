---
knowledge_id: KH-VFGLF-HA-MONITOR-0V-225
kind: case_summary
status: draft
card_version: 1
title: "VFGLF — ヘルスエアモニター出力 0V（降圧トランス疑い）"
symptoms:
  - "ヘルスエア"
  - "モニター出力"
  - "2.375"
  - "0V"
model_scope:
  lists_model_label: ["VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "225"
  - ref_type: kb_document
    document_number: "C-30-H2.1-J"
    kb_verify_status: pending
---

# VFGLF — ヘルスエアモニター出力 0V（降圧トランス疑い）

## 使う場面・対象条件

**モニター出力** 基準 **2.375〜2.770 V** に対し **0 V**（Lists 225）。

## 症状・現象

- **抵抗端子間** 電圧は **あり**（Lists）。

## ソース要約

### Lists（225）

- **cause**: 情報管理 **保留**（降圧トランス不良タイトル）。
- **Notes**: **R1 抵抗** オープン（過電圧）確認 — 添付手順。
- **Materials**: C-30-H2.1-J、YA184A956。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[360 HE R1 オープン](./KH-ALL-HA-MONITOR-R1-OPEN-360.md) は **同系 2 件目** — **225**/**360** 併読。

## 調査・確認手順

1. モニター出力 **2.375〜2.770 V**（Lists）。
2. **R1 抵抗値**（Lists Notes）。
3. C-30-H2.1-J（pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **225** | **0 V** |
| [360](./KH-ALL-HA-MONITOR-R1-OPEN-360.md) | **R1 故障** |
| [207](../practice-guides/KH-ALL-HA-AC-DIP-SW6-207.md) | **HA+AC SW6** |

## KB確認に基づく追記

（C-30-H2.1-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §225 |

## 未確認事項

- cause 本文 — 情報管理保留。
