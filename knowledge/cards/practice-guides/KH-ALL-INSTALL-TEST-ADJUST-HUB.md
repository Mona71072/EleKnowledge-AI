---
knowledge_id: KH-ALL-INSTALL-TEST-ADJUST-HUB
kind: practice_guide
status: draft
card_version: 1
title: "据付・試験・調整 — 横断入口（Lists 事例 ↔ 要領・索引）"
symptoms:
  - "据付"
  - "試験"
  - "調整"
  - "本スロー"
  - "調整不良"
  - "設定不良"
  - "G寸法"
  - "CLT"
  - "OLT"
  - "パラメータ調整"
  - "検査試験調整"
model_scope:
  lists_model_label: []
  observed_on: []
  may_apply_to:
    - "Lists 上で原因が調整・設定・寸法と読める不具合から、正本の調整要領・手順カードへ寄せるとき"
  excludes:
    - "索引頁の別テーマタイトルを本文に転記すること（navigation のみ）"
  scope_note: "Lists 単独 ID なし — INDEX §据付・試験・調整 のハブ"
source_refs:
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:153"
    page_role: cross_topic
    note: "本スロー～高速調整 不具合事例 PDF 索引 — navigation のみ"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:98"
    page_role: hybrid
    note: "巻上ロープ張力・振動診断ツール — navigation"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:99"
    page_role: hybrid
    note: "メンテコン・S/W 書込要領 EA-030 等 — navigation"
  - ref_type: onenote_page
    onenote_id: "ec02c9c5-cdb7-4e83-bc9a-e950a58b6a11:110"
    page_role: index
    note: "VFGH 検査試験調整要領書索引 — navigation"
  - ref_type: onenote_page
    onenote_id: "a8c15103-95f4-4d08-897a-403d412bffb5:116"
    page_role: content
    note: "群管理パラメータ調整 C 資料リンク — navigation"
---
# 据付・試験・調整 — 横断入口（Lists 事例 ↔ 要領・索引）

## 使う場面・対象条件

**調整・設定・寸法** が原因候補の不具合で、まず **どの要領・どのテーマカード** を開くか決めたいとき。  
正本は **Lists 事例カード** と **C/TI KB**（`kb_verify_status` 未確認の手順は断定しない）。OneNote は **索引・添付への navigation** のみ（Wave 64–67 方針）。

## 症状・現象（入口キーワード）

- **本スロー / WOS 切替後** に運転不能・BK 系表示
- **ドア調整後** の異音・戸閉不良・G 寸法
- **終点 SW・ランバイ・ピット** の寸法・位置
- **群管理パラメータ**・据付完了フラグ
- **VFGH 高速** 試験調整・巻上トルク

## ソース要約

### テーマカード（優先して開く）

| 軸 | カード | 備考 |
| --- | --- | --- |
| **本スロー・BK** | [392 本スロー BK1](../case-summaries/KH-VFGLF-BRAKE-SW-392.md) / [63 BK2](../case-summaries/KH-LINKS-BK2-SETTING-63.md) / [81 BK SW](../case-summaries/KH-LINKS-BK-SW-SETTING-81.md) | 設定不良→要領で再調整 |
| **Nexcube QC** | [NEXWAY→Nexcube 品質確認](./KH-NEXCUBE-VFGH-QC-HUB.md) | VFGH チェック。振動は防振ゴム・戸を先に見る |
| **巻上・93F** | [113 レゾルバ基板](../case-summaries/KH-VFGLF-RESOLVER-BOARD-113.md) / [411 レゾルバ線](../case-summaries/KH-VFGLF-HOIST-RESOLVER-WIRE-411.md) | duplicate — **基板 vs 断線** |
| **本スロー後・運転** | [176](../case-summaries/KH-ALL-GROUND-N00-NORMAL-SLOW-176.md) / [87 RHQ](../case-summaries/KH-LINKS-RHQ-CONNECTOR-87.md) / [139 94D](../case-summaries/KH-LINKS-POLE-ALIGN-94D-139.md) / [414 421](../case-summaries/KH-VFGLF-LINE-LED-GROUND-414.md) / [407 気配り](../case-summaries/KH-ALL-KEIAIN-DOOR-WIRING-407.md) | **392 `:156`** 索引と双方向 |
| **PSL・DN** | [55](../case-summaries/KH-LINKS-PSL-PIN-55.md) / [342](../case-summaries/KH-LINKS-PSL-PIN-S21-342.md) | 本スロー DN |
| **短ランバイ・終端** | [428 短ランバイ HTOP](./KH-VFGH-SHORT-LANDING-LIMIT-428.md) / [182 VFEL DZ](./KH-VFEL-DZ-PLATE-SHORT-RUN-182.md) | 保留記載は Lists 正本 |
| **LV 戸寸法** | [432 CLT/OLT](../practice-guides/KH-LV5K-LV6K-CLT-432.md) / [433 G寸法異音](../case-summaries/KH-LV5K-2S-DOOR-NOISE-433.md) | 433 は **調整起因** 事例 |
| **据付・ピット** | [361 据付フラグ](../practice-guides/KH-VFGLF-INSTALL-FLAG-361.md) / [85 AXIEZ 据付フラグ](../practice-guides/KH-AXIEZ-INSTALL-FLAG-85.md) / [394 ピット](../practice-guides/KH-PIT-TRAP-POSITION-394.md) / [29 躯体隙間](../practice-guides/KH-LINKS-HOIST-WALL-GAP-29.md) | install_dim 横断 |
| **ESC** | [430 手摺テンション](../case-summaries/KH-ESC-U-HANDRAIL-TENSION-430.md) | エスカ調整 |

