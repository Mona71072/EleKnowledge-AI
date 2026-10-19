---

knowledge_id: KH-ALL-HA-AC-DIP-SW6-207
kind: practice_guide
status: draft
card_version: 1
title: "ヘルスエア併設 AC — SW6-3 と MF1 200V"
symptoms:
  - "ヘルスエア"
  - "併設エアコン"
  - "SW6-3"
  - "MF1"
  - "200V"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "207"
  - ref_type: onenote_page
    onenote_id: "a7093375-48f1-412b-9975-f83bd3e65ff1:1"
  - ref_type: kb_document
    document_number: "C-30-G5.3"
    kb_verify_status: pending
---
# ヘルスエア併設 AC — SW6-3 と MF1 200V

## 使う場面・対象条件

**ヘルスエア併設エアコン** で **HA 不起動** — **設定漏れ** 疑い（Lists 207・中）。

## 症状・現象

- エアコン運転しても **ヘルスエア起動せず**（Lists 要旨）。

## ソース要約

### Lists（207）

- **据付時**: エアコン基板 **ディップ SW6-3 ON**（**工場設定 24/08B~**、調整時確認）（Lists）。
- **漏れ時**: **MF1 から 200V 不出** → AC 運転でも HA 不出（Lists）。
- C-30-G5.3 **MEA-20B-MI2**（Lists Notes — pending）。

### OneNote

- **索引頁** `a7093375-48f1-412b-9975-f83bd3e65ff1:1`（`onenote-f7c73ea0096b4b87217f2241.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

[221 タイマーリレー誤品](../case-summaries/KH-HEALTH-AIR-AC-TIMER-221.md)・[98 HA リレー](../case-summaries/KH-HEALTH-AIR-TIMER-RELAY-98.md) は **部品/組立** — **207** は **SW6-3 設定**。

## 調査・確認手順

1. 併設 AC 現場か。
2. 基板 **SW6-3 ON**（Lists）。
3. **MF1 200V**（Lists 要旨 — 測定手順は KB pending）。
4. C-30-G5.3（pending）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **207** | SW6-3 |
| [221](../case-summaries/KH-HEALTH-AIR-AC-TIMER-221.md) | 24V リレー誤品 |
| [98](../case-summaries/KH-HEALTH-AIR-TIMER-RELAY-98.md) | HA 単体リレー |

## KB確認に基づく追記

（C-30-G5.3 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §207 |
| OneNote | a7093375-48f1-412b-9975-f83bd3e65ff1:1 |
| KB | C-30-G5.3（pending） |

## 未確認事項

- 24/08B 以前現場の工場設定差（Lists は以降確認を明記）。
