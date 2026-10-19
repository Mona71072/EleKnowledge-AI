---
knowledge_id: KH-JRE-EMER-INTERCOM-MONITOR-423
kind: case_summary
status: draft
card_version: 1
title: "JRE — 非常釦時インターホン通報のみ LAN 監視盤で不出"
symptoms:
  - "JRE"
  - "非常釦"
  - "インターホン"
  - "LAN監視盤"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "423"
---

# JRE — 非常釦時インターホン通報のみ LAN 監視盤で不出

## 使う場面・対象条件

**IND 運転** で **かご内非常釦** — **JRE LAN 監視盤** で **インターホン通報のみ** 不出（Lists 423）。

## 症状・現象

- 他通報は **推定良好**（Lists progress）。

## ソース要約

### Lists（423）

- **progress**: P1～JRE モニタリング **結線良好** 推定；**DCP #72 = 6 V**；**IBA/IBB** 調査中。
- **Notes / progress 詳細**: 情報管理 **保留** 部分あり。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**423** は **JRE 監視系** — 一般 [239](../practice-guides/KH-ALL-INTERCOM-CMODE-CPD-K-239.md) 等と **物件仕様** が異なる。

## 調査・確認手順

1. **IND** 下 **非常釦** 動作。
2. **DCP 72** 6 V（Lists）。
3. **分岐基板 IBA/IBB** 電圧（Lists 調査中）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **423** | **JRE** 非常 IH |
| [328](./KH-LINKS-CPDK-INTERCOM-RESET-328.md) | **CPDK リセット IH** |
| [239](../practice-guides/KH-ALL-INTERCOM-CMODE-CPD-K-239.md) | **C モード** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §423 |

## 未確認事項

- IBA/IBB 確定 cause — Lists 調査中。
