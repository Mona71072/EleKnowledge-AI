---
knowledge_id: KH-CM-LB-PRIMARY-FIRE-SDE-288
kind: case_summary
status: draft
card_version: 1
title: "CM-LB — 一次消防 #FE2 渡線抜け 727"
symptoms:
  - "一次消防"
  - "727"
  - "SDE"
  - "FE2"
model_scope:
  lists_model_label: ["CM-LB"]
source_refs:
  - ref_type: lists_item
    list_item_id: "288"
---

# CM-LB — 一次消防 #FE2 渡線抜け 727

## 使う場面・対象条件

**CM-LB** **一次消防** — 目的階へ **走行しない**（**二次消防 OK**）（Lists 288）。

## 症状・現象

- **727 リア(1,2)かご SDE OFF 異常**（Lists）。

## ソース要約

### Lists（288）

- 一次消防時 **SDE 切離** — かご上 ST **#FE1（2G は #FE2 も）**（Lists Notes）。
- **#FE2 端子間渡線抜け** → SDE エラー継続（Lists）。
- 渡線追加で **正常**（Lists progress）。

## 統合した回答・ノウハウ

[290 火災管制](../practice-guides/KH-ALL-EMERG-ELEV-FIRE-SERVICE-290.md)・[227 遮煙](../practice-guides/KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) は **仕様** — 本件は **#FE リレー箱内配線**。

## 調査・確認手順

1. 一次 vs **二次** 消防の切り分け。
2. かご上 **#FE1/#FE2** リレー・**12V** 動作。
3. **#FE2 内渡線**（Lists progress）。
4. 727 **SDE OFF** 再現。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **288** | #FE2 渡線 |
| [290](../practice-guides/KH-ALL-EMERG-ELEV-FIRE-SERVICE-290.md) | 火災管制 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §288 |

## 未確認事項

- 2G 以外の #FE 構成。
