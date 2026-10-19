---
knowledge_id: KH-VFGH-VIBRATION-JUMPER-416
kind: practice_guide
status: draft
card_version: 3
title: "長周期振動感知器の短絡ジャンパとBSER/BSER-CP"
symptoms:
  - "長周期振動感知器"
  - "短絡ジャンパ"
  - "BSER"
  - "BSER-CP"
  - "VFGH"
  - "LV0"
  - "LV1"
  - "LV2"
  - "スローリセット"
  - "2024年4月"
  - "LV3"
  - "非常用エレベーター"
  - "キースイッチ"
  - "運転モード2"
  - "消防運転"
  - "追い出し"
  - "サービスカット"
model_scope:
  lists_model_label:
    - "VFGH"
  product_lines:
    - "Nexcube"
  model_abbreviations: []
  control_methods:
    - "VFGH"
  observed_on:
    - "VFGH"
  may_apply_to:
    - "長周期振動感知器・BSER/BSER-CP 付加動作を持つ機種（Lists は VFGH 事例）"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "416"
    source_id: evidence-list-long-period-vibration-jumper-id416
  - ref_type: onenote_page
    onenote_id: "dbb30fea-8579-4464-89a0-7fb8c36b9def:1"
  - ref_type: kb_document
    document_number: "C-6-R56.1"
    kb_verify_status: not_in_catalog
    locator: ""
    summary_from_kb: ""
  - ref_type: kb_document
    document_number: "D-C-844.1"
    kb_verify_status: not_in_catalog
    locator: ""
    summary_from_kb: ""
  - ref_type: kb_document
    document_number: "S-1-Z06.1"
    kb_verify_status: not_in_catalog
    locator: ""
    summary_from_kb: ""
    note: "OneNote スナップショットに S-1-Z06.1-J.pdf リンクあり。KB カタログ filename 未収載"
  - ref_type: kb_document
    document_number: "TI-1371"
    kb_filename: "TI-1371.pdf"
    kb_category: "テクニカルインフォメーション"
    kb_verify_status: catalog_matched
    locator: ""
    summary_from_kb: ""
    note: "BSER-CP・長周期振動管制（OneNote 資料リンク）"
  - ref_type: draft_record
    record_id: knowhow-elv-long-period-vibration-jumper-id416
    note: "Lists 416 の draft 写し"
review_status: in_review
publication_status: not_published
cloud_approval: not_reviewed
---

# 長周期振動感知器の短絡ジャンパとBSER/BSER-CP

## 使う場面・対象条件

- **長周期振動感知器の短絡ジャンパ**が外れている／付け忘れ疑い（VFGH 事例）
- **2024 年 4 月以降**の **BSER-CP** 原則適用現場で、旧 **BSER** 運用（ジャンパ外し）のまま作業されていないか

## 症状・現象

- 短絡ジャンパが **外れた状態**（Lists）
- 分類: 豆知識・据付工程・資料（Lists）
- ステータス: 対応不要（復旧済み）/ 重要度 高

## ソース要約

### Lists（list_item_id: 416）

**経緯・原因**

- 以前: 付加動作 **BSER のみ** → **短絡ジャンパを外す**運用
- **2024/4 以降**: 原則 **BSER-CP** → **ジャンパは付けたまま**が正
- 本件: 仕様追加後も **旧認識のまま** → ジャンパ外れ

**対応**

- 短絡ジャンパを **正規位置に復旧**（progress 記載）

**Notes（作業・仕様）**

- 短絡箇所: 資料 **C-6-R56.1**
- ジャンパ **付けた状態**で **長周期 LV2 まで自動復帰**。**スローリセット必要**（Lists）
- BSER/BSER-CP 適用条件: **S-1-Z06.1**
- 作業前に **付加動作仕様を必ず確認**

### OneNote（`dbb30fea-8579-4464-89a0-7fb8c36b9def:1`）

**BSER / BSER-CP 方針（OneNote 要約）**

- **2024/4 から原則 BSER-CP**
- **他社製 ELV 併設**等: 設計で従来動作との差を説明し **客先了承**があれば BSER-CP。了承なければ **従来 BSER** も可
- 今後 BSER-CP 物件が **標準化**していく、との記載

**資料リンク（スナップショット）**

- S-1-Z06.1-J.pdf
- TI-1371（ご位置利用長周期振動時管制運転 BSER-CP）— KB **`TI-1371.pdf`** と索引一致

**復帰条件（OneNote 抜粋 — ジャンパ・LV 理解用）**

| レベル | Lists/OneNote で触れる復帰 |
| --- | --- |
| LV0 | 検知後 **300 秒**で自動復帰（OneNote） |
| LV1 | レベル 0 オフで自動復帰（OneNote） |
| LV2 | レベル 0 オフ＋**スローリセット**（Lists Notes と OneNote レベル 2 解除条件） |
| LV3 | **人為リセット**（OneNote） |

※監視盤表示は現場により LV 灯 / 長周期（弱・中・強）表記の違いあり（OneNote）。

### OneNote 詳細（BSER-CP 長周期振動管制 — スナップショット全文要約）

