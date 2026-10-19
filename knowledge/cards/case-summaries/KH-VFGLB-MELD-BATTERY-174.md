---
knowledge_id: KH-VFGLB-MELD-BATTERY-174
kind: case_summary
status: draft
card_version: 1
title: "MELD バッテリー低電圧で移行せず — 交換後も戸開ボタン点滅"
symptoms:
  - "MELD"
  - "バッテリー"
  - "閉じ込め"
  - "戸開ボタン"
  - "点滅"
  - "43V"
  - "VFGLB"
  - "残量チェック"
model_scope:
  lists_model_label:
    - "VFGLB"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLB"
  model_abbreviations: []
  door_families: []
  door_types: []
  observed_on:
    - "VFGLB"
  may_apply_to:
    - "停電・MELD 移行疑いと開戸内 SW 点検時の戸開ボタン表示"
  excludes: []
  scope_note: "Lists Model=VFGLB。132 RHY 抜け・167 活線とは別系"
source_refs:
  - ref_type: lists_item
    list_item_id: "174"
  - ref_type: onenote_page
    onenote_id: "c3cbdf09-d13b-4aa5-9561-35eec9fc56a6:190"
    page_role: content
    note: "MELD/バッテリー — Lists 174 リンク + ELD 保管注意"
---

# MELD バッテリー低電圧で移行せず — 交換後も戸開ボタン点滅

## 使う場面・対象条件

**VFGLB（MRL）** で **MELD バッテリー残量** や **停電時の MELD 移行** を疑うとき。**132**（RHY 未挿）・**167**（配線活線）と混同しない。

## 症状・現象

- バッテリー電圧 **約 35V**、**MELD へ移行せず閉じ込め**（Lists 報告）
- **開戸内 SW 点検 ON** でカゴ内正操作盤 **戸開ボタン点滅**（43V 未満表示）
- 交換後 **MELD 動作良好（約 53V）** でも **点滅が残る** 事例あり

## ソース要約

### Lists（174）

- **初期**: 低電圧 → MELD バッテリー交換要。**43V 未満** で戸開ボタン **点滅**、以上で **点灯**、灯切れで **消灯**（残量チェック結果の表示）。
- **交換後**: MELD 良好でも点滅継続 → **表示は「最新の残量チェック結果」でありリアルタイム電圧ではない**。過去 NG 結果が残っていた。
- **更新手順（Notes）**: ① AUTO 階間走行中またはカゴ低速自動で **客先電源遮断**（急停→MELD→最寄階→戸開閉→約 70 秒後バッテリー遮断）② **電源投入復帰**（**スローリセットするとチェック完了しない**）③ カゴ内 **点検 SW ON** ④ 残量チェック結果更新。
- **対応欄**: 対応不要（Lists）。閉じ込め解消の独立確認は draft 上未確認。

### OneNote（`:190`）

- **Lists 174 同一タイトル**へのリンクあり。手順・43V 表示は **Lists 174 正**。
- **ELD ブレーカー ON のまま 2〜3 ヶ月主電源遮断** → バッテリー上がり事例 — 工事無しは **ELD OFF**（OneNote 対応）。過放電防止機能は **上がり防止を保証しない**（稲電回答要旨）。
- 遮煙 **MELD 要件** は [227](../../practice-guides/KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) — **174** は VFGLB 残量表示が中心。

## 統合した回答・ノウハウ

低電圧時は **交換** と **残量チェック結果の再実施** をセットで考える。交換直後に点滅が残るのは **チェック未更新** の可能性が Lists 上明示されている。**132** は実停電 MELD 不動、**174** は電圧・表示ロジックが中心。

## 調査・確認手順

1. 開戸内 SW 点検 ON で戸開ボタン **点灯/点滅/消灯** を確認（43V 閾値は Lists 記載）。
2. バッテリー電圧・MELD 走行を **実停電** で確認（132 カード参照）。
3. 交換後も点滅なら Lists Notes の **遮断→復帰→点検 SW** で残量チェック更新（スローリセット回避）。
4. RHY 等 **MELDEN 回路** は **132** を別途確認。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **174** | 低電圧・**残量表示の更新** |
| [132](./KH-VFGLF-MELD-RHY-CONNECTOR-132.md) | RHY 未挿・**実停電 MELD** |
| [167](./KH-MR-MELD-CP-LIVE-WORK-167.md) | MELD 配線 **CP 活線** 安全 |
| [101](./KH-IPU-MELD-BATTERY-POLARITY-101.md) | バッテリー **極性** |
| [123](../practice-guides/KH-VFGH-MDU-BACKUP-BATTERY-123.md) | MELD **なし** 時の受電盤バッテリー用途 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §174 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 閉じ込め解消手順・対応欄「対応不要」の現場意味（draft 参照記録どおり未確認）。
- 測定端子・交換手順の KB 未レビュー（断定しない）。
