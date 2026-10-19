---
knowledge_id: KH-VFGLB-ARES-SERVICE-STOP-175
kind: case_summary
status: draft
card_version: 1
title: "ARES 戸自閉対策 — 乗場休止で閉じ込め風"
symptoms:
  - "ARES"
  - "戸自閉"
  - "休止"
  - "ドアカット"
  - "VFGLB"
model_scope:
  lists_model_label: ["VFGLB"]
  machine_room: ["MRL"]
  control_methods: ["VFGLB"]
source_refs:
  - ref_type: lists_item
    list_item_id: "175"
---

# ARES 戸自閉対策 — 乗場休止で閉じ込め風

## 使う場面・対象条件

**1 階乗場休止**・**戸閉休止** — **ARES（据付休止・戸自閉対策）** 絡み（Lists 175）。

## 症状・現象

- **運転/休止 SW を運転** でも **休止のまま**（Lists progress）。

## ソース要約

### Lists（175）

- **原因**: **ARES 動作中** に **乗場休止** した（Lists）。
- **ARES 条件**: ①P1 **MON 06** ②P1 **メンテ R/M** ③かご **独立**（Lists）。
- **動作**: 管理外・呼び不可、表示消灯、**ドアカット+戸閉阻止**、戸全閉後 **再カット** 等（Lists Notes）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**ARES 中は乗場休止しない** — 復帰は Lists progress の **スローリセット** 経路。 [173 メンテモード](./KH-VFGLB-MAINT-MODE-FLICKER-173.md) と **MNT/独立** 設定が重なる。

## 調査・確認手順

1. **MON 06**・**メンテ R/M**・**かご独立**（Lists 条件）。
2. **ARES** 動作中か。
3. **乗場休止** 操作タイミング。
4. Lists progress **スローリセット** 復帰。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **175** | ARES+休止 |
| [173](./KH-VFGLB-MAINT-MODE-FLICKER-173.md) | メンテモード |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §175 |

## 未確認事項

- ARES 解除の正規手順（Lists progress のみ）。
