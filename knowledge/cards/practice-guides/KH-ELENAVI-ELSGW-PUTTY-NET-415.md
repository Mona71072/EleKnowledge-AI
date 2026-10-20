---
knowledge_id: KH-ELENAVI-ELSGW-PUTTY-NET-415
kind: practice_guide
status: draft
card_version: 1
title: "ELSGW — PuTTY ログ採取と IP 設定"
symptoms:
  - "ELSGW"
  - "PuTTY"
  - "エレナビ"
  - "IPアドレス"
  - "通信"
model_scope:
  lists_model_label:
    - "エレナビ"
  observed_on: []
  may_apply_to:
    - "ELSGW から PuTTY でログ採取できない"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "415"
  - ref_type: kb_document
    document_number: "C-7-C3331.1"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-7-C3333.1"
    kb_verify_status: catalog_ambiguous
    note: "C-7-C3333.1-J-D.pdf / C-7-C3333.1-E-C.pdf — 機種別要選択"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:106"
    page_role: content
    note: "PuTTY/ELSGW 索引 — C-7-C3333 系"
---

# ELSGW — PuTTY ログ採取と IP 設定

## 使う場面・対象条件

**エレナビ** **ELSGW 盤** から **PuTTY** でログ採取 — **通信不可**（Lists 415）。

## 症状・現象

- PuTTY 通信確立せずログ採取不可（Lists）。

## ソース要約

### Lists（415）

- **原因**: ELSGW **ネットワークが標準と異なる** と客先と通信不可 — PC 側 IP/マスク/GW 変更も必要（Lists）。
- **ELSGW 側**: IP/マスク/GW は **ロータリー** 設定（Lists Notes）。
- **IDS** でデフォルト値と比較（Lists Notes）。
- 参照: **C-7-C3331.1** p10～、材料 **C-7-C3333.1**（Lists）。
- **progress**: PC 側 IP/マスク変更で対応（Lists）。

### OneNote（:106 抜粋）

- **ELSGW ネットワーク**: IDS で **デフォルトと一致** 確認（Lists 415 と同趣旨）。
- PuTTY 手順索引は [130](./KH-ELECALL-PUTTY-INSTALL-130.md)。**373** 工事 DOAS 頁にも ELSGW/PuTTY リンクあり — 混同しない。

## 統合した回答・ノウハウ

**263**（ESC PuTTY）/ **415**（**ELSGW IP**）は別系統。[336](./KH-ELENAVI-ISSUES-INDEX-336.md) エレナビ横断索引。

## 調査・確認手順

1. IDS vs デフォルトネットワーク。
2. ELSGW ロータリー IP/GW。
3. PC 側同一セグメント設定。
4. C-7-C3331.1（pending）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **415** | **ELSGW IP** |
| [130](./KH-ELECALL-PUTTY-INSTALL-130.md) | エレコール **PuTTY** |
| [336](./KH-ELENAVI-ISSUES-INDEX-336.md) | エレナビ **索引** |
| [263](../case-summaries/KH-ESC-SVFC-TRACE-PUTTY-263.md) | **ESC** トレース |
| [119](./KH-ELECALL-PUTTY-LOG-ADMIN-119.md) | PuTTY **管理者実行** |

## KB確認に基づく追記

（C-7-C3333.1 — **catalog_ambiguous**。C-7-C3331.1 同上。PDF 本文未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §415 |
| OneNote | `a8c15103-95f4-4d08-897a-403d412bffb5:106` | **content** `onenote-15fdf4b73ce899ff2c9eee95.md`（`read_this_page`）。子 content は `:107` `onenote-dbf139ed6555627dc834f457.md`、`:108` `onenote-2847082e91becb1e2d7049e4.md`（タイトル転記なし） |
| KB | C-7-C3331.1、C-7-C3333.1 |

## 未確認事項

- 標準 IP 値 — IDS/KB 未レビュー。
