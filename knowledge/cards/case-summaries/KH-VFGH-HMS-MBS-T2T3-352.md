---
knowledge_id: KH-VFGH-HMS-MBS-T2T3-352
kind: case_summary
status: draft
card_version: 1
title: "VFGH — HMS/MBS I/F ユニット T2/T3 誤結線"
symptoms:
  - "HMS"
  - "MBS"
  - "T2"
  - "T3"
  - "I/Fユニット"
  - "DOR-120"
model_scope:
  lists_model_label: ["VFGH"]
  machine_room: ["MRL"]
  control_methods: ["VFGH"]
source_refs:
  - ref_type: lists_item
    list_item_id: "352"
  - ref_type: kb_document
    document_number: "C-6-S196.1-J"
    kb_verify_status: pending
---

# VFGH — HMS/MBS I/F ユニット T2/T3 誤結線

## 使う場面・対象条件

**VFGH** で **HMS/MBS** の動作が **期待と逆**・**検知おかしい** — 駆動基板 **エラーなし** で全自動可のとき（Lists 352）。

## 症状・現象

- **Reported symptoms**: 情報管理保留 — 現象詳細は再掲しない。
- **Observed phenomenon**: 配線誤り（Lists）。

## ソース要約

### Lists（352）

- **Notes（要点）**:
  - **MBS と HMS** とも **I/F ユニット** 出荷 — 基板表記 **（T2/T3）** で **誤結線しやすい**。
  - **T2/T3 テレコ** でも **駆動基板エラーなし・全自動可**。
  - **HMS** は扉間隔・戸当たりで **かご上 ST 側無効化** あり — **HMS 本体＋取付腕** で調整。
  - **静止物体非検知**・**検知対象残留** で他対象の検知低下あり。
- **progress**: C-6-S196.1-J 参照確認後、**MBS/HMS I/F の T2/T3 テレコ** を発見して解消。
- **Reported cause**: 情報管理保留。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

エラー無しの **気配り系不調** は **T2/T3** を疑う — [408 気配り HMS](../case-summaries/KH-VFGH-KEIAIN-HMS-DOOR-408.md) と **同系**。

## 調査・確認手順

1. **JP10-0** 等で HMS 無効化の切分（Lists progress）。
2. **I/F ユニット** の **T2/T3** ラベルと実配線。
3. C-6-S196.1-J の **表示灯・検知エリア** 確認（pending）。
4. 扉間隔・戸当たり（Lists Notes）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **352** | **T2/T3 テレコ** |
| [408](../case-summaries/KH-VFGH-KEIAIN-HMS-DOOR-408.md) | 気配り **HMS** |
| [407](../practice-guides/KH-ALL-AIRDOOR-WIRE-PINCH-407.md) | 配線 **挟み** |

## KB確認に基づく追記

（C-6-S196.1-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §352 |
| KB | C-6-S196.1-J（pending） |

## 未確認事項

- 情報管理保留の **symptoms/cause** 詳細。
