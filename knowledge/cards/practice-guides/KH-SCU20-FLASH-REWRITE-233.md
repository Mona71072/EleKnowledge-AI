---
knowledge_id: KH-SCU20-FLASH-REWRITE-233
kind: practice_guide
status: draft
card_version: 1
title: "SCU-20 フラッシュ書換 — CN37・メンテコン ver4（duplicate primary）"
symptoms:
  - "SCU-20"
  - "フラッシュ書換"
  - "メンテコン"
  - "CN37"
  - "FwCard"
  - "エレコール"
model_scope:
  lists_model_label:
    - "エレコール"
  machine_room: []
  control_methods: []
  observed_on: []
  may_apply_to:
    - "SCU-20 盤の S/W 書換（制御盤書換ツールとは別）"
  excludes: []
  scope_note: "duplicate primary: elv-scu20-flash-rewrite-tool-compatibility-id233（索引 elv-sw-change-reference は参照のみ）"
source_refs:
  - ref_type: lists_item
    list_item_id: "233"
---

# SCU-20 フラッシュ書換 — CN37・メンテコン ver4（duplicate primary）

## 使う場面・対象条件

**SCU-20** の **パラメータ書換**。**制御盤用書換ツールとは別**（Lists 233）。**149/422** は通信・GS3 設定の別論点。

## 症状・現象

- SCU-20 書換に **専用ツール** が必要（Lists）
- 2023/10/25 メンテコン更新で **フラッシュ書換プログラム4 に SCU-20 追加**（Lists 追記）

## ソース要約

### Lists（233）

1. 扉裏ポリ袋 **中継コネクタ → CPU CN37**、書換ケーブル接続（わかりにくい — 添付参照）。
2. **フラッシュメモリ書換 ver4.2** 起動（メンテコン統合後は **プログラム4**）。
3. **読込 → 書換**（対象 S/W は **パラメータのみ** 選択可）。
4. **C-6-S951.1 A.2**、インストーラーは Lists 添付。
- **Notes**: ver4.2 起因で通常書換時 **パワーマネージメント制御設定** エラーで終了する可能性 — **McEnv.ini** の Debug=0→1（FwCard / FLASH 両方、Lists パス記載）。

### OneNote

- タイトル直接一致なし（2026-10-19）。

## 統合した回答・ノウハウ

通信不成立（**149 B/5**、**422 品番-03/LM2B**）を直したあと S/W 書換が必要なら **233** の CN37 経路と **制御盤書換との混同禁止**。duplicate の **elv-sw-change-reference** は本カードの手順根拠にしない。

## 調査・確認手順

1. 作業対象が **SCU-20 盤** か制御盤か確認。
2. CN37 中継コネクタ・ケーブル（Lists 添付図）。
3. メンテコン **フラッシュ書換プログラム4 / SCU-20** 有無。
4. 読込→書換（パラメータのみ）。
5. パワーマネージメントエラー時 McEnv.ini Debug（Lists Notes）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **233** | **書換手順** |
| [149](../case-summaries/KH-VFGLF-SCU20-GS3-149.md) | GS3 ロータリー B/5 |
| [422](../case-summaries/KH-GS3-PART-NO-SCU20-422.md) | GS3 **品番 -03 / LM2B** |
| [158](../case-summaries/KH-HA-PANEL-ELECALL-158.md) | HA **エレコール**（通信確立後） |
| [228](./KH-SCU20-CONN-TEST-228.md) | 接続テスト注意 |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §233 |
| OneNote | なし |
| KB | C-6-S951.1、C-7-C3343（pending） |

## 未確認事項

- メンテコン現行版でのメニュー名称（Lists 2023 追記以降未検証）。
- インストーラー添付のリポジトリ同梱有無。
