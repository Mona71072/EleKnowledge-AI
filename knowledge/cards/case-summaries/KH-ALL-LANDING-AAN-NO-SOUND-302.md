---
knowledge_id: KH-ALL-LANDING-AAN-NO-SOUND-302
kind: case_summary
status: draft
card_version: 1
title: "スイング — 乗場アナウンス鳴らない"
symptoms:
  - "AAN"
  - "反対側が使用中"
  - "SPコネクタ"
  - "7seg"
model_scope:
  lists_model_label: ["全エレ機種"]
  may_apply_to: ["スイング運転"]
source_refs:
  - ref_type: lists_item
    list_item_id: "302"
---

# スイング — 乗場アナウンス鳴らない

## 使う場面・対象条件

**スイング運転** で **乗場アナウンス**（反対側使用中）が **鳴らない**（Lists 302）。

## 症状・現象

- **7seg 不点灯** → **AAN 電源なし**（Lists）。

## ソース要約

### Lists（302）

- **SP コネクタ抜け**、**AAN 電源 OFF**（Lists）。
- **progress**: RSW 設定、プロトコル変換基板 **7seg/D2**、各 CN 電圧、N3 スピーカ電圧（Lists）。

## 統合した回答・ノウハウ

[78 ESC アナウンス](../practice-guides/KH-ESC-SVFC-ANNOUNCE-RSW-78.md)・[322 LHV-10X](../practice-guides/KH-ALL-ANNOUNCE-LHV10X-MODE-322.md) は **別装置** — 本件は **乗場 AAN スイング連動**。

## 調査・確認手順

1. **7seg 点灯**（電源）。
2. **音声合成 SP** 嵌合。
3. Lists progress **RSW / 7seg / 電圧** 順。
4. 最上階 **終端抵抗 TM4→TM1**（Lists）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **302** | 乗場 AAN |
| [399](./KH-ALL-HALL-CHIME-SIGNAL-399.md) | 乗場チャイム |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §302 |

## 未確認事項
