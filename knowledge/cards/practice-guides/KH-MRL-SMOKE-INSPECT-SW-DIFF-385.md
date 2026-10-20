---
knowledge_id: KH-MRL-SMOKE-INSPECT-SW-DIFF-385
kind: practice_guide
status: draft
card_version: 1
title: "VFGLB vs VFGLF — 煙感知器点検口 SW 動作差"
symptoms:
  - "煙感知器"
  - "点検口"
  - "29"
  - "41DG"
model_scope:
  lists_model_label: ["MRL機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "385"
---

# VFGLB vs VFGLF — 煙感知器点検口 SW 動作差

## 使う場面・対象条件

**点検口 SW** ライン変更 — **VFGLB（新 AXIEZ）** と **VFGLF（LINKs）** で **挙動が異なる**（Lists 385）。

## 症状・現象

- **豆知識**（Lists）。

## ソース要約

### Lists（385）

- **VFGLB**: 点検口 OFF → **安全回路 29 遮断** — **自閉・運転不可**。
- **VFGLF**: 点検口 OFF → **乗場扉開判定（41DG）** — **戸閉は可** だが **動かない** 現象。
- **復帰 VFGLB**: 7SEG **29**、盤 **73〜77 短絡**。
- **確認 VFGLF**: **戸短** or **41DG 点灯**、**D41B〜SMD 短絡**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[150 煙感 SW 取付](./KH-ALL-SMOKE-SW-MOUNT-150.md)・[270 点検口施錠](./KH-ALL-INSPECTION-LOCK-TYPES-270.md) と **制御方式** を合わせて読む。

## 調査・確認手順

1. 機種 **VFGLB / VFGLF** 特定。
2. 点検口 **物理開閉** 確認。
3. Lists Notes の **29 / 41DG** 手順。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **385** | **点検口差** |
| [150](../practice-guides/KH-ALL-SMOKE-SW-MOUNT-150.md) | **取付** |
| [270](./KH-ALL-INSPECTION-LOCK-TYPES-270.md) | **施錠** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §385 |

## 未確認事項

- なし。
