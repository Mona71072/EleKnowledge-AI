---
knowledge_id: KH-MRL-ISO-TRANS-CST-HST-260
kind: practice_guide
status: draft
card_version: 1
title: "絶縁トランス — CST/HST 停止時電圧上振れ"
symptoms:
  - "CST"
  - "HST"
  - "絶縁トランス"
model_scope:
  lists_model_label: ["MRL機種"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "260"
---

# 絶縁トランス — CST/HST 停止時電圧上振れ

## 使う場面・対象条件

**電源相間 OK** だが **CST/HST が 200 V+5% 超**（例 **214 V**）（Lists 260）。

## 症状・現象

- **停止中・負荷小** で顕在化（Lists）。

## ソース要約

### Lists（260）

- **絶縁トランス** 経由で HST/CST 分岐 — **無負荷時変動率約 5% 上振れ**（Lists）。
- **静観 OK**（制開回答）（Lists）。
- **タップ調整不可**（Lists progress）。

## 統合した回答・ノウハウ

[306 NL 差動](../practice-guides/KH-MR-NL-DIFF-TRANS-ESTOP-306.md)・[54 PWFH](../case-summaries/KH-KM-LD-PWFH-PHASE-54.md) は **別トランス** — 本件は **CST/HST 絶縁**。

## 調査・確認手順

1. **電源相間** vs **CST/HST**。
2. **負荷状態**（停止/運転）。
3. 上振れが **変動率範囲** か（Lists）。
4. 記載基準なし部分は **静観判断**（Lists progress）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **260** | CST/HST |
| [397](../case-summaries/KH-VFGLF-M1-AC-SAG-397.md) | M1 電圧 |

## KB確認に基づく追記

（技評記載なし — Lists）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §260 |

## 未確認事項

- 乗場/カゴ電圧の正式規格文書。
