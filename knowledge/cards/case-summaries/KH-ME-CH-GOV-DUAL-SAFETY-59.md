---
knowledge_id: KH-ME-CH-GOV-DUAL-SAFETY-59
kind: case_summary
status: draft
card_version: 1
title: "ME-CH — 張車 SW と RUN OFF の二重安全遮断"
symptoms:
  - "安全回路"
  - "閉じ込め"
  - "GOV"
  - "張車"
model_scope:
  lists_model_label: ["ME-CH"]
source_refs:
  - ref_type: lists_item
    list_item_id: "59"
---

# ME-CH — 張車 SW と RUN OFF の二重安全遮断

## 使う場面・対象条件

**ME-CH** **安全回路遮断** で **要因を1つと決めつけない** 切り分け（Lists 59）。

## 症状・現象

- 最上部 **UL 停止振動** → **CWT GOV 張車 SW 誤作動** → 閉じ込め（Lists）。
- **カゴ上 RUN OFF** も並存（Lists）。

## ソース要約

### Lists（59）

- **原因**: ① **カゴ上 RUN SW OFF** ② **CWT 張車 SW 遮断**（張車位置高設定＋ロープ伸び）（Lists）。
- **対応**: 79-G4 短絡では回路不入 → **73–75 昇降路短絡** で **張車 SW 復帰**（Lists）。参考 **EA97 短絡ピン**。
- **教訓**: 遮断要因 **単一思込み禁止**、**ストレート未確認で 79-G4 短絡** 誤判断（Lists）。

## 統合した回答・ノウハウ

7SEG 安全不入時は **R1 短絡ピン順**（79-73→…→79-G4）と **複数物理要因** を並行。

## 調査・確認手順

1. 7SEG **安全回路** 状態。
2. **短絡ピン** エリア分割（Lists progress）。
3. **RUN SW**・**張車／予報 SW**・GOV 系。
4. EA97 短絡例（KB pending）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **59** | 二重要因 |
| **64** | #5 指令 |

## KB確認に基づく追記

（EA97 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §59 |

## 未確認事項

- EA97 抜粋の現行版。
