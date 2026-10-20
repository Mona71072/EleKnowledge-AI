---
knowledge_id: KH-ELECALL-PUTTY-LOG-ADMIN-119
kind: practice_guide
status: draft
card_version: 1
title: "Putty — ログが保存されない（管理者実行）"
symptoms:
  - "putty.log"
  - "ログ採取"
  - "管理者として実行"
model_scope:
  lists_model_label: ["エレコール"]
  product_lines: ["elecall"]
source_refs:
  - ref_type: lists_item
    list_item_id: "119"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:106"
    page_role: content
    note: "Putty まとめ頁 — 130 と共有索引"
---

# Putty — ログが保存されない（管理者実行）

## 使う場面・対象条件

**エレコール** 保守で **Putty ログ** が保存されない（Lists 119）。**130**（インストール）とセット。

## 症状・現象

- `putty.log` が保存先に無い（Lists）。

## ソース要約

### Lists（119）

- **管理者として Putty 未実行** → C ドライブにログ作成不可。**右クリック→管理者として実行**（Lists）。

### OneNote

- PuTTY 共通索引 [130](./KH-ELECALL-PUTTY-INSTALL-130.md) と **同一頁**（:106）。**119 固有**は Lists の管理者実行のみ。

## 統合した回答・ノウハウ

ログ採取前に **管理者起動** — パス設定だけでは足りない。

## 調査・確認手順

1. Putty を管理者実行。
2. ログ設定・保存先再試行。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **119** | ログ |
| **130** | インストール |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §119 |

## 未確認事項

- OS 版による保存先差。
