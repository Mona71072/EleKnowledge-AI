---
knowledge_id: KH-VFGLF-CPU-RESET-HAND-204
kind: practice_guide
status: draft
card_version: 1
title: "VFGLF — かご不可時の P1 電源リセット"
symptoms:
  - "P1"
  - "MP"
  - "HAND"
  - "運転阻止"
  - "UCMP"
model_scope:
  lists_model_label: ["VFGLF"]
  machine_room: ["MRL"]
  control_methods: ["VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "204"
  - ref_type: kb_document
    document_number: "菱技ノート第3201号"
    kb_verify_status: pending
---

# VFGLF — かご不可時の P1 電源リセット

## 使う場面・対象条件

**VFGLF** **かごに入れず** **スロー/自動不可** で **CPU リセット** が必要（Lists 204・中）。

## 症状・現象

- エラー取得後 **運転不能**、**かご内スロー不可**（Lists）。

## ソース要約

### Lists（204）

- **AUTO で MP 遮断** でも **P1 は ~3 分維持** — かご不可時のリセットは **運転阻止コネクタ抜き（HAND）＋ MP 遮断** → **P1 即断**（Lists）。
- **UCMP ラッチ**: HAND/ED でリセット後 **起動 ~10 秒は HAND/ED 維持** — 早い AUTO 戻しは **UCMP リセット不可**（Lists Notes）。
- 菱技ノート **3201**（Lists — pending）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[79 UCMP 電源](../practice-guides/KH-LINKS-UCMP-RESET-POWER-79.md)・[305 UCMP 副番](../case-summaries/KH-ALL-UCMP-SW-PARAM-MISMATCH-305.md) は **UCMP 論理** — **204** は **VFGLF P1 残荷** の **物理リセット手順**。[222 のエラー 204](../case-summaries/KH-LINKS-UCAN-MMS-CABLE-222.md)（CS 重故障）と **番号混同注意**。

## 調査・確認手順

1. **HAND**（運転阻止）確認。
2. **MP 遮断** — AUTO では P1 残る（Lists）。
3. UCMP 疑い → **10 秒 HAND/ED**（Lists Notes）。
4. 菱技 3201（pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **204** | P1 即断手順 |
| [79](../practice-guides/KH-LINKS-UCMP-RESET-POWER-79.md) | LINKs UCMP |
| [222](../case-summaries/KH-LINKS-UCAN-MMS-CABLE-222.md) | エラー **204**（CS） |

## KB確認に基づく追記

（菱技ノート 3201 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §204 |
| KB | 菱技ノート第3201号（pending） |

## 未確認事項

- VFGLB 等への同一手順適用（Lists は VFGLF のみ）。
