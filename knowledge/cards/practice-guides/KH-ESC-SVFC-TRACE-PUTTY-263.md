---
knowledge_id: KH-ESC-SVFC-TRACE-PUTTY-263
kind: practice_guide
status: draft
card_version: 1
title: "SVFC — トレースデータ採取（PuTTY）"
symptoms:
  - "トレース"
  - "PuTTY"
  - "SVFC"
  - "E-1"
  - "パラメータ"
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
    - "P2 パラメータ確認・周波数異常調査時のログ採取"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "263"
---

# SVFC — トレースデータ採取（PuTTY）

## 使う場面・対象条件

**product: エスカレーター SVFC**。**P2 パラメータ** 等の調査で **トレースデータ** が必要なとき（Lists 263）。事例文脈は **電源周波数 60Hz 表示** と **E-1 系**（Lists）。

## 症状・現象

- Lists 記載: 動作せず **E-1 305（電源位相異常 PLL）**、P2 で **60Hz**（Lists symptoms / error 行は **E-1 301** もあり — スナップショットどおり両方索引）。

## ソース要約

### Lists（263）

- **トレースデータは PuTTY で採取可能**（Lists cause/response）。
- ステータス: 対応不要（Lists）。

### OneNote

- なし。

## 統合した回答・ノウハウ

周波数・位相の **原因切り分け** は **427** 正本。**263** は **採取手段（PuTTY）** の索引。

## 調査・確認手順

1. 現象・E-1 コードを Lists/現場ログで確認。
2. P2 パラメータ（周波数等）。
3. **PuTTY** でトレース採取（Lists）。
4. 周波数不一致疑い → **427** / RSW 手順。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **263** | **PuTTY 採取** |
| **427** | **周波数/RSW** 不一致 |

## KB確認に基づく追記

（Lists のみ — KB 未指定）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §263 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- PuTTY 接続条件・ポート — Lists に手順なし（427/ESC 資料待ち）。
