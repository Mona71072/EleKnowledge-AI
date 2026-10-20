---
knowledge_id: KH-VFGLF-BGM-WIRING-363
kind: practice_guide
status: draft
card_version: 1
title: "VFGLF/B — 二線式アッテネータ無 BGM 結線"
symptoms:
  - "BGM"
  - "音量小"
  - "カゴ上スピーカ"
model_scope:
  lists_model_label: ["VFGLB", "VFGLF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "363"
---

# VFGLF/B — 二線式アッテネータ無 BGM 結線

## 使う場面・対象条件

**二線式アッテネータ無** **カゴ上スピーカ** で **非常放送音量小**（Lists 363）。

## 症状・現象

- BGM 結線後 **音量小**（Lists）。

## ソース要約

### Lists（363）

- **誤**: BGM3→通常/緊急、BGM2→コモン。
- **正**: **BGM1→通常/緊急、BGM2→コモン**（BGM3 不要）。
- **Notes**: 仕様書特記・品目据付注意を確認。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[179 非常放送配線](./KH-ALL-BGM-EMERG-WIRING-179.md) と **アッテネータ有無** で分岐 — **363** は **無**。

## 調査・確認手順

1. 仕様 **特記**（Lists Notes ②）。
2. 制御盤下 **BGM1/2/3** 実配線。
3. 正規結線後 **鳴動**。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **363** | **BGM 無 ATN** |
| [179](./KH-ALL-BGM-EMERG-WIRING-179.md) | **非常** 一般 |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §363 |

## 未確認事項

- なし。
