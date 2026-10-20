---
knowledge_id: KH-VFGH-ER-OPERATION-DL-A-379
kind: case_summary
status: draft
card_version: 1
title: "ER 運転 — DL-A/DOT-A と緩衝器前停止"
symptoms:
  - "ER運転"
  - "DL-A"
  - "DOT-A"
  - "緩衝器"
  - "ランバイ"
  - "VFGH"
model_scope:
  lists_model_label:
    - "VFGH"
  machine_room:
    - "MR"
  control_methods:
    - "VFGH"
  observed_on:
    - "VFGH"
  may_apply_to:
    - "ER 運転で緩衝器圧縮前に停止・ランバイ約 80mm"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "379"
  - ref_type: onenote_page
    onenote_id: "c551ee58-7bc9-4565-873c-7b6626d8a4e9:1"
    page_role: content
    note: "ER 運転 DL/DOT — Lists 379/348 共有頁"
---

# ER 運転 — DL-A/DOT-A と緩衝器前停止

## 使う場面・対象条件

**VFGH**。**ER 運転** で **緩衝器圧縮前に停止**（Lists 379）。

## 症状・現象

- **ランバイ約 80mm** で停止 — 緩衝器未圧縮（Lists）。

## ソース要約

### Lists（379）

- **ER 適用**: PD＞3000。**DL-A**＝通常 ER 停止位置、**DOT-A**＝安全回路切断位置（Lists）。
- **設計**: 緩衝器全圧縮当たり面から **300mm 切らない** — DOT-A で 300mm 切断。**DL-A は当たり面から 500mm**（裕度 200mm）（Lists）。
- 本物件 **ストローク 424mm** 緩衝器 → **DL-A で圧縮前停止** は仕様（Lists）。
- **progress**: 電気設計確認 — 現状問題なし（Lists）。
- 据付寸法: 品目 **599** 行き過ぎ SW（Lists Notes）。

### OneNote（`c551ee58-7bc9-4565-873c-7b6626d8a4e9:1`）

- **PD＞3000** ER 適用、**DL-A**（通常 ER 停止）と **DOT-A**（安全回路切断）の位置関係 — Lists 379 と一致。
- **深ピット**: ER 中 DL/DOT 離隔 → **DL-1/DOT-1** 追加手配の理由は [348](../../practice-guides/KH-MR-ER-EXTRA-DL-DOT-348.md)。
- 短 **ランバイ** は **YE400B075** 等で別計算（OneNote 注意）— **428** 手動系と混同しない。

## 統合した回答・ノウハウ

**428**（短ランバイ手動）/ **379**（**ER 終点 SW**）を分離。**348** と **同一 OneNote 頁** — 役割分担で相互リンク。

## 調査・確認手順

1. ER 運転実施か。
2. 緩衝器ストローク・PD。
3. **599** 行き過ぎ SW 変数。
4. 電気設計への ER 動作点確認（Lists 先例）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **379** | **ER DL-A** |
| **388** | **ロックダウン** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §379 |
| OneNote | なし |
| KB | 品目 599（pending） |

## 未確認事項

- 物件別 599 変数 — 現物品目表要確認。
