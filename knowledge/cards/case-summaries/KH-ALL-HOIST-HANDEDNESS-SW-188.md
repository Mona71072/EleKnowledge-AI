---
knowledge_id: KH-ALL-HOIST-HANDEDNESS-SW-188
kind: case_summary
status: draft
card_version: 1
title: "巻上勝手不一致 — 空回し UP/DN 瞬動停止"
symptoms:
  - "空回し"
  - "勝手"
  - "右勝手"
  - "左勝手"
  - "PMF020MB"
  - "エンコーダ"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "188"
---

# 巻上勝手不一致 — 空回し UP/DN 瞬動停止

## 使う場面・対象条件

**空回し不可** — **UP→一瞬 DN 停止**、**DN→一瞬 UP 停止**（Lists 188）。

## 症状・現象

- ポータブル運転の **逆瞬動**（Lists）。

## ソース要約

### Lists（188）

- **原因**: 営設 **右勝手** 指定 → **S/W 右勝手** — **PMF020MB** 等 H/W は **標準左勝手**（Lists）。
- progress: エンコーダ配線 OK → **稲電 S/W 左/右取違え**（Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[238 PMF020MB 嵩上げ](../practice-guides/KH-CM-LB-PMF020MB-SPACER-238.md) と **PMF020MB** 同型番 — **188** は **勝手/S/W**。配線は **型番決定**、S/W は **営設仕様** と突合（Lists）。

## 調査・確認手順

1. 巻上 **型番・標準勝手**（Lists: PMF020MB=左）。
2. 営設 **勝手指定** vs **S/W**。
3. エンコーダ **ピンアサイン**（Lists progress — 断線なし例）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **188** | S/W 勝手 |
| [238](../practice-guides/KH-CM-LB-PMF020MB-SPACER-238.md) | 据付部品 |
| [187](../case-summaries/KH-MRL-SETS-ENCODER-DIR-187.md) | エンコーダ方向 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §188 |

## 未確認事項

- 右勝手標準の巻上型番一覧（Lists は PMF020MB のみ）。
