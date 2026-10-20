---
knowledge_id: KH-ALL-CR-SECURITY-FLOOR-DISPLAY-269
kind: case_summary
status: draft
card_version: 1
title: "乗場CR/顔認証で前回ユーザーの権限階が表示される（S/W）"
symptoms:
  - "セキュリティ"
  - "乗場CR"
  - "顔認証"
  - "タッチパネル"
  - "権限階"
  - "制御S/W"
model_scope:
  lists_model_label:
    - "全エレ機種"
  control_methods: []
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on: []
  may_apply_to:
    - "乗場CR/顔認証→三菱セキュリティ盤→ELSGW→GC→制御盤 経路の現場"
  excludes: []
  scope_note: "全エレ機種ラベル — セキュリティ付加仕様のみ"
source_refs:
  - ref_type: lists_item
    list_item_id: "269"
---

# 乗場CR/顔認証で前回ユーザーの権限階が表示される（S/W）

## 使う場面・対象条件

**セキュリティカード/顔認証** で、**付与外の階**が **かご内タッチパネル** に出る（複数回タッチで再現 — Lists 269）。

## 症状・現象

- 権限外階床の表示
- カード・顔認証双方（Lists）

## ソース要約

### Lists（269）

- **原因（Lists）**: 制御 S/W 設計不良 — **前回のセキュリティ解除命令** が **今回** として処理され、**前回ユーザーの権限階** が表示。
- **経路**: 乗場CR/顔認証 → 三菱セキュリティ盤 → ELSGW → GC → **制御盤**。
- **対応**: #30/#31 **制御盤 S/W 改造**、電気設計指示の確認試験で解消。
- **再発防止（Lists）**: 権限が **重複しない複数カード** を **連続認証** で試験（スローリセットのみでは見逃し得る）。

## 統合した回答・ノウハウ

権限階のゴースト表示は **制御 S/W 改造履歴（#30/31）** と **連続認証試験** を確認。DOAS/行先制限（373）とは別。

## 調査・確認手順

1. 現象が CR/顔認証後の **タッチパネル階表示** か特定。
2. 制御 S/W 改造（#30/31）の適用有無を保守/設計に確認。
3. **権限非重複カード** を連続認証試験（Lists 流出原因欄）。
4. 改造後は電気設計指示どおり確認試験。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **269** | CR/顔認証 **S/W** |
| **373** | DOAS **行先制限** |
| 群管理・呼び | [338 背後呼び](../practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) / [99 行先階](./KH-VFGLF-CAR-IND-DEST-FLOOR-99.md) / [371 群管理給電](./KH-MR-GROUP-PANEL-POWER-371.md) |
| [384 3car](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) / [92 パニック](../case-summaries/KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | 群管理連動 |

## KB確認に基づく追記

（該当 KB なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §269 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 改造 S/W の現行標準装備か（Lists 2024 事例）。
