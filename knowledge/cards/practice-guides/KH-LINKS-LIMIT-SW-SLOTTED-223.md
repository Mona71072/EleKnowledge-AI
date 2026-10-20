---
knowledge_id: KH-LINKS-LIMIT-SW-SLOTTED-223
kind: practice_guide
status: draft
card_version: 1
title: "LINKs — 制限スイッチ長穴固定と検査指摘"
symptoms:
  - "制限スイッチ"
  - "長穴"
  - "YX202B934"
  - "引継ぎ検査"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  product_lines: ["AXIEZ-LINKs"]
  machine_room: ["MRL"]
  control_methods: ["VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "223"
  - ref_type: kb_document
    document_number: "ASHO30163"
    kb_verify_status: pending
---

# LINKs — 制限スイッチ長穴固定と検査指摘

## 使う場面・対象条件

**AXIEZ-LINKS** **行き過ぎ制限スイッチ** が **長穴** で固定され **引継ぎで単穴指摘**（Lists 223）。

## 症状・現象

- 組立 **YX202B934** — **下部取付腕** が長穴固定（Lists）。

## ソース要約

### Lists（223）

- **背景**: 終点 SW BOX と制限 SW BOX **モジュール共通化** → 終点用 **長穴** で下部腕固定可（Lists）。
- **設計回答（MEE）**: **上部取付腕は単穴** のため **ずれ落ちしない** → **問題なし**（Lists progress）。
- ASHO30163（Lists — pending）。

### OneNote

- スナップショット照合: Lists §223 の **タイトル一致・ID 索引未検出**（Lists のみ。OneNote 追探索は別途）。


## 統合した回答・ノウハウ

[229 下部終点 BOX 腕](./KH-LINKS-LOWER-TERM-BOX-MOUNT-229.md)・[7 終点嵌合](../case-summaries/KH-LINKS-TERM-BOX-S2A-7.md)・[209 USL/CWL](./KH-LINKS-END-SW-USL-CWL-209.md) と **終点/制限 BOX** 同系 — 本件は **長穴＝設計意図** の説明用。

## 調査・確認手順

1. **上下取付腕** — 上 **単穴** / 下 **長穴** か。
2. 不発回答（Lists Notes）・ASHO30163（pending）。
3. 検査指摘時は **設計確認済** 回答を Lists progress どおり引用。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **223** | 長穴・検査 |
| [229](./KH-LINKS-LOWER-TERM-BOX-MOUNT-229.md) | 終点 BOX 腕位置 |
| [7](../case-summaries/KH-LINKS-TERM-BOX-S2A-7.md) | S2A 嵌合 |
| [229](./KH-LINKS-LOWER-TERM-BOX-MOUNT-229.md) | 終点腕位置 |

## KB確認に基づく追記

（ASHO30163 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §223 |
| KB | ASHO30163（pending） |

## 未確認事項

- 不発 rev と現行モジュール品番の対応。
