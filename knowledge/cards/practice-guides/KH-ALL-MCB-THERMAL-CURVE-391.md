---
knowledge_id: KH-ALL-MCB-THERMAL-CURVE-391
kind: practice_guide
status: draft
card_version: 1
title: "負荷試験 110% が MCB 定格超えてもトリップしない理由"
symptoms:
  - "MCB"
  - "負荷試験"
  - "110%"
  - "時延"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "391"
---

# 負荷試験 110% が MCB 定格超えてもトリップしない理由

## 使う場面・対象条件

**110% 負荷試験電流** が **品目 MCB In 超** でも **落ちない** 質問（Lists 391）。

## 症状・現象

- **豆知識・技評**（Lists）。

## ソース要約

### Lists（391）

- **In** は **長時間通電** 上限 — **短時間過電流** は **時限特性** で許容。
- **110% 継続** なら **トリップ可能性**（Lists）。
- **Notes**: **時延**（例 40A で 45A 数十分〜1 h）、**瞬時**（短絡級は ms）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[405 MCB 接点](../practice-guides/KH-ALL-MCB-TRIP-CONTACTS-405.md) は **接点** — **391** は **曲線** 説明。

## 調査・確認手順

1. Lists **添付特性曲線**。
2. 試験 **電流・時間** と **In** 比較。
3. **始動突入** vs **継続過負荷** 切分。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **391** | **MCB 曲線** |
| [405](./KH-ALL-MCB-TRIP-CONTACTS-405.md) | **接点** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §391 |

## 未確認事項

- なし。
