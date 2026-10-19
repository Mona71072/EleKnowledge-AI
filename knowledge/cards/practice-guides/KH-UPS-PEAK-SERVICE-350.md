---
knowledge_id: KH-UPS-PEAK-SERVICE-350
kind: practice_guide
status: draft
card_version: 1
title: "UPS（アップピーク）不作動と監視盤・群管理の制御優先"
symptoms:
  - "UPS"
  - "アップピークサービス"
  - "群管理"
  - "監視盤"
  - "VFGLF"
  - "VFGLB"
  - "VFGH"
  - "混雑"
  - "最下階乗場"
  - "BE28"
  - "DPS"
  - "LTS"
model_scope:
  observed_on:
    - "VFGLF"
    - "VFGLB"
    - "VFGH"
  may_apply_to:
    - "ΣAI-2200C 系で UPS/DPS/LTS/IUP 等が付加され監視盤付きの現場"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "350"
    source_id: evidence-list-ups-control-source-mismatch-350
  - ref_type: onenote_page
    onenote_id: "a556a262-6275-4d00-b70a-c492c569169a:1"
  - ref_type: onenote_page
    onenote_id: "1e0ad6f4-e63b-463a-bc40-8a9000843691:1"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:145"
  - ref_type: kb_document
    document_number: "群管理モニタ使用方法 47P"
    kb_verify_status: not_in_catalog
    locator: ""
    summary_from_kb: ""
---

# UPS（アップピーク）不作動と監視盤・群管理の制御優先

## 使う場面・対象条件

引渡し前後で **UPS（アップピーク）・DPS・LTS** 等の時間帯サービスが付加され、**PC 式監視盤** がある現場。Lists 事例は VFGLF/VFGLB/VFGH。混雑時の最下階乗場前など、客先で「UPS が動いていない」と判明しやすい。

## 症状・現象

- 引渡し後、最下階乗場前で混雑すると UPS が動作していないと判明
- 群管理モニターで強制 UPS を掛けても動作しない
- エラー表示なし（Lists 350）

## ソース要約

### Lists（list_item_id 350）

- **原因（報告）**: 稲電側 S/W 設定の食い違い。監視盤に UPS 制御が無いのに、UPS が **監視盤制御あり** になっており、群管理 S/W 側設定が実質無効。
- **メカニズム（報告）**: 監視盤 UPS 制御あり S/W では監視盤制御が優先され、群管理 S/W による UPS は選ばれない。**予約時刻を設定しても無効**。
- **教訓**: ΣAI-2200C 標準仕様で UPS がある前提の確認不足。引渡し前に混雑関連動作を確認。監視盤付きでは UPS/DPS/LTS 各動作に注意。
- **確認方法（Lists）**: メンテコンで予約操作・負荷値変更で UPS 動作確認可能。**群管理モニタ使用方法 47P**（KB 未突合）。

### OneNote 詳細

**ページ `a556a262-…:1`**（群管理技術メモ系）

- 監視盤からの制御・表示がなくても **UPS 等の動作確認は必須**。
- PC 式監視盤パラメータ（有=01 / 無=00）:
  - UPS 制御: **BE28**
  - LTS 制御: **BE29**
  - DPS 制御: **BE2A**
  - BSO 制御: **BE2B**
- いずれかが **有** のとき監視盤制御優先 → 群管理 S/W の UPS/DPS/LTS/IUP は同様に無効化されうる。

**ページ `1e0ad6f4-…:1`**（UPS/DPS 動作確認メモ）

- 負荷変動検知のため **主階床で 20% 乗降後** に負荷設定。
- 標準予約時間はオフィス・ホテル・住宅で異なる。
- 群管理モニタ利用時は一台に **保守合理化 S/W** を入れておく。
- ホテル・住宅は UPS/DPS アナウンス無し設定に注意（UPS 標準時間が夕方のため）。
- 添付 **UPS,DPS動作確認方法.pptx** はスナップショット未同梱。

**索引 `a8c15103-…:145`**

- 技術情報リストに本件タイトルへのリンク行あり（本文は上記ページへ）。

## 統合した回答・ノウハウ

UPS が「群管理で掛からない」ときは、まず **監視盤側 BE28〜BE2B が「制御あり」になっていないか** と、Lists/OneNote が述べる **制御元の優先関係** を疑う。**JB 設置** は [211 監視盤取付](./KH-LINKS-MONITOR-JB-MOUNT-211.md)。引渡し前 **ELE-QUICK 灯** は [168](./KH-ALL-ELEQUICK-LAMP-TEST-168.md)。監視盤制御ありのままでは群管理の強制 UPS・予約時刻は効かない。引渡し試験では混雑想定の階・時間帯で、メンテコンまたは OneNote 記載の負荷・予約手順で **実動** を確認する。

## 調査・確認手順

1. 付加サービス（UPS/DPS/LTS/IUP）と監視盤の有無を構成表で確認。
2. PC 式監視盤なら **BE28（UPS）** 他、Lists/OneNote 記載アドレスが 01（有）か確認。
3. 01 の場合、監視盤側の UPS 制御・連携を優先して確認（群管理だけで判断しない）。
4. メンテコンで予約・負荷変更による UPS 試験（Lists: 47P 参照 — KB 未確認）。
5. OneNote 手順: 主階 20% 乗降後負荷設定、仕様別予約時間、必要なら保守合理化 S/W 準備。

## 関連事例と条件の違い

| 条件 | 本カード（350） | 備考 |
| --- | --- | --- |
| 制御元 | 監視盤「あり」設定 vs 実機無制御 | 設定食い違い |
| 確認タイミング | 引渡し後・混雑時 | 事前試験推奨 |

## KB確認に基づく追記

（未実施 — 47P 等は `kb_verify_status: not_in_catalog`）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §350 |
| OneNote | `a556a262-6275-4d00-b70a-c492c569169a:1`, `1e0ad6f4-e63b-463a-bc40-8a9000843691:1`, 索引 `…:145` |
| KB | 群管理モニタ 47P — カタログ未突合 |

## 未確認事項

- 監視盤「UPS 制御無」現場での BE28 推奨値の正式表（KB/PDF 未レビュー）。
- UPS,DPS 動作確認パワポ本文（OneNote 添付未同梱）。
