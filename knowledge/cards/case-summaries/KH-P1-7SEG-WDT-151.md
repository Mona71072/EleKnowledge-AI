---
knowledge_id: KH-P1-7SEG-WDT-151
kind: case_summary
status: draft
card_version: 1
title: "P1基板不良で7SEG・WDTが点灯しない"
symptoms:
  - "P1基板"
  - "7SEG"
  - "WDT"
  - "VFGH"
  - "CPUリセット"
  - "電源リセット"
  - "S/W書換"
  - "IC72"
  - "C240"
  - "DC-DCコンバータ"
model_scope:
  observed_on:
    - "VFGH"
  may_apply_to:
    - "同一 P1 基板世代で S/W 書換後に 7SEG/WDT 消灯が多発する現場"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "151"
    source_id: evidence-list-p1-7seg-wdt-failure-151
  - ref_type: kb_document
    document_number: "添付資料（Lists 参照）"
    kb_verify_status: not_in_catalog
    locator: ""
    summary_from_kb: ""
---

# P1基板不良で7SEG・WDTが点灯しない

## 使う場面・対象条件

VFGH 等で **CPU リセット・電源リセットや S/W 書換後** に **7SEG や WDT が点灯しない** 事象が続くとき。Lists では S/W 書換での発生が多いと報告。

## 症状・現象

- CPU リセット・電源リセット後、7SEG / WDT が点灯しない（多発）
- S/W 書換後の発生が多い（Lists）
- エラー表示: 未確認（Lists）

## ソース要約

### Lists（list_item_id 151）

- **調査結果（報告）**: P1 基板で +5V-GND 間抵抗低下、3.3VCC-GND 間ショート。**DC-DC コンバータ IC72 不良** が原因。発生メカニズムは調査中。
- **現場確認方法（Lists）**:
  - IC72 はんだ付け部が黒変
  - C240 電圧が 0V 近傍（正常 +3.3V）
  - C240 両端抵抗が 0Ω 近傍（正常約 320Ω）
- **progress**: P1 チェックピン（+5V/+12V/-12V）は正常値の現場もある。**+5V が供給されていない現場**も。制御盤内ファン 6 個のうち一列のみ回転確認、との記載。
- **詳細**: 添付資料参照（スナップショットに PDF 本文なし）。

### OneNote

- **list タイトル完全一致ページなし**（2026-10-19 スナップショット全文検索）。
- 7SEG / P1 / WDT は他ページ（運転確認手順、群管理・メンテ基板浮き等）に断片あり。**本件 IC72/C240 系とは混同しない。**

## 統合した回答・ノウハウ

7SEG/WDT 消灯がリセット・書換後に繰り返す場合、Lists 151 は **P1 上の電源系（IC72→C240 3.3V 系）** を疑う。**P1 型番互換** は [156 Notes](../practice-guides/KH-VFGLF-KCD-P1-COMPAT-156.md)。現場では Lists 記載の **IC72 外観・C240 電圧/抵抗** を先に見る。チェックピン正常でも +5V 未供給の報告があるため、表示だけで基板正常と断定しない。根本原因の再発条件は Lists 上「調査中」。

## 調査・確認手順

1. 事象前後の操作（S/W 書換、リセット種別）を記録。
2. IC72 はんだ部の変色有無。
3. C240 対地電圧（目安 +3.3V）と両端抵抗（目安 320Ω 程度）。
4. P1 チェックピン +5V/+12V/-12V（Lists: 現場差あり）。
5. 制御盤ファン列の回転（Lists progress の付随観察）。
6. 添付資料（Lists 言及）— KB/OneNote スナップショット未同梱のため内容は未統合。

## 関連事例と条件の違い

| テーマ | 151 本件 | 別カード候補 |
| --- | --- | --- |
| 7SEG 不点灯 | IC72/C240 電源系 | メンテ基板浮き・接続不良（他 OneNote） |
| P1 損傷 | コンバータ不良 | 349 誤結線による Z03/P1 焼損（別 list） |

## KB確認に基づく追記

（未実施）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §151 |
| OneNote | 本タイトル専用页なし |
| KB | Lists「添付資料」— 番号未記載・未突合 |

## 未確認事項

- IC72 不良が S/W 書換と相関する機序（Lists: 調査中）。
- 添付資料の図番・KB 所在。
- OneNote への同事例転記の有無（リンク解決前）。
