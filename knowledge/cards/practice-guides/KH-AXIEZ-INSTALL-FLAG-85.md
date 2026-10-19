---
knowledge_id: KH-AXIEZ-INSTALL-FLAG-85
kind: practice_guide
status: draft
card_version: 1
title: "据付完了フラグ — AXIEZ（100930CF）を未完了へ戻す"
symptoms:
  - "据付完了フラグ"
  - "メンテコン"
  - "パラメータ"
  - "100930CF"
  - "新AXIEZ"
  - "KE-PF"
model_scope:
  lists_model_label:
    - "新AXIEZ"
  machine_room:
    - "MRL"
  control_methods:
    - "AXIEZ"
  model_abbreviations: []
  observed_on: []
  may_apply_to:
    - "AXIEZ(KE-PF) で完了→未完了に戻したい"
  excludes: []
  scope_note: "361 VFGLF は別アドレス。稲電確認・協力会社非開示（Lists）"
source_refs:
  - ref_type: lists_item
    list_item_id: "85"
---

# 据付完了フラグ — AXIEZ（100930CF）を未完了へ戻す

## 使う場面・対象条件

**新 AXIEZ（KE-PF）** で **据付完了フラグ** を **完了→未完了** に戻す必要があるとき。**361**（VFGLF・別アドレス）と混同しない。

## 症状・現象

- 据付完了フラグを **未完了** にしたい（Lists）

## ソース要約

### Lists（85）

- **方法**: **保守合理化 S/W + メンテコン** — アドレス **100930CF**、**00（完了）→ FF（未完了）**。
- **操作**: 昇降機メニュー **パラメータ書換**。
- **Notes**: 稲電は **基本変更非推奨**。他支社協力会社には **非開示**。変更前 **稲電確認**。引渡し時は **完了状態の確認**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

フラグ操作は **機種・制御世代でアドレスが異なる**（85 vs 361）。Lists の稲電確認 Notes を守り、手順の断定は **C 資料レビュー後** に KB へ移す。

## 調査・確認手順

1. Lists Model が **新 AXIEZ** か **VFGLF** かで **85 / 361** を選択。
2. 稲電確認（Lists 必須 Notes）。
3. メンテコン接続・保守合理化 S/W 有無。
4. 書換後、引渡しフローで **意図したフラグ状態** を確認。

## 関連事例と条件の違い

| list | プラットフォーム | アドレス（Lists） |
| --- | --- | --- |
| **85** | 新 AXIEZ | 100930CF |
| **361** | VFGLF | 1009 30CF（段階 FF/01/00） |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §85 |
| OneNote | なし |
| KB | C-7-C3900（361 参照、85 は Lists のみ） |

## 未確認事項

- KE-PF 以外の AXIEZ 派生への同一アドレス適用。
- 100930CF の現行パラメータ辞書（KB 未レビュー）。
