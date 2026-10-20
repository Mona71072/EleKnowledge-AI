---
knowledge_id: KH-VFGLF-ICAN-HALL-BACKUP-417
kind: case_summary
status: draft
card_version: 3
title: "VFGLFで乗場バックアップができない"
symptoms:
  - "I-CAN"
  - "乗場バックアップ"
  - "E30"
  - "MON1/0"
  - "VFGLF"
  - "電気的"
model_scope:
  lists_model_label:
    - "VFGLF"
  product_lines:
    - "AXIEZ-LINKs"
  model_abbreviations: []
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to: []
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "417"
    source_id: evidence-list-vfglf-i-can-hall-backup-id417
  - ref_type: draft_record
    record_id: case-elv-vfglf-i-can-disconnected-hall-backup-unavailable-id417
    note: "Lists 417 の draft 写し"
review_status: in_review
publication_status: not_published
cloud_approval: not_reviewed
---

# VFGLFで乗場バックアップができない

## 使う場面・対象条件

- VFGLF で **I-CAN 未接続** が疑われ、**乗場バックアップ**ができない
- 据付完了後の MON 表示に **E30** が出ている（Lists スナップショット）

## 症状・現象

- 乗場バックアップ不可（Lists タイトル・分類: 電気的）
- エラー表示: MON1/0→E/0、【E30】（据付完了後のため **2 桁エラーのみ**、Lists 記載）
- 症状・原因・Notes の自由記述はスナップショット上 **情報管理確認まで保留**

## ソース要約

### Lists（list_item_id: 417）

| 項目 | 内容 |
| --- | --- |
| タイトル | I-CAN 未接続により乗場バックアップできない |
| 機種 | VFGLF |
| 重要度 | 高 |
| ステータス | 対応済み |
| 共有日 | 2026/02/16 |
| エラー表示 | （MON1/0→E/0）【E30】 |
| 症状・原因・Notes | 保留（識別情報を含む可能性） |

### OneNote

- **同一タイトル**（I-CAN / Lists 417）の専用ページ: スナップショット **未検出**

**関連 OneNote（別テーマ — 混同禁止）**

| onenote_id | ファイル | 要約 |
| --- | --- | --- |
| `a8c15103-95f4-4d08-897a-403d412bffb5:119` | `onenote-bbfe4d1e1e0ed4ed9ede888e.md` | **乗場バックアップ**一般: マルチカー点検時に他号機へ影響させない回路。乗場直電源 DC12V・直伝 DIH/DOH・C-8-S450.1-J P10。2C-2BC / ΣAI 等の群管理通信 |

→ I-CAN 未接続・E30 とは **別問題**。417 の統合回答には **載せない**（将来別カード候補。[onenote-merge-coverage](../validation/onenote-merge-coverage-wave1-2.md)）

## 統合した回答・ノウハウ

Lists 上は **I-CAN 未接続** と **乗場バックアップ不可** がセットで報告され、**E30** が MON 上に出ている。対応済みだが、**復旧手順・配線確認の原文は未開示** のため、現場手順はここでは書かない。

## 調査・確認手順

1. MON1/0→E/0 と 【E30】の表示を Lists 記載どおり確認（現行定義は KB 未確認）
2. I-CAN 配線・接続（因果は Lists 保留のため **未確認**）
3. Lists 原文開示後: 症状・原因・対策を本カード §4 に追記

## 関連事例と条件の違い

| 条件 | 本テーマ |
| --- | --- |
| 機種 | VFGLF のみ（Lists） |
| エラー桁 | 据付完了後 2 桁のみ、との Lists 注記 |

## KB確認に基づく追記

（未実施 — KB 資料参照なし。E30 / I-CAN の正式定義は KB 突合後。）

## 正式資料・元情報（参照元）

| 種別 | 識別子 | 補足 |
| --- | --- | --- |
| Lists | §417 |
| **OneNote** | — | スナップショット未検出（2026-10-19） |
| **KB** | — | 後続 |

編集用写し: `record_id` `case-elv-vfglf-i-can-disconnected-hall-backup-unavailable-id417`

## 未確認事項

- Lists 保留フィールド（症状・原因・Notes）
- E30 / I-CAN の現行資料（KB）
- OneNote 上の個別ページ（再スナップショット後）
