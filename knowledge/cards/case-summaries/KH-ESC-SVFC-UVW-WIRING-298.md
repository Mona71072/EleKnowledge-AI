---
knowledge_id: KH-ESC-SVFC-UVW-WIRING-298
kind: case_summary
status: draft
card_version: 1
title: "SVFC UVW 結線ミス — E-1 001 / E-2 061"
symptoms:
  - "SVFC"
  - "UVW"
  - "E-1 001"
  - "E-2 061"
  - "走行"
  - "エスカレーター"
model_scope:
  lists_model_label:
    - "SVFC"
  product_lines:
    - "escalator"
  control_methods:
    - "SVFC"
  observed_on:
    - "SVFC"
  may_apply_to:
    - "エスが片方向だけ短走行で停止・キーン音"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "298"
  - ref_type: kb_document
    document_number: "C-60-631-VF31"
    kb_verify_status: pending
---

# SVFC UVW 結線ミス — E-1 001 / E-2 061

## 使う場面・対象条件

**product: エスカレーター SVFC**。ステップ半取付等で **UP/DN 片方向のみ短走行**（Lists 298、↑高）。

## 症状・現象

- **E-1 001**（インバータ異常）、**E-2 061**（コンバータ IPM 異常）。
- ブレーキ開・走行試行・**キーン**（Lists Notes）。

## ソース要約

### Lists（298）

- **原因**: **受電 JB 動力線結線ミス**（X/Y がテレコで **X-Y 取違え**）。
- **対応**: 結線修正で解消。
- **Notes**: EV は相順ミスで走行不可が多いが、**ES は回生方向のみ走行しうる** — 現象差に注意。C-60-631-VF31 **E-2 061** 参照。

### OneNote

- Lists §298 **タイトル一致なし**。UVW/相順の現象差（ES は回生方向のみ走行しうる）は **Lists Notes が正**。
- SVFC クラスタ: [325](./KH-ESC-SVFC-P2-FWR-TOGGLE-325.md)（P2 FWR）、[326](./KH-ESC-SVFC-STEP-CHAIN-GAP-326.md)（機械隙間）、[263](../practice-guides/KH-ESC-SVFC-TRACE-PUTTY-263.md)（トレース）。


## 統合した回答・ノウハウ

**298（UVW）** / **325（P2 FWR SW）** / **103・301（待機・センサ）** を切り分け。

## 調査・確認手順

1. 制御盤エラー（001/061）。
2. **受電 JB X/Y/Z** 相順・テレコ。
3. C-60-631-VF31 該当項。
4. 修正後走行試験（両方向）。

## 関連事例と条件の違い

| list | 原因 |
| --- | --- |
| **298** | **UVW** |
| [325](./KH-ESC-SVFC-P2-FWR-TOGGLE-325.md) | **P2 FWR** |
| [301](./KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301.md) | B センサ待機 |

## KB確認に基づく追記

（C-60-631-VF31 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §298 |
| OneNote | なし |
| KB | C-60-631-VF31 |

## 未確認事項

- 添付結線図は Lists のみ — KB 突合 pending。
