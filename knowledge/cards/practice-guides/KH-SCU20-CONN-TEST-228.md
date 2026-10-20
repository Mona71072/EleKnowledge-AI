---

knowledge_id: KH-SCU20-CONN-TEST-228
kind: practice_guide
status: draft
card_version: 1
title: "SCU-20 接続テスト — 現地仕様は反映されず自動登録"
symptoms:
  - "SCU-20"
  - "接続テスト"
  - "カゴ照合"
  - "CR"
  - "カードリーダ"
  - "対向試験"
  - "C-7-C3344"
model_scope:
  lists_model_label:
    - "エレコール"
  machine_room: []
  observed_on: []
  may_apply_to:
    - "SCU 接続テストでカゴ内が自動登録される一方、現地は手動登録仕様"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "228"
  - ref_type: onenote_page
    onenote_id: "2dbb1e7c-e6c4-4b52-87b1-9e8896eaa58b:1"
    page_role: index
    note: "Lists タイトル一致 — SCU-20 事例索引（navigation のみ）"
---
# SCU-20 接続テスト — 現地仕様は反映されず自動登録

## 使う場面・対象条件

**SCU-20** **エレコール** で **接続テスト（かご照合）** を使うとき。**149/422/233** の通信・書換とは別の **試験仕様** 論点。

## 症状・現象

- カードリーダ–EV 不連動調査中、**C-7-C3344 P20 接続テスト** で **現地は手動登録なのに自動登録**（Lists）

## ソース要約

### Lists（228）

- 実不具合原因は **カードリーダ側接続不良**（Lists）。
- **開発回答**: **接続テストでは現地仕様は反映されず自動登録** — EV↔SCU-20 **通信確立** は見えるが **パラメータ一致までは不可**。
- **現地仕様確認は対向試験のみ** — **確実に実施**（Lists 結論）。

### OneNote

- **索引頁** `2dbb1e7c-e6c4-4b52-87b1-9e8896eaa58b:1`（`onenote-758605d7c606a475a4eeb209.md`）— **navigation のみ**。 他テーマタイトルはカード本文に載せない。リンク先本文はスナップショット参照。


## 統合した回答・ノウハウ

接続テスト OK ≠ 現地 CR 仕様 OK。**228** を **233 書換・149 通信** カードと併読し、引渡しは **対向試験** で締める。

## 調査・確認手順

1. 物理層（リーダ接続等）— 本件 Lists の実原因例。
2. SCU–ELV 通信（149/422 系）。
3. **接続テスト** の限界を理解（自動登録）。
4. **対向試験** で手動/自動登録・連動を確認。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **228** | 試験 **仕様の限界** |
| [233](./KH-SCU20-FLASH-REWRITE-233.md) | **書換** 手順 |
| [149](../case-summaries/KH-VFGLF-SCU20-GS3-149.md) | GS3 **B/5** |
| [158](../case-summaries/KH-HA-PANEL-ELECALL-158.md) | HA 盤エラー |
| [422 GS3](../case-summaries/KH-GS3-PART-NO-SCU20-422.md) / [384](../case-summaries/KH-CM-MA-3CAR-GROUP-2C2BC-384.md) / [338 背後呼び](./KH-AXIEZ-LINKS-BACK-CALL-DISABLE-338.md) | 群管理 **索引** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §228 |
| OneNote | 2dbb1e7c…:1（索引 navigation） |
| KB | C-7-C3344（pending） |

## 未確認事項

- 現行 SCU ソフトで仕様変更の有無（KB 未検証）。
