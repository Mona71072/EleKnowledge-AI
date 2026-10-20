---
knowledge_id: KH-KE-BF-AC-SAG-E-STOP-181
kind: case_summary
status: draft
card_version: 1
title: "客先電線細径 — フルロード AC 低下 E-STOP"
symptoms:
  - "AC電源低下"
  - "E-STOP"
  - "フルロード"
  - "電圧降下"
  - "KE-BF"
model_scope:
  lists_model_label: ["KE-BF"]
source_refs:
  - ref_type: lists_item
    list_item_id: "181"
---

# 客先電線細径 — フルロード AC 低下 E-STOP

## 使う場面・対象条件

**KE-BF** **官検後フルロード UP** で **E-STOP** — 調整時 **110% 負荷** は問題なし（Lists 181）。

## 症状・現象

- **トレース** で **AC 電源低下** 停止（Lists）。

## ソース要約

### Lists（181）

- **原因**: キュービクル～盤 **~130m** — 要求 **38sq** に対し **22sq 敷設**（電気屋こう長計算）。**営設 22sq 了承**（Lists）。
- **同系統** 他負荷（空調等）で **割当容量低下** も（Lists）。
- **対策**: **電源線引直し** → 解消（Lists）。
- **progress**: 情報管理保留 — 再掲しない。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[191 電圧降下](../practice-guides/KH-ALL-VOLTAGE-DROP-CABLE-191.md) の **現場事例** — **181** は **径不足＋負荷増** で **E-STOP**。

## 調査・確認手順

1. 停止 **トレース** — AC 低下か。
2. **客先径・距離** vs 要求（Lists 38 vs 22 例）。
3. **同系統負荷**（Lists）。
4. 191 の **内線規程・式** 照合（pending なし）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **181** | 細径 E-STOP |
| [191](../practice-guides/KH-ALL-VOLTAGE-DROP-CABLE-191.md) | 降下一般 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §181 |

## 未確認事項

- progress 保留節の現場固有情報（Lists）。
