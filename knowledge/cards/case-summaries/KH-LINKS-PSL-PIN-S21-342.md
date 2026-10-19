---
knowledge_id: KH-LINKS-PSL-PIN-S21-342
kind: case_summary
status: draft
card_version: 1
title: "LINKs — PSL ピン抜け（S21・342②）"
symptoms:
  - "847"
  - "PSL"
  - "リレベル"
  - "S21"
  - "4m"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "342"
---

# LINKs — PSL ピン抜け（S21・342②）

## 使う場面・対象条件

**AXIEZ-LINKS** **本スロー DN・リレベル** で **847 PSL ON**、現象は Lists **55①** と同型（Lists 342②）。

## 症状・現象

- 高速出し後 **管理外（追い出し）** の報告あり（Lists 342①）。
- **②**: リレベル噛み→停止、再 DN **4 m/min**、外れ **15 m/min**（Lists — **55 と同一記述**）。
- リレベルコネクタ抜きで **② 消える**（Lists）。

## ソース要約

### Lists（342）

- **調査**: 847 → PSL 導通・電圧 OK → **下部終点 SW 内 S21 コネクタ B01/B02 ピン抜け**（Lists）。
- **暫定**: 差し直し。**固定不足** → 代品手配（Lists）。
- **ATHO07121** 同型（Lists）。

## 統合した回答・ノウハウ

**55（S12）** と **342（S21）** は **終点 SW 内ピン抜け** の同族 — コネクタ型だけ違う。→ [KH-LINKS-PSL-PIN-55](./KH-LINKS-PSL-PIN-55.md)。

## 調査・確認手順

1. [KH-LINKS-PSL-PIN-55](./KH-LINKS-PSL-PIN-55.md) の DN・847 切り分け。
2. 終点 SW 内 **S21** B01/B02（342）または **S12**（55）。
3. ピン固定・代品（Lists progress）。

## 関連事例と条件の違い

| list / カード | 備考 |
| --- | --- |
| **55** | [KH-LINKS-PSL-PIN-55](./KH-LINKS-PSL-PIN-55.md) — **S12** |
| **342** | **S21** |
| [392](./KH-VFGLF-BRAKE-SW-392.md) | 本スロー **`:156`** 索引 |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §342 |

## 未確認事項

- ATHO07121 本文。
