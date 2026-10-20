---
knowledge_id: KH-MR-CONTROL-CABLE-HANG-420
kind: practice_guide
status: draft
card_version: 1
title: "MR — 制御ケーブル吊り高さ（据付ノート・C-10-C5.3）"
symptoms:
  - "制御ケーブル"
  - "吊り高さ"
  - "ER運転"
  - "ピット干渉"
  - "IN-EL-08-111-05"
model_scope:
  lists_model_label: ["MR機種"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "420"
  - ref_type: kb_document
    document_number: "C-10-C5.3-J"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "IN-EL-08-111-05"
    kb_verify_status: pending
---

# MR — 制御ケーブル吊り高さ（据付ノート・C-10-C5.3）

## 使う場面・対象条件

**ER 運転後** **ピット床と制御ケーブル底** が **干渉** — 据付ノート計算式どおり **吊っていない** 疑い（Lists 420）。例: **180 m/min**, **PD 3450 mm**, **ピット点検口あり**。

## 症状・現象

- **寸法不良・作業的現象**（Lists）。

## ソース要約

### Lists（420）

- **原因**: 吊り高さ **検討不足**（「ピット床から 60 mm 以上あればよい」誤認）。
- **対応**: 据付ノート **計算式** を満たすよう **吊り直し** — 総点シートへ式記載、引継ぎで **かご下吊手～U 字底** 計測。
- **Notes（公式）**:
  - **鋼芯あり**: L=(ランバイ+バッファ+吊り間隔)/2+A（高速 A=1000、低速 A=500）。L が大きすぎてバッファ時ピット接触なら **D=(ランバイ+バッファ)/2** で吊る。
  - **鋼芯なし**: 同式。L>(PD-60) なら **D≈60 mm** で吊る。
  - **稲電開発**: 原則 **計算 L** — 接触恐れ時は鋼芯ありは **接触させず**、鋼芯なしは **一時接触可**（U 字周辺に突起なし前提）。
- **Referenced**: IN-EL-08-111-05、C-10-C5.3-J。
- **progress**: 稲電に **静観可否** 問合せ → **静観可**（C-10-C5.3 補足）も **式未充足なら吊り直し予定**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[348 ER 追加 DL/DOT](./KH-MR-ER-EXTRA-DL-DOT-348.md) は **深ピット ER スイッチ** — **420** は **U 字吊り D/L**。[201 立上げ](./KH-MR-CAGE-CP-PROTECTOR-201.md) と併読。

## 調査・確認手順

1. ER 後 **ピット床～ケーブル底** クリアランス。
2. **鋼芯有無** で **L/D 式**（Lists Notes）。
3. IN-EL-08-111-05 計算 vs 実測（吊手～U 字底）。
4. 静観判断は **稲電開発** 見解（Lists）— 式未充足は **是正**。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **420** | **吊り L/D** |
| [348](./KH-MR-ER-EXTRA-DL-DOT-348.md) | **DL-1/DOT-1** 追加 |
| [201](./KH-MR-CAGE-CP-PROTECTOR-201.md) | **立上げ側** |

## KB確認に基づく追記

（C-10-C5.3-J / IN-EL-08-111-05 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §420 |
| KB | C-10-C5.3-J、IN-EL-08-111-05（pending） |

## 未確認事項

- KB 本文で **式記号** を再確認。
