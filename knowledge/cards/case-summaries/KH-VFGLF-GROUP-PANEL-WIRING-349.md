---
knowledge_id: KH-VFGLF-GROUP-PANEL-WIRING-349
kind: case_summary
status: draft
card_version: 1
title: "増設盤 MAF/MAG と MKF/MKG 誤結線 — Z03/P1 焼損"
symptoms:
  - "増設盤"
  - "Z03"
  - "P1"
  - "I-CAN"
  - "2C2BC"
  - "火災管制"
  - "地震管制"
  - "306"
  - "30C"
model_scope:
  lists_model_label:
    - "VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "2C2BC 増設盤で通常運転可でも管制運転が効かない"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "349"
---

# 増設盤 MAF/MAG と MKF/MKG 誤結線 — Z03/P1 焼損

## 使う場面・対象条件

**VFGLF 2C2BC** **増設盤** 工事後、**Z03/P1 損傷** や **火災・地震管制運転不動** 疑い。**Lists 重要**（症状・原因欄は情報管理保留）。

## 症状・現象

- **MAF/MAG（200V）** と **MKF/MKG（I-CAN）** **誤結線** → **Z03 焼損**（Lists タイトル・症状要約）
- 通常運転は継続していたが **最終調整** で Z03 交換後も **火災・地震管制運転不動**（Lists）
- エラー例 **306, 30C**（Lists）

## ソース要約

### Lists（349）

- **Reported cause and response**: **情報管理確認まで保留**
- **progress**: **保留**

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

増設盤 **200V 系と I-CAN 系コネクタ取違え** は通常運転を残し得る — **管制系** で顕在化（Lists 症状）。詳細結線は保留解除まで **Lists §349 全文** を正とする。

## 調査・確認手順

1. 増設盤 **MAF/MAG vs MKF/MKG** ラベル・結線（Lists 症状）。
2. Z03/P1 状態、**306/30C**。
3. **火災・地震管制** 試験（Lists 顕在化タイミング）。
4. **171 E-CAN** / **384 群管理** との混同回避。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **349** | 増設盤 **誤結線** |
| **171** | MAG **未接続** |
| [384](./KH-CM-MA-3CAR-GROUP-2C2BC-384.md) | 3car **2C-2BC** |

## KB確認に基づく追記

（保留 — 原因本文未取得）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §349 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- **原因・progress 保留**（識別情報含む可能性）。
- duplicate: `knowhow-elv3-group-control-mixed-model-power-review` は **349 カード根拠にしない**（別 record）。
