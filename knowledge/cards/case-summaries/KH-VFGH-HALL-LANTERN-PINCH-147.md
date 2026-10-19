---
knowledge_id: KH-VFGH-HALL-LANTERN-PINCH-147
kind: case_summary
status: draft
card_version: 1
title: "ホールランタン施工で N5A 621A 挟み込み — 乗場釦失效"
symptoms:
  - "ホールランタン"
  - "621A"
  - "621H"
  - "620H"
  - "乗場押釦"
  - "地絡"
  - "VFGH"
  - "N2"
  - "N3"
model_scope:
  lists_model_label:
    - "VFGH"
  control_methods:
    - "VFGH"
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on:
    - "VFGH"
  may_apply_to:
    - "ホールランタン新設・施工直後の乗場 ST 失效"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "147"
---

# ホールランタン施工で N5A 621A 挟み込み — 乗場釦失效

## 使う場面・対象条件

**制御 VFGH**。**ホールランタン施工後**、**乗場押釦・HL が動かない**（Lists 147）。症状原文はスナップショット **情報管理保留** — **progress/原因** を参照。

## 症状・現象

- 乗場押釦不動（Lists 原因・progress より）
- 直流電源・乗場 ST 停止疑い

## ソース要約

### Lists（147）

- **原因（Lists）**: 施工時 **N5A の 621A 線挟み込み地絡** → 直流電源装置・乗場 ST 停止推測。ビニテ応急後正常（ケーブル交換予定）。
- **progress**:
  - N2: **621H 12V なし**
  - N1: **620H 12V あり**
  - N3/N4 抜きで押釦正常確認
- **Notes**: 挟み込み写真・【VFGH】乗場配線図添付（スナップショット未同梱）。

## 統合した回答・ノウハウ

HL 施工後の乗場失效は **621A/621H 12V** と **N コネクタ切り分け**（Lists 147）。群管理電源（371）と配線経路が異なる。

## 調査・確認手順

1. N2 **621H 12V**、N1 **620H 12V**（Lists）。
2. N3/N4 抜き試験。
3. 621A 挟み込み・地絡の目視。
4. VFGH 乗場配線図で N5A 経路確認（KB/図面未レビュー）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **147** | HL 施工 **621A** |
| [371](./KH-MR-GROUP-PANEL-POWER-371.md) | 群管理盤 **電源** |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §147 |
| OneNote | なし |
| KB | VFGH 乗場配線図（Lists 参照・未突合） |

## 未確認事項

- Lists 症状原文（保留）。
- ケーブル交換後の最終結果（Lists 予定のみ）。
