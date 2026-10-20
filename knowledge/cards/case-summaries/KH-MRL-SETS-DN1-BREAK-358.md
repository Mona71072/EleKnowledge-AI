---
knowledge_id: KH-MRL-SETS-DN1-BREAK-358
kind: case_summary
status: draft
card_version: 1
title: "MRL — SETS DN1/DN2 断線で 62D 最寄階停止"
symptoms:
  - "62D"
  - "SETS"
  - "DN1"
  - "DN2"
  - "E00"
model_scope:
  lists_model_label: ["MRL機種"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "358"
  - ref_type: kb_document
    document_number: "C-7-C3700"
    kb_verify_status: pending
---

# MRL — SETS DN1/DN2 断線で 62D 最寄階停止

## 使う場面・対象条件

**高速出し後** **最上階で起動不能** — **P1 62D**（SETS 最寄階停止要求）、**SETS E00/H00**（Lists 358）。

## 症状・現象

- 独立/自動で **最上階着床後に走れない**（Lists）。

## ソース要約

### Lists（358）

- **原因**: **秤装置～SETS 盤** 間 **DN1/DN2 配線破断** — **基準位置未読込** → ガバナエンコーダ誤差修正不可 → **62D**。
- **推定**: 揚重 **チェーンブロック** と配線摩擦（Lists Notes）。
- **Notes**: SETS 概要・**基準位置センサ UP1/UP2/DN1/DN2**・書込み運転（長文 — Lists）。
- **progress**: DN1/DN2 **SETS 基板未取込** 確認 → 断線特定。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[418 64C](./KH-VFGLB-SETS-64C-MON1-418.md)・[436 664/665](./KH-MRL-SETS-664-665-436.md) と **SETS エラー族** — **358** は **DN 系断線**。

## 調査・確認手順

1. **62D** vs **64C/664** 判別。
2. **DN1/DN2** センサ取込（SETS 盤）。
3. 秤～SETS **配線導通**（揚重経路）。
4. 基準位置 **再書込**（C-7-C3700 p.73 — pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **358** | **DN 断線** |
| [418](../practice-guides/KH-VFGLB-SETS-64C-MON1-418.md) | **64C** 表示 |
| [436](../practice-guides/KH-MRL-SETS-664-665-436.md) | **664/665** |

## KB確認に基づく追記

（C-7-C3700 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §358 |
| KB | C-7-C3700（pending） |

## 未確認事項

- なし（Lists cause 確定）。
