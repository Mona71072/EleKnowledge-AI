---
knowledge_id: KH-LINKS-FMS-BDD-WIRING-11
kind: case_summary
status: draft
card_version: 1
title: "LINKs — FMS 前 BDD 短絡誤結で不走"
symptoms:
  - "FMS"
  - "95D"
  - "A43"
  - "64E"
  - "BDD"
  - "1D2G"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "11"
---

# LINKs — FMS 前 BDD 短絡誤結で不走

## 使う場面・対象条件

**AXIEZ-LINKS** **FMS 前** **手動/ED とも不走**（Lists 11・重要）。**1D2G 2 停止・乗場 FR/RR 混在** 例（Lists progress）。

## 症状・現象

- 最下階乗場 **電源 BOX 嵌合直後** 発生例（Lists）。
- エラー **95D, A43, 64E**（Lists）。

## ソース要約

### Lists（11）

- **原因**: **BDD 短絡** が **リア側基板** ではなく **フロント側 BDD** へ — 図面指示不備＋結線不良（Lists）。
- **切り分け**: 戸短コネクタ・**SCS-D41B/SMD** 短絡で **乗場開放階** 特定 → **BDD 短絡箇所変更** で解消（Lists progress）。
- 図 YE317C138 / C630（Lists — pending）。

## 統合した回答・ノウハウ

[12 DL 暫定](../practice-guides/KH-LINKS-DL-SHORT-12.md)・[304 DS/電源BOX](./KH-LINKS-DS-CONNECTOR-1D2G-304.md)・[408 HMS 戸](../case-summaries/KH-VFGH-KEIAIN-HMS-DOOR-408.md) と **最下階コネクタ** 同系。**27 G6** は本スロー別枝。

## 調査・確認手順

1. 直前作業（乗場電源 BOX 等）。
2. start→7→1→OK **エラー**（Lists progress）。
3. **戸短** 短絡で **階特定**。
4. **RDS/DS/BDD** フロント vs リア（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **11** | BDD |
| [12](../practice-guides/KH-LINKS-DL-SHORT-12.md) | DL S2A |
| [408](./KH-VFGH-KEIAIN-HMS-DOOR-408.md) | HMS 戸 |

## KB確認に基づく追記

（YE317 系 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §11 |

## 未確認事項
