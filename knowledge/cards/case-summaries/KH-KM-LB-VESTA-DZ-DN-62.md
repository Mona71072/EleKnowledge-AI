---
knowledge_id: KH-KM-LB-VESTA-DZ-DN-62
kind: case_summary
status: draft
card_version: 1
title: "KM-LB — 最上階 DN で DZ 抜け E-stop"
symptoms:
  - "61E"
  - "61F"
  - "DZU"
  - "ベスタクト"
  - "E-stop"
model_scope:
  lists_model_label: ["KM-LB"]
source_refs:
  - ref_type: lists_item
    list_item_id: "62"
  - ref_type: kb_document
    document_number: "EA-98"
    kb_verify_status: pending
---

# KM-LB — 最上階 DN で DZ 抜け E-stop

## 使う場面・対象条件

**KM-LB** **最上階自動 DN** で **DZ 付近 E-stop**、**インジ階床欠落**（Lists 62）。

## 症状・現象

- DN で DZ 抜け **約1000 mm 下で E-stop**（Lists）。
- 自動時 **インジ未表示階**（ランダム）（Lists）。
- エラー例: 61E, 61F, 631, 64C, 712, C11, C13, 012（Lists）。

## ソース要約

### Lists（62）

- **原因**: **着床装置（ベスタクト）＋ R1 基板** 疑い — 交換で両症状解消（Lists）。
- **progress**: DZU 異常、DZ 食い込み是正、**EA-98 P80j 6-13-4** で検知確認、ベスタクト交換、**R1 交換** でインジ復旧（Lists）。

## 統合した回答・ノウハウ

DZ 系 E-stop と **インジ表示** は **別部品** もあり得る（Lists 上 R1 で②解消）。

## 調査・確認手順

1. メンテコン **DZU** 状態。
2. DZ プレート食い込み。
3. EA-98 **着床検知** 表示（pending）。
4. ベスタクト → **R1** 順（Lists）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **62** | KM-LB DZ |
| **182** | 終端 DZ 停止 |

## KB確認に基づく追記

（EA-98 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §62 |
| KB | EA-98（pending） |

## 未確認事項

- 返却品調査結果（Lists 時点調査中）。
