---
knowledge_id: KH-ALL-MCB-TRIP-CONTACTS-405
kind: practice_guide
status: draft
card_version: 1
title: "MCB ブレーカ — 2 接点標準化（AX / AL）"
symptoms:
  - "MCB"
  - "トリップ接点"
  - "AX"
  - "AL"
  - "2接点"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "トリップ信号線が2接点分あるが現場は1接点仕様"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "405"
---

# MCB ブレーカ — 2 接点標準化（AX / AL）

## 使う場面・対象条件

**全エレ** — **MCB ブレーカのトリップ信号** が **2 接点分** あるが **片側のみ仕様** に見える現場（Lists 405）。

## 症状・現象

- 配線・仕様の **接点数不一致** 疑い（Lists）。

## ソース要約

### Lists（405）

- **従来**: 必要な **AX/AL** を標準外で追加取付していた。
- **現在**: **2 接点用ブレーカーが標準化** — 片側しかない仕様表記でも **2 接点用が適用**（Lists progress）。
- **AX**: レバー ON/OFF 識別。**AL**: トリップ接点（Lists Notes）。
- 設計資料は **未整備**（Lists Notes）。

### OneNote

- なし。

## 統合した回答・ノウハウ

不具合では **品目標準の移行** — **429 M14** 等の MELDEN 系とは別論点。[214 客先 NF 容量](./KH-ALL-CUSTOMER-BREAKER-CAPACITY-214.md) は **上流選定**。

## 調査・確認手順

1. ブレーカー型式・カセット 2 接点か。
2. **AX/AL** 配線目的の確認。
3. 設計資料更新待ち（Lists）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **405** | **MCB 接点標準** |
| [391](./KH-ALL-MCB-THERMAL-CURVE-391.md) | **110%** 時限特性 |
| [293](../case-summaries/KH-ALL-PL-BREAKER-L10A-293.md) | PL・100V 分配器 |
| **429** | **M14 MELDEN** |

## KB確認に基づく追記

（Lists のみ — KB 未指定）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §405 |
| OneNote | なし |
| KB | なし（設計資料整備待ち） |

## 未確認事項

- 標準化後の正式図面 — Lists 注記どおり未整備。
