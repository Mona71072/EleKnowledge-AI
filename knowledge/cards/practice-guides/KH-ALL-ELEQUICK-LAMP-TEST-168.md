---
knowledge_id: KH-ALL-ELEQUICK-LAMP-TEST-168
kind: practice_guide
status: draft
card_version: 1
title: "引渡し前 — ELE-QUICK 仮復旧灯の確認"
symptoms:
  - "ELE-QUICK"
  - "仮復旧灯"
  - "据付省力"
  - "SET1/0"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "168"
  - ref_type: kb_document
    document_number: "C-8-S452-J"
    kb_verify_status: pending
---

# 引渡し前 — ELE-QUICK 仮復旧灯の確認

## 使う場面・対象条件

**引渡し前** **監視盤自動診断仮復旧灯** を試験したい — 通常は **MOP 後** まで無効（Lists 168）。

## 症状・現象

- **豆知識** — 総点試験タイミング（Lists）。

## ソース要約

### Lists（168）

- **通常**: 引渡し後 **MELTEC MOP+S/W 改造** 後に初めて有効。
- **引渡し前**: **フロント正 COP** ロータリ **SET1/0=0/6**、**自階釦** で **据付省力モード** → 仮復旧灯確認可（Lists）。
- **省力モード例**: 管制試験・乗場表示報知・**ELE-Quick 灯試験**・輝度低下・省力乗場運転（Lists Notes）。
- C-8-S452-J（Lists — pending）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[157 地震 SW](./KH-MR-SEISMIC-SW-ELEQUICK-157.md)・[350 UPS](./KH-UPS-PEAK-SERVICE-350.md) — **168** は **引渡し前灯試験** の **省力モード** 入口。

## 調査・確認手順

1. MOP 前か。
2. SET1/0=0/6 + 自階釦（Lists）。
3. C-8-S452-J モード選択（pending）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **168** | 灯試験モード |
| [157](./KH-MR-SEISMIC-SW-ELEQUICK-157.md) | 地震 SW |
| [350](./KH-UPS-PEAK-SERVICE-350.md) | 監視盤制御 |

## KB確認に基づく追記

（C-8-S452-J pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §168 |
| KB | C-8-S452-J（pending） |

## 未確認事項

- 機種別 SET1/0 操作可否（KB 未照合）。
