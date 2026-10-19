---
knowledge_id: KH-VFGLB-MAINT-MODE-FLICKER-173
kind: case_summary
status: draft
card_version: 1
title: "保守点検モード未解除 — 液晶階床点滅"
symptoms:
  - "メンテモード"
  - "MNT"
  - "フリッカ"
  - "液晶インジ"
  - "VFGLB"
model_scope:
  lists_model_label: ["VFGLB"]
  machine_room: ["MRL"]
  control_methods: ["VFGLB"]
source_refs:
  - ref_type: lists_item
    list_item_id: "173"
---

# 保守点検モード未解除 — 液晶階床点滅

## 使う場面・対象条件

**VFGLB** **正操作盤液晶の階床のみ点滅** — 運転は正常、**CPU/電源リセット无效**（Lists 173）。

## 症状・現象

- **MNT トグル R/M** でも **MNT LED 消えず**（Lists）。
- MON **E/0 エラーなし**（Lists）。

## ソース要約

### Lists（173）

- **原因**: **保守点検機能（メンテモード）解除忘れ** — 遠隔監視立上げ時 **MNT 設定** 推定（Lists）。
- **解除**: ①保守合理化 S/W 書込み ②最下階着床 **独立自動** ③**戸開** ④**戸開+戸閉同時押し**（Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[186 見守り](../practice-guides/KH-VFGLF-REMOTE-WATCH-186.md) — **遠隔監視後作業** は **MIC 作業届**。**173** は **メンテモード UI** 残留。[170 ソフト MNT](../practice-guides/KH-MRL-SOFT-MNT-170.md) で **トグル回避**可。

## 調査・確認手順

1. **MNT LED/トグル** 状態。
2. 遠隔監視 **立上げ履歴**（Lists 推定）。
3. Lists **戸開+戸閉同押し** 解除手順。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **173** | メンテモード |
| [186](../practice-guides/KH-VFGLF-REMOTE-WATCH-186.md) | 見守り通報 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §173 |

## 未確認事項

- 保守合理化 S/W 有無の確認手順（KB 未照合）。
