---



knowledge_id: KH-LINKS-PSL-PIN-55
kind: case_summary
status: draft
card_version: 1
title: "LINKs — PSL ピン抜けで DN リレベル停止"
symptoms:
  - "847"
  - "PSL"
  - "リレベル"
  - "4m"
  - "15m"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "55"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:156"
    page_role: hybrid
    note: "監査適用 (title_hit) — `onenote-1ce36975e184ab075d978bd7.md`（navigation）"
---
# LINKs — PSL ピン抜けで DN リレベル停止

## 使う場面・対象条件

**AXIEZ-LINKS** **本スロー DN** で **リレベル噛み→停止・速度異常**、**847 PSL ON**（Lists 55① — **342②** は [KH-LINKS-PSL-PIN-S21-342](./KH-LINKS-PSL-PIN-S21-342.md)）。

## 症状・現象

- リレベル噛みで **一旦停止→再 DN で 4 m/min**、外れると **15 m/min**（Lists）。
- UP は正常（Lists）。
- リレベルコネクタ抜きで現象消える（Lists）。

## ソース要約

### Lists（55）

- **原因**: **下部終点 SW 内 S12 コネクタ ピン抜け** — 差し直し（Lists）。
- **切り分け**: DN 中 **PSL** で停止、R1 **RCA/RDT テレコなし**（HW01–04）（Lists）。
- **progress**: タイラップ固定不足で再抜け → **代品手配**（Lists）。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:156`（`onenote-1ce36975e184ab075d978bd7.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

847＋リレベル DN 異常は **終点 SW 内コネクタ** を Lists 上優先。

## 調査・確認手順

1. **847** 再現条件（DN・リレベル）。
2. かご上 ST **リレベルコネクタ** 抜き試験（Lists）。
3. **下部終点 S12** ピン・固定。
4. RCA/RDT テレコ（ストレート — pending）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **55** | ① **S12** ピン |
| **342** | [② S21 ピン](./KH-LINKS-PSL-PIN-S21-342.md) |
| [392 本スロー BK](./KH-VFGLF-BRAKE-SW-392.md) | 同 **`:156`** 索引（終点 SW 系） |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §55 |

## 未確認事項

- ATHO07121 と 342 の対応関係。
