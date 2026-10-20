---
knowledge_id: KH-ALL-DOOR-DC321-PULSE0-381
kind: case_summary
status: draft
card_version: 1
title: "ドア駆動基板 321（入力パルス0）— 基板不良例"
symptoms:
  - "321"
  - "入力パルス0"
  - "PLG"
  - "OLT"
  - "CLT"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "381"
---

# ドア駆動基板 321（入力パルス0）— 基板不良例

## 使う場面・対象条件

**本スロー後** **戸閉せず** — DC **321**（Lists 381）。

## 症状・現象

- 据付中 **一度も戸開閉なし**（Lists）。

## ソース要約

### Lists（381）

- **調査**: OLT/CLT **5±1 mm**、ジャンパー（YX401C695）、PLG **4〜6 V** 動作中 — **正常**。
- **結論**: **ドア駆動基板交換** で再発なし → **基板不良**。
- **Notes**: 321 検出 — **#21/#22** 区間で **10 s 以上パルス≈0**；復帰は **次回全閉**。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

T/S 321 は **低速戸開閉** 想定だが **未開閉** でも表示され得る（Lists progress）— [407 戸配線](../case-summaries/KH-ALL-KEIAIN-DOOR-WIRING-407.md) とは切分。

## 調査・確認手順

1. **位置 SW**・**PLG** 電圧（YX401B228）。
2. 基板 **設定** 確認後 **交換** 判断（Lists）。
3. 321 **検出区間**（Notes）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **381** | **321 基板** |
| [382](./KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) | **421 伝送** |
| [407](../case-summaries/KH-ALL-KEIAIN-DOOR-WIRING-407.md) | **配線** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §381 |

## 未確認事項

- なし。
