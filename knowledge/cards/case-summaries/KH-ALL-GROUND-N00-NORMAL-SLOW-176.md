---
knowledge_id: KH-ALL-GROUND-N00-NORMAL-SLOW-176
kind: case_summary
status: draft
card_version: 1
title: "N00 アース未結線 — 531 HDRN 本スロー不可"
symptoms:
  - "アース"
  - "N00"
  - "HDRN"
  - "531"
  - "本スロー"
  - "WOS"
  - "カゴ下JB"
  - "RCA"
model_scope:
  lists_model_label:
    - "全エレ機種"
  machine_room: []
  control_methods: []
  observed_on: []
  may_apply_to:
    - "WOS→本スロー切替後ポータブル不能・531 HDRN"
  excludes: []
  scope_note: "duplicate primary: case-elv-normal-slow-unavailable-ground-connection-id176"
source_refs:
  - ref_type: lists_item
    list_item_id: "176"
---

# N00 アース未結線 — 531 HDRN 本スロー不可

## 使う場面・対象条件

**WOS から本スロー** 後、**機械室・かご上ポータブル不能** で **531（HDRN on 故障）** のとき（Lists 176・全エレ機種表記）。

## 症状・現象

- 本スロー切替後 **ポータブル不能**
- **531 … HDRN on 故障**
- RCA **HDRN**: 挿入時 **20–30V 不安定**、抜くとコネクタ側 **100V 安定**（Lists）

## ソース要約

### Lists（176）

- **J2 他信号**: **N00** も HDRN 同様の異常電圧。
- **原因**: **カゴ下 JB** で **N00 アース線未結線** → ターミナル結線後 **0V**、**ポータブル運転可**。HDRN に **不安定電圧**（アース未落ち **逆流** 推測）。
- **Notes**: 類似時は **同コネクタ他信号電圧** と **アースライン** 確認。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

HDRN だけ見ず **N00** と **カゴ下 JB アース** を Lists 176 の切り分けどおり。不安定・中途半端電圧は **アース** 疑い。

## 調査・確認手順

1. 531 / HDRN 表示確認。
2. R1 **RCA** HDRN 電圧（挿抜比較 — Lists パターン）。
3. **J2 内 N00** 等の他信号電圧。
4. **カゴ下 JB** N00 **アース** 結線。
5. 本スロー・ポータブル再試験。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **176** | **N00 アース**・531 |
| [392](./KH-VFGLF-BRAKE-SW-392.md) | BK1 ストローク（VFGLF）・**`:156`** 索引 |
| [83](./KH-LINKS-TERM128-EARTH-83.md) | アース **128 番誤結線**（別 list） |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §176 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- progress **保留**（識別情報）。
- 個別機種・JB 図番（Lists 未記載）。
