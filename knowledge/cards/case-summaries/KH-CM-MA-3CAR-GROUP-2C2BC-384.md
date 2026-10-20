---
knowledge_id: KH-CM-MA-3CAR-GROUP-2C2BC-384
kind: case_summary
status: draft
card_version: 1
title: "3台群管理が 2C-2BC 状態になる（CM-MA）"
symptoms:
  - "群管理"
  - "2C-2BC"
  - "3car"
  - "CM-MA"
  - "#28"
  - "#29"
  - "#30"
  - "バンク分割"
model_scope:
  lists_model_label:
    - "CM-MA"
  product_lines:
    - "Nexcube"
  machine_room:
    - "MR"
  model_abbreviations:
    - "CM-MA"
  control_methods:
    - "VFGH"
  door_families: []
  door_types: []
  observed_on:
    - "CM-MA"
  may_apply_to:
    - "マルチカー3台群管理の工事使用中"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "384"
  - ref_type: onenote_page
    onenote_id: "cf01bae3-86fc-4307-949e-3798361c2ee3:1"
    page_role: hybrid
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:145"
---
# 3台群管理が 2C-2BC 状態になる（CM-MA）

## 使う場面・対象条件

**機種 CM-MA**（**制御 VFGH**）。**3台群管理** 工事使用中、乗場2箇所の押釦が **連動点灯せず** バンク分割様（Lists 384）。

## 症状・現象

- 片方乗場: **#28,#29** 反応、他方: **#30** のみ → **2C-2BC**（Lists）
- Lists **対応中**（2025-01）

## ソース要約

### Lists（384）

- **症状**: 3car 群管理運転中に上記分割状態。
- **原因欄**: **GH1基盤とGP1基盤間で** — スナップショット **文途中で切れ**（詳細未記載）。
- **現象分類**: 接触不良（Lists）。

### OneNote

- **索引頁** `cf01bae3-86fc-4307-949e-3798361c2ee3:1`（`onenote-d05fbfbc0a7736e3a5d23b5d.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

3car 群管理で **2C-2BC** 表示のとき **GH1↔GP1 間** を Lists/OneNote 索引から追うが、**Lists 原因文は未完成** — 断定手順は載せない。群管理 **結線完了**・**371 給電** も併せ確認。

## 調査・確認手順

1. 群管理モニタ/押釦反応（#28–30）で 2C-2BC か確認。
2. 群管理盤—各制御盤 **結線完了**（OneNote 関連: 据付省力乗場モード不可事例）。
3. **GH1/GP1 間** コネクタ・配線（Lists 途中原因 — 現地最新 Lists 要確認）。
4. 群管理盤給電（[371](./KH-MR-GROUP-PANEL-POWER-371.md)、[253](../practice-guides/KH-VFGLF-GROUP-WIRING-SAVE-MODE-253.md) 索引）。

## 関連事例と条件の違い

| list | 状態 |
| --- | --- |
| **384** | 3car **2C-2BC**（対応中） |
| [371](./KH-MR-GROUP-PANEL-POWER-371.md) | 群管理盤 **電源抜け** |
| [253](../practice-guides/KH-VFGLF-GROUP-WIRING-SAVE-MODE-253.md) | 群管理 **配線セーブ** 索引 |
| **286/47** | [群管理異常の試験発報](../practice-guides/KH-ALL-GROUP-ALARM-TRIGGER-286.md) |
| [241](./KH-ALL-MONITOR-CRT-TELECO-241.md) | **監視盤 CRT** |
| [422](./KH-GS3-PART-NO-SCU20-422.md) | GS3 **LM2B** / SCU 通信 |
| [171](./KH-GROUP-ECAN-MAG-171.md) | 群管理 **E-CAN** |
| [92](./KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | **パニック** / 呼び |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |
| [371 群管理給電](./KH-MR-GROUP-PANEL-POWER-371.md) | 盤 **電源** |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §384（原因文不完全） |
| OneNote | cf01bae3…:1、a8c15103…:145 |
| KB | 群管理系統図（OneNote リンク・未レビュー） |

## 未確認事項

- Lists **384 原因・対策の全文**（スナップショット切れ）。
- 対応完了後の確定原因（status 対応中）。
