---
knowledge_id: KH-ALL-MONITOR-FIRE-GEN-LAMP-14
kind: practice_guide
status: draft
card_version: 1
title: "監視盤 — 火災停電時の非常電源と自家発ランプ"
symptoms:
  - "監視盤"
  - "自家発ランプ"
  - "保安負荷"
  - "火災停電"
model_scope:
  lists_model_label: ["監視盤"]
source_refs:
  - ref_type: lists_item
    list_item_id: "14"
---

# 監視盤 — 火災停電時の非常電源と自家発ランプ

## 使う場面・対象条件

**監視盤** 連動試験で **#3/#4 保安負荷** と **自家発ランプ** 挙動（Lists 14 — タイトルは情報管理保留）。

## 症状・現象

- Lists **症状** は情報管理 **保留**。

## ソース要約

### Lists（14）

- **#3/#4**: **保安負荷** — 火災停電時 **非常電源をもらえない**。
- **自家発ランプ**: 日立は **自家発識別＋非常電源** 後点灯、三菱は **両方前提** — 切替直後 **非常未供給でもランプ点灯** し得る。
- **対応**: 火災ランプは **営設説明**；自家発ランプは **S/W 書換** で是正（Lists progress）。

### OneNote

- スナップショット照合: Lists §14 の **タイトル一致・ID 索引未検出**（Lists のみ。OneNote 追探索は別途）。


## 統合した回答・ノウハウ

[241 CRT テレコ](../case-summaries/KH-ALL-MONITOR-CRT-TELECO-241.md) は **配線** — **14** は **電源系統・ランプ仕様差**。

## 調査・確認手順

1. 連動試験 **動画** 記録（Lists progress ①）。
2. **電気設計・営設** へ仕様確認（Lists ②③）。
3. 自家発ランプ — **S/W** 要否（Lists Notes）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **14** | **自家発ランプ** |
| [241](../case-summaries/KH-ALL-MONITOR-CRT-TELECO-241.md) | **CRT** |
| [227](./KH-ALL-SMOKE-FIRE-SERVICE-MELD-227.md) | **火災管制** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §14 |

## 未確認事項

- 症状・物件識別 — 情報管理保留。添付動画は Lists 正本。
