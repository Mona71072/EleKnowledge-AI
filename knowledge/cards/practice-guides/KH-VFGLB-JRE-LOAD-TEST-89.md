---
knowledge_id: KH-VFGLB-JRE-LOAD-TEST-89
kind: practice_guide
status: draft
card_version: 1
title: "JRE 仕様 — 点検 SW 時の負荷試験（リモコン 7C/75）"
symptoms:
  - "JRE"
  - "負荷試験"
  - "点検SW"
  - "リモコン"
  - "7C"
  - "75"
  - "VFGLB"
model_scope:
  lists_model_label:
    - "VFGLB"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLB"
  observed_on:
    - "VFGLB"
  may_apply_to:
    - "JRE で点検 SW 入り自動不可・負荷試験"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "89"
  - ref_type: kb_document
    document_number: "C-7-C3300.1"
    kb_verify_status: pending
---

# JRE 仕様 — 点検 SW 時の負荷試験（リモコン 7C/75）

## 使う場面・対象条件

**VFGLB JRE 仕様** — **かご内点検 SW** で **自動運転不可** → 通常 **09+点検 SW** 負荷試験ができない（Lists 89）。

## 症状・現象

- 負荷試験方法の問合せ（Lists）。

## ソース要約

### Lists（89）

- **リモコン 7C** → **中間位置表示**
- **リモコン 75** → **速度表示**
- 点検 SW なしで表示可。**中間位置と速度は同時不可** — **UP/DN 各 2 往復**（Lists）。
- **C-7-C3300.1** P34/P37（Lists）。

### OneNote

- なし。

## 統合した回答・ノウハウ

**437**（110% E-stop）/ **89**（**JRE 手順**）は別。**141**（JR 29 ラッチ）も JRE だが論点分離。

## 調査・確認手順

1. JRE 物件確認。
2. **7C** で中間位置 — UP/DN 往復。
3. **75** で速度 — UP/DN 往復。
4. C-7-C3300.1 節（pending）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **89** | **負荷試験** |
| **141** | **29 ラッチ** |

## KB確認に基づく追記

（C-7-C3300.1 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §89 |
| OneNote | なし |
| KB | C-7-C3300.1 |

## 未確認事項

- リモコンコマンド現行機種差 — KB 待ち。
