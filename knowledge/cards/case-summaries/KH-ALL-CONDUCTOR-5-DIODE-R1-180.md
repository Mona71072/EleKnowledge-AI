---
knowledge_id: KH-ALL-CONDUCTOR-5-DIODE-R1-180
kind: case_summary
status: draft
card_version: 1
title: "コンダクタ #5 ダイオード不良 — P1 消灯・WOS 不能"
symptoms:
  - "コンダクタ"
  - "DYN"
  - "P1"
  - "7SEG"
  - "空回し"
  - "WOS"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "180"
---

# コンダクタ #5 ダイオード不良 — P1 消灯・WOS 不能

## 使う場面・対象条件

**空回し後 WOS** で **UP/DN 不能**、**DYN コンダクタ一瞬励磁→P1 7SEG/LED 消灯**（Lists 180）。

## 症状・現象

- モーター空回し後 **WOS 不動**（Lists）。

## ソース要約

### Lists（180）

- **原因**: **#5 コンダクタ A1–A2 ダイオード（SSC）** 整流特性喪失 — **DYN/M5 は正常**（Lists progress）。
- **対策**: **R1 基板交換**（サージ影響推定）。据付中 **MELD 不使用** 確認 — 一時 **M5 と取替**（Lists）。
- **Notes**: **DYN/#5/M5 先が R1** でも **ダイオード確認せず R1 交換** → 再故障リスク。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[197 SSC/JGS/CR1](./KH-VFGLF-SSC-JGS-CR1-197.md) と同じ **SSC ダイオードモード** 切分 — **180** は **#5 コンダクタ→R1**。

## 調査・確認手順

1. WOS 前 **空回し** 有無。
2. **#5 A1–A2** ダイオードモード（DYN/M5 比較）。
3. **R1** 状態 — ダイオード修復後に交換要否。
4. 据付 **MELD** 運用確認（Lists）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **180** | #5→R1 |
| [197](./KH-VFGLF-SSC-JGS-CR1-197.md) | JGS/CR1 |

## KB確認に基づく追記

（Lists 参考 URL — 本文未転載）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §180 |

## 未確認事項

- 図面 DYN/#5/M5 の正式対応表（KB 未照合）。
