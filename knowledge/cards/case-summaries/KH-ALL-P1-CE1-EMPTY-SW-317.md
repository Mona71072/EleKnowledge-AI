---
knowledge_id: KH-ALL-P1-CE1-EMPTY-SW-317
kind: case_summary
status: draft
card_version: 1
title: "P1 — 空ソフト送付で cE1・空回し不可"
symptoms:
  - "cE1"
  - "CE1"
  - "WDT"
  - "空回し"
  - "Epits"
model_scope:
  lists_model_label: ["全エレ機種"]
  may_apply_to: ["P1 現場ソフト未書込"]
source_refs:
  - ref_type: lists_item
    list_item_id: "317"
  - ref_type: kb_document
    document_number: "C-7-C3900-J"
    kb_verify_status: pending
---

# P1 — 空ソフト送付で cE1・空回し不可

## 使う場面・対象条件

**巻上機空回し不可**、P1 **7セグ cE1（WDT）**（Lists 317）。

## 症状・現象

- 空回し不可（Lists）。

## ソース要約

### Lists（317）

- **原因**: **工場出荷ソフトが空** — 書込不良（Lists）。
- **対応**: **Epits** から現場ソフト DL → **P1 インストール** → 空回し良好（Lists）。
- **注意**: **RST トグルでリセット後** にエラー確認（Lists Notes）。WDT 説明 **C-7-C3900-J**（pending）。

## 統合した回答・ノウハウ

[151 WDT](../case-summaries/KH-P1-7SEG-WDT-151.md)・[10 LINKs U/V](./KH-LINKS-UV-PHASE-FREE-RUN-10.md)・[305 UCMP 副番](./KH-ALL-UCMP-SW-PARAM-MISMATCH-305.md) と **S/W 系** の切り分け — **cE1 単独** でも **ソフト未書** を疑う。

## 調査・確認手順

1. **RST** 後の **cE1** 再現。
2. **Epits/現場ソフト** 書込履歴。
3. 書込後 **空回し**。
4. 仍 cE1 → 151 系ハード WDT（Lists Notes 参照）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **317** | 空ソフト |
| [151](../case-summaries/KH-P1-7SEG-WDT-151.md) | WDT ハード |
| [10](./KH-LINKS-UV-PHASE-FREE-RUN-10.md) | 相順 |

## KB確認に基づく追記

（C-7-C3900-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §317 |
| KB | C-7-C3900-J（pending） |

## 未確認事項

- Epits 手順の現行 UI。
