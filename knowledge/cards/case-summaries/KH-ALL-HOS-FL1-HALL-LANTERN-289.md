---
knowledge_id: KH-ALL-HOS-FL1-HALL-LANTERN-289
kind: case_summary
status: draft
card_version: 1
title: "運転休止 SW — FL1=8（HOS 有）誤設定"
symptoms:
  - "運転休止"
  - "FL1"
  - "ホールランタン"
  - "HOS"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "289"
---

# 運転休止 SW — FL1=8（HOS 有）誤設定

## 使う場面・対象条件

**乗場インジ運転休止 SW** が **休止側でも休止動作しない**（Lists 289）。

## 症状・現象

- **MON1/0=E/0 なし**（Lists）。

## ソース要約

### Lists（289）

- **乗場 ST・乗場インジ CPU** の **FL1=8（ホールランタン有）** — 現場 **無→0 必須**（Lists）。
- **最下階** 修正で良好 → **全階 FL=0**（稲電赤マーカー）（Lists）。
- Mc3 **HOS アドレス**（100902FA 等）— Notes 参照（Lists）。

## 統合した回答・ノウハウ

[15 ホール釦](./KH-VFGH-HALL-BUTTON-ZONE-15.md) は **乗場釦区域** — 本件は **FL1/HOS パラメータ**。[300 Mc3](../practice-guides/KH-ALL-ALARM-HISTORY-MC3-300.md) と **アドレス確認** 併用可。

## 調査・確認手順

1. **ホールランタン** 仕様有無。
2. 各階 **FL1**（ST・CPU）。
3. キー SW 電圧・配線（Lists progress）。
4. Mc3 **SL_HOS / SH_HOS**（Lists Notes）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **289** | FL1/HOS |
| [15](./KH-VFGH-HALL-BUTTON-ZONE-15.md) | 釦区域 |
| [267](./KH-ALL-HALL-LANTERN-WRONG-TYPE-267.md) | ランタン群番 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §289 |

## 未確認事項

- FL1 設定手順の C 資料正本。
