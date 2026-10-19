---
knowledge_id: KH-LINKS-QB1-REVERSAL-82
kind: case_summary
status: draft
card_version: 1
title: "LINKs — QB1 復帰ミスで BK テレコ・437"
symptoms:
  - "437"
  - "614"
  - "631"
  - "64C"
  - "64F"
  - "BK1"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "82"
---

# LINKs — QB1 復帰ミスで BK テレコ・437

## 使う場面・対象条件

**AXIEZ-LINKS** **437（BK1 閉成故障）** 等複数エラー、**ブレーキ開放点検で UP/DN と逆 BK が開く**（Lists 82）。

## 症状・現象

- 437, 614, 631, 64C, 64F 等（Lists）。
- ブレーキ点検: **UP 側 BK1・DN 側 BK2 期待と逆**（Lists progress）。

## ソース要約

### Lists（82）

- **原因**: BK 設定不良で **QB1 交換** 後、**ファストン端子逆付け** → ブレーキ回路テレコ → 437 等（Lists）。
- **是正**: QP5-QP6、QP7-QP8 **逆接** を YE317C123 どおり修正（Lists progress）。

## 統合した回答・ノウハウ

437 群＋**点検時 BK 左右逆** は **QB1 内部配線** を疑う。**81 設定** 対策後も残るパターン。

## 調査・確認手順

1. BK1/2 **取り込み・電圧**（Lists progress 順）。
2. **ブレーキ開放点検** で UP/DN と開く BK の対応。
3. QB1 **QP5–QP8** ファストン向き（図面 YE317C123 — 添付、KB 未レビュー）。
4. 巻上機内部 BK 配線（Lists — 問題なし例）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **82** | **QB1 逆接** |
| **81** | スイッチ設定 |

## KB確認に基づく追記

（添付図 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §82 |

## 未確認事項

- YE317C123 正本パス・現行改訂。
