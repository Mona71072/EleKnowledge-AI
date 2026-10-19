---
knowledge_id: KH-ME-CM-TEMP-POWER-S-431
kind: case_summary
status: draft
card_version: 1
title: "仮設動力 S 相不良 — B1/E1 焼損のあと OCR-BL OFF"
symptoms:
  - "仮設配線"
  - "動力電源"
  - "S相"
  - "B1/E1"
  - "OCR-BL"
  - "011"
  - "311"
  - "911"
  - "ME-CM"
model_scope:
  lists_model_label:
    - "ME-CM"
  machine_room:
    - "MR"
  model_abbreviations:
    - "ME-CM"
  control_methods: []
  observed_on:
    - "ME-CM"
  may_apply_to:
    - "高速出し後の遮断復帰で ELV 起動不能・D89 不点灯"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "431"
---

# 仮設動力 S 相不良 — B1/E1 焼損のあと OCR-BL OFF

## 使う場面・対象条件

**ME-CM（MR）** で **仮設動力** 使用中、遮断復帰後 **全面運転不能**。**19**（CM-LB 仮設盤 RA1）と同系の **仮設電源** 論点だが、本件は **三相 S 相ジョイント** が中心。

## 症状・現象

- 高速出し後遮断→復帰で **自動/手動不能**。**D89 のみ不点灯**（Lists）
- エラー **011,012,131,631,64E** → 基板交換後 **311,312,34C,631** → **R-S 0V** → 最終 **911,921,931** + **OCR-BL OFF**

## ソース要約

### Lists（431）

- **原因**: 動力仮設 **S 相ジョイントスリーブ抜けかけ** → 瞬断繰返し **過電流→B1/E1 損傷** 推測。
- **経過**: B1/E1 交換でも未起動 → **R-S 0V** で S 相不良発見 → 再施工後も **OCR-BL OFF** で BLW 不動 → **ON で起動**。
- **類似**: ASHO30357（DCV-DCP 降下で B1/E1 疑い、Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

基板焼損を疑う前後で **一次動力 R-S/T-S** と **仮設ジョイント** を必ず見る。Lists では **2 週間後** に真因 S 相が判明 — 仮設工事完了段階の **相間全確認** を **19** と併読。

## 調査・確認手順

1. エラーコード群（011 系→311 系→911 系）の Lists 順。
2. 動力 **460V 前後**、**DCV-DCP** 降下（B1/E1 疑い）。
3. **R-S 相間**（0V なら仮設 S 相）。
4. ジョイントスリーブ・電気屋再施工。
5. **OCR-BL** SW、A1-A2、BLW コンタクタ。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **431** | ME-CM・**S 相仮設** |
| **19** | CM-LB・**RA1 仮設盤** |
| **437** | 本設・**電圧降下 E-stop**（MRL） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §431 |
| OneNote | なし |
| KB | ASHO30357（未同定） |

## 未確認事項

- ME-CM と CM-MA/LB の仮設標準の共通化（Lists 単一事例）。
