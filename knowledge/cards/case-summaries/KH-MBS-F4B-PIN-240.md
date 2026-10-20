---
knowledge_id: KH-MBS-F4B-PIN-240
kind: case_summary
status: draft
card_version: 1
title: "MBS F4B ピン逆 — カゴ内 12V 消失・インジ消灯"
symptoms:
  - "MBS"
  - "F4B"
  - "カゴ内インジ"
  - "621-601"
  - "12V"
  - "ケーブルベア"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF・VFGLB・VFGH"
  machine_room: []
  control_methods:
    - "VFGLF"
    - "VFGLB"
    - "VFGH"
  observed_on: []
  may_apply_to:
    - "MBS 接続後カゴ内操作盤 0V・戸開釦无效"
  excludes: []
  scope_note: "duplicate primary: case-elv-mbs-connection-car-indicator-off-id240"
source_refs:
  - ref_type: lists_item
    list_item_id: "240"
---

# MBS F4B ピン逆 — カゴ内 12V 消失・インジ消灯

## 使う場面・対象条件

**VFGLF/VFGLB/VFGH** で **MBS 接続後** **カゴ内インジ不点灯・戸開釦无效**。**Lists ↑高**。

## 症状・現象

- カゴ上戸開釦无效、カゴ内インジ不点灯
- **621-601 が 0V** — **F4B 外すと 12V 復帰**（Lists）

## ソース要約

### Lists（240）

- **原因**: カゴ上 ST～MBS **ケーブルベア中継**の **F4B-J01/J02 茶/青が逆**（青/茶になっていた）。
- **類似**: ASHO30261 / ASKI05776（MBS 側テレコ、Lists 資料欄）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

12V 系が MBS 接続で落ちるときは **F4B 抜き差し** で切り分け後、**ベア線ピンアサイン** を Lists 240 どおり（茶/青）確認。

## 調査・確認手順

1. カゴ内操作盤 **621-601** 電圧。
2. カゴ上 ST **F4B** 取外しで 12V 復帰か。
3. ベア中継 **J01/J02** 色順。
4. 類似不発資料（Lists 記載）との照合。

## 関連事例と条件の違い

| テーマ | 240 |
| --- | --- |
| 焦点 | **MBS 配線** |
| 302 | 乗場アナウンス電源（別） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §240 |
| OneNote | なし |
| KB | YA346C980 等（pending） |

## 未確認事項

- 個別機種略称（Lists は制御系列表記のみ）。
