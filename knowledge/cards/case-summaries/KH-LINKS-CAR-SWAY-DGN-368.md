---
knowledge_id: KH-LINKS-CAR-SWAY-DGN-368
kind: case_summary
status: draft
card_version: 1
title: "LINKs — 長時間停止後 UP でかご揺すり（DGN 調整）"
symptoms:
  - "かご揺すり"
  - "DGN"
  - "レゾルバ"
  - "C-7-C3900"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
source_refs:
  - ref_type: lists_item
    list_item_id: "368"
  - ref_type: kb_document
    document_number: "C-7-C3900"
    kb_verify_status: pending
---

# LINKs — 長時間停止後 UP でかご揺すり（DGN 調整）

## 使う場面・対象条件

**長時間停止後** **最下階 UP 初運転** で **かご揺すり**（DN では出にくい）（Lists 368）。

## 症状・現象

- **2〜3 回目** 以降は **検知しにくい**（Lists）。

## ソース要約

### Lists（368）

- **原因**: **絶対角未確定** 時の **レゾルバ誤差補正** → 共振 — C-7-C3900 **6-1-2 注意**。
- **対策**: **DGN 下げ**（8→4 または 2）で解消例。
- **Notes**: 長時間停止時は **エンコーダ/レゾルバノイズ** も疑う — シールド・分離配線。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[341 振動測定](../practice-guides/KH-ALL-IPHONE-VIB-NOISE-APP-341.md) — 調査 **7/D・0/D・5/2**（Lists progress）。

## 調査・確認手順

1. 付録 C **DGN**（Lists Notes ②）。
2. **レゾルバ線** 係合・シールド。
3. CWT **ローラー**・ガイドシュー給油（Lists ③〜⑤）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **368** | **DGN** |
| [272](./KH-ME-CH-ARG-GAIN-VIB-272.md) | **ARG** 振動 |

## KB確認に基づく追記

（C-7-C3900 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §368 |

## 未確認事項

- 高揚程以外でも **発生可能性**（Lists cause）。
