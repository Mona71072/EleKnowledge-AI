---
knowledge_id: KH-MR-SEISMIC-SW-ELEQUICK-157
kind: practice_guide
status: draft
card_version: 1
title: "MR 地震感知器 — 同時リセット SW と ELE-QUICK"
symptoms:
  - "地震感知器"
  - "ELE-QUICK"
  - "低ガル"
  - "高ガル"
  - "非常用"
model_scope:
  lists_model_label: ["MR機種"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "157"
---

# MR 地震感知器 — 同時リセット SW と ELE-QUICK

## 使う場面・対象条件

**MR** **地震感知器 SW** の意味不明、**ELE-QUICK 高ガル解除** 仕様（Lists 157）。

## 症状・現象

- **豆知識**（Lists）。

## ソース要約

### Lists（157）

- **一般**: P 波自動復帰、S 波低/高ガルは **低のみ自動** — **高ガル手動**（Lists）。
- **非常用**: **低ガル後リモートリセット** 要 — **S 波 DIP SW1 ON**（Lists）。
- **ELE-QUICK**: 基本 **低ガル** — **高ガル解除仕様** 時は **MR 高ガル未検知**＋**ピット感知器** 等。**ピット SW「ELE-QUICK」** で **高・低同時リセット**（Lists Notes）。
- **据付**: ピット SW は **通常側**（工場出荷）（Lists Notes）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[168 ELE-QUICK 灯](./KH-ALL-ELEQUICK-LAMP-TEST-168.md)・[138 精密 S 波点検](./KH-MRL-PRECISION-S-WAVE-TEST-138.md)・[155 低ガル解除](../case-summaries/KH-KM-LD-SEISMIC-HARNESS-155.md) — **157** は **SW 意味**。

## 調査・確認手順

1. **常用 vs 非常用**。
2. **ELE-QUICK 高ガル解除** OP 有無。
3. ピット **同時リセット SW** 位置（Lists Notes）。
4. 非常用 **DIP SW1**（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **157** | 感知器 SW |
| [155](../case-summaries/KH-KM-LD-SEISMIC-HARNESS-155.md) | ハーネス誤品 |
| [168](./KH-ALL-ELEQUICK-LAMP-TEST-168.md) | 監視盤灯 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §157 |

## 未確認事項

- VFGH/MRL への SW 表記差（Lists は MR 中心）。
