---
knowledge_id: KH-MRL-LANDING-NS-RSW-FW-184
kind: case_summary
status: draft
card_version: 1
title: "乗場 NS テンキー — インジ CPU RSW FW=1"
symptoms:
  - "NS"
  - "NSHR-T"
  - "テンキー"
  - "RSW"
  - "FW"
  - "M3"
model_scope:
  lists_model_label: ["MRL機種"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "184"
---

# 乗場 NS テンキー — インジ CPU RSW FW=1

## 使う場面・対象条件

**MRL** 調整で **NS テンキー解除（NSHR-T）** — **PAS 入力後 呼び登録不可**（Lists 184）。

## 症状・現象

- テンキー **DC12V 正常** も **乗場釦不点灯**（Lists progress）。

## ソース要約

### Lists（184）

- **原因**: 品目表改定 **RSW FW=0→1** — 現地 **FW=0** のまま（Lists）。
- **FW=0**: **全階床**（HOP 等）。**FW=1**: **その NS 解消のみ**（Lists Notes）。
- **FW=1** で良好（Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[292 予約 RSW](../practice-guides/KH-ALL-RESERVE-TIMER-RSW-292.md)・[315 NS 点滅](../practice-guides/KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) と **RSW/NS** 同桶 — **184** は **FW ビット**。

## 調査・確認手順

1. **M3** 抜き **テンキー 12V**（Lists progress）。
2. 乗場インジ CPU **RSW FW**（Lists）。
3. 品目表 **最新 FW 指定**（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **184** | NS FW |
| [292](../practice-guides/KH-ALL-RESERVE-TIMER-RSW-292.md) | 予約タイマー |
| [315](../practice-guides/KH-LINKS-NS-TEMP-RELEASE-BLINK-315.md) | NS 仕様変更 |
| [171](./KH-GROUP-ECAN-MAG-171.md) | E-CAN/群管理 |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §184 |

## 未確認事項

- 制御方式別 FW 既定（Lists は MRL 一般）。
