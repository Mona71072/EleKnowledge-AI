---
knowledge_id: KH-ALL-MONITOR-CRT-TELECO-241
kind: case_summary
status: draft
card_version: 1
title: "監視盤 — CRT 通信線テレコで表示チラつき"
symptoms:
  - "監視盤"
  - "CRT"
  - "RCS"
  - "チラつき"
model_scope:
  lists_model_label: ["監視盤"]
source_refs:
  - ref_type: lists_item
    list_item_id: "241"
---

# 監視盤 — CRT 通信線テレコで表示チラつき

## 使う場面・対象条件

**監視盤** ランプ **チラつき**・**RCS 時間差**（Lists 241）。

## 症状・現象

- WPJB～WP の **CRT2/CRT4** 系（Lists）。

## ソース要約

### Lists（241）

- **原因**: EPS 内 **CRT2 と CRT4 がテレコ** のまま接続。
- **対応**: **CRT ライン導通** — 電気業者手直し。
- **Notes**: 他バンク **CRT 入替** でも **盤内ラッチ** で見え方に注意 — 添付詳細。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

群管理 **CRT** は [384](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) 等 **バンク分割** と切分 — **241** は **配線テレコ**。

## 調査・確認手順

1. **CRT ライン** 導通（Lists）。
2. EPS 内 **テレコ** 有無。
3. バンク **入替** 試験時の **ラッチ**（Lists Notes）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **241** | **CRT テレコ** |
| [422](../case-summaries/KH-GS3-PART-NO-SCU20-422.md) | **GS3** 通信 |

## KB確認に基づく追記

（Lists 添付 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §241 |

## 未確認事項

- progress は情報管理保留。
