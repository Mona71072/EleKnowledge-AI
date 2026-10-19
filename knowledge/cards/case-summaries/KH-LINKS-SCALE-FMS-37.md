---
knowledge_id: KH-LINKS-SCALE-FMS-37
kind: case_summary
status: draft
card_version: 1
title: "LINKs — 高速出し後の秤逆転・FMS"
symptoms:
  - "秤異常"
  - "高速出し"
  - "FMS"
  - "50%L"
  - "SET7"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "37"
  - ref_type: kb_document
    document_number: "C-7-C3900"
    kb_verify_status: pending
---

# LINKs — 高速出し後の秤逆転・FMS

## 使う場面・対象条件

**AXIEZ-LINKS** **高速出し後** **秤値逆転・運転休止**、**簡易50%L書込み不可**（Lists 37）。

## 症状・現象

- SET7/2–4 で **0%L と 50%L 表示が逆転**（Lists）。
- **16XX / -16** 等（Lists）。

## ソース要約

### Lists（37）

- **原因**: **高速出し前スロー FMS 未実施** 疑い — 後から FMS でも修正せず（Lists）。
- **対応**: **独立自動** で 50% 書込み（SET0/3）等 → **簡易50%L** 再実施で解消（Lists progress）。
- 参照 **C-7-C3900 P71**、YA112A923 G03（Lists — pending）。

## 統合した回答・ノウハウ

高速出し前 **スロー FMS** を [KH-VFGLF-BRAKE-SW-392](./case-summaries/KH-VFGLF-BRAKE-SW-392.md) 系の本スロー手順と並べて確認。秤は **FMS 順序** が Lists 上の核心。

## 調査・確認手順

1. 高速出し **前後** の FMS 実施有無。
2. SET7 **秤値** の逆転有無。
3. **独立自動** 50% 書込み（Lists progress）。
4. C-7-C3900 **簡易50%L**（pending）。

## 関連事例と条件の違い

| 参照 | 備考 |
| --- | --- |
| **37** | FMS 順 |
| **392** | 本スロー BK |
| **340** | ME-BL 秤固定金 |

## KB確認に基づく追記

（C-7-C3900 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §37 |
| KB | C-7-C3900、YA112A923 G03（pending） |

## 未確認事項

- 簡易50%L 未実施時の標準手順（Lists Notes）。
