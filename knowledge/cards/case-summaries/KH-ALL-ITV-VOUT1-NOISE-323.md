---
knowledge_id: KH-ALL-ITV-VOUT1-NOISE-323
kind: case_summary
status: draft
card_version: 1
title: "ITV — VOUT1 未接続でインジ映像ノイズ"
symptoms:
  - "VOUT1"
  - "VOUT2"
  - "ITV"
  - "白ノイズ"
  - "インピーダンス"
model_scope:
  lists_model_label: ["全エレ機種"]
  may_apply_to: ["かご内カメラ→インジ表示"]
source_refs:
  - ref_type: lists_item
    list_item_id: "323"
---

# ITV — VOUT1 未接続でインジ映像ノイズ

## 使う場面・対象条件

**かご内 ITV** を **インジ表示** した際 **白ノイズ全体**（Lists 323）。

## 症状・現象

- **VOUT2 のみ** にインジ接続、**VOUT1 側モニタ未設置**（Lists）。

## ソース要約

### Lists（323）

- **配線**: 分配器出力 **VOUT1＝客先モニタ**、**VOUT2＝インジ** 想定 — モニタ将来設置で **VOUT1 空**（Lists）。
- **対応**: **VOUT1 にインジ接続** → 表示良好（Lists）。
- **Notes**: **VOUT1 に機器未接続** だと **インピーダンス** でノイズ。**機器配** どおり **カゴインジ映像は VOUT1**。**VOUT2** は **遠距離・出力大** — 近距離接続は **輝度高** 注意（Lists）。

## 統合した回答・ノウハウ

[334 分配器SW](../practice-guides/KH-LINKS-VDA-CAMERA-SPLIT-334.md)・[145 信号](../practice-guides/KH-ALL-CAMERA-COMPOSITE-NTSC-145.md) と **出力端子** をセット確認。[134](./KH-KE-WF-CABIN-CAMERA-FLICKER-134.md) は **照度** 系で別枝。

## 調査・確認手順

1. 分配器 **VOUT1/VOUT2** の接続先。
2. **VOUT1 空負荷** の有無。
3. Lists どおり **インジ→VOUT1** へ変更試験。
4. [334](../practice-guides/KH-LINKS-VDA-CAMERA-SPLIT-334.md) **75Ω/HIGH** 設定。

## 関連事例と条件の違い

| 参照 | 備考 |
| --- | --- |
| **323** | VOUT 取り |
| [334](../practice-guides/KH-LINKS-VDA-CAMERA-SPLIT-334.md) | 2台・終端 |
| [145](../practice-guides/KH-ALL-CAMERA-COMPOSITE-NTSC-145.md) | NTSC |

## KB確認に基づく追記

（機器配正本 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §323 |

## 未確認事項

- 機種別分配器型番と VOUT 定義。
