---
knowledge_id: KH-HA-PANEL-ELECALL-158
kind: case_summary
status: draft
card_version: 1
title: "HA 制御盤内部エラー — エレコール連動停止"
symptoms:
  - "HA"
  - "アイホン"
  - "エレコール"
  - "SCU-20"
  - "RS-422"
  - "解錠"
  - "主階待機"
model_scope:
  lists_model_label:
    - "エレコール"
  machine_room: []
  observed_on: []
  may_apply_to:
    - "来客連動（解錠+主階待機）だけ失效、CR は可"
  excludes: []
  scope_note: "duplicate primary: case-elv-aiphone-ha-panel-error-elecall-id158。Lists ↑高"
source_refs:
  - ref_type: lists_item
    list_item_id: "158"
---

# HA 制御盤内部エラー — エレコール連動停止

## 使う場面・対象条件

**エレコール** で **HA（アイホン）連動**（自動解錠・主階待機）が動かず **CR は可** のとき。**Lists ↑高**。

## 症状・現象

- 来客時 **部屋からの解錠 + 主階床待機** 不能
- **CR 正常** → SCU～制御盤通信は良さそう（Lists 推測）

## ソース要約

### Lists（158）

- **progress**: 部屋番号 OK、HA～SCU **RS-422** 2–3V・ピン OK、**1200bps**、設計ソフト OK、**SCU20 エラーなし**。
- **原因**: **HA 制御盤内部エラー** — **PC システムリセット** で ELV 良好。
- **Notes**: HA 盤 **ELV 連動パラメータ OFF** も確認。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

SCU 側が清いときは **HA 盤**（内部エラー・連動パラメータ）。Lists 添付 **手動リセット箇所** はスナップショット未同梱 — KB レビュー前に手順断定しない。

## 調査・確認手順

1. CR / SCU 通信（Lists 158 progress）。
2. HA 制御盤 **エラー・連動パラメータ**。
3. 添付資料の **システムリセット**（Lists 参照）。
4. **228** 対向試験との役割分担。

## 関連事例と条件の違い

| list | 層 |
| --- | --- |
| **158** | **HA 盤** |
| [149](./KH-VFGLF-SCU20-GS3-149.md) / [422](./KH-GS3-PART-NO-SCU20-422.md) | GS3 / **RS-422 経路** |
| [228](../practice-guides/KH-SCU20-CONN-TEST-228.md) | SCU **接続試験** |
| [92](./KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | パニック（**別**） |
| [221](./KH-HEALTH-AIR-AC-TIMER-221.md) | HA **併設 AC**（duplicate primary） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §158（添付） |
| OneNote | なし |
| KB | catalog-elv-elecall-troubleshooting-reference（索引のみ・出典にしない） |

## 未確認事項

- 添付リセット手順の本文未取得。
