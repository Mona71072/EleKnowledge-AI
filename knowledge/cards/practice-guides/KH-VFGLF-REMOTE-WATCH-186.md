---
knowledge_id: KH-VFGLF-REMOTE-WATCH-186
kind: practice_guide
status: draft
card_version: 1
title: "遠隔監視 — 保守作業見守り機能と MIC 作業届"
symptoms:
  - "遠隔監視"
  - "見守り機能"
  - "MNT"
  - "情報センター"
  - "作業届"
  - "MIC"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLB・VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
    - "VFGLB"
  observed_on: []
  may_apply_to:
    - "遠隔監視後の官検・保守で自動通報が上がる"
  excludes: []
  scope_note: "Lists ↑高。170 ソフトMNT とは別"
source_refs:
  - ref_type: lists_item
    list_item_id: "186"
---

# 遠隔監視 — 保守作業見守り機能と MIC 作業届

## 使う場面・対象条件

**VFGLF/VFGLB** **遠隔監視** 後、保守・官検で **情報センターへ自動通報**（上長報告）が上がる懸念。**Lists ↑高**。

## 症状・現象

- **MNT 側** で見守り発報（**R/M は通常故障発報イメージ**、R/M では見守り発報しない — Lists）

## ソース要約

### Lists（186）

- **機能**: 自動モード中の **ピット/カゴ上侵入** 等を検知 → **情報センター自動通報**。
- **検出例**: ①昇降路侵入 ②走行中侵入 ③ピットイン ④カゴ上搭乗 ⑤リモート走行後 RUN 30 秒長押し ⑥最下階切離し忘れ。
- **Notes**: 作業前 **MIC に作業届**（建物番号・社員証・連絡先・日時）。手順守れば **発報しない** 想定。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[173 メンテモード未解除](../case-summaries/KH-VFGLB-MAINT-MODE-FLICKER-173.md) — 遠隔監視立上げ時の **MNT** 残留に注意。

通報は **故障ではなく見守り** の線。**186** = 届出運用、**170** = ソフト MNT 投入方法。

## 調査・確認手順

1. 遠隔監視 **開始済み** か。
2. 作業時 **自動モード・侵入** 条件（Lists ①–⑥）。
3. **MIC 作業届** 有無。
4. MNT vs R/M 発報差（Lists）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **186** | **見守り** 通報 |
| **170** | **ソフト MNT** |
| **173** | メンテモード解除（別） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §186 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 見守り資料本文（Lists: 資料へ全面記載困難）。
