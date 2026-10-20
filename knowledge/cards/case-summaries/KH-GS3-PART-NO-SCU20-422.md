---
knowledge_id: KH-GS3-PART-NO-SCU20-422
kind: case_summary
status: draft
card_version: 1
title: "GS3 品番 -24/-03 と LM2B — SCU-20 通信不成立"
symptoms:
  - "GS3"
  - "SCU-20"
  - "群管理盤"
  - "LM2B"
  - "ジャンパ"
  - "YX305B744"
  - "品番"
model_scope:
  lists_model_label:
    - "群管理盤"
  machine_room: []
  control_methods: []
  observed_on: []
  may_apply_to:
    - "SCU-20 と高層バンク通信 NG でロータリー・導通 OK のとき"
  excludes: []
  scope_note: "149（VFGLF -01/-02・B/5）と設定ミス内容が異なる"
source_refs:
  - ref_type: lists_item
    list_item_id: "422"
---

# GS3 品番 -24/-03 と LM2B — SCU-20 通信不成立

## 使う場面・対象条件

**群管理盤** で **SCU-20**（高層バンク等）との **通信確立 NG**。**149** は VFGLF 品目 **-01/-02** 誤り、**422** は **YX305B744 品番指定** と **LM2B ジャンパ**。

## 症状・現象

- SCU-20 と高層バンク **通信できない**（Lists）

## ソース要約

### Lists（422）

- **progress**: C-7-C3343.1-J でロータリー誤り **B→A** 変更も **通信せず** → GS3–SCU **導通 OK** → 他バンク GS3 と比較で **LM2B ジャンパ有無差**。
- **品目**: 不具合バンク **-24 指定**、他バンク **-03**。
- **対応**: **LM2B ジャンパ抜き** で -24 相当を **-03** 相当に → **通信良好**。
- **原因（報告）**: 設計段階 **GS3 品番指定誤り**。
- **Notes（26/4/6）**: 基本 **GS3 は品番 -03 以外使用しない**。ロータリー・導通正常でも **品目表の -03 以外** と **LM2B** を確認。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

SCU 通信トラブルは **(1) ロータリー B/5（149）(2) 品番 -03 / LM2B（422）(3) 配線** の順で Lists 事例を当てはめる。相互に設定値を流用しない。

## 調査・確認手順

1. C-7-C3343.1-J フロー（ロータリー・導通）。
2. 他バンク GS3 の **LM2B ジャンパ** 標準状態。
3. 品目 **YX305B744** サフィックス **-03 vs -24** 等。
4. ジャンパ修正後の通信・エレコール試験。

## 関連事例と条件の違い

| list | ミス内容 |
| --- | --- |
| [149](./KH-VFGLF-SCU20-GS3-149.md) | YX306B128 **-01/-02**、ロータリー **5 vs B** |
| **422** | YX305B744 **-24 vs -03**、**LM2B** |
| [158](./KH-HA-PANEL-ELECALL-158.md) | HA 盤 **エレコール**（SCU 側清） |
| [384](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 3car **2C-2BC** |
| [371](./KH-MR-GROUP-PANEL-POWER-371.md) | 群管理盤 **給電** |
| [228](../practice-guides/KH-SCU20-CONN-TEST-228.md) | SCU **索引** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 横断入口 |
| [233](../practice-guides/KH-SCU20-FLASH-REWRITE-233.md) | SCU-20 **書換** |
| [149](./KH-VFGLF-SCU20-GS3-149.md) | GS3 **B/5** 設定 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §422 |
| OneNote | なし |
| KB | C-7-C3343.1-J（pending） |

## 未確認事項

- -24/-03 と LM2B の現行品目表ルール（Notes 2026/4/6 以降の改定）。
