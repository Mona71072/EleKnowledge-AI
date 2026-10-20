---
knowledge_id: KH-MR-ER-EXTRA-DL-DOT-348
kind: practice_guide
status: draft
card_version: 1
title: "MR — 深ピット ER 運転時の DL-1/DOT-1 追加手配"
symptoms:
  - "ER運転"
  - "DL-1"
  - "DOT-1"
  - "深ピット"
  - "PD 3000"
model_scope:
  lists_model_label: ["MR機種"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "348"
  - ref_type: onenote_page
    onenote_id: "c551ee58-7bc9-4565-873c-7b6626d8a4e9:1"
    page_role: content
    note: "ER DL/DOT 深ピット — 379 と共有"
---

# MR — 深ピット ER 運転時の DL-1/DOT-1 追加手配

## 使う場面・対象条件

**ピット深い** **ER 運転** 物件で **DL-1～/DOT-1～** が **通常 DL/DOT 以外** 手配されている理由の説明（Lists 348）。例: **ピット 10 m**。

## 症状・現象

- **豆知識** — 品目の **DL/DOT 複数**（Lists 症状）。

## ソース要約

### Lists（348）

- **設計**: 緩衝器全圧縮時 **当たり面から 500 mm** が **DL-A**（通常 ER 停止位置）が標準。
- **深ピット**: ER 中 **DL と DOT が離れる** — ER 中も **終点/行過 SW を切り続ける** ため **DL-1～、DOT-1～** 追加手配あり。
- **Notes**: ER 中に SW が離れても **ER 不可にはならない** が **安全性** で追加。
- **ER 概要**: DL 一時停止 → **ER SW + 下ボタン** 継続で **DL-A まで** 追加下降。適用 **PD>3000** 等（Lists Notes 抜粋）。

### OneNote（`c551ee58-7bc9-4565-873c-7b6626d8a4e9:1`）

- **ピット約 10 m** 等で ER 中 **DL と DOT が離れる** → **DL-1～/DOT-1～** 追加（Lists 348 と一致）。
- **DL-A/DOT-A 動作高さ**・品目 **599** の詳細は [379](../case-summaries/KH-VFGH-ER-OPERATION-DL-A-379.md)（VFGH 事例）参照。

## 統合した回答・ノウハウ

[420 ケーブル吊り](./KH-MR-CONTROL-CABLE-HANG-420.md) は **U 字位置** — **348** は **ER 用追加 SW**。[379 ER 動作点](../case-summaries/KH-VFGH-ER-OPERATION-DL-A-379.md) は **VFGH** 別機種。

## 調査・確認手順

1. **ピット深さ**・**ER 適用**。
2. 品目 **DL/DOT 系統**（通常 vs -1～）。
3. ER 走行中 **各 SW** の **連続 ON** を確認。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **348** | **追加 DL/DOT** |
| [420](./KH-MR-CONTROL-CABLE-HANG-420.md) | 制御ケーブル **吊り** |
| [379](../case-summaries/KH-VFGH-ER-OPERATION-DL-A-379.md) | ER **動作点**（VFGH） |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §348 |

## 未確認事項

- なし（Lists cause/Notes で説明完結）。
