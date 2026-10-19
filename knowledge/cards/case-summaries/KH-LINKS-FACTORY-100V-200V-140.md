---
knowledge_id: KH-LINKS-FACTORY-100V-200V-140
kind: case_summary
status: draft
card_version: 1
title: "工場誤結線 — 100V/200V 混供（原因・progress 保留）"
symptoms:
  - "100V"
  - "200V"
  - "かご下照明"
  - "かご上コンセント"
  - "MCB"
  - "AXIEZ-LINKS"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  observed_on: []
  may_apply_to:
    - "MCB OFF でかご下照明消灯・コンセント 200V 級"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "140"
---

# 工場誤結線 — 100V/200V 混供（原因・progress 保留）

## 使う場面・対象条件

**product: AXIEZ-LINKs**（Lists `Model: AXIEZ-LINKS`、制御ラベル **VFGLF**）。**100V/200V 混線疑い**（Lists 140）。**原因・progress は情報管理保留** — 公開症状のみ索引。

## 症状・現象

- **MCB 遮断** で **かご下照明消灯**、通常より明るい点灯。
- **かご上コンセント ~200V**（Lists）。
- 他支社: **100V 未受電でもかご内照明点灯** の類似（Lists）。

## ソース要約

### Lists（140）

- **Reported cause and response**: **情報管理保留**（カードに再掲しない）。
- タイトルどおり **工場組立部位の配線** が疑われる切り分け起点。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**32**（新 AXIEZ CST/SCB 対地電圧）と **140**（LINKs 照明/コンセント）は **混線切り分け** で並べる。確定原因は Lists 解除待ち。

## 調査・確認手順

1. MCB/CST 状態別 **対地電圧**。
2. 照明・コンセント系統図。
3. 稲電/工場 FB（Lists 保留解除後）。

## 関連事例と条件の違い

| list | 軸 |
| --- | --- |
| **140** | LINKs **保留** |
| **32** | 新 AXIEZ **L10/L20** |
| **414** | **U-CAN** 照明地絡 |

## KB確認に基づく追記

（該当なし — 原因保留）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §140（症状のみ） |
| OneNote | なし |
| KB | なし |

## 未確認事項

- Lists **140 原因・progress — 情報管理確認まで未索引**。
