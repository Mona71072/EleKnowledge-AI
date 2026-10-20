---
knowledge_id: KH-LINKS-VDA-CAMERA-SPLIT-334
kind: practice_guide
status: draft
card_version: 1
title: "ITV — 分配器2台・VDA-106B スイッチ"
symptoms:
  - "VDA-106B"
  - "VIDEO_IN"
  - "75Ω"
  - "画質"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  may_apply_to: ["ITV・カメラ分配器"]
source_refs:
  - ref_type: lists_item
    list_item_id: "334"
---

# ITV — 分配器2台・VDA-106B スイッチ

## 使う場面・対象条件

**ITV** で **分配器盤に分配器2台**、または **画質不良**（Lists 334）。

## 症状・現象

- （豆知識 — 設定確認）

## ソース要約

### Lists（334）

- **分配器間**: **VIDEO_IN 同士** 接続（Lists）。
- **VDA-106B**: 終端プラグ廃止 → **切替 SW** — **1台**: **75Ω** 側；**2台**: **1台目 HIGH**、**2台目 75Ω**（Lists）。
- 図 **YE207B585**（Lists — KB pending）。

## 統合した回答・ノウハウ

[取付腕本数](./KH-LINKS-VIDEO-DIST-ARM-33.md)（**33**）とセットで **物理＋終端 SW** を確認。信号方式は [145 NTSC](./KH-ALL-CAMERA-COMPOSITE-NTSC-145.md)。**VOUT1 未接続ノイズ** は [323](../case-summaries/KH-ALL-ITV-VOUT1-NOISE-323.md)。照度系は [134](../case-summaries/KH-KE-WF-CABIN-CAMERA-FLICKER-134.md)。

## 調査・確認手順

1. 分配器 **台数**。
2. **VIDEO_IN** チェーン。
3. **HIGH / 75Ω** 設定（334）。
4. 仍不良 → 配線・[145](./KH-ALL-CAMERA-COMPOSITE-NTSC-145.md)・134 フリッカー系。

## 関連事例と条件の違い

| 参照 | 備考 |
| --- | --- |
| **334** | 2台・SW |
| [33](./KH-LINKS-VIDEO-DIST-ARM-33.md) | 取付腕 |
| [145](./KH-ALL-CAMERA-COMPOSITE-NTSC-145.md) | コンポジット |
| [323](../case-summaries/KH-ALL-ITV-VOUT1-NOISE-323.md) | VOUT1 ノイズ |
| **134** | 照度フリッカー |

## KB確認に基づく追記

（YE207B585 未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §334 |

## 未確認事項

- 旧型分配器（終端プラグ）との混在現場。
