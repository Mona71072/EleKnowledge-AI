---
knowledge_id: KH-HEALTH-AIR-TIMER-RELAY-98
kind: case_summary
status: draft
card_version: 1
title: "タイマーリレー誤品でヘルスエアーが起動しない"
symptoms:
  - "ヘルスエア"
  - "ヘルスエアー"
  - "エアコン併設"
  - "タイマーリレー"
  - "DC24V"
  - "AC200V"
  - "起動しない"
model_scope:
  observed_on: []
  may_apply_to:
    - "エアコン併設型ヘルスエアー"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "98"
    source_id: evidence-list-health-air-timer-relay-98
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:94"
  - ref_type: kb_document
    document_number: "TI-1406"
    kb_filename: "TI-1406.pdf"
    kb_category: "テクニカルインフォメーション"
    kb_verify_status: catalog_matched
    locator: "OneNote 索引参照"
    summary_from_kb: ""
---

# タイマーリレー誤品でヘルスエアーが起動しない

## 使う場面・対象条件

**エアコン併設型ヘルスエアー** で、エアコンは動くが **ヘルスエアーだけ起動しない** とき。

## 症状・現象

- エアコン起動、ヘルスエアー未起動（Lists 98）
- エラー表示: 未確認

## ソース要約

### Lists（list_item_id 98）

- **原因（報告）**: **AC200V 用ではなく DC24V 用タイマーリレー** が取付。後日交換予定。
- **添付**: 詳細・動作原理を添付に整理（スナップショット未同梱）。
- **progress（確認順）**:
  1. エアコン内基板ディップ SW
  2. コネクタ結線
  3. 配線挟み込み
  4. エアコン電源部・タイマーリレー端子台・天井内電源 BOX 基板の電圧出力
  5. 稲電へ取付状況確認

### OneNote

**索引 `a8c15103-…:94`**（ヘルスエア系一覧）

- 本 list タイトル **一致页なし**。関連リンク: ヘルスエアモニター出力、降圧トランス、併設エアコン動作不良、設定方法、TI-1406 PDF 等（いずれも **別事例** — 98 はタイマーリレー誤品）。

## 統合した回答・ノウハウ

併設型でエアコンのみ動く場合、Lists 98 は **タイマーリレーの定格取違え（DC24V 品が AC200V 系に）** を示す。現場 progress のとおり、設定・結線・挟み込み・各点電圧を確認したうえで **リレー仕様・品番** を疑う。**8極コネクタ抜け** は [320](./KH-LINKS-HEALTH-AIR-CONNECTOR-320.md)。動作原理の詳細は Lists 添付（未レビュー）。

## 調査・確認手順

1. Lists progress ①〜④（SW・結線・挟み込み・電圧）。
2. タイマーリレーの **定格電圧・型式** が AC200V 系要件と一致するか。
3. 稲電へ取付状況照会（Lists ⑤）。
4. OneNote 索引の併設エアコン設定資料（別経路 — KB 未レビュー）。

## 関連事例と条件の違い

| テーマ | 98 | 備考 |
| --- | --- | --- |
| 原因 | タイマーリレー誤品 | Lists §98 |
| [221](./KH-HEALTH-AIR-AC-TIMER-221.md) | 併設 AC **動作不良** | HA 横断 |
| [158](./KH-HA-PANEL-ELECALL-158.md) | HA 盤 **エレコール** |
| [320](./KH-LINKS-HEALTH-AIR-CONNECTOR-320.md) | 8極コネクタ | LINKs |
| [207](../practice-guides/KH-ALL-HA-AC-DIP-SW6-207.md) / [206](../practice-guides/KH-ALL-HA-RESISTOR-POLARITY-206.md) | HA 設定・極性 | |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |

## KB確認に基づく追記

（TI-1406 — **catalog_matched** のみ。本文 `content_reviewed` 前）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §98 |
| OneNote | 索引 `…:94` |
| KB | Lists 添付・TI-1406 — 未 `content_reviewed` |

## 未確認事項

- 誤品の品番・手配経路。
- Lists 添付資料の正式タイトルと KB 所在。
