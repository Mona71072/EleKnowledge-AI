---
knowledge_id: KH-MR-IMV-LV1-RESET-357
kind: case_summary
status: draft
card_version: 1
title: "MR — IMV 長周期振動感知 Lv1 リセット結線訂正"
symptoms:
  - "ASHO50160"
  - "IMV"
  - "Lv1"
  - "RSBA"
  - "TB1"
model_scope:
  lists_model_label: ["MR機種"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "357"
---

# MR — IMV 長周期振動感知 Lv1 リセット結線訂正

## 使う場面・対象条件

**長周期 Lv1** が **自動復帰しない** — **48 V 印加箇所** 疑い（Lists 357）。

## 症状・現象

- Lv0 は復帰、**Lv1 保持**（Lists 症状）。

## ソース要約

### Lists（357）

- **原因**: **標準図ミス** — **RSBA（+48 V）** は **TB1-2** 想定が **TB1-6 指示**。**リセットコイルはマイナスコモン**。
- **稲電**: **テレコ部分繋ぎ替え** で **静観可**（Lists Notes）。
- 結線訂正指示 **添付**（スナップショット本文なし）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[157 地震 SW](./KH-MR-SEISMIC-SW-ELEQUICK-157.md)・[155 低ガル](../case-summaries/KH-KM-LD-SEISMIC-HARNESS-155.md) と **地震系** — **357** は **IMV 長周期**。

## 調査・確認手順

1. **Lv0/Lv1** 復帰試験記録。
2. **TB1-2～TB1-6** RSBA/RBSA 配線 vs **訂正図**。
3. **一括リセット** ライン（Lists 症状）。
4. 稲電 **静観** 見解確認。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **357** | **IMV Lv1** |
| [157](../practice-guides/KH-MR-SEISMIC-SW-ELEQUICK-157.md) | **同時リセット SW** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §357 |

## 未確認事項

- 訂正指示添付の最新版。
