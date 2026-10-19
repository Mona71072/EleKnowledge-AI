---
knowledge_id: KH-ALL-UCMP-SW-PARAM-MISMATCH-305
kind: case_summary
status: draft
card_version: 1
title: "S/W 書換 — UCMP パラメータと副番アンマッチ"
symptoms:
  - "613"
  - "631"
  - "UCMP"
  - "積水ハウス"
  - "S/W書換"
model_scope:
  lists_model_label: ["全エレ機種"]
  may_apply_to: ["UCMP 型名変更を伴う S/W 更新"]
source_refs:
  - ref_type: lists_item
    list_item_id: "305"
---

# S/W 書換 — UCMP パラメータと副番アンマッチ

## 使う場面・対象条件

**積水ハウス型式認定** 変更等で **S/W 書換** 後 **動作不良**（Lists 305）。

## 症状・現象

- エラー例 **613, 631, 633…**（Lists 欄 — 転記のみ）。

## ソース要約

### Lists（305）

- **UCMP 型名変更** に伴う S/W 更新で **UCMP パラメータと S/W 副番アンマッチ**（Lists）。
- **再書換** で良好（Lists）。
- **progress**: バックアップ復帰で良好 → **戸開走行短絡以外**。**A07/A37** リレベル異常（UCMP S/W 組合せ）、**D3F** 規格化係数（S/W 版）（Lists — 断定は稲電解析待ち）。

## 統合した回答・ノウハウ

[57 UCMP B モード](../case-summaries/KH-LINKS-UCMP-BMODE-57.md)・[79 UCMP 電源](../practice-guides/KH-LINKS-UCMP-RESET-POWER-79.md)・[317 空ソフト](./KH-ALL-P1-CE1-EMPTY-SW-317.md) と **S/W 系** を分岐 — 本件は **UCMP パラメータ整合**。[39 専用運転](./KH-KM-LD-DEDICATED-MODE-39.md) も **305** 相互参照。

## 調査・確認手順

1. 書換 **契機**（型式認定・UCMP 型名）。
2. **UCMP パラメータ** と **S/W 副番** 照合（Lists）。
3. 整合後 **再書込**。
4. 仍不良 → 57/79 系 UCMP 手順（別論点）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **305** | 副番アンマッチ |
| [57](../case-summaries/KH-LINKS-UCMP-BMODE-57.md) | B モード |
| [317](./KH-ALL-P1-CE1-EMPTY-SW-317.md) | 空ソフト |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §305 |

## 未確認事項

- 副番対照表の正本（Epits/稲電）。
