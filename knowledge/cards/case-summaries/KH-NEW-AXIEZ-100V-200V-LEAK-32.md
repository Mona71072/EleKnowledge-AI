---
knowledge_id: KH-NEW-AXIEZ-100V-200V-LEAK-32
kind: case_summary
status: draft
card_version: 1
title: "新 AXIEZ — 動力から 100V 系への漏えい（YE315C379）"
symptoms:
  - "100V"
  - "200V"
  - "メガー"
  - "SCB"
  - "CST"
  - "L10"
  - "L20"
model_scope:
  lists_model_label:
    - "新AXIEZ"
  observed_on: []
  may_apply_to:
    - "建物 100V 盤メガ不可・ELV 動力から電圧かかる"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "32"
---

# 新 AXIEZ — 動力から 100V 系への漏えい（YE315C379）

## 使う場面・対象条件

**新 AXIEZ** で **100V 系に動力漏えい** — メガ測定不可、SCB OFF/CST ON で **L10/L20 対地 ~40–60V**（Lists 32）。

## 症状・現象

- R-S-T 線間 ~215V、**対地不平衡**（107/186/107V 等）。
- Lists progress: 稲電 **製品的問題なし・静観** 例あり — 現場は **YE315C379** 手順で切分。

## ソース要約

### Lists（32）対応概要

- GREEN **C10/C20** を ORANGE 余り線へ振替 → 24V 級。
- **別ケーブル** で CST–かご上 ST へ C10/C20 → **0V** 目標。
- **アース配列**（Y/W/O/G）電圧確認 — **GREEN(L20)=53V** 等で混線箇所特定（Lists 詳細）。

### OneNote

- なし。

## 統合した回答・ノウハウ

**191** は客先径・降下 — **32** は **制御 100V 対地異常**。**140**（LINKs 工場誤結線）と症状近接。

## 調査・確認手順

1. SCB/CST 状態固定で L10/L20 対地。
2. YE315C379 **段階 0→3**。
3. 稲電判断（静観 vs 配線修正）。

## 正式資料

| 種別 | 参照 |
| --- | --- |
| Lists | §32 |
| KB | YE315C379（pending） |

## 未確認事項

- 静観判断の適用条件（Lists 1 現場例）。
