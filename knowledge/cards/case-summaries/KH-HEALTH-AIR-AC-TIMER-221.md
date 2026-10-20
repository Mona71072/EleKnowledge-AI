---
knowledge_id: KH-HEALTH-AIR-AC-TIMER-221
kind: case_summary
status: draft
card_version: 1
title: "ヘルスエア併設 — タイマーリレー 24V 誤品と AC 基板"
symptoms:
  - "ヘルスエア"
  - "エアコン"
  - "タイマーリレー"
  - "24V"
  - "200V"
  - "7SEG"
  - "AXIEZ-LINKS"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  machine_room:
    - "MRL"
  control_methods:
    - "AXIEZ-LINKS"
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "ヘルスエア電源投入後の異音・リレー破損・エアコン 7SEG 消灯"
  excludes: []
  scope_note: "duplicate primary: case-elv-health-air-aircon-relay-misselection-damage-id221。**98** は据付別件（リレー誤品）"
source_refs:
  - ref_type: lists_item
    list_item_id: "221"
---

# ヘルスエア併設 — タイマーリレー 24V 誤品と AC 基板

## 使う場面・対象条件

**AXIEZ-LINKS** **ヘルスエア併設エアコン** 設定後の **異音・リレー破損・エアコン不動**。**98**（タイマーリレー誤品で HA 単体不動）と **組立ミス経路** が Lists 上関連。

## 症状・現象

- ヘルスエア電源後 **大きな動作音** → 連続運転中 **タイマーリレー爆発**
- エアコン **7SEG 点灯せず**（Lists）

## ソース要約

### Lists（221）

- **報告原因**: **DC24V 用リレーを 200V 品に誤使用**（稲電回答 — 24V 品多・200V 品は週1 程度、ボルト確認未実施）。
- **対策（稲電）**: 保管場所掲示、キッティングシート、検査成績書に **電圧表示確認** 追加。
- **エアコン基板不点灯**: 原因 **不明**（Lists）、不具合品送付。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**98** と同系の **リレー定格取違え**。**221** は **ヘルスエア→エアコン連鎖** の現場事例。リレー本体の **電圧刻印** を Lists 稲電回答どおり確認。[207 SW6-3](../practice-guides/KH-ALL-HA-AC-DIP-SW6-207.md)・[206 抵抗方向](../practice-guides/KH-ALL-HA-RESISTOR-POLARITY-206.md) と **併設/据付** を分岐。

## 調査・確認手順

1. タイマーリレー **定格（24V vs 200V 系）**。
2. ヘルスエア単体 / 併設エアコン設定の切り分け。
3. エアコン基板 7SEG — Lists 上は返却調査待ちだった経路。
4. **98** カード（据付 HA リレー誤品）と照合。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **221** | ヘルスエア **併設 AC** |
| [98](./KH-HEALTH-AIR-TIMER-RELAY-98.md) | HA **単体** リレー誤品 |
| [158](./KH-HA-PANEL-ELECALL-158.md) | HA 盤 **エレコール**（別 duplicate） |
| [207](../practice-guides/KH-ALL-HA-AC-DIP-SW6-207.md) / [206](../practice-guides/KH-ALL-HA-RESISTOR-POLARITY-206.md) | 併設 **DIP** / 抵抗極性 |
| [225](./KH-VFGLF-HA-MONITOR-0V-225.md) | HA モニタ TR（情報管理保留） |
| [360](./KH-ALL-HA-MONITOR-R1-OPEN-360.md) | HA モニタ降圧 TR |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §221 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- エアコン基板不点灯の確定原因（Lists 時点不明）。
