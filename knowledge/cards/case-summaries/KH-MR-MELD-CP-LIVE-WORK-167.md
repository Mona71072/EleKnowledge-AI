---
knowledge_id: KH-MR-MELD-CP-LIVE-WORK-167
kind: case_summary
status: draft
card_version: 1
title: "MELD R4-S4-T4 結線時 CP 活線 — コンダクタ焼損（↑高）"
symptoms:
  - "MELD"
  - "R4"
  - "S4"
  - "T4"
  - "311"
  - "312"
  - "ASTM"
  - "MR"
model_scope:
  lists_model_label: ["MR機種"]
  machine_room: ["MR"]
  control_methods: []
  observed_on: []
  may_apply_to: ["MELD 繋ぎ込み・盤内作業"]
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "167"
  - ref_type: onenote_page
    onenote_id: "b137030d-994c-4d06-972b-6d44a8793623:1"
---

# MELD R4-S4-T4 結線時 CP 活線 — コンダクタ焼損（↑高）

## 使う場面・対象条件

**MR** **MELD** の **R4-S4-T4** 結線作業時。**Lists 重要度 ↑高**。

## 症状・現象

- S 相地絡で **ASTM コンダクタ焼損**（Lists）
- 311/312、PW1/PW2 LED 点滅、89M リレー点滅
- 原因/ progress 欄 **情報管理保留** — **Notes** の安全指示を優先

## ソース要約

### Lists（167）

- **Notes（Must）**: 盤内作業は **ブレーカ遮断・活線禁止**。**CP～ターミナル間にブレーカ無し** → **CP 投入で R4/S4/T4 活線**。
- MELD R4-S4-T4 は **必ず CP 遮断** 下で実施。感電リスク（Lists）。

## 統合した回答・ノウハウ

MELD 配線は **132 RHY 抜け**（機能）と **167 活線**（安全）を別カードで参照。作業手順は Lists Notes を正とする。

## 調査・確認手順

1. 作業前 **CP 遮断・ブレーカ** 確認（Lists Notes）。
2. 結線後にのみ CP 投入試験。
3. 311/312 発生時は地絡・欠相・コンダクタ状態（Lists 症状 — 詳細保留）。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **167** | **活線作業禁止** |
| [132](./KH-VFGLF-MELD-RHY-CONNECTOR-132.md) | RHY 抜け |
| [174](./KH-VFGLB-MELD-BATTERY-174.md) / [101](./KH-IPU-MELD-BATTERY-POLARITY-101.md) | MELD **電源** |

## KB確認に基づく追記

（なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §167 |
| OneNote | b137030d…:1 |

## 未確認事項

- 原因/ progress 原文（情報管理保留）。