> 出典: `onenote-fa58bf35d09298d2a6f0be4a.md`。図・添付は **スナップショット未取込**。現場差（LV 灯表記）は OneNote 注記どおり。

**レベル 0** — 復帰: レベル 0 検知後 **300 秒**で自動復帰。共振階/非共振階とも運転モード 0。監視盤 LV0 灯（または「長周期（弱）」）。**カゴ動作: 変化なし**。

**レベル 1** — 復帰: **レベル 0 がオフ**で自動復帰。共振階: 運転モード 1。LV1 灯＋長周期振動時管制運転灯（または「長周期（中）」）。停止時は呼び登録階移動完了後 **追い出し→退避階**。非共振階: 運転モード 0.5 相当。LV1 灯。停止時は共振階をかご・乗場 NS 強として LV1 検知前状態を継続（監視盤 **サービスカット**表示）。**独立運転時は共振階に運転可能**。解除: レベル 1 **非検知**。

**レベル 2** — 復帰: **レベル 0 がオフ**で自動復帰（Lists の LV2/スローリセット要件と併読）。共振階: 運転モード 2。LV2 灯＋管制運転灯（または「長周期（強）」）。呼び登録階移動完了後 **その場で追い出し→当階停止**。解除: 感知器 **復帰**かつ **スローリセット**。非共振階: LV2 灯。停止時の扱いはレベル 1 非共振階と同趣旨（サービスカット・独立運転時共振階可）。解除: レベル 2 **非検知**。

**レベル 3** — 復帰: **人為的に長周期振動感知器をリセット**。共振/非共振とも運転モード 2 系。LV3 灯＋管制運転灯。追い出し→当階停止。解除: 感知器復帰＋**スローリセット**（レベル 2/3 共通記載）。

**監視盤キースイッチ（手動投入）** — 選択: キー SW「**手動**」。復帰: 「**自動**」。共振/非共振: 運転モード 1、管制運転灯点灯。追い出し後 **退避階**へ。

**非常用エレベーター（OneNote 抜粋）**

| レベル | 呼び出し / 消防（概要） |
| --- | --- |
| 0 / 1 | 呼び出し・1 消防・2 消防とも **可能** |
| 2 / 3 | 呼び出し中は最寄り階停止後 **運転モード 2**。監視盤キー「**解除**」で呼び出し（速度 60〜90 m/min）。解除後もモード 2 継続。1・2 消防もモード 2 移行（最寄り階停止の有無は不明、FE 戸開閉に従う）。キー「解除」で消防（60〜90 m/min）。復帰後モード 2 継続。**キー「解除」時の復帰: EER リセット＋スローリセット**。消防中に解除しなかった場合の復帰方法は **OneNote 上「わからない」** と記載 |

## 統合した回答・ノウハウ

**ジャンパ**: BSER 時代は外し運用だったが、BSER-CP では **装着が正**。外れていたら正規位置へ復帰。**作業前に付加動作（BSER/BSER-CP）を確認**。短絡位置は C-6-R56.1 参照（KB filename 未確定）。

**復帰・管制**: Lists の「LV2 まで自動復帰＋スローリセット」と、OneNote の **レベル 2/3 解除（復帰＋スローリセット）** を一体で理解する。LV0 は 300 秒自動復帰。非常用ではレベル 2/3 で **運転モード 2**・キー「解除」・EER/スローリセットが絡む（OneNote 詳細 §上記）。

## 調査・確認手順

1. 付加動作が **BSER か BSER-CP か**（物件・客先了承含む。OneNote 方針）
2. 短絡ジャンパの **有無・位置**（Lists 事例: 外れ）
3. 図: C-6-R56.1（KB 未収載 → RAG/資料探索）
4. 適用条件: S-1-Z06.1（OneNote リンクあり、KB カタログ未収載）
5. 復旧後: LV 状態と **スローリセット**要否（Lists Notes / OneNote LV2）

## 関連事例と条件の違い

| 条件 | ジャンパ | 備考 |
| --- | --- | --- |
| BSER のみ（旧） | 外し運用あり | Lists 経緯 |
| BSER-CP（2024/4〜原則） | **付けたまま** | Lists / OneNote |
| 併設・客先了承なし | BSER 継続可 | OneNote |

## KB確認に基づく追記

（未実施 — TI-1371 / S-1-Z06.1 本文、C-6-R56.1 ファイル特定後。）

## 正式資料・元情報（参照元）

| 種別 | 識別子 | 補足 |
| --- | --- | --- |
| Lists | §416 |
| **OneNote** | `dbb30fea-8579-4464-89a0-7fb8c36b9def:1` | `onenote-fa58bf35d09298d2a6f0be4a.md` |
| **KB** | TI-1371 → `TI-1371.pdf` | カタログ確認済 |
| **KB** | C-6-R56.1 / D-C-844.1 / S-1-Z06.1 | 2026-08-26 カタログ **filename 無し**（OneNote は S-1-Z06.1-J 表記） |

編集用写し: `record_id` `knowhow-elv-long-period-vibration-jumper-id416`

## 未確認事項

- C-6-R56.1 等の KB 実ファイル名
- TI-1371 / S-1-Z06.1 本文と Lists Notes の完全一致
- 物件ごとの BSER/BSER-CP 決定記録
