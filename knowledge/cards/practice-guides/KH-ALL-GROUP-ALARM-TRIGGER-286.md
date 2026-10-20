---
knowledge_id: KH-ALL-GROUP-ALARM-TRIGGER-286
kind: practice_guide
status: draft
card_version: 1
title: "群管理異常 — 発報させる方法（2BC / LAN）"
symptoms:
  - "群管理異常"
  - "2C-2BC"
  - "GP1-ELNET"
  - "PD6"
  - "PD8"
model_scope:
  lists_model_label: ["全エレ機種"]
  may_apply_to: ["群管理運転 ΣAI", "2C-2BC"]
source_refs:
  - ref_type: lists_item
    list_item_id: "286"
  - ref_type: lists_item
    list_item_id: "47"
---

# 群管理異常 — 発報させる方法（2BC / LAN）

## 使う場面・対象条件

**群管理以上の異常を意図的に出す** 総点・確認（Lists **286**・**47** 同一内容）。

## 症状・現象

- （テスト手順 — 故障症状ではない）

## ソース要約

### Lists（286 / 47）

- **群管理盤（LAN あり）**: **GP1-ELNET 有線 LAN 抜き** → CPU・群管理 **リセット** → すぐ異常（286）。
- **2C-2BC（LAN なし）**: キーカー制御盤 **PD6・PD8 を外す** → **数分待機** → **群管理異常（＋異常）**（286・47）。

## 統合した回答・ノウハウ

運転異常切り分けと混同しない **試験用** 手順。実機の **2C-2BC 表示** 不具合は [KH-CM-MA-3CAR-GROUP-2C2BC-384](./case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md)・**371 給電** を参照。

## 調査・確認手順

1. 形式: **ΣAI 群管理** vs **2C-2BC**。
2. LAN 系 → **ELNET 抜き＋リセット**（286）。
3. 2BC → **PD6/PD8 外し・待機**（47/286）。
4. 本番異常時は上記と逆に **結線・給電** を確認（384/371）。

## 関連事例と条件の違い

| 参照 | 備考 |
| --- | --- |
| **286 / 47** | 異常 **出す** 方法 |
| [384](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 3car **2C-2BC** |
| [371](../case-summaries/KH-MR-GROUP-PANEL-POWER-371.md) | 群管理盤 **給電抜け** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §286、§47 |

## 未確認事項

- PD6/PD8 の機種別端子表（KB）。
