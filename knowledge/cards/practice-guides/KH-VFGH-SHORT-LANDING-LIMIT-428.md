---
knowledge_id: KH-VFGH-SHORT-LANDING-LIMIT-428
kind: practice_guide
status: draft
card_version: 1
title: "短ランバイ — 終端階から UL/DL 手動運転制限"
symptoms:
  - "短ランバイ"
  - "終端階"
  - "手動運転"
  - "HTOP"
  - "4m/min"
  - "VFGH"
model_scope:
  lists_model_label:
    - "VFGH"
  machine_room:
    - "MR"
  control_methods:
    - "VFGH"
  observed_on:
    - "VFGH"
  may_apply_to:
    - "終端階 FL から手動で UL/DL まで行けない"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "428"
  - ref_type: kb_document
    document_number: "C-7-F2900.1-J"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-7-D-C2950"
    kb_verify_status: pending
---

# 短ランバイ — 終端階から UL/DL 手動運転制限

## 使う場面・対象条件

**VFGH**（**machine_room: MR**）。**短ランバイ適用** で **終端階 FL から手動 UL/DL まで運転できない**（Lists 428）。

## 症状・現象

- 終端階から **UL/DL まで手動運転不可**（Lists）。

## ソース要約

### Lists（428）

- **仕様動作**（不具合ではない）。
- **UL/DL まで運転したい場合**: 制御盤 **P1** で手動速 **4 m/min（HTOP＝1）** — **低速機種**は自動 4 m/min のため盤操作不要（Lists）。
- **短ランバイ判定**: **高速**は品目 **599** 記載。**低速**は現地対応なしで記載なし（Lists）。
- 参照: C-7-D-C2950 P33、C-7-F2900 P44、H12 建告 1423（Lists）。

### OneNote

- なし。

## 統合した回答・ノウハウ

**437**（負荷試験 E-stop）/ **428**（**短ランバイ手動制限**）を分ける。

## 調査・確認手順

1. 短ランバイ適用（599 / 高速・低速）。
2. 終端階か。
3. 必要なら **HTOP＝1**（高速）。
4. C-7-F2900 / C2950（pending）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **428** | **短ランバイ手動** |
| **437** | **110% E-stop** |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（C-7-F2900.1-J / C-7-D-C2950 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §428 |
| OneNote | なし |
| KB | C-7-F2900.1-J、C-7-D-C2950 |

## 未確認事項

- HTOP 設定手順の KB 節 — 未レビュー。
