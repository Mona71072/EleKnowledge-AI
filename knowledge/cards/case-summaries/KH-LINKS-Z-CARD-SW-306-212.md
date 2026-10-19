---
knowledge_id: KH-LINKS-Z-CARD-SW-306-212
kind: case_summary
status: draft
card_version: 1
title: "306 Z 系カード重故障 — SW Z11 設定不一致"
symptoms:
  - "306"
  - "Z系カード"
  - "Z11"
  - "10090924"
  - "群管理"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  product_lines: ["AXIEZ-LINKs"]
  machine_room: ["MRL"]
  control_methods: ["VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "212"
  - ref_type: kb_document
    document_number: "C-8-S450.1-J"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-8-D-S438.90-J"
    kb_verify_status: pending
---

# 306 Z 系カード重故障 — SW Z11 設定不一致

## 使う場面・対象条件

**AXIEZ-LINKS** 引渡前 **MON E/0 → 306**（Z 系カード重故障）（Lists 212）。

## 症状・現象

- **306**、群管理 **#9/#10** もエラー（Lists progress）。
- 群管理 **MODE/DATE** 8~9/1~F、**LED2/3=F/F** 等（Lists progress）。

## ソース要約

### Lists（212）

- **原因**: **SW で Z11 カード有り** — **アドレス 10090924 データ 11→41** 変更で良好（Lists）。
- **備考**: MODE/DATE=A/A、LED2/3=8/7 は **エレコールサービス切放し** で問題なし（Lists Notes）。
- progress: 結線・イーサネット問題なし → **稲電 SW 不良**（Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[39 専用運転 Z11](./KH-KM-LD-DEDICATED-MODE-39.md) は **KM-LD キー SW** — **212** は **群管理オプション Z カード SW**。306 単独でも **SW 書換** を Lists どおり疑う。

## 調査・確認手順

1. C-8-S450.1-J で **306** 意味（pending）。
2. 群管理盤 **Z 系**・**#9/#10**（Lists progress）。
3. **SW 10090924** データ **11 vs 41**（Lists）。
4. C-8-D-S438.90-J（pending）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **212** | Z カード SW |
| [39](./KH-KM-LD-DEDICATED-MODE-39.md) | Z11 24V 専用運転 |

## KB確認に基づく追記

（C-8-S450.1-J / C-8-D-S438.90-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §212 |
| KB | C-8-S450.1-J / C-8-D-S438.90-J（pending） |

## 未確認事項

- Z11 有無と現場オプション構成の突合手順（KB 未照合）。
