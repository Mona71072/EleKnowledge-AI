---
knowledge_id: KH-KM-LD-REGEN-LID-SW-NVA-287
kind: case_summary
status: draft
card_version: 1
title: "KM-LD — 回生盤フタ SW 不足で NVA 後起動不可"
symptoms:
  - "回生コンバータ"
  - "NVA"
  - "WOS"
  - "フタスイッチ"
model_scope:
  lists_model_label: ["KM-LD"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "287"
  - ref_type: kb_document
    document_number: "YE310C814"
    kb_verify_status: pending
    locator: "PT.13A"
---

# KM-LD — 回生盤フタ SW 不足で NVA 後起動不可

## 使う場面・対象条件

**KM-LD 回生** — **仮結線 WOS 8 m/min OK**、**本結線後 #5/#DYN 不引**（Lists 287）。

## 症状・現象

- **NVA** コネクタ差替で **一時起動可**（Lists）。

## ソース要約

### Lists（287）

- **コンバータ盤フタ（開放）SW 押込不足** 疑い（Lists）。
- C/P～コンバータ **KC01–KC11**（PT.13A YE310C814 — pending）。

## 統合した回答・ノウハウ

[80 CCP 回生](./KH-KM-LD-CCP-REGEN-80.md)・[54 PWFH](./KH-KM-LD-PWFH-PHASE-54.md) と **KM-LD 回生系** — 本件は **盤蓋インタロック + NVA 切替**。

## 調査・確認手順

1. **仮結線 vs 本結線** の差。
2. **フタ SW** 押込・NVA 操作。
3. **#5/#DYN** 状態。
4. PT.13A 結線（Lists progress）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **287** | フタ SW |
| [80](./KH-KM-LD-CCP-REGEN-80.md) | CCP |
| [54](./KH-KM-LD-PWFH-PHASE-54.md) | PWFH |

## KB確認に基づく追記

（YE310C814 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §287 |
| KB | YE310C814 PT.13A（pending） |

## 未確認事項

- フタ SW 正常押込の定量基準。
