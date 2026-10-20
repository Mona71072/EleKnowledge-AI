---
knowledge_id: KH-LINKS-BK-SW-SETTING-81
kind: case_summary
status: draft
card_version: 1
title: "LINKs — ブレーキスイッチ設定不良で運転不能"
symptoms:
  - "BK"
  - "ブレーキスイッチ"
  - "運転不能"
  - "乗場インジ"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "81"
---

# LINKs — ブレーキスイッチ設定不良で運転不能

## 使う場面・対象条件

**AXIEZ-LINKS** 据付中 **1階でスロー・自動とも運転不可**、**エラーなし・乗場インジ BK 点滅**（Lists 81）。

## 症状・現象

- 電源リセット无效（Lists）。
- 乗場インジ **「BK」点滅**（Lists）。

## ソース要約

### Lists（81）

- **原因**: **BK2 側ブレーキスイッチ設定不良** — ストッパーボルトマーキングずれなし、**C 資料確認方法** で設定不良→調整で解消。
- **progress**: BK 回路・コネクタ・QB1 QP9 電圧・他現場 QB1 交換・**BK2 取り込みなし** まで（Lists）。

## 統合した回答・ノウハウ

エラー無し BK 表示は **スイッチ設定** を C 手順で確認。**82** は **QB1 復帰逆接** — 切り分け注意。

## 調査・確認手順

1. 乗場インジ **BK** 表示。
2. 巻上・制御盤 **BK コネクタ・導通**（Lists progress）。
3. **C 資料** ブレーキスイッチ設定確認・調整。
4. QB1 交換後も残る場合 **82** 参照。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **81** | **設定** |
| **82** | **QB1 逆接** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（C 資料 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §81 |

## 未確認事項

- 参照 C 条文の現行版。
