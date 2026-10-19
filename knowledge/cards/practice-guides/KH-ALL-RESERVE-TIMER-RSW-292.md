---
knowledge_id: KH-ALL-RESERVE-TIMER-RSW-292
kind: practice_guide
status: draft
card_version: 1
title: "予約タイマー — メンテコン無し RSW 設定"
symptoms:
  - "予約タイマー"
  - "RSW"
  - "メンテコン"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "292"
  - ref_type: kb_document
    document_number: "C-8-S438"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-8-S436"
    kb_verify_status: pending
---

# 予約タイマー — メンテコン無し RSW 設定

## 使う場面・対象条件

**メンテコン不調** でパラメータ書換不可 — **予約タイマーのみ RSW/トグルで変更可**（Lists 292）。

## 症状・現象

- （豆知識 — 代替操作）

## ソース要約

### Lists（292）

- 手順 **C-8-S438**、アドレス **C-8-S436**（Lists — pending）。
- [315 NS 点滅](../practice-guides/KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) も **C-8-S436/S451** 言及 — **予約/NS** は同資料群。

## 統合した回答・ノウハウ

[300 Mc3 履歴](../practice-guides/KH-ALL-ALARM-HISTORY-MC3-300.md) は **ログ採取** — 本件は **パラメータ入力経路** の代替。

## 調査・確認手順

1. **予約タイマー** のみ必要か。
2. **C-8-S438** 操作（pending）。
3. **C-8-S436** アドレス（pending）。
4. メンテコン復旧後の正規経路へ戻す。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **292** | RSW 予約 |
| [315](../practice-guides/KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) | NS・S436 |

## KB確認に基づく追記

（C-8 系 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §292 |
| KB | C-8-S438 / S436（pending） |

## 未確認事項

- 制御方式別の RSW 組合せ。
