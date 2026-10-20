---
knowledge_id: KH-VFGR-FLASH-WRITE-CABLE-284
kind: practice_guide
status: draft
card_version: 1
title: "VFGR — フラッシュ書換時は LAN 外す"
symptoms:
  - "VFGR"
  - "フラッシュメモリ"
  - "メンテコン"
  - "MCカード"
model_scope:
  lists_model_label: ["VFGR"]
  control_methods: ["VFGR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "284"
---

# VFGR — フラッシュ書換時は LAN 外す

## 使う場面・対象条件

**VFGR** **メンテコン「フラッシュメモリ書換」** で **エラー**（Lists 284・↓低）。

## 症状・現象

- P1–MC **フラット**、MC–メンテコン **シリアル＋有線 LAN** 同時接続（Lists progress）。

## ソース要約

### Lists（284）

- **原因**: 書換画面時 **有線 LAN 接続**（Lists progress）。
- **対応**: **シリアル変換のみ** — **LAN 外す**（Lists）。

## 統合した回答・ノウハウ

[317 空ソフト](../case-summaries/KH-ALL-P1-CE1-EMPTY-SW-317.md)・[233 SCU 書換](./KH-SCU20-FLASH-REWRITE-233.md) と **書込経路** を混同しない — 本件は **VFGR MC 配線**。[319 RUN SW](../case-summaries/KH-VFGR-CAR-TOP-RUN-SW-319.md) は別。

## 調査・確認手順

1. 書換メニュー直前の **接続**（シリアル vs LAN）。
2. LAN 抜いて再試行。
3. 仍失敗 → Epits/ソフト版（317 系）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **284** | VFGR LAN |
| [319](../case-summaries/KH-VFGR-CAR-TOP-RUN-SW-319.md) | RUN SW |
| [233](./KH-SCU20-FLASH-REWRITE-233.md) | SCU-20 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §284 |

## 未確認事項

- VFGR 以外制御での同現象。
