---
knowledge_id: KH-LINKS-POLE-ALIGN-94D-139
kind: case_summary
status: draft
card_version: 1
title: "磁極未学習 94D — コイン電池と HAND 運転"
symptoms:
  - "94D"
  - "磁極合わせ"
  - "スロー運転不能"
  - "AXIEZ-LINKS"
  - "コイン電池"
model_scope:
  lists_model_label:
    - "AXIEZ-LINKS"
  product_lines:
    - "AXIEZ-LINKs"
  control_methods:
    - "VFGLF"
  observed_on: []
  may_apply_to:
    - "本スロー後、翌日スロー/HAND で運転不能・94D"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "139"
---

# 磁極未学習 94D — コイン電池と HAND 運転

## 使う場面・対象条件

**AXIEZ-LINKS** **本スロー完了後**、前日までスロー可だったが **HAND/かご上運転で不能**（Lists 139）。

## 症状・現象

- **94D, 95D, A43, 64E** — **94D 磁極未学習**（Lists progress）。
- 29 点灯、本スロー完了済みでも **磁極合わせモードに自動移行しない** 経路あり。

## ソース要約

### Lists（139）

- **原因**: 初回スロー前 **P1 コイン電池未装着** → ROM 磁極学習不可。RAM 保存は **長時間遮断で消失**。
- **Notes**: ① ETP 運転 → 投入時磁極補正へ。② **HAND + 未学習** → **94D** で不能。③ RAM は短時間は保持（当日のみ動いた例）。
- **対応**: **磁極合わせ** 実施。資料 YE317C127/126、C-7-C3900-J-C（Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

**185**（回生未配線）は VFGL 系 — **139** は LINKs **94D + 電池/RAM**。ED リレー不動は **#5 未引** 等も Lists progress 参照。

## 調査・確認手順

1. 94D 確認。
2. **P1 コイン電池** 装着。
3. 磁極未学習モードで運転可否。
4. **磁極合わせ** 実施。

## 関連事例と条件の違い

| list | 論点 |
| --- | --- |
| **139** | LINKs **94D** |
| **185** | 回生 **141** |
| [392](./KH-VFGLF-BRAKE-SW-392.md) | 本スロー後 **94D** — `:156` 索引 |
| [Nexcube QC `:177`](../practice-guides/KH-NEXCUBE-VFGH-QC-HUB.md) | **VFGH** の P1 コイン電池。制御が違う |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | **横断入口** |

## KB確認に基づく追記

（C-7-C3900 — pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §139 |
| KB | YE317C127/126 |

## 未確認事項

- なし。
