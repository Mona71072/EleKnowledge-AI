---
knowledge_id: KH-ALL-CUSTOMER-BREAKER-CAPACITY-214
kind: practice_guide
status: draft
card_version: 1
title: "客先ブレーカ — 1 回線化と容量大小"
symptoms:
  - "客先ブレーカ"
  - "MCB"
  - "NF"
  - "品目表"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "214"
---

# 客先ブレーカ — 1 回線化と容量大小

## 使う場面・対象条件

**動力・照明** の **客先 NF とエレ MCB** 選定・周知（Lists 214・↓低）。

## 症状・現象

- 豆知識・技評周知（Lists）。

## ソース要約

### Lists（214）

- **①** 客先 NF とエレ MCB を **1 台 1 回線** に — エレ MCB 交換時 **他設備停電** を避ける（Lists）。
- **②** **客先 NF 容量 ＞ エレ MCB** — 同格だと **客先 NF 先トリップ** で **復旧・救出遅れ** の恐れ（Lists）。
- **同容量引渡** は **客先了承**＋**客先 NF 位置** を現主経由伺い（Lists Notes）。
- 品目例: **NV 20A**（動力）、**BL-2C 30A**（照明）（Lists Notes）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[405 MCB 2 接点](./KH-ALL-MCB-TRIP-CONTACTS-405.md) は **トリップ信号配線** — **214** は **客先側容量・回線分割**。[80 CCP](../case-summaries/KH-KM-LD-CCP-REGEN-80.md) 等 **盤内ブレーカ** とは別レイヤ。

## 調査・確認手順

1. 品目表・据付図 **工事区分表**・内線規程（Lists Notes）。
2. 客先 NF とエレ MCB **回線構成**。
3. 容量 **大小関係** — 例外時は了承・伺い（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **214** | 客先 NF 容量 |
| [405](./KH-ALL-MCB-TRIP-CONTACTS-405.md) | MCB 接点標準 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §214 |

## 未確認事項

- 機種別品目表の最新 rev。
