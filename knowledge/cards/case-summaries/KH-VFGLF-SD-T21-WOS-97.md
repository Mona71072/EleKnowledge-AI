---
knowledge_id: KH-VFGLF-SD-T21-WOS-97
kind: case_summary
status: draft
card_version: 1
title: "WOS 時 SD-T21 #5 コンタクタ動作不良（M5 交換）"
symptoms:
  - "SD-T21"
  - "WOS"
  - "#5"
  - "M5"
  - "VFGLF"
  - "UP"
  - "DN"
  - "29"
  - "PWFH"
  - "432"
  - "452"
model_scope:
  lists_model_label:
    - "VFGLF"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  model_abbreviations: []
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "WOS 運転時 #5 コンタクタ系"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "97"
    source_id: evidence-list-sd-t21-wos-id97
---

# WOS 時 SD-T21 #5 コンタクタ動作不良（M5 交換）

## 使う場面・対象条件

**VFGLF / LINKs** の **WOS 運転** で UP/DN 釦を押しても走行しない、または **走行開始が遅い**。Lists 97。関連: [KH-VFGLF-SD-T21-CONTACTOR-96](./KH-VFGLF-SD-T21-CONTACTOR-96.md)（48V 不吸引）。

## 症状・現象

- WOS 時 UP/DN 不動または反応遅延
- P1 7SEG3: PWFH・**29** 常時点灯、UP/DN 信号取込あり（Lists）
- **432/452 は確認されなかった**（Lists）
- WOS ポータブル時 #5 接点部が僅かに動く程度

## ソース要約

### Lists（list_item_id 97）

- **対応**: **M5 コンタクタと入替** → 動作良好。#5 不良疑い、返却品製造元確認中。
- **progress**: ①#5 T1-L1 等接触抵抗 0Ω ②UP/DN 押下時 A1/A2 対地 **48V** ③**M5 入替** → 良好。
- 参照 ASHO29423。

### OneNote

- タイトル一致页なし。

## 統合した回答・ノウハウ

WOS 時の #5 系は Lists 97 では **48V・主回路抵抗正常でも M5 入替で改善**。**96（不吸引）** と併読し、#5↔M5 暫定の **MELD 不可**（96 注意）を踏まえる。432/452 が出ないケースあり。

## 調査・確認手順

1. WOS 限定か通常運転もか記録。
2. 7SEG3 PWFH/29 と UP/DN 取込（Lists 記載）。
3. #5 接触抵抗・A1/A2 48V（progress ①②）。
4. M5 入替試験（Lists ③）— MELD 影響は 96 カード参照。
5. 432/452 有無は断定材料にしない（Lists 97）。

## 関連事例と条件の違い

| list | 条件 | 結果 |
| --- | --- | --- |
| **97** | WOS・48V あり | M5 交換 |
| **96** | 48V あるが不吸引 | #5↔M5 暫定 |
| **95** | SD-T12 BK 不引 | 接触抵抗 |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §97 |
| OneNote | なし |
| KB | ASHO29423 — 未突合 |

## 未確認事項

- #5 返却品調査結果。
- 96/97 共通根本原因。
