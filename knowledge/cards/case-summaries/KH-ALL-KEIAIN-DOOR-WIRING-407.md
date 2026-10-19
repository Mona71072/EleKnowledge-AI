---

knowledge_id: KH-ALL-KEIAIN-DOOR-WIRING-407
kind: case_summary
status: draft
card_version: 2
title: "気配りドア配線挟み込みでカゴ内・上運転不可"
symptoms:
  - "気配りドア"
  - "挟み込み"
  - "WDT"
  - "地絡"
  - "TX2"
  - "本スロー"
  - "ETP"
  - "12V"
  - "5V"
model_scope:
  lists_model_label:
    - "全エレ機種"
  product_lines: []
  control_methods: []
  door_families: []
  door_types:
    - "気配りドア付"
  model_abbreviations: []
  scope_note: "Lists Model=全エレ — 適用は気配りドア配線がある構成"
  observed_on: []
  may_apply_to:
    - "気配りドア信号線（TX2 等）・レゾルバ/HMS ライン付加現場"
  excludes:
    - "気配りドア無しの LV5K-only 戸型調整（432/433 系）"
source_refs:
  - ref_type: lists_item
    list_item_id: "407"
    source_id: evidence-list-keiain-door-wiring-407
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:156"
---
# 気配りドア配線挟み込みでカゴ内・上運転不可

## 使う場面・対象条件

**door_types: 気配りドア付**（Lists Model は **全エレ機種** だが、内容は **気配りドア配線** 限定）。**本スロー切替後**、**カゴ内・上運転不可**（**ETP は可**）。

## 症状・現象

- 本スロー後カゴ内・上運転不可
- 制御盤 MON エラーなし（Lists 記載）
- ドア駆動基板チェックピン: +5≈3V、±12V≈0V

## ソース要約

### Lists（list_item_id 407）

- **判断**: 12V 未印加または地絡 → **気配りドア・レゾルバ・HMS ライン** を順次遮断し **WDT 点灯** を確認。
- **特定**: **気配りドアライン遮断** で WDT 点灯。**TX2 ケーブル** をバインド締め過ぎ→内部傷・地絡推測。
- **WDT**: CPU 異常で消灯、消灯時リセット（Lists Notes）。
- progress: 保留。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:156`（`onenote-1ce36975e184ab075d978bd7.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

±12V 喪失と WDT は **気配りドア系地絡** を疑う。Lists 407 は **TX2 の締め付け挟み** が典型。本スロー後初出でも **配線束の締め付け痕** を見る。制御方式問わず横断。

## 調査・確認手順

1. ドア駆動基板 +5/±12V チェックピン。
2. 気配りドア→レゾルバ→HMS ライン遮断で WDT 変化。
3. TX2 走査・バインド締め痕。
4. 地絡修復後 WDT・カゴ内/上運転確認。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **407** | TX2 挟み・12V 系 |
| [408](./KH-VFGH-KEIAIN-HMS-DOOR-408.md) | 戸閉 HMS/警報 |
| [222](./KH-LINKS-UCAN-MMS-CABLE-222.md) | MMS 噛み・U-CAN |
| [382](./KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) | **TX1** 挟み・12V |
| [424](./KH-ALL-KEIAI-RX1-PINCH-424.md) | **RX1** 2C-2BC |
| [414](./KH-VFGLF-LINE-LED-GROUND-414.md) | ライン LED **421** |
| [392](../case-summaries/KH-VFGLF-BRAKE-SW-392.md) | U-CAN 索引 **`:156`** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断 |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §407 |
| OneNote | 索引 `a8c15103-…:156` |
| KB | なし |

## 未確認事項

- progress 保留。機種別配線図。
