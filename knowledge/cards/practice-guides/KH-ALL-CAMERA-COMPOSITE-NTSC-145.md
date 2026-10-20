---
knowledge_id: KH-ALL-CAMERA-COMPOSITE-NTSC-145
kind: practice_guide
status: draft
card_version: 1
title: "かご内防犯カメラ — コンポジット信号（NTSC）"
symptoms:
  - "防犯カメラ"
  - "コンポジット"
  - "NTSC"
  - "PAL"
  - "映像モニタ"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "モニタに映像が出ない・方式不一致"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "145"
---

# かご内防犯カメラ — コンポジット信号（NTSC）

## 使う場面・対象条件

**全エレ** — **かご内防犯カメラ** の **コンポジット映像信号** 理解（Lists 145）。

## 症状・現象

- Lists は **豆知識** 共有（特定故障コードなし）。

## ソース要約

### Lists（145）

- **コンポジット**: 同期・輝度・色を合成した **アナログ映像**（Lists）。
- **NTSC**（日/米/韓 30fps）vs **PAL**（欧中 25fps）— **三菱製品は基本 NTSC**（Lists）。
- **注意**: 客先モニタが **電源重畳方式・NTSC 以外** だと動作しない場合あり（Lists）。
- **配線**: 同軸/光ファイバ/2 線式で **NTSC コンポジット**。**信号と電源は別配線**（電源重畳方式ではない）（Lists Notes）。
- **ビデオトランス**（ノイズ低減）、**ケーブル補償器**（長距離クロマ減衰）（Lists Notes）。

### OneNote

- なし。

## 統合した回答・ノウハウ

モニタ仕様と **NTSC/配線方式** を先に確認 — **134**（照度フリッカー）は [別カード](../case-summaries/KH-KE-WF-CABIN-CAMERA-FLICKER-134.md)。**178** サイネージも [ビデオトランス/補償器](../case-summaries/KH-ALL-SIGNAGE-TWIST-NOISE-178.md) 索引。

## 調査・確認手順

1. モニタ入力方式（NTSC/PAL、電源重畳の有無）。
2. カメラ出力（Lists: 基本 NTSC）。
3. 同軸 vs 2 線 + 電源別配線。
4. 長距離なら補償器検討（Lists Notes）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **145** | **信号方式** |
| [334](./KH-LINKS-VDA-CAMERA-SPLIT-334.md) | 分配器2台・終端SW |
| [323](../case-summaries/KH-ALL-ITV-VOUT1-NOISE-323.md) | VOUT1 未接ノイズ |
| **134** | [フリッカー](../case-summaries/KH-KE-WF-CABIN-CAMERA-FLICKER-134.md)（KE-WF） |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §145 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 機種別カメラ型式 — Lists 横断記述のみ。
