---
knowledge_id: KH-VFGLF-SCU20-GS3-149
kind: case_summary
status: draft
card_version: 1
title: "SCU-20 通信不成立 — GS3 ロータリー設定（品目表 -01/-02）"
symptoms:
  - "SCU-20"
  - "エレコール"
  - "GS3"
  - "通信"
  - "ロータリー"
  - "VFGLF"
  - "群管理"
model_scope:
  lists_model_label:
    - "VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
  model_abbreviations: []
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "エレコール対抗試験で ELV↔SCU 盤通信不成立"
  excludes: []
  scope_note: "422 は別品番不一致事例。設定値の流用禁止"
source_refs:
  - ref_type: lists_item
    list_item_id: "149"
---

# SCU-20 通信不成立 — GS3 ロータリー設定（品目表 -01/-02）

## 使う場面・対象条件

**VFGLF** 現場で **SCU-20 盤** とエレベーター **通信が確立しない** とき。C 資料トラブルシュートで結線・導通 OK でも通信 NG の経路。

## 症状・現象

- エレコール **対抗試験で動作せず**
- C 資料（C-7-C3343.1-J）フローで **ELV と SCU 盤通信不成立** と判明（Lists）

## ソース要約

### Lists（149）

- 結線・I/O 導通は問題なし。稲電連絡先照会も問題なし回答。
- **原因（報告）**: 品目表 YX306B128（GS3 設定要領）が **「-01」** 表記、正規 **「-02」**。現地ロータリー **「5」**、正規 **「B」** → 変更後 **通信良好**。
- **Notes**: SCU-20 → **B**、SCU-20 **以前** → **5**。
- **状態**: 対応済み。

### OneNote

- タイトル一致索引なし（2026-10-19）。

## 統合した回答・ノウハウ

通信不良で配線が清い場合は **GS3 品番表記（-01/-02）とロータリー** を Lists 149 の SCU 世代別設定（B vs 5）で切り分ける。**422** は別事例（群管理 GS3 品番設定ミス）— 品番・設定を混同しない。

## 調査・確認手順

1. C 資料記載の通信トラブルフロー（Lists が参照した版）に沿って ELV 側・I/O 結線・導通。
2. 品目表 **YX306B128** のサフィックス **-01 / -02** と現地 GS3 **ロータリー**。
3. SCU-20 なら **B**、旧 SCU なら **5**（Lists Notes）。
4. 変更後の通信・エレコール試験。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **149** | VFGLF・**-01/-02 と B/5** |
| [422](./KH-GS3-PART-NO-SCU20-422.md) | 群管理 GS3 **品番設定** 別内容 |
| [158](./KH-HA-PANEL-ELECALL-158.md) | HA **エレコール** 連動 |
| [228](../practice-guides/KH-SCU20-CONN-TEST-228.md) / [233](../practice-guides/KH-SCU20-FLASH-REWRITE-233.md) | SCU 接続テスト・書換 |
| [384 3car](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 群管理 **運転モード** |

## KB確認に基づく追記

（該当なし — C 資料本文は Lists 経由のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §149 |
| OneNote | なし |
| KB | C-7-C3343.1-J（未 content_review） |

## 未確認事項

- YX306B128 現行版とロータリー操作の KB 突合未了。
- 422 との現場同一性（常に別件として扱う）。
