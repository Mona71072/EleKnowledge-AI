---


knowledge_id: KH-ALL-FWCARD-MCENV-DEBUG-118
kind: practice_guide
status: draft
card_version: 1
title: "書換プログラム4 — パワーマネジメントエラー"
symptoms:
  - "書換プログラム"
  - "FwCard"
  - "McEnv.ini"
  - "debug"
model_scope:
  lists_model_label: []
  may_apply_to: ["メンテコン書換プログラム4利用時"]
source_refs:
  - ref_type: lists_item
    list_item_id: "118"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:99"
    page_role: hybrid
    note: "Lists タイトル一致 — snapshot `onenote-15468ff5c23b32fb76396b16.md`（本文未転載）"
---
# 書換プログラム4 — パワーマネジメントエラー

## 使う場面・対象条件

**書換プログラム4** で **パワーマネジメント関連エラー**（Lists 118）。Lists **Model 行なし** — メンテコン横断。

## 症状・現象

- 書換プログラム4使用時エラー（Lists）。

## ソース要約

### Lists（118）

- 特定ファイル書換済み。**McEnv.ini** の **debug=0→1**（2 か所）:
  - `C:\ProgramFilem\FwCard\ini\McEnv.ini`
  - `C:\ProgramFilem\FLASH\ini\McEnv.ini`
- **1 行目の debug** を変更（DEBUG 列と混同注意）（Lists）。

### OneNote

- **索引頁** `a8c15103-95f4-4d08-897a-403d412bffb5:99`（`onenote-15468ff5c23b32fb76396b16.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

Lists 記載パス・値どおり **debug 有効化** — 環境差は現場確認。

## 調査・確認手順

1. 両 McEnv.ini の 1 行目 debug。
2. 書換再実行。

## 関連事例と条件の違い

| テーマ | 備考 |
| --- | --- |
| **118** | McEnv debug |
| **130/119** | Putty 系 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §118 |

## 未確認事項

- ProgramFilem 表記は Lists 原文（typo 可能性）。
