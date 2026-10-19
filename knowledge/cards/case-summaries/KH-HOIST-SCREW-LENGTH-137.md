---
knowledge_id: KH-HOIST-SCREW-LENGTH-137
kind: case_summary
status: draft
card_version: 1
title: "巻上機ロープカバー取付ビスの首下長さ違いによる異音"
symptoms:
  - "PM040MR"
  - "巻上機"
  - "ロープカバー"
  - "異音"
  - "首下長さ"
  - "ドラムカバー"
  - "ブレーキディスク"
  - "CM-MA"
model_scope:
  lists_model_label:
    - "CM-MA"
  product_lines:
    - "Nexcube"
  machine_room:
    - "MR"
  model_abbreviations:
    - "CM-MA"
  control_methods:
    - "VFGH"
  observed_on:
    - "CM-MA"
  may_apply_to:
    - "PM-025/040MR タイプ巻上機のロープカバー付属品取付"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "137"
    source_id: evidence-list-hoist-cover-screw-length-137
  - ref_type: onenote_page
    onenote_id: "c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:131"
  - ref_type: kb_document
    document_number: "D-A-56.801-J"
    kb_verify_status: not_reviewed
    locator: ""
    summary_from_kb: ""
  - ref_type: kb_document
    document_number: "高速エレ巻上機トルク調整ボルト首下長さ.pdf"
    kb_verify_status: not_in_catalog
    locator: "OneNote 参照のみ"
    summary_from_kb: ""
---

# 巻上機ロープカバー取付ビスの首下長さ違いによる異音

## 使う場面・対象条件

**機種略称 CM-MA**（Nexcube・**MR**・**制御 VFGH**）の **PM040MR** 巻上機で、**ロープカバー** 等付属品を取付けた直後、試運転で **引っ掛かるような異音** が出るとき。Lists `Model` 欄は CM-MA（制御名ではない）。

## 症状・現象

- ロープカバー取付後の試運転で異音
- カバー外し・ビス緩めで一時消音、締付で再発（Lists）

## ソース要約

### Lists（list_item_id 137）

- **原因（報告）**: 径同じで **首下長さの異なるビス** が手配される。ロープカバーは **首下の短いビス** が正施工。現場は **長いビス** を使用。
- **結果**: ビス首下がロープカバーを突き抜け、ドラムカバーを押し、**ドラムカバーとブレーキディスク接触** で異音。
- **調査の罠**: 巻上機異音のためロープカバー疑い→外すと消えるが、締付で再接触。**原因特定に時間**（Lists）。
- 詳細は添付資料（スナップショット本文なし）。

### OneNote（`c3cbdf09-…:131`）

- NEXCUBE (CM-MA / ME-CH / ME-CM) 標準要目・PML-F34 巻上機等へのリンク索引。
- **首下長さ** 関連 PDF 参照: 「高速エレ巻上機トルク調整ボルト首下長さ、ライニング基準値について」— トルク調整ボルトの首下基準。**PM-025/040MR には首下基準値が無かった** と明記（Lists 137 のビス混同リスクと整合）。
- 本 OneNote 页は **Lists 137 タイトル一致なし**（関連資料・機種索引）。

## 統合した回答・ノウハウ

PM040MR 系でロープカバー付け後の異音は、まず **付属ビスの首下長さ** を確認する。正しくは **短首下ビス** でカバーを止め、長首下を使うと内部で **ドラムカバー↔ブレーキディスク** 接触になりうる。カバー単体の問題に見えても、締付状態で再現するならビス長の見落としを疑う。PM-025/040MR は OneNote 上、トルク調整用首下表が無い世代— **付属品用ビスは Lists/添付の施工指示** を優先。

## 調査・確認手順

1. ロープカバー取付ビスの **首下長** を仕様・手配リストと照合（短い方が正、Lists）。
2. 取付後、ドラムカバーとブレーキディスク間の接触痕・隙間を目視。
3. ビス緩め/外しで異音変化を記録（再発条件の切り分け）。
4. 必要なら D-A-56.8xx 要目・OneNote 索引の据付/調整資料（PDF 未同梱）。
5. Lists 添付資料（詳細手順 — 未レビュー）。

## 関連事例と条件の違い

| 項目 | 137 ロープカバー | トルク調整ボルト（OneNote PDF） |
| --- | --- | --- |
| 目的 | 付属カバー取付 | 巻上機トルク調整 |
| 首下 | 短/長ビス混同 | PM040MR は表記なし |

## KB確認に基づく追記

（未実施 — D-A-56.801-J は filename 突合のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | `list_item_id` 137 |
| OneNote | `c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:131`（索引・首下 PDF 言及） |
| KB | D-A-56.801-J 等 — `content_reviewed` 前 |

## 未確認事項

- Lists 添付資料の正式図番・ビス品番。
- PM040MR ロープカバー専用 OneNote 页（タイトル hit なし）。
