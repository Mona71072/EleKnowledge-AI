---
knowledge_id: KH-ALL-E-MRL-SUPPLY-VOLTAGE-84
kind: practice_guide
status: draft
card_version: 1
title: "E系 MRL — 受電電圧許容と品質記録"
symptoms:
  - "受電電圧"
  - "200V"
  - "400V"
  - "品質記録"
  - "IDS"
model_scope:
  lists_model_label: ["（Lists 機種空）"]
  machine_room: ["MRL"]
  may_apply_to: ["KE-LG", "KE-*F", "AXIEZ 容量拡張"]
source_refs:
  - ref_type: lists_item
    list_item_id: "84"
  - ref_type: kb_document
    document_number: "S-91-A-EG-A040-J"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "S-91-A-EF-A002-J"
    kb_verify_status: pending
  - ref_type: kb_document
    document_number: "S-91-A-EF-C030-J"
    kb_verify_status: pending
---

# E系 MRL — 受電電圧許容と品質記録

## 使う場面・対象条件

**E系 MRL**（KE-LG / KE-*F 等）の **客先要求電圧・許容変動** と **引渡し時の品質記録** の整理（Lists 84・品質記録確認）。

## 症状・現象

- （豆知識・技評 — 故障症状ではない）

## ソース要約

### Lists（84）

- **客先要求**: 200V 系 **200–220 V**、400V 系 **380–440 V**；変動 **+5%～−10%**、不平衡 **5%**（Lists）。
- **製品裕度例**: 200V 系 **180–231 V** まで IPU 組立差なし（Lists）。
- **Notes（2024 追記）**: 製品上限と **工事試験報告書「定格±5%・相間3%」** の差 — 超過時は **営設相談**（官検待ちしない）。稲電主張: **IDS ±5%** を引渡し目標 vs **製品絶対限界** の区別。資料間差異あり明確指示なし（Lists）。

## 統合した回答・ノウハウ

現場判断は **IDS ±5%（品質記録）** と **製品裕度（180–231 V 等）** を混同しない。数値の最終解釈は **稲電・営設確認**（Lists Notes）。

## 調査・確認手順

1. 受電 **実測** と IDS 定格。
2. 工事試験報告書基準との **差分** 記録。
3. 許容超過 → **営設相談**（Lists Notes）。
4. S-91 系資料で機種別確認（KB pending）。

## 関連事例と条件の違い

| テーマ | 備考 |
| --- | --- |
| **84** | E系 MRL 電圧 |
| **80** | KM-LD 回生 |

## KB確認に基づく追記

（S-91 系未レビュー）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §84 |
| KB | S-91-A-EG-A040-J、S-91-A-EF-A002-J、S-91-A-EF-C030-J（pending） |

## 未確認事項

- 2024 以降の稲電統一指示の有無。
