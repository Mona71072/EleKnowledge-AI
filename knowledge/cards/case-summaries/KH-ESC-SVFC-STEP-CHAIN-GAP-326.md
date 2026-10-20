---
knowledge_id: KH-ESC-SVFC-STEP-CHAIN-GAP-326
kind: case_summary
status: draft
card_version: 1
title: "SVFC チェーン隙間 — DN 異音ゴンゴン"
symptoms:
  - "SVFC"
  - "異音"
  - "ステップ"
  - "ブロックトラック"
  - "BG調整"
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
    - "上部 DN 異音・ローラがトラックに非接触"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "326"
  - ref_type: onenote_page
    onenote_id: "c3c2f392-7d60-46db-b6a4-f3973a5f37e4:80"
    page_role: content
    note: "SVFC 据付メモ — ブロックトラック/スプロケット（Lists 326 と整合）"
---

# SVFC チェーン隙間 — DN 異音ゴンゴン

## 使う場面・対象条件

**SVFC** **DN 運転** で上部 **ゴンゴン異音** — 特定ステップで **ローラがブロックトラック非接触**（Lists 326）。

## 症状・現象

- 隙間 **1mm 超** — ハサミ金でトラック移動すると **スプロケット隙間消失**（Lists）。
- **上部右** チェーン–スプロケット **0.5mm 未満**（基準 **0.5mm 以上**）。

## ソース要約

### Lists（326）

- **原因**: 右隙間不足 → ステップ流れ左寄り → 左ローラ浮き。
- **対応**: **帰路駆動レール BG 調整**（IN-ES-0B-019-26）、トラック接触確認。
- **Notes**: スカート隙間調整済なら **再確認**。B 組心出しは工場だが **現地確認**。

### OneNote（`c3c2f392-7d60-46db-b6a4-f3973a5f37e4:80`）

- **ブロックトラックとスプロケット**: 駆動ローラが中心を通るよう整える。基準外は片寄り→**脱輪**リスク（Lists 326 の隙間・ローラ浮きと同軸）。
- **DN 運転での DCS 確認**: チェーン張力が出ている状態で測定が必要、等の据付メモあり（326 本体は Lists の BG 調整・0.5mm 基準を正）。
- 横断メモ（B/C センサ、手巻き等）は [301](./KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301.md)・[263](../practice-guides/KH-ESC-SVFC-TRACE-PUTTY-263.md) クラスタ — **本カードへ混載しない**。


## 統合した回答・ノウハウ

**301/103**（センサ待機）と **326**（機械隙間）は別軸。

## 調査・確認手順

1. 異音ステップ特定・ローラ/トラック。
2. チェーン–スプロケット隙間 **0.5mm+**。
3. BG 調整（据付ノート）。
4. スカート隙間再調整。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **326** | **機械隙間** |
| [301](./KH-ESC-ALL-B-SENSOR-SLOW-STANDBY-301.md) | **B センサ** |
| [325](./KH-ESC-SVFC-P2-FWR-TOGGLE-325.md) | P2 **FWR** |
| [263](../practice-guides/KH-ESC-SVFC-TRACE-PUTTY-263.md) | SVFC **トレース** |

## KB確認に基づく追記

（IN-ES-0B-019-26 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §326 |
| OneNote | c3c2f392…:80（据付メモ・要約） |
| KB | IN-ES-0B-019-26 |

## 未確認事項

- IN-ES-0B-019-26 本文 — pending。
