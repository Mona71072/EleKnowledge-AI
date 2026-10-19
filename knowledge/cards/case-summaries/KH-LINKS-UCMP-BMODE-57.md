---
knowledge_id: KH-LINKS-UCMP-BMODE-57
kind: case_summary
status: draft
card_version: 1
title: "LINKs — UCMP 制動距離と B モード取違え"
symptoms:
  - "UCMP"
  - "制動距離"
  - "UOT"
  - "Bモード"
  - "ETP"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
  control_methods: ["LINKS"]
source_refs:
  - ref_type: lists_item
    list_item_id: "57"
  - ref_type: kb_document
    document_number: "C-7-C3900-J"
    kb_verify_status: pending
---

# LINKs — UCMP 制動距離と B モード取違え

## 使う場面・対象条件

**AXIEZ-LINKS** **UCMP 制動距離確認** で数値不出・**UOT 通過** 等（Lists 57）。

## 症状・現象

- UCMP 制動確認で **インジ数値なし・急停止せず**（Lists）。
- ETP 接続・手動で **UL 通過→UOT まで**（Lists）。

## ソース要約

### Lists（57）

- **原因**: 作業員が **LINKs 用 B モード 5/C** ではなく **AXIEZ の B モード 0/A** で実施（Lists）。
- **0/A** は **UOT 動作点測定** モードのため UOT まで走行し得る（Lists — 詳細未確認）。
- **技評** UCMP 欄の **0/A 表記修正予定**（Lists）。参照 **C-7-C3900-J P44/P81–83**。

## 統合した回答・ノウハウ

LINKs UCMP は **B 5/C**（Lists）。AXIEZ 手順の **流用禁止**。**S/W 書換** で **UCMP 副番不一致** は [305](./KH-ALL-UCMP-SW-PARAM-MISMATCH-305.md)。

## 調査・確認手順

1. 実施した **B モード／サブモード** を記録。
2. C-7-C3900 **LINKs UCMP 手順**（pending）。
3. ETP 有無・手動条件を分離。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **57** | B モード |
| [79](../practice-guides/KH-LINKS-UCMP-RESET-POWER-79.md) | UCMP 電源入切 |

## KB確認に基づく追記

（C-7-C3900-J 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §57 |
| KB | C-7-C3900-J（pending） |

## 未確認事項

- 技評表記修正の反映状況。