### OneNote（navigation のみ — 本文転記しない）

| onenote_id | スナップショット | 役割 |
| --- | --- | --- |
| `a8c15103…:153` | `onenote-23a1681a723be842db636d84.md` | **本スロー～高速調整 不具合事例** PDF 添付索引 |
| `a8c15103…:156` 等 | 392 カード §3 参照 | **BK / 本スロー** 不具合リスト索引 |
| `a8c15103…:98` | `onenote-bbde917c12a4aa975f724a2c.md` | ロープ張力・振動診断 **C-1-E10** / AM-218 |
| `a8c15103…:99` | （ハイブリッド索引） | VFGL* **検査試験調整要領** EA-030 等 |
| `ec02c9c5…:110` | `onenote-18d9613f585c8d2f94ed4965.md` | **VFGH 調整資料** — EA-097 検査試験調整要領、C-7-F2900.1-J 据付調整資料、高速運転調整 |
| `a8c15103…:116` | `onenote-069a048b18233339abda2d6a.md` | **群管理パラメータ** C-8-S451 / S436 等 |

## 統合した回答・ノウハウ

1. **症状＋機種・戸型** で [INDEX.md §据付・試験・調整](../INDEX.md#据付試験調整横断入口) から **practice_guide** を選ぶ。  
2. **Lists に「調整で」「設定不良」** とある **case_summary** では、§6 の **調整入口** 行（本カード）と **432/392** 等へ既にリンクを張る（Wave 68）。  
3. OneNote の PDF 一覧は **手順の代わりに使わない** — 該当 **C 番号** を KB カタログで解決してから §7 追記。

## 調査・確認手順

1. Lists スナップショットの **原因・Notes** に「調整」「設定」「寸法」があるか確認。
2. 上表の **軸**（本スロー / ドア / 据付 / 群管 / VFGH）を 1 つ選び、リンク先カードを開く。
3. カードの **KB document_number** が `pending` なら、手順は Lists progress と索引のみで案内。
4. 横断 PDF 索引が必要なら OneNote スナップショットを開き、**document_number** をメモ（RAG は S3 PDF 本体）。

## 関連事例と条件の違い

| 観点 | 本ハブ | 機種別 INDEX |
| --- | --- | --- |
| 目的 | **調整知への最短経路** | VFGLF / VFGH / ドア 等の網羅 |
| 深さ | 入口・相互リンク | 全 list テーマ |

## KB確認に基づく追記

（未実施 — 各子カードの `content_reviewed` 後に要約を足す。本ハブに手順を複写しない。）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| INDEX | [§据付・試験・調整](../INDEX.md#据付試験調整横断入口) |
| OneNote | frontmatter の 5 頁。開き方は [ONENOTE-JUMP.md](../../validation/ONENOTE-JUMP.md)（`:99` は子 content、`:98` `:110` は引用カード） |
| Lists | 各 `list_item_id` カード |

## 未確認事項

- カード KB **ingest** 未実装 — アプリ RAG では本ハブは未検索
- OneNote 添付 PDF の **KB 突合** は子カード単位
