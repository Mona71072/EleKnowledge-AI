---
knowledge_id: KH-IPU-MELD-BATTERY-POLARITY-101
kind: case_summary
status: draft
card_version: 1
title: "MELD バッテリー極性逆 — M1 カード D41・停電移行ループ"
symptoms:
  - "MELDバッテリー"
  - "極性"
  - "M1カード"
  - "IPU"
  - "E84"
  - "PWD"
  - "停電"
  - "追い出し"
model_scope:
  lists_model_label: []
  machine_room: []
  control_methods: []
  model_abbreviations: []
  observed_on: []
  may_apply_to:
    - "MELD バッテリー取付後に放置で停電移行が繰り返す IPU/M1 系"
  excludes: []
  scope_note: "Lists Model 空欄。174 低電圧・132 RHY とは別"
source_refs:
  - ref_type: lists_item
    list_item_id: "101"
---

# MELD バッテリー極性逆 — M1 カード D41・停電移行ループ

## 使う場面・対象条件

**MELD バッテリー取付直後** に **全自動放置で停電移行・追い出し** が繰り返し、リセットで一時復旧するパターン（Lists 101）。**174**（低電圧）・**132**（RHY）と切り分ける。

## 症状・現象

- 放置で **停電移行 + 追い出し**、電源リセットで一時復旧後再発
- **E84 / #PWD（停電検出）**（Lists）

## ソース要約

### Lists（101）

- **原因（報告）**: MELD バッテリー **±逆結線** → IPU 内 **M1 カード D41 ダイオード線切れ** → **M1 交換**。
- **調査 progress**: P1 LED、エラー、マルチ電源、BK 結線、#5/M5、**動的ブレーキトルク**、M1 裏側確認。
- **Notes**: ブレーキトルク確認中の急停止で「M1 焼け」事例あり — **EA-11-F** 抜粋手順で M1 損傷疑いを強める（Lists）。類似 **ASHA19108**。
- **Model 欄**: 未記載。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

極性ミスは **MELD 機能以前に M1/PWD 系** を壊す。Lists の **動的ブレーキトルク確認** は M1 疑いの補助。**174** は電圧低下、**101** は **配線極性** が報告原因。

## 調査・確認手順

1. E84 / PWD 系エラーと MELD バッテリー **極性・端子**（Lists 原因）。
2. Lists progress 順: 電源・BK・#5/M5。
3. **動的ブレーキトルク**（Notes / EA-11-F — KB 未レビュー）。
4. **M1 カード** 外観・裏側（D41 損傷報告）。
5. 交換後 **極性再確認** と MELD/停電試験（手順は KB 待ち）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **101** | **±逆** → M1 |
| [174](./KH-VFGLB-MELD-BATTERY-174.md) | 低電圧・残量表示 |
| [132](./KH-VFGLF-MELD-RHY-CONNECTOR-132.md) | RHY 未挿・実停電 MELD |
| [167](./KH-MR-MELD-CP-LIVE-WORK-167.md) | **CP 活線** 安全 |
| [180](./KH-ALL-CONDUCTOR-5-DIODE-R1-180.md) | WOS サージ D 不良（Lists 上別回路） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §101 |
| OneNote | なし |
| KB | EA-11-F、C-54-B203-54a（pending） |

## 未確認事項

- 対象機種・制御（Lists Model 空欄）。
- M1 交換後の MELD 独立確認（draft 上は Lists 対応済み表示のみ）。
