---
knowledge_id: KH-ALL-FCC-A-6FLOOR-153
kind: practice_guide
status: draft
card_version: 1
title: "いたずら呼びキャンセル（FCC-A）— 6階以上の基本仕様"
symptoms:
  - "FCC-A"
  - "いたずら呼び"
  - "試験報告書"
  - "6階"
  - "DOAS"
model_scope:
  lists_model_label:
    - "全エレ機種"
  control_methods:
    - "VFGLB"
    - "VFGH"
    - "VFGLF"
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on: []
  may_apply_to:
    - "階床6階以上の VFGLB/VFGH/VFGLF"
  excludes: []
  scope_note: "品目未記載でも試験書に FCC-A 欄がある場合"
source_refs:
  - ref_type: lists_item
    list_item_id: "153"
---

# いたずら呼びキャンセル（FCC-A）— 6階以上の基本仕様

## 使う場面・対象条件

**試験報告書（AXIEZ-LINKs 副番 C 等）** の **FCC-A** 良否欄で、**品目に記載が無く** 仕様不明なとき（Lists 153）。

## 症状・現象

- FCC-A の有無が品目から読めない（Lists）

## ソース要約

### Lists（153）

- **6階以上** → **FCC-A は基本仕様**（VFGLB、VFGH、VFGLF）。
- **DOAS 適用時は FCC-A 無効** — 併用注意（Lists）。

## 統合した回答・ノウハウ

6 階以上は **FCC-A ありがデフォルト** と Lists 153 を参照。DOAS 現場では **無効**  side を確認（373/153 連携）。

## 調査・確認手順

1. 停止数（6階以上か）。
2. 制御（VFGLB/VFGH/VFGLF）。
3. DOAS 有無 → FCC-A 期待値を切替。
4. 試験報告書 FCC-A 欄の判定根拠を記録。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **153** | FCC-A **基本仕様** |
| **373** | DOAS **無効化** |

## KB確認に基づく追記

（なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §153 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 5階以下・特殊バンクの例外（Lists 未記載）。
