---
knowledge_id: KH-ALL-PL-BREAKER-L10A-293
kind: case_summary
status: draft
card_version: 1
title: "制御盤 PL — L10A 分配器未結線地絡"
symptoms:
  - "PL"
  - "L10A"
  - "L20A"
  - "分配器"
  - "乗場モニター"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "293"
---

# 制御盤 PL — L10A 分配器未結線地絡

## 使う場面・対象条件

**高速調整** で **PL** ブレーカ **投入直後トリップ** — **SCB は可**（Lists 293）。

## 症状・現象

- **PL 二次側** 原因疑い（Lists）。
- **T76（L10A）～分配器** 抜くと PL 投入可（Lists progress）。

## ソース要約

### Lists（293）

- **分配器内 L10A/L20A（100V）未結線** → **蓋接触地絡**（Lists）。
- UGG 勘合 OK、ピット/昇降路照明・100V ブザー無、**乗場モニター有**（Lists）。

## 統合した回答・ノウハウ

[405 MCB](../practice-guides/KH-ALL-MCB-TRIP-CONTACTS-405.md) は **AX/AL 接点** — 本件は **100V 分配器結線漏れ**。

## 調査・確認手順

1. **PL vs SCB** の切り分け。
2. **L10A 系** 仕様・配線ミス。
3. **分配器内 L10A/L20A** 端子。
4. 適用機器（乗場モニター等）（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **293** | PL・100V |
| [405](../practice-guides/KH-ALL-MCB-TRIP-CONTACTS-405.md) | MCB 接点 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §293 |

## 未確認事項

- 分配器型式別の結線図。
