---
knowledge_id: KH-VFGLB-SETS-64C-MON1-418
kind: practice_guide
status: draft
card_version: 1
title: "VFGLB — SETS 適用時 MON 64C（カゴ上確認の罠）"
symptoms:
  - "64C"
  - "SETS"
  - "バッファ速制限"
  - "MON1/0"
  - "リモコン71"
model_scope:
  lists_model_label: ["VFGLB"]
  machine_room: ["MRL"]
  control_methods: ["VFGLB"]
source_refs:
  - ref_type: lists_item
    list_item_id: "418"
---

# VFGLB — SETS 適用時 MON 64C（カゴ上確認の罠）

## 使う場面・対象条件

**官検後** **カゴ上** で **MON1/0=1/0** を見ると **64C（SETS バッファ速制限）** が出て **リセットしても消えない**（Lists 418）。

## 症状・現象

- **64C** ラッチ seemingly（Lists 症状）。

## ソース要約

### Lists（418）

- **64C 検出タイミング**: **ETS 書込前**、**#29 遮断復帰直後**、**スロー投入後 SETS ステータス未確認** 等 — **SETS 盤** で **カゴ上搭乗（スロー投入）確認** すると **必ず 64C 表示**。
- **正しい確認**: **かご中** でリモコン **「71」** を使用。
- **復帰条件**: **高速運転で終端走行**し位置 SW 等を動かし **問題なし** をシステムに認識させる。
- **Notes**: SETS 概要 — 60/105 m/min 範囲で緩衝器設置等。**スーパー可変速外** でも **速度変化なしでエラーのみ** の物件あり。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**436 664/665** は **定期検査未実施**。[358 62D](../case-summaries/KH-MRL-SETS-DN1-BREAK-358.md) は **DN 断線** — **418 64C** は **MON 確認タイミングの仕様表示**。[419 戸短](./KH-VFGLB-DOOR-SHORT-RELEASE-419.md) も **官検後の確認手順** 系。

## 調査・確認手順

1. **SETS 適用** の有無。
2. 確認場所が **カゴ上 MON** か **かご中 71** か。
3. 本当に要復帰なら **終端高速走行**（Lists 復帰条件）。
4. **664/665** と **64C** を混同しない。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **418** | **64C 表示タイミング** |
| [436](./KH-MRL-SETS-664-665-436.md) | **664/665** 11 か月 |
| [358](../case-summaries/KH-MRL-SETS-DN1-BREAK-358.md) | **62D** DN 断線 |
| [419](./KH-VFGLB-DOOR-SHORT-RELEASE-419.md) | 戸短 **解除** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §418 |

## 未確認事項

- リモコン **71** の詳細は VFGLB 保守資料で確認。
