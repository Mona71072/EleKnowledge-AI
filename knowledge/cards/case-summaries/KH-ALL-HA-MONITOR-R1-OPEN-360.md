---
knowledge_id: KH-ALL-HA-MONITOR-R1-OPEN-360
kind: case_summary
status: draft
card_version: 1
title: "ヘルスエア — モニター出力なし（R1 抵抗オープン）"
symptoms:
  - "ヘルスエア"
  - "モニター出力"
  - "R1抵抗"
  - "高電圧電源"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "360"
---

# ヘルスエア — モニター出力なし（R1 抵抗オープン）

## 使う場面・対象条件

**ヘルスエアモニター出力電圧** が **出ない**（Lists 360）。

## 症状・現象

- **電気的**（Lists）。

## ソース要約

### Lists（360）

- **HE 本体要因なし** — **据付中過大電力/ノイズ** 推測。
- **R1 抵抗オープン** → 交換で正常（Lists cause）。
- **Notes**: モニター出力なし時 **高電圧電源 R1** 抵抗値測定。
- **progress**: 情報管理保留部分あり。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

[320 コネクタピン](./KH-LINKS-HEALTH-AIR-CONNECTOR-320.md)・[206 抵抗極性](../practice-guides/KH-ALL-HA-RESISTOR-POLARITY-206.md) と **HE 系** — **360** は **R1 オープン**。

## 調査・確認手順

1. HE **本体** vs **周辺電源** 切分。
2. **R1** 抵抗値（Lists Notes）。
3. 交換後 **モニター出力** 規格値。
4. 過大印加 **履歴**（据付工程）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **360** | **R1 オープン** |
| [320](./KH-LINKS-HEALTH-AIR-CONNECTOR-320.md) | **8 極 CN 抜け** |
| [98](./KH-HEALTH-AIR-TIMER-RELAY-98.md) | タイマーリレー |
| [225](./KH-VFGLF-HA-MONITOR-0V-225.md) | **モニター 0V** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §360 |

## 未確認事項

- progress 保留部分。
