---
knowledge_id: KH-LINKS-BLOCKING-DEVICE-G6-27
kind: case_summary
status: draft
card_version: 1
title: "LINKs — カゴ固定装置未接続で本スロー不可"
symptoms:
  - "本スロー"
  - "41DG"
  - "ブロッキング"
  - "G6"
  - "USL"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "27"
---

# LINKs — カゴ固定装置未接続で本スロー不可

## 使う場面・対象条件

**AXIEZ-LINKS** **本スロー出し** で **41DG 不点灯・カゴ不動**、**WOS は可**（Lists 27）。

## 症状・現象

- UP 未検出→USL 後 UP 検出も **不走**（Lists）。
- **41DG 未点灯**（Lists）。

## ソース要約

### Lists（27）

- **原因**: **カゴ固定装置 SW 未接続**（かご上 ST **G6**）（Lists）。
- **Notes**: かご内点検 SW 投入時 **UP/DN→29→41DG** 回路 — **41DG 消灯だけで乗場/ゲート断定不可**（Lists）。
- **progress**: SCG・D41 短絡試験（Lists）。

## 統合した回答・ノウハウ

本スロー系は [392 BK](./KH-VFGLF-BRAKE-SW-392.md)・[176 アース](./KH-ALL-GROUND-N00-NORMAL-SLOW-176.md)・[7 終点 S1A/S2A](./KH-LINKS-TERM-BOX-S2A-7.md) と並ぶ **別枝** — **G6 固定装置**。[16 G4 誤挿](./KH-LINKS-CAR-TOP-G4-HAND-16.md) は **41DG・HAND スロー** 同族。

## 調査・確認手順

1. **G6**・固定装置接続。
2. USL/UP 信号と **41DG**（Lists Notes 参照）。
3. SCG/D41 短絡切り分け（Lists progress）。
4. WOS 可・本スロー不可の分岐。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **27** | G6 未接 |
| [16](./KH-LINKS-CAR-TOP-G4-HAND-16.md) | G4 誤挿 |
| [36](./KH-CM-LB-GATE-EARTH-36.md) | D41/アース |
| [392](./KH-VFGLF-BRAKE-SW-392.md) | BK 本スロー |
| [7](./KH-LINKS-TERM-BOX-S2A-7.md) | S1A/S2A 嵌合 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §27 |

## 未確認事項

- G6 ピンアサイン正本（KB）。
