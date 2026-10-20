---
knowledge_id: KH-ALL-AC-RUN-MANUAL-255
kind: practice_guide
status: draft
card_version: 1
title: "手動運転時もエアコンが動作する仕様変更"
symptoms:
  - "手動運転"
  - "エアコン停止"
  - "ヘルスエア併設"
  - "MD-20B-MI4"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "255"
  - ref_type: kb_document
    document_number: "C-30-H2.1-J"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-30-G1.52-J"
    kb_verify_status: pending
---

# 手動運転時もエアコンが動作する仕様変更

## 使う場面・対象条件

**手動運転** で **エアコンが止まる** 旧認識と、現場の **併設型ヘルスエア** 負荷の食い違い（Lists 255）。

## 症状・現象

- **Reported symptoms**: 情報管理保留 — 再掲しない。

## ソース要約

### Lists（255）

- **変更理由**: **ヘルスエア併設** で手動時に **エアコンだけ停止** すると **ヘルスエアに負荷集中**。
- **仕様**: **併設型** に加え **非併設エアコン付き** も **手動でエアコン動作** に変更。
- **Referenced**: C-30-H2.1-J（MED2）4-4 項、C-30-G1.52-J（MD-20B-MI4）4.3 項。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[207 併設 SW6-3](./KH-ALL-HA-AC-DIP-SW6-207.md)・[221 タイマーリレー](../case-summaries/KH-HEALTH-AIR-AC-TIMER-221.md) と **併設設定** — **255** は **手動時 AC 停止廃止**。

## 調査・確認手順

1. 併設型か（Lists cause）。
2. C-30 **4-3 / 4-4 項**（pending）。
3. 手動時 **エアコン＋HE** 期待動作を資料で確認。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **255** | **手動 AC 継続** |
| [207](./KH-ALL-HA-AC-DIP-SW6-207.md) | SW6-3 **設定** |

## KB確認に基づく追記

（C-30 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §255 |
| KB | C-30-H2.1-J、C-30-G1.52-J（pending） |

## 未確認事項

- 機種別例外は KB 本文で確認。
