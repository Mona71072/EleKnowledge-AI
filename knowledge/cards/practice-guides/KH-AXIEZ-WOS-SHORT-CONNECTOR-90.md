---

knowledge_id: KH-AXIEZ-WOS-SHORT-CONNECTOR-90
kind: practice_guide
status: draft
card_version: 1
title: "AXIEZ-LINKS WOS用短絡コネクタの取外し誤り（本スロー後）"
symptoms:
  - "WOS"
  - "短絡コネクタ"
  - "RDS"
  - "RHQ"
  - "本スロー"
  - "AXIEZ-LINKS"
  - "走行不能"
  - "USL ON"
  - "かご上UP"
  - "着床プレート"
model_scope:
  observed_on:
    - "AXIEZ-LINKS"
  may_apply_to:
    - "WOS→本スロー切替・煙感知器点検口なし現場の短絡コネクタ作業"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "90"
    source_id: evidence-list-knowhow-id90
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:156"
  - ref_type: kb_document
    document_number: "短絡コネクタに関する注意点.ppt"
    kb_verify_status: not_in_catalog
    locator: ""
    summary_from_kb: ""
---
# AXIEZ-LINKS WOS用短絡コネクタの取外し誤り（本スロー後）

## 使う場面・対象条件

**AXIEZ-LINKS** で WOS 準備または **WOS から本スローへ切替** する際。Lists は ↑高 重要事例として二パターンの誤取外しを1節にまとめている。

## 症状・現象

**パターンA（WOS 準備・煙感知器点検口なし）**

- 製品添付 RDS を取外す作業で、稲電出荷時点で **R1 に既接続の RDS 短絡コネクタ** を誤廃棄
- **戸短コネクタなし** → 走行不能（自動も不可）

**パターンB（本スロー切替）**

- WOS 用短絡コネクタ取外し時に、**出荷時から短絡されていた RHQ コネクタ** まで取外し返却
- **かご上 UP** で着床プレート検出 → **USL ON 故障**、UP 運転不可

## ソース要約

### Lists（list_item_id 90）

- **教訓**: 不要コネクタ取外しが本スロー以降の不具合として散見。紛失時は手配が必要。
- **注意A**: 出荷段階から RDS に短絡コネクタ接続済みなら **治具 RDS は使わない**。
- **注意B**: 本スロー切替時は **黄色い電線入り短絡コネクタだけ** 取外す（RHQ は残す）。
- **参照**: 短絡コネクタ注意点 ppt（スナップショット未同梱）。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:156`（`onenote-1ce36975e184ab075d978bd7.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

WOS 関連作業では「取外すコネクタ」と「出荷時から付いている短絡」の区別が核心。RDS/RHQ を混同すると **走行不能** または **本スロー後のかご上 UP 制限** に直結する。既接続短絡がある現場では **治具側 RDS を追加しない**。本スロー切替は **黄色電線入り1種のみ** 外す。

## 調査・確認手順

1. 煙感知器点検口の有無と WOS 準備手順を確認。
2. R1 付近: 出荷時接続済み RDS 短絡の有無（あれば治具 RDS 不使用）。
3. 本スロー切替前: RHQ 短絡の位置を記録し、取外し対象を黄色電線コネクタに限定。
4. 切替後: 戸短・走行、かご上 UP＋着床プレートで USL 系を確認。
5. 不具合時: 紛失コネクタの手配要否（Lists 注意）。

## 関連事例と条件の違い

| テーマ | 90 | 345（別カード） |
| --- | --- | --- |
| 焦点 | RDS/RHQ 誤取外し | GAW→WOS DL/DP 等 |
| 機種 | AXIEZ-LINKS | LINKs 系 WOS 一般 |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §90 |
| OneNote | 索引 `…:156` |
| KB | ppt 参照 — 未突合 |

## 未確認事項

- OneNote リンク先詳細页・SF安全回路 PDF（索引末尾参照）本文。
- リスト ID87（RHQ 類似）との手順差分の現行版。
