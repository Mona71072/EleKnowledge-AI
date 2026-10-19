---
knowledge_id: KH-VFGH-KEIAIN-HMS-DOOR-408
kind: case_summary
status: draft
card_version: 2
title: "戸閉時の気配りドアセンサーとHMS動作不良"
symptoms:
  - "気配りドア"
  - "HMS"
  - "VFGH"
  - "ピーピー"
  - "戸反転"
  - "戸閉"
  - "-33b"
model_scope:
  lists_model_label:
    - "VFGH"
  product_lines:
    - "Nexcube"
  control_methods:
    - "VFGH"
  door_families: []
  door_types:
    - "気配りドア付"
    - "HMS"
  model_abbreviations: []
  observed_on:
    - "VFGH（Lists Model。戸型コードは未記載）"
  may_apply_to:
    - "気配りドアセンサー・HMS 付加現場（制御は VFGH 以外も起きうる — Lists 外は未確認）"
  excludes:
    - "LV5K/LV6K 戸型のみの調整・CLT 不具合"
source_refs:
  - ref_type: lists_item
    list_item_id: "408"
    source_id: evidence-list-keiain-hms-door-408
  - ref_type: onenote_page
    onenote_id: "97d4ebd4-396d-4083-b8ca-0bf27391d4ea:1"
---

# 戸閉時の気配りドアセンサーとHMS動作不良

## 使う場面・対象条件

**door_types: 気配りドア付 + HMS** が前提。**Lists Model=VFGH** は制御ラベル。 **戸閉時** に気配りドアセンサーが干渉なく **連続警報音**、**HMS 手かざしで戸反転しない**（Lists 408）。

## 症状・現象

- 戸閉・非干渉でも「ピーピー」鳴動
- 戸閉 HMS に手をかざしても戸反転しない
- エラー表示: **-33b-**（Lists。意味は未独立確認）

## ソース要約

### Lists（list_item_id 408）

- **対応（報告）**: 東流より新しい基板を取寄せ交換。
- **progress / Notes**: 情報管理確認まで **保留**（スナップショット伏せ字）。

### OneNote

**索引 `97d4ebd4-…:1`** に **[HMS動作不具合時の確認について](list 316 タイトル)** 等のリンク行あり。本件 **408 タイトル一致页なし**。詳細手順はリンク先未取得。

## 統合した回答・ノウハウ

戸閉中の気配り/HMS 同時異常は Lists 408 では **基板交換** で解消報告。**T2/T3 誤結線** は [352](./KH-VFGH-HMS-MBS-T2T3-352.md) 索引。現場 progress は保留のため **切り分け手順は Lists 本文に無い**。HMS 一般確認は OneNote 索引 **316 系** を別途辿る（未取得）。

## 調査・確認手順

1. 現象を戸閉・戸開・干渉有無で切り分け記録。
2. 表示 **-33b-** を VFGH エラー参照（Vault `ELV_VFGH制御エラー` — 表本体未写し）と照合予定。
3. Lists 保留解除後 progress を追記。
4. OneNote list 316 / HMS 確認页（リンク解決後）。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **408** | 戸閉・警報+HMS |
| [352](./KH-VFGH-HMS-MBS-T2T3-352.md) | HMS/MBS 誤配線逆動作 |
| [407](./KH-ALL-KEIAIN-DOOR-WIRING-407.md) | 気配り配線挟み・WDT |
| [382](./KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) | TX1 挟み |
| [424](./KH-ALL-KEIAI-RX1-PINCH-424.md) | RX1 2C-2BC |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §408 |
| OneNote | 索引 `97d4ebd4-396d-4083-b8ca-0bf27391d4ea:1` |
| KB | なし |

## 未確認事項

- progress 保留内容・-33b- 定義。
- 交換基板の型式・東流手配の正式記録。
