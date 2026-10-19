---
knowledge_id: KH-VFGLF-DOOR-SHORT-CHECK-160
kind: case_summary
status: draft
card_version: 1
title: "戸短検出 — 独立運転復帰では戸短チェック不可"
symptoms:
  - "戸短"
  - "戸短チェック"
  - "独立運転"
  - "官検"
  - "EDモード"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "官検後かご上復帰で管理外・起動不能"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "160"
---

# 戸短検出 — 独立運転復帰では戸短チェック不可

## 使う場面・対象条件

**VFGLF** **官検** 等で **かご上から独立運転復帰** 後、**戸短検出** して **管理外・起動不能** のとき。

## 症状・現象

- 戸短検出 → **戸短チェック未実施** → 復帰不能（Lists）

## ソース要約

### Lists（160）

- **戸短検出契機**: **CLT 全閉** で **ED モード** や **安全 SW** → **ドアカット＝戸短検出**。
- **復帰**: **戸短チェック状態** — 戸短後 **全自動** で戸開閉し **戸短でないことを確認**。
- **独立運転では戸開閉不可 → 戸短チェック不可**（Lists 核心）。
- **Notes**: 乗場 PT **ED** でかご上に乗るとき **かご中は全自動**。
- **参照**: C-7-C3900 P10 1-9。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**419**（戸短解除）・**CM-LB 戸短** と並べ、**160** は **復帰モード選び**（全自動でチェック）。

## 調査・確認手順

1. 戸短検出の直前操作（ED/安全 SW/CLT）。
2. 現在 **独立 vs 全自動**。
3. **全自動** で戸短チェックシーケンス（Lists）。
4. 乗場 PT ED 時は **かご内全自動**（Notes）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **160** | **戸短チェック** モード |
| **419** | VFGLB **戸短解除** 手順 |
| [据付・試験・調整ハブ](./KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |
| [419 VFGLB 戸短解除](../practice-guides/KH-VFGLB-DOOR-SHORT-RELEASE-419.md) | 解除手順 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §160 |
| OneNote | なし |
| KB | C-7-C3900（pending） |

## 未確認事項

- なし（Lists 手順明示）。
