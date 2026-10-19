---
knowledge_id: KH-VFGR-CAR-TOP-RUN-SW-319
kind: case_summary
status: draft
card_version: 1
title: "VFGR かご上 RUN SW OFF — 手動運転不能"
symptoms:
  - "VFGR"
  - "RUN"
  - "トグル"
  - "かご上ST"
  - "手動運転"
  - "ポータブル"
model_scope:
  lists_model_label:
    - "VFGR"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGR"
  observed_on:
    - "VFGR"
  may_apply_to:
    - "かご上・かご中・乗場 PT すべて手動不能"
  excludes: []
  scope_note: "duplicate primary: elv-vfgr-manual-operation-disabled-run-state-id319（172 初回保守 AS とは別）"
source_refs:
  - ref_type: lists_item
    list_item_id: "319"
---

# VFGR かご上 RUN SW OFF — 手動運転不能

## 使う場面・対象条件

**VFGR（MRL）** で **かご上/中・乗場ポータブル手動不能**。PD5 UP/DN 48V 正常でも運転しないとき。

## 症状・現象

- かご上 ST **RUN トグル OFF 側**
- 手動運転不可（Lists）

## ソース要約

### Lists（319）

- **progress**: ポータブル UP/DN → P1 **PD5-B04/B05 48V OK**、HAND 時 **60 番回路 OK** → **かご上 RUN=OFF**。
- **対応**: **RUN 側へ倒す** → 手動可。
- **参照**: EA-011（Lists Notes）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

制御・電圧が良くても **かご上 RUN** は VFGR の運転ゲート。Lists 319 は **状態確認** の短い事例。

## 調査・確認手順

1. ポータブル信号・P1 48V（Lists progress）。
2. **かご上 ST RUN トグル** 位置。
3. RUN ON 後再試験。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **319** | RUN **OFF** |
| **354** | VFGR B3/B7 直伝（別） |
| [284](../practice-guides/KH-VFGR-FLASH-WRITE-CABLE-284.md) | 書換 LAN |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §319 |
| OneNote | なし |
| KB | EA-011（pending） |

## 未確認事項

- なし（Lists 対応不要・原因明示）。
