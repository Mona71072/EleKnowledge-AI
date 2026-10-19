---


knowledge_id: KH-MRL-HEALTH-AIR-MED-VERSION-266
kind: practice_guide
status: draft
card_version: 1
title: "ヘルスエア — MED-2 / 2.1 / 2.2 / 3 の違い"
symptoms:
  - "MED-2"
  - "MED-2.1"
  - "MED-3"
  - "ヘルスエア"
model_scope:
  lists_model_label: ["MRL機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "266"
  - ref_type: kb_document
    document_number: "TI-1406"
    kb_verify_status: pending
  - ref_type: onenote_page
    onenote_id: "a7093375-48f1-412b-9975-f83bd3e65ff1:1"
    page_role: hybrid
    note: "Lists タイトル一致 — snapshot `onenote-f7c73ea0096b4b87217f2241.md`（本文未転載）"
---
# ヘルスエア — MED-2 / 2.1 / 2.2 / 3 の違い

## 使う場面・対象条件

**MED 版違い** で **SW/FAN 動作** を誤解しない（Lists 266）。

## 症状・現象

- （豆知識 — 24/08B～ **MED-3** 適用）（Lists）。

## ソース要約

### Lists（266）

- **MED-2**: FAN+HA **2 SW**、管制時 FAN 休止も **HA 休止せず** → **MED-2.1 へ移行**（Lists）。
- **MED-2.1/2.2**: **空気清浄 SW 1 つ**、管制・手動・自家発管制で **HA 休止** 仕様（Lists）。
- サイズ: 2.1 **L-30-W10.4**、2.2 **W10.5**（Lists Notes）。

### OneNote

- **索引頁** `a7093375-48f1-412b-9975-f83bd3e65ff1:1`（`onenote-f7c73ea0096b4b87217f2241.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

[261 MED ハーネス誤配](../case-summaries/KH-KM-LD-MED-HARNESS-E35-261.md)・[98 タイマー](../case-summaries/KH-HEALTH-AIR-TIMER-RELAY-98.md)・[320 8極](../case-summaries/KH-LINKS-HEALTH-AIR-CONNECTOR-320.md) と **併設 HA** 系 — 本件は **版ごとの SW 論理**。

## 調査・確認手順

1. 品目 **MED 版**（2 / 2.1 / 2.2 / 3）。
2. **SW 数** と **管制時動作**。
3. TI-1406（pending）。

## 関連事例と条件の違い

| 版 | 管制時 HA |
| --- | --- |
| MED-2 | 休止しない例 |
| 2.1/2.2 | 休止 |

## KB確認に基づく追記

（TI-1406 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §266 |
| KB | TI-1406（pending） |

## 未確認事項

- MED-3 詳細（Lists は適用時期のみ）。
