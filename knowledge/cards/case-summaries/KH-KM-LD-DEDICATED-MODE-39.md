---
knowledge_id: KH-KM-LD-DEDICATED-MODE-39
kind: case_summary
status: draft
card_version: 1
title: "KM-LD — 専用運転に切替わらない（S/W）"
symptoms:
  - "専用運転"
  - "Z11"
  - "キーSW"
  - "パラメータ"
model_scope:
  lists_model_label: ["KM-LD"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "39"
---

# KM-LD — 専用運転に切替わらない（S/W）

## 使う場面・対象条件

**KM-LD** 乗場 **専用キー SW ON** でも **全自動のまま**（Lists 39）。

## 症状・現象

- 配線・導通・Z11 まで **24V 良好**（Lists）。
- **入力パラメータ** は 00/01 変化、**出力（専用灯指令）が 00 固定**（Lists）。

## ソース要約

### Lists（39）

- 稲電 **S/W 問題なし** 回答後も、**パラメータ出力不変** で **S/W 原因確定** → **デモ機再現** → **対策 S/W 製作**（Lists）。
- 不発 ATHO07091/07092、書換・動作フロー改訂（Lists progress）。

## 統合した回答・ノウハウ

配線正常でも **出力パラメータ不変** が S/W 疑いの Lists 上の確証手順。

## 調査・確認手順

1. キー SW 入切・Z11 **24V**。
2. メンテコン **入力／出力パラメータ**（専用 SW 信号・専用灯）。
3. 出力 00 固定 → S/W 経路（Lists）。
4. ATHO07091 系（pending）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **39** | 専用運転 S/W |
| [305](./KH-ALL-UCMP-SW-PARAM-MISMATCH-305.md) | UCMP 副番 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §39 |

## 未確認事項

- 現行 S/W 版とパラメータ番号。
