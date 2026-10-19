---
knowledge_id: KH-LINKS-RDB-RSLV-EMPTY-RUN-309
kind: case_summary
status: draft
card_version: 1
title: "LINKs — RDB/RSLV 短絡残で空回し巻上不动"
symptoms:
  - "空回し"
  - "RDB"
  - "RSLV"
  - "95d"
  - "64E"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "309"
  - ref_type: kb_document
    document_number: "IN-EL-12-104-13"
    kb_verify_status: pending
    locator: "P17"
---

# LINKs — RDB/RSLV 短絡残で空回し巻上不动

## 使う場面・対象条件

**制御盤単独 #5/UP/DN OK** だが **巻上機空回しで BK のみ・巻上不动**（Lists 309）。

## 症状・現象

- 多数 **2 桁/3 桁** エラー例（Lists 欄 — 転記のみ）。
- **#5** で BK 動作、巻上 **不動**（Lists）。

## ソース要約

### Lists（309）

- **RDB・RSLV** 短絡コネクタは **制御盤事前確認のみ**（IN-EL-12-104-13 P17 — pending）。
- **空回し時に短絡残** → **本設ケーブル差替** で良好（Lists）。

## 統合した回答・ノウハウ

[10 U/V](../case-summaries/KH-LINKS-UV-PHASE-FREE-RUN-10.md)・[317 空ソフト](./KH-ALL-P1-CE1-EMPTY-SW-317.md)・[31 RDU/RDF](./KH-LINKS-RDU-RDF-SWAP-31.md) と **空回し前チェック** を並列 — 本件は **試験用短絡コネクタの抜忘れ**。

## 調査・確認手順

1. 盤単独 vs **TOP 据付** の差。
2. **RDB/RSLV** 短絡有無（Lists）。
3. 本設ケーブルへ差替。
4. IN-EL-12-104-13 P17（pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **309** | RDB/RSLV |
| [10](./KH-LINKS-UV-PHASE-FREE-RUN-10.md) | 相順 |
| [7](./KH-LINKS-TERM-BOX-S2A-7.md) | RDF/RDT 導通 |

## KB確認に基づく追記

（IN-EL-12-104-13 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §309 |
| KB | IN-EL-12-104-13 P17（pending） |

## 未確認事項

- RDB/RSLV コネクタ位置の図面改訂。
