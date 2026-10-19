---

knowledge_id: KH-MR-GROUP-PANEL-POWER-371
kind: case_summary
status: draft
card_version: 1
title: "群管理盤への電源線抜けで乗場釦のみ失效"
symptoms:
  - "群管理盤"
  - "乗場釦"
  - "電源供給"
  - "MR機種"
  - "本設切替"
model_scope:
  lists_model_label:
    - "MR機種"
  machine_room:
    - "MR"
  control_methods: []
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on: []
  may_apply_to:
    - "仮設→本設切替後、乗場釦のみ効かずカゴ内・全自動は可"
  excludes: []
  scope_note: "Lists Model=MR機種。個別機種略称未記載"
source_refs:
  - ref_type: lists_item
    list_item_id: "371"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:145"
  - ref_type: onenote_page
    onenote_id: "c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:183"
---
# 群管理盤への電源線抜けで乗場釦のみ失效

## 使う場面・対象条件

**MR 系群管理**。**本設電源切替後**、**乗場釦のみ効かない**・**全自動は動く**（Lists 371）。

## 症状・現象

- 乗場 ST 失效、カゴ内押釦・全自動は可
- 群管理盤に電源無し

## ソース要約

### Lists（371）

- **発見**: 受電盤内 **群管理盤電源線が抜け**（養生テープ絶縁）。#6/#7 照明電源間結線で **電気屋作業後の挿し忘れ** 疑い（Lists Notes）。
- **対応**: ブレーカ遮断→結線直し→群管理盤給電復帰。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:145`（`onenote-c75d78f366e15996a2b04bde.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

乗場だけ死ぬパターンでは **群管理盤給電** を本設切替直後に確認。他業者作業後は **抜け・緩み** を Lists Notes どおり点検。

## 調査・確認手順

1. カゴ内・全自動の可否で群管理/乗場系を切り分け。
2. 群管理盤入力電源の有無。
3. 受電盤内 **群管理盤電源線** の接続（Lists 371 経路）。
4. 他業者作業後の再確認。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **371** | 群管理盤 **給電** |
| [384](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 3car **群管理運転** |
| [253](../practice-guides/KH-VFGLF-GROUP-WIRING-SAVE-MODE-253.md) | **省力乗場** 索引 |
| [19](./KH-CM-LB-TEMP-POWER-TRIP-19.md) | CM-LB **仮設盤** RA1 |
| [422](./KH-GS3-PART-NO-SCU20-422.md) / [171](./KH-GROUP-ECAN-MAG-171.md) | GS3 / **E-CAN** |
| [338](../practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) / [92](./KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | 背後呼び / **パニック** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |
| [422 GS3/SCU](./KH-GS3-PART-NO-SCU20-422.md) / [171 E-CAN](./KH-GROUP-ECAN-MAG-171.md) | 群管理盤 **通信** |
| [338 背後呼び](../practice-guides/KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) / [92 パニック](./KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | **呼び** 系 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §371 |
| OneNote | 索引 2 页 |
| KB | なし |

## 未確認事項

- 具体 **機種略称**（ME-CH 等）は Lists 未記載。
