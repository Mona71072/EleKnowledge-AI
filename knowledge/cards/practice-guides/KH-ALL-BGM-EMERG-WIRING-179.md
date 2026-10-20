---
knowledge_id: KH-ALL-BGM-EMERG-WIRING-179
kind: practice_guide
status: draft
card_version: 1
title: "非常放送音量小 — 2/3 線式と 4 芯入線の取違え"
symptoms:
  - "非常放送"
  - "BGM"
  - "音量"
  - "2線式"
  - "3線式"
  - "PC-391T"
  - "4芯"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "非常放送のみ現場で音量が極端に小さい"
  excludes: []
  scope_note: "duplicate primary: case-elv-emergency-broadcast-low-volume-bgm-wiring-mismatch-id179。122 2/3線説明と併読"
source_refs:
  - ref_type: lists_item
    list_item_id: "179"
---

# 非常放送音量小 — 2/3 線式と 4 芯入線の取違え

## 使う場面・対象条件

**非常放送** 試験で **音量が小さい**（カゴ上も同様）、**アッテネータ設定 OK** のとき（Lists 179）。

## 症状・現象

- **非常放送のみ** 現場、音量小（Lists）

## ソース要約

### Lists（179）

- **原因**: 機械室 **4 芯入線** なのに放送側 **2 芯結線** — **2 線式/3 線式** の違い未理解（**PC-391T** 例）。
- **対応**: 協連絡メモ **品証－06－118** どおり結線変更で音量改善。
- [122](./KH-ALL-BROADCAST-2-3-WIRE-122.md)（Lists 別件）: 2/3 線式と BGM 操作盤 SW — 概念補助。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

音量問題を **アッテネータだけ** で見ない。**入線芯数** と **放送設備側 2/3 線** の整合 — [122](./KH-ALL-BROADCAST-2-3-WIRE-122.md)・[363](./KH-VFGLF-BGM-WIRING-363.md) を併読。

## 調査・確認手順

1. 非常のみか一般放送もか。
2. アッテネータ・操作盤 SW（122 条件）。
3. **機械室入線芯数** vs **放送側結線**。
4. PC-391T / 品証メモどおり是正（KB pending）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **179** | **結線芯数** ミス |
| [363](./KH-VFGLF-BGM-WIRING-363.md) | **二線 ATN 無** BGM1/2 |
| [122](./KH-ALL-BROADCAST-2-3-WIRE-122.md) | 2/3 線 **概念** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §179、§122 |
| OneNote | なし |
| KB | 品証－06－118（pending） |

## 未確認事項

- 2/3 線式の概念は [KH-ALL-BROADCAST-2-3-WIRE-122](./KH-ALL-BROADCAST-2-3-WIRE-122.md)（Wave 16）。
