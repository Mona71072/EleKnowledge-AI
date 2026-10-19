---
knowledge_id: KH-ELECALL-HA-SECOM-26
kind: case_summary
status: draft
card_version: 1
title: "エレコール — HA メーカー取違え（E,0）"
symptoms:
  - "E,0"
  - "HA"
  - "セコム"
  - "対向試験"
  - "9600bps"
model_scope:
  lists_model_label: ["エレコール"]
source_refs:
  - ref_type: lists_item
    list_item_id: "26"
---

# エレコール — HA メーカー取違え（E,0）

## 使う場面・対象条件

**エレコール** **模擬 OK** だが **(E,0)** で **HA 対向不可**、**IDS/品目と現地 HA メーカー不一致**（Lists 26）。

## 症状・現象

- 美和ロック対向 OK、**HA 側 NG**（Lists）。
- 仕様 **パナ** 記載→現地 **セコム MS-4M**（Lists progress）。

## ソース要約

### Lists（26）

- **原因**: **営設検討不足**（Lists）。
- **対応**: SCU **HA パラメータ** パナ→**セコム** リモート書換で良好（Lists）。
- **Notes**: S-6-D08 P25 — セコム **1200/9600 bps** 2系統、**RS-422**（Lists）。

## 統合した回答・ノウハウ

物理層は [17 模擬試験 RPE/RNE](../practice-guides/KH-ELECALL-MOCK-RPE-RNE-17.md) を先に。[158 HA 盤](./KH-HA-PANEL-ELECALL-158.md) と **メーカー・速度** を突合。

## 調査・確認手順

1. **現地 HA メーカー/機種**（IDS だけ信用しない）。
2. 模擬試験 vs 対向。
3. SCU **HA パラメータ**（Lists 26）。
4. 通信速度 **1200/9600**（Lists Notes）。

## 関連事例と条件の違い

| 参照 | 備考 |
| --- | --- |
| **26** | メーカー違い |
| [17](./KH-ELECALL-MOCK-RPE-RNE-17.md) | 伝送テレコ |
| [158](./KH-HA-PANEL-ELECALL-158.md) | HA 盤 |
| [92](./KH-ELECALL-PANIC-OPEN-HALL-CALL-92.md) | パニックオープン |

## KB確認に基づく追記

（S-6-D08、EA-116 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §26 |

## 未確認事項

- 識別情報を含む progress 詳細（転記しない）。
