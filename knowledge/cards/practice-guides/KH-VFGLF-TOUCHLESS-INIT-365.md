---
knowledge_id: KH-VFGLF-TOUCHLESS-INIT-365
kind: practice_guide
status: draft
card_version: 1
title: "VFGLF/B/VFGH — タッチレス釦初期設定"
symptoms:
  - "タッチレス"
  - "LHS-105"
  - "C-32-A902.1"
model_scope:
  lists_model_label: ["VFGLF", "VFGLB", "VFGH"]
source_refs:
  - ref_type: lists_item
    list_item_id: "365"
  - ref_type: kb_document
    document_number: "C-32-A902.1"
    kb_verify_status: pending
---

# VFGLF/B/VFGH — タッチレス釦初期設定

## 使う場面・対象条件

**操作盤交換後** **タッチレス無反応**（押込は OK）（Lists 365）。

## 症状・現象

- **非接触のみ** 不良（Lists）。

## ソース要約

### Lists（365）

- **cause**: 出荷後 **初期設定解除** の可能性。
- **設定**: センサ認識、**LHS-105x 通信**、ボタン種別（EN81-70 等）。
- **Notes**: **フイルムセンサ断裂** も疑う。
- **progress**: C-32-A902.1 で **中継基板交換設定** → 復旧。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[321 LHS-1050A リセット](./KH-ALL-TOUCHLESS-LHS1050A-RESET-321.md) と **C-32-A902.1** を併読。

## 調査・確認手順

1. C-32-A902.1 **初期設定**。
2. 設定後も不良 → **フイルム** 部。
3. 誤登録時 **接触不良** 先例（Lists Notes）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **365** | **初期設定** |
| [321](./KH-ALL-TOUCHLESS-LHS1050A-RESET-321.md) | **1050A** |

## KB確認に基づく追記

（C-32-A902.1 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §365 |

## 未確認事項

- なし。
