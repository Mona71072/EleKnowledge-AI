---

knowledge_id: KH-VFGH-DOAS-CONSTRUCTION-373
kind: case_summary
status: draft
card_version: 1
title: "工事使用時の行先階制限（DOAS）でカゴ呼びが登録できない"
symptoms:
  - "DOAS"
  - "行先階制限"
  - "エレナビ"
  - "工事使用"
  - "cc0c"
  - "VFGH"
model_scope:
  lists_model_label:
    - "VFGH"
  product_lines:
    - "Nexcube"
  control_methods:
    - "VFGH"
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on:
    - "VFGH"
  may_apply_to:
    - "行先階登録制限（セキュリティ有）で工事使用する現場"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "373"
  - ref_type: onenote_page
    onenote_id: "abb52884-8508-4401-8c6a-5f0f5b93b9ec:1"
    page_role: content
  - ref_type: kb_document
    document_number: "C-8-S436.1"
    kb_verify_status: pending
---
# 工事使用時の行先階制限（DOAS）でカゴ呼びが登録できない

## 使う場面・対象条件

**制御 VFGH**。**行先階制限（エレナビ/DOAS）** 有効のまま **工事使用** し、かご内で行先階を押しても **「ただいま押された階には止まりません」** となるとき（Lists 373）。

## 症状・現象

- 行先階登録不可（ロビー階のみ制限など）
- 仮乗場押釦・HOP 未取付の工事段階（Lists 状況例）

## ソース要約

### Lists（373）

- **原因**: **エレナビ（DOAS）登録制限**。
- **対応**: 群管理盤 **［DOAS動作有効/無効］cc0c** を **01→00**（無効化）。電気設計確認後実施（Lists）。
- **Notes**: セキュリティ有で工事する場合は **DOAS 無効パラメータを工事前に** 入れる。

### OneNote（`abb52884-8508-4401-8c6a-5f0f5b93b9ec:1`）

- **工事使用・行先階**: 行先階登録制限あり仕様では **カゴ呼び登録不可** に注意（Lists 373 / **cc0c** と同軸）。
- **ELSGW**: PuTTY 通信不可事例リンク — [415](../../practice-guides/KH-ELENAVI-ELSGW-PUTTY-NET-415.md) へ。IDS でデフォルトネット確認。
- 表示器取付・試験要領など **373 外** の BM/エレナビ一般論は [336](../../practice-guides/KH-ELENAVI-ISSUES-INDEX-336.md) — **本カードへ混載しない**。

## 統合した回答・ノウハウ

工事フェーズで行先階が取れない場合、**DOAS/cc0c** を疑う。VFGLF の **行先階予約 FL1（list 99）** とは別経路。

## 調査・確認手順

1. 行先階制限の有無・対象階を確認。
2. 群管理盤 **cc0c**（DOAS 有効/無効）。
3. 工事使用前に DOAS 無効化可否を **電気設計** に確認（Lists）。
4. C-8-S436.1 参照（KB 未レビュー）。

## 関連事例と条件の違い

| list | テーマ |
| --- | --- |
| **373** | DOAS / 工事 |
| [99](./KH-VFGLF-CAR-IND-DEST-FLOOR-99.md) | LINKs **FL1** ロータリ |
| [153](../practice-guides/KH-ALL-FCC-A-6FLOOR-153.md) | FCC-A（DOAS で無効） |
| [336](../practice-guides/KH-ELENAVI-ISSUES-INDEX-336.md) | **エレナビ** まとめ |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §373 |
| OneNote | abb52884…:1 |
| KB | C-8-S436.1 |

## 未確認事項

- cc0c の現行パラメータ表記（Lists 2024）。
