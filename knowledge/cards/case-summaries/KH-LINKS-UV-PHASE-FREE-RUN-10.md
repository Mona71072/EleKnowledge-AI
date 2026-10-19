---
knowledge_id: KH-LINKS-UV-PHASE-FREE-RUN-10
kind: case_summary
status: draft
card_version: 1
title: "LINKs — 制御盤 U/V 逆相で空回し不可"
symptoms:
  - "空回し"
  - "92"
  - "94"
  - "95"
  - "巻上機"
  - "キューン"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "10"
  - ref_type: kb_document
    document_number: "C-7-C3900"
    kb_verify_status: pending
---

# LINKs — 制御盤 U/V 逆相で空回し不可

## 使う場面・対象条件

**AXIEZ-LINKS** **空回し** で **巻上機が少し回転→停止・異音・BK 落下**（Lists 10）。

## 症状・現象

- MON1/0=0/0 で **92/94/95**（Lists）。
- **3 桁エラー不可**（カゴ上 ST 未接続）（Lists Notes）。

## ソース要約

### Lists（10）

- **原因**: 制御盤側 **U 相と V 相誤結線**（Lists）。
- **教訓**: 2 桁のみだと **電源系なし** → **巻上方向** に寄せがち — **相順** も疑う（Lists）。
- 参照 C-7-C3900（Lists — pending）。

## 統合した回答・ノウハウ

[46 89M](./KH-ME-CH-PHASE-89M-46.md)・[50 トランス](./KH-LINKS-TRANS-CRIMP-50.md)・[31 RDU/RDF](./KH-LINKS-RDU-RDF-SWAP-31.md)・[309 RDB/RSLV](./KH-LINKS-RDB-RSLV-EMPTY-RUN-309.md) と **空回し前チェック** を並列。[77](../practice-guides/KH-ALL-ERROR-CODE-3DIGIT-77.md) は接続後の 3 桁用。

## 調査・確認手順

1. **空回し前** 制御盤 **U/V/W** 相順。
2. MON1/0=0/0 **92–95** 意味（接続前は 2 桁のみ）。
3. 巻上 **短回転停止** パターン。
4. C-7-C3900 空回し手順（pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **10** | 盤 U/V |
| [46](./KH-ME-CH-PHASE-89M-46.md) | 仮設 RST |
| [50](./KH-LINKS-TRANS-CRIMP-50.md) | ROA/SOA |
| [309](./KH-LINKS-RDB-RSLV-EMPTY-RUN-309.md) | RDB/RSLV |

## KB確認に基づく追記

（C-7-C3900 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §10 |
| KB | C-7-C3900（pending） |

## 未確認事項

- Lists progress 保留部分。
