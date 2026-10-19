---
knowledge_id: KH-LINKS-HEALTH-AIR-CONNECTOR-320
kind: case_summary
status: draft
card_version: 1
title: "LINKs — ヘルスエア 8極コネクタピン抜け"
symptoms:
  - "ヘルスエア"
  - "MD-20B-MI4"
  - "抵抗端子"
  - "モニタ電圧"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "320"
  - ref_type: kb_document
    document_number: "C-30-G5.3"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "C-30-G1"
    kb_verify_status: pending
---

# LINKs — ヘルスエア 8極コネクタピン抜け

## 使う場面・対象条件

**エアコン付ヘルスエア（MD-20B-MI4）** で **抵抗端子間・モニタ出力が規定外**（Lists 320）。

## 症状・現象

- 抵抗端子間 **DC12.4–13.0V**、モニタ **DC2.375–2.770V** 外（Lists）。
- **補助 FAN 不動** 例（Lists）。

## ソース要約

### Lists（320）

- **原因**: 吸込ダクト BOX ↔ 天蓋 **電源 BOX** 間 **8極コネクタピン抜け**（YA186A628）（Lists）。
- **切り分け**: 200V→**13.7V/15V** 降圧、FAN 動作、結線確認（Lists）。
- 同系: **タイマーリレー型違い**、**エアコン制御基板 DIP** — [98](../case-summaries/KH-HEALTH-AIR-TIMER-RELAY-98.md)・C-30-G5.3/G1（Lists）。

## 統合した回答・ノウハウ

[98 リレー](../case-summaries/KH-HEALTH-AIR-TIMER-RELAY-98.md)・[221 AC併設](../case-summaries/KH-HEALTH-AIR-AC-TIMER-221.md)・[112 MD20B](../practice-guides/KH-ALL-MD20B-MI4-FORCED-AC-112.md) と **ヘルスエア電源系** を共有 — 本件は **ダクト↔電源 BOX 配線**。

## 調査・確認手順

1. エアコン **200V**（Lists）。
2. 天蓋 **直流変換機** 2 系統（13.7V / 15V）。
3. ダクト BOX **補助 FAN**。
4. **8極コネクタ** 嵌合（YA186A628）。
5. 仍不良 → 98/221/DIP（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **320** | ピン抜け |
| [98](./KH-HEALTH-AIR-TIMER-RELAY-98.md) | リレー型 |
| [221](./KH-HEALTH-AIR-AC-TIMER-221.md) | AC 併設 |
| [112](../practice-guides/KH-ALL-MD20B-MI4-FORCED-AC-112.md) | MD-20B |

## KB確認に基づく追記

（C-30 系 pending）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §320 |
| KB | C-30-G5.3 / G1（pending） |

## 未確認事項

- YA186A628 ピン割当。
