---
knowledge_id: KH-VFGLF-MELD-RHY-CONNECTOR-132
kind: case_summary
status: draft
card_version: 1
title: "RHY コネクタ未挿 — 64D と MELD 実動作しない"
symptoms:
  - "RHY"
  - "MELD"
  - "64D"
  - "MELDEN"
  - "VFGLF"
  - "停電"
model_scope:
  lists_model_label: ["VFGLF"]
  product_lines: ["AXIEZ-LINKs"]
  control_methods: ["VFGLF"]
  machine_room: ["MRL"]
  door_families: []
  door_types: []
  observed_on: ["VFGLF"]
  may_apply_to: ["着床後かごドア開で 64D、停電時 MELD 不動"]
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "132"
  - ref_type: onenote_page
    onenote_id: "61fae6e2-29db-44a5-8172-67b612b50316:1"
  - ref_type: kb_document
    document_number: "YE317C142"
    kb_verify_status: pending
---

# RHY コネクタ未挿 — 64D と MELD 実動作しない

## 使う場面・対象条件

**制御 VFGLF**。**64D**（MON 2桁表示設定時）、**着床後かごドア開** で再表示。**Lists 重要度: 重要**。

据付中 **MELD 試験モード** では動くが **実停電で MELD しない** 隠れ不具合（Lists Notes）。

## 症状・現象

- 64D 安全回路リセット指令
- 走行中は消える、かごドア開で再発
- 乗場ドアのみ開では出ない（Lists）

## ソース要約

### Lists（132）

- **原因**: **RHY コネクタ未挿** — MELDEN 回路遮断 → 64D 検知。
- **気付きにくい理由**: 通常走行可、MELD 試験モード可、**実停電のみ MELD 失效**。
- **対応**: 制御盤 RHY 挿入。
- **参照**: YE317C142、MELDEN 機能資料。

## 統合した回答・ノウハウ

VFGLF の 64D + MELD 疑いは **RHY** を据付ノート事前確認に加え **実停電試験**（132 Notes）。

## 調査・確認手順

1. 3桁/64D 表示条件の確認（Lists progress）。
2. 制御盤 **RHY** 嵌合。
3. MELD 試験 vs **客先ブレーカ遮断** の差を試験。
4. YE317C142 配線確認。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **132** | RHY 未挿 |
| [167](./KH-MR-MELD-CP-LIVE-WORK-167.md) | MELD 配線・**活線** |
| [227](../practice-guides/KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) | 遮煙時 MELD 必須（法令） |
| [174](./KH-VFGLB-MELD-BATTERY-174.md) | バッテリー **低電圧** |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §132 |
| OneNote | `61fae6e2-29db-44a5-8172-67b612b50316:1` |
| KB | YE317C142 |

## 未確認事項

- なし（Lists 原因明記）。
