---
knowledge_id: KH-ALL-WELDER-LOW-VOLT-DN-383
kind: case_summary
status: draft
card_version: 1
title: "仮設ウェルダー低電圧で高速 DN のみ E-STOP"
symptoms:
  - "高速DN"
  - "160V"
  - "ウェルダー"
  - "631"
model_scope:
  lists_model_label: ["全エレ機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "383"
---

# 仮設ウェルダー低電圧で高速 DN のみ E-STOP

## 使う場面・対象条件

**KE-LG** 等 **高速 DN のみ** 短距離 **E-STOP**、**UP は可**（Lists 383）。

## 症状・現象

- 631/64D/E34 系 — **U-CAN 切断推測**（Lists progress）。

## ソース要約

### Lists（383）

- **原因**: 調整可能ウェルダー **160 V のまま** — **CWT 持上げ DN** で **電圧不足**（エラー出ず例）。
- **対応**: **200 V** 設定で解消。
- **Notes**: 入線時 **RST 電圧** 再徹底 — 300 V 出力機は **基板過電圧** も疑う。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

終点 SW 疑い **切分後** **電源測定**（Lists ③）— **383** と [382](./KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) は **症状似る** が **電圧** vs **12V 地絡**。

## 調査・確認手順

1. **リミット** MON3/3（Lists ①②）。
2. **RST 電圧**（DN 負荷時）。
3. ウェルダー **定格/前使用者設定**。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **383** | **仮設電圧** |
| [382](./KH-VFGLF-KEIAIN-HARNESS-PINCH-382.md) | **CAN/12V** |
| [据付・試験・調整ハブ](../practice-guides/KH-ALL-INSTALL-TEST-ADJUST-HUB.md) | 設定・寸法・本スロー **横断** |

## KB確認に基づく追記

（Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §383 |

## 未確認事項

- なし。
