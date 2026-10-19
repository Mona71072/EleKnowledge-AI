---
knowledge_id: KH-VFGLB-CAR-TOP-ORDER-104
kind: practice_guide
status: draft
card_version: 1
title: "かご上 ST — オーダー確認（7seg・ラベル）"
symptoms:
  - "かご上"
  - "オーダー"
  - "7seg"
  - "DOR-1301A"
  - "搬入間違い"
model_scope:
  lists_model_label:
    - "VFGLB"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLB"
  observed_on:
    - "VFGLB"
  may_apply_to:
    - "かご上 ST 誤搬入・仕様部品欠け"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "104"
---

# かご上 ST — オーダー確認（7seg・ラベル）

## 使う場面・対象条件

**VFGLB** **かご上ステーション誤搬入** 疑い — **オーダー確認**（Lists 104）。

## 症状・現象

- 仕様の **インターホン基板・ITV 中継** 等欠品例（Lists Notes）。

## ソース要約

### Lists（104）

- **7seg オーダー情報**: **C-18-D50.1-J P5 2.1.2(2)**。
- **DOR-1301A ラベル位置**: 添付 label.xlsx（Lists — ファイル未 KB 化）。

### OneNote

- なし。

## 統合した回答・ノウハウ

据付前 **104** でオーダー一致 → **318**（G14/G24 誤基板）類の **ハード違い** 予防。

## 調査・確認手順

1. 7seg 手順（C-18-D50.1-J）。
2. 基板ラベル位置（Lists 添付）。
3. 品目 vs 実装（インターホン等）。

## 正式資料

| 種別 | 参照 |
| --- | --- |
| Lists | §104 |
| KB | C-18-D50.1-J（pending） |

## 未確認事項

- label.xlsx リポジトリ未同梱。
