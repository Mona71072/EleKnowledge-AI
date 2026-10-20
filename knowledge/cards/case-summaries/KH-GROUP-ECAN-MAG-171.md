---

knowledge_id: KH-GROUP-ECAN-MAG-171
kind: case_summary
status: draft
card_version: 1
title: "E-CAN MAG 未接続 — NS 不能と群管理 GC エラー読取"
symptoms:
  - "E-CAN"
  - "MAGコネクタ"
  - "群管理"
  - "NS"
  - "切り放し"
  - "新AXIEZ"
  - "3Car"
model_scope:
  lists_model_label:
    - "群管理盤"
  machine_room: []
  control_methods: []
  observed_on: []
  may_apply_to:
    - "群管理 NS 不動・E-CAN 通信エラー疑い"
  excludes: []
  scope_note: "duplicate primary: case-elv-e-can-special-operation-hall-call-failure-id171。索引 elv-group-operation-issues は事例根拠にしない"
source_refs:
  - ref_type: lists_item
    list_item_id: "171"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:145"
  - ref_type: kb_document
    document_number: "C-8-S438.1"
    kb_verify_status: pending
---
# E-CAN MAG 未接続 — NS 不能と群管理 GC エラー読取

## 使う場面・対象条件

**群管理盤** 系で **NS（特殊運転）が動かない**、**E-CAN 通信エラー** 疑い。**371**（群管理給電）・**384**（3car 群管理）と配線論点が異なる場合あり。

## 症状・現象

- Lists **症状欄保留**（情報管理）
- **切り放し** は調整時 OK、官検時未確認の報告（Lists 原因欄）

## ソース要約

### Lists（171）

- **原因（報告）**: **E-CAN ライン（MAG コネクタ）未接続** — 群管理盤から各台へ管制・群管理信号。
- **状況**: 制御盤下 **奥** のコネクタ — 調整確認後、官検等の **蓋開閉で外れた** 可能性（Lists）。
- **Notes**: 新 AXIEZ・3Car・SAI-22 — 添付 **群管理盤 GC カード上のエラー読取** 参照。
- **参照**: C-8-S438.1。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:145`（`onenote-c75d78f366e15996a2b04bde.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

調整で一度 OK でも **MAG 嵌合** は官検・メガー後に再確認。Lists 添付の **GC エラー読取** とセット（本文未同梱）。

## 調査・確認手順

1. NS / 切り放しの再現条件（官検前後）。
2. **MAG コネクタ** 嵌合（制御盤下・奥）。
3. E-CAN ライン（Lists 定義: 群管理盤↔各 ELV）。
4. GC カード上エラー表示（Lists 添付資料）。
5. **371** 給電欠落の除外。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **171** | **E-CAN / MAG** |
| [371](./KH-MR-GROUP-PANEL-POWER-371.md) | 群管理 **電源線** |
| [384](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 3car **2C-2BC** |
| [422](./KH-GS3-PART-NO-SCU20-422.md) | GS3 **LM2B** / SCU |
| [184](./KH-MRL-LANDING-NS-RSW-FW-184.md) | 乗場 NS **FW** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §171 |
| OneNote | a8c15103-95f4-4d08-897a-403d412bffb5:145 |
| KB | C-8-S438.1（pending） |

## 未確認事項

- Reported symptoms / progress **保留**。
- 添付 GC エラー読取のスナップショット未同梱。
