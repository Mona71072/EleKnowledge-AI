---
knowledge_id: KH-ESC-SVFC-ANNOUNCE-RSW-78
kind: practice_guide
status: draft
card_version: 1
title: "SVFC — 標準アナウンス RSW 設定"
symptoms:
  - "アナウンス"
  - "SVFC"
  - "RSW"
  - "標準メッセージ"
model_scope:
  lists_model_label: ["SVFC"]
  may_apply_to: ["エスカレーター SVFC 制御"]
source_refs:
  - ref_type: lists_item
    list_item_id: "78"
  - ref_type: kb_document
    document_number: "C-60-631-VF35.1"
    kb_verify_status: pending
---

# SVFC — 標準アナウンス RSW 設定

## 使う場面・対象条件

**SVFC 制御** で **標準／特殊アナウンス** を **RSW** に落とすとき（Lists 78）。

## 症状・現象

- （豆知識 — 設定変更の手順整理）

## ソース要約

### Lists（78）

- **標準 vs 特殊**: **P5 表4** の内容のみ → 標準。それ以外 → 特殊（Lists）。
- **設定**: **P9** — メッセージを **4つずつブロック**、各ブロックを **4桁2進**（発報1/非発報0）→ **16進4桁** → **上2桁＝上位RSW、下2桁＝下位RSW**（Lists）。
- 他制御は **上位/下位 RSW の割当だけ異なる** 概ね同型（Lists）。
- **添付 Excel** 利用可（Lists — ファイル未転記）。

## 統合した回答・ノウハウ

2進→16進→RSW の流れが Lists 上の本体。**C-60-631-VF35.1 P5–P9** が正本（KB pending）。Excel は Lists 添付参照。

## 調査・確認手順

1. 標準／特殊の要件確認（表4）。
2. 発報メッセージを4つ単位で **2進** 化。
3. **16進** と **上下位 RSW** 設定。
4. KB **P5–P9** と突合（未レビュー）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **78** | SVFC アナウンス |
| **103** | SVFC 光電停止待機 |

## KB確認に基づく追記

（C-60-631-VF35.1 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §78 |
| KB | C-60-631-VF35.1（pending） |

## 未確認事項

- Lists 添付 Excel の所在・現行 P 改訂。
