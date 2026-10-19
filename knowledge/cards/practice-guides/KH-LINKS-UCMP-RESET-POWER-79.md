---
knowledge_id: KH-LINKS-UCMP-RESET-POWER-79
kind: practice_guide
status: draft
card_version: 1
title: "独立 UCMP — 電源入切り時の故障検出"
symptoms:
  - "614"
  - "UCMP"
  - "独立UCMP-CPU"
  - "NRS"
  - "電源リセット"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
  control_methods: ["LINKS"]
source_refs:
  - ref_type: lists_item
    list_item_id: "79"
---

# 独立 UCMP — 電源入切り時の故障検出

## 使う場面・対象条件

**AXIEZ-LINKS** **独立自動** で **乗場 MP スイッチ電源リセット** 後 **614／独立 UCMP-CPU 故障・NRS**（Lists 79）。

## 症状・現象

- 独立自動で電源リセット → **独立 UCMP-CPU 故障**（Lists）。

## ソース要約

### Lists（79）

- **指示**: 乗場 MP で電源リセットする場合は **必ず手動**（Lists）。
- **原理**: LO または戸開リレベル後、**一度も GS ON せず電源喪失** → 独立 UCMP-CPU 故障（最上階多いが階固定なし）。
- **全自動**: ELD 投入時 MELD で GS ON → 通常検出しない。**独立自動** は戸開のまま MELD 切替 → 故障検出。
- **Notes**: 個別不具合扱いせず **C 資料注記** 方向。ETP **ED モード** では UCMP エラー **リセットしない**（60 番不入でも UCMP 条件不成立）。

## 統合した回答・ノウハウ

**電源リセットは手動** が Lists 上の必須運用。614 は **操作手順** より **状態遷移** を先に確認。**VFGLF P1 即断** は [204](../practice-guides/KH-VFGLF-CPU-RESET-HAND-204.md)。

## 調査・確認手順

1. リセット前 **自動／手動**・**LO/リレベル** 有無。
2. **614** 表示確認。
3. **手動** での MP リセット再実施可否。
4. ED モード利用有無（Lists Notes）。

## 関連事例と条件の違い

| テーマ | 備考 |
| --- | --- |
| **79** | UCMP＋電源入切 |
| **81/82** | ブレーキ系運転不能 |

## KB確認に基づく追記

（C 資料注記 — KB 未突合）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §79 |

## 未確認事項

- 現行 C 資料への注記掲載状況。
