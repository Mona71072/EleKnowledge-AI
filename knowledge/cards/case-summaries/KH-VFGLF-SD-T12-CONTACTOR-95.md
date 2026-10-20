---
knowledge_id: KH-VFGLF-SD-T12-CONTACTOR-95
kind: case_summary
status: draft
card_version: 1
title: "SD-T12（LBA/LBB）吸引後にブレーキが引かない"
symptoms:
  - "SD-T12"
  - "LBA"
  - "LBB"
  - "VFGLF"
  - "コンタクタ"
  - "ブレーキ"
  - "接触抵抗"
  - "417"
  - "41A"
  - "439"
  - "43C"
model_scope:
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "SD-T12 盤・LBA/LBB コンタクタ系"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "95"
    source_id: evidence-list-case-id95
  - ref_type: kb_document
    document_number: "C-7-C3900-J"
    kb_verify_status: filename_in_catalog
    locator: "C-7-C3900-J-E.pdf"
    summary_from_kb: ""
---

# SD-T12（LBA/LBB）吸引後にブレーキが引かない

## 使う場面・対象条件

**VFGLF** で **SD-T12 系（LBA/LBB）** コンタクタは吸引するが **ブレーキが引かない** とき。Lists ↑高。

## 症状・現象

- コンタクタはピックアップ、**ブレーキが引かない**
- 報告エラー表示: 417, 41A, 439, 43C, 943, 953（Lists 記載。意味の独立確認は未実施）

## ソース要約

### Lists（list_item_id 95）

- **原因（報告）**: コンタクタ **T1-L1 / T2-L2 / T3-L3 接触抵抗が 10Ω 以上**。
- **測定条件**: **MCB・ELD 遮断**、**手動でコンタクタ吸引** 状態で測定。テスタ接触不良に注意し垂直に確実に。
- **判定**: **10 回中 1 回でも 10Ω 以上** → 本件不具合とし **LBA/LBB 交換**。
- **除外**: すべて 10Ω 以下なら **他原因** を疑う。
- **progress**: 不発返却品を製造元確認中、接触抵抗増大原因調査中、Q シート発行予定。

### OneNote

- list タイトル **一致页なし**（2026-10-19）。

## 統合した回答・ノウハウ

「吸引するが BK が引かない」系で LBA/LBB を疑う場合、Lists 95 は **主回路端子接触抵抗** の定量手順が核心。**遮断・手動吸引・複数回測定** のうえ 10Ω 閾値で交換判断。正常抵抗ならコンタクタ以外を探す。

## 調査・確認手順

1. 症状と Lists 記載エラー表示を記録（コード定義は KB/別資料）。
2. MCB・ELD 遮断。
3. 手動吸引下で T1-L1 / T2-L2 / T3-L3 接触抵抗を **10 回** 測定。
4. 1 回でも ≥10Ω → LBA/LBB 交換（Lists 対応）。
5. すべて ≤10Ω → 他原因調査。

## 関連事例と条件の違い

| list | 症状 | 判定 |
| --- | --- | --- |
| **95** SD-T12 | 吸引するが BK 不引 | 接触抵抗 ≥10Ω |
| **96** SD-T21 | A1-A2 48V でも不吸引 | #5↔M5 暫定（MELD 不可） |
| **97** SD-T21 WOS | UP/DN 遅延・不動 | M5 交換で改善報告 |

## KB確認に基づく追記

（未実施 — C-7-C3900-J はカタログ filename のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §95 |
| OneNote | なし |
| KB | C-7-C3900-J-E.pdf（突合のみ） |

## 未確認事項

- 10Ω 閾値の設計根拠（Lists 記載のみ）。
- 製造元調査・Q シート結果。
