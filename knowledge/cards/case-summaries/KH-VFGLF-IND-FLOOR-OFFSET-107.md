---
knowledge_id: KH-VFGLF-IND-FLOOR-OFFSET-107
kind: case_summary
status: draft
card_version: 1
title: "かご内行先予報灯 — 1 階床ズレ（インジ S/W）"
symptoms:
  - "行先予報灯"
  - "1階ズレ"
  - "インジソフト"
  - "RSW"
  - "特殊S/W"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "かご内呼び登録で予報灯だけ階床が1つずれる"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "107"
---

# かご内行先予報灯 — 1 階床ズレ（インジ S/W）

## 使う場面・対象条件

**VFGLF** で **かご内呼び** 時、**行先予報灯だけ 1 階床ズレ**（釦・到着表示は OK）。

## 症状・現象

- 例: **B1 呼び → 1F 予報灯**（Lists）
- かご内釦・到着位置表示は良好

## ソース要約

### Lists（107）

- **原因**: **インジソフトパラメータミス** — 書換・再設定で解消（Lists）。
- **Notes**: 通常は **RSW** で対応可。**特殊 S/W** 時 RSW=F（品目 535 FLB 指定）— B3 以下・不停止階等。**ASHO29539**。
- **progress**: 開発依頼、ロータリー変更、厚石 TL 書換（特殊 S/W で RSW のみ不可例）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

表示系は **予報灯だけズレ** なら **インジ S/W/RSW** 系。**99**（行先階 FL1 予約表示）と症状が近いが **107** は **ソフト不備** 報告。

## 調査・確認手順

1. 釦・到着表示 vs **予報灯** の切り分け。
2. 特殊 S/W 条件（Lists Notes / 品目 535）。
3. インジ **RSW・ロータリー**、ソフト書換（Lists progress）。
4. 不発 **ASHO29539** 参照（KB pending）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **107** | **予報灯** ズレ |
| **99** | 行先階 **予約** FL1 |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §107 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 現行 VFGLF ソフト版での再発有無。
