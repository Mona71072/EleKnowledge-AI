---
knowledge_id: KH-CM-MA-LHC1130-ANNOUNCE-BUSY-22
kind: case_summary
status: draft
card_version: 1
title: "CM-MA — LHC-1130 COP アナウンス基板 E225/227"
symptoms:
  - "225"
  - "227"
  - "LHC-1130"
  - "アナウンス基板"
model_scope:
  lists_model_label: ["CM-MA"]
source_refs:
  - ref_type: lists_item
    list_item_id: "22"
---

# CM-MA — LHC-1130 COP アナウンス基板 E225/227

## 使う場面・対象条件

**タッチパネル COP** で **E/0=225,227**（アナウンス軽/重故障）（Lists 22 — タイトル保留）。

## 症状・現象

- 引渡し直前 **リアルタイム診断** 表示（Lists）。

## ソース要約

### Lists（22）

- **原因**: **LHC-1130X** にアナウンス基板との **ビジー信号** 処理未実装（設計流出、初現場）。
- **結果**: ビジー信号やり取り可能化で **エラー解消**（Lists cause）。
- **progress**: OP=0/MODE=7、別アナウンス、メンテコン調査 — 解消前手順。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**225/227** 表示時は **COP 基板世代** と **アナウンス伝送** を疑う — [423 JRE IH](../case-summaries/KH-JRE-EMER-INTERCOM-MONITOR-423.md) とは別系。

## 調査・確認手順

1. **E225/227** リアルタイム表示確認。
2. アナウンス **OP/MODE**（Lists progress ①）。
3. **LHC-1130** 仕様・ビジー信号（Lists cause）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **22** | **ビジー未実装** |
| [423](../case-summaries/KH-JRE-EMER-INTERCOM-MONITOR-423.md) | **JRE IH** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §22 |

## 未確認事項

- タイトル・識別 — 情報管理保留。
