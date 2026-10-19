---


knowledge_id: KH-LINKS-UCAN-MMS-CABLE-222
kind: case_summary
status: draft
card_version: 1
title: "U-CAN 異常 — ドア MMS コネクタ線噛みで起動不能"
symptoms:
  - "U-CAN"
  - "204"
  - "207"
  - "-42-"
  - "MMS"
  - "PLG"
  - "ドアモーター"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  product_lines: ["AXIEZ-LINKs"]
  machine_room: ["MRL"]
  control_methods: ["VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "222"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:136"
    page_role: index
  - ref_type: kb_document
    document_number: "C-18-D31-K2.1-J"
    kb_verify_status: pending
---
# U-CAN 異常 — ドア MMS コネクタ線噛みで起動不能

## 使う場面・対象条件

**AXIEZ-LINKS** で **EV 起動不能**、制御盤 **204/207**、ドア基板 **-42-**（Lists 222）。

## 症状・現象

- **MON E/0** — **204**（CS 重故障）**207**（DC 重故障）、ドア基板 **伝送異常 -42-**（Lists）。
- **U-CAN 0V**、対地 **7V 程度**（Lists progress）。

## ソース要約

### Lists（222）

- **原因**: ドアモーター **MMS コネクタ** 線 **噛み込み** → **U-CAN 異常**（Lists）。
- **切分**: **PLG** 切離し U-CAN **~3V** 復帰 → モーター側 **圧痕**、**アンプ仮復旧**、OH で **モーター交換予定**（Lists progress）。
- 参考: C-8-S450.1-J、C-18-D60.2-J、C-6-S1200.1-J；**ASC(U-CAN)** は DC 基板 **5V 降下・ノイズ** も — **C-18-D31-K2.1-J**（Lists Notes — pending）。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:136`（`onenote-e18a48e912f86f9c533e4345.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

[414 ライン LED 地絡](./KH-VFGLF-LINE-LED-GROUND-414.md)・[407 気配り TX2](./KH-ALL-KEIAIN-DOOR-WIRING-407.md) と **421/-42- 系** 同桶 — 本件は **PLG→MMS 物理損傷**。Lists progress の **PLG 切離し電圧** を先に取る。

## 調査・確認手順

1. 204/207/-42- 確認。
2. **UCAH–UCAL**、対地電圧（Lists progress）。
3. **PLG** 切離し再測定。
4. ドアモーター **MMS/配線圧痕**。
5. C-18-D31-K2.1-J（5V/ノイズ — pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **222** | MMS 噛み・PLG |
| [414](./KH-VFGLF-LINE-LED-GROUND-414.md) | 照明 G1/G2 地絡 |
| [407](./KH-ALL-KEIAIN-DOOR-WIRING-407.md) | TX2 挟み・12V |

## KB確認に基づく追記

（C-18-D31-K2.1-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §222 |
| OneNote | a8c15103-95f4-4d08-897a-403d412bffb5:136 |
| KB | C-8-S450.1-J / C-18-D60.2-J / C-6-S1200.1-J / C-18-D31-K2.1-J（pending） |

## 未確認事項

- 仮復旧後の恒久交換完了（Lists 時点は OH 予定）。
