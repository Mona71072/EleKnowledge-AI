---
knowledge_id: KH-VFGH-HALL-BUTTON-ZONE-15
kind: case_summary
status: draft
card_version: 1
title: "VFGH — 乗場ボタン一部階不可"
symptoms:
  - "乗場ボタン"
  - "H10A"
  - "H20A"
  - "階区分"
model_scope:
  lists_model_label: ["VFGH"]
source_refs:
  - ref_type: lists_item
    list_item_id: "15"
---

# VFGH — 乗場ボタン一部階不可

## 使う場面・対象条件

**VFGH** **乗場ボタン** が **階ブロックで一部のみ効く**（Lists 15 — B1–7 不可、8–13 可の例）。

## 症状・現象

- 階により **ボタン無効**（Lists）。

## ソース要約

### Lists（15）

- **progress**: **機器接続配置図** で **H10A/H20A** 適用確認 → 線あり **結線先・ブレーカーなし** → 電気設計連絡 → 解消（Lists）。
- **cause 欄**: 情報管理保留 — **断定は progress の設計対策** のみ（Lists）。

## 統合した回答・ノウハウ

[147 HL 挟み](../case-summaries/KH-VFGH-HALL-LANTERN-PINCH-147.md) 等 **乗場系** と並べ **階別** 切り分け。配置図 **H10A/H20A** が Lists 上の索引。

## 調査・確認手順

1. **どの階範囲** か地図化。
2. **機器接続配置図** H10A/H20A。
3. 電気設計 **結線・ブレーカー** 手配（Lists progress）。
4. 保留 cause の詳細は **Lists 正本更新待ち**。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **15** | 階ブロック |
| [110](./KH-VFGLB-TOUCHLESS-PHANTOM-CALL-110.md) | タッチレス誤動 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §15 |

## 未確認事項

- cause 欄（情報管理保留）。
