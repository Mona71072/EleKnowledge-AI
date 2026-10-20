---
knowledge_id: KH-MR-NL-DIFF-TRANS-ESTOP-306
kind: practice_guide
status: draft
card_version: 1
title: "MR 高速 — NL 差動トランス調整後 E-STOP 確認"
symptoms:
  - "NL"
  - "差動トランス"
  - "E-STOP"
model_scope:
  lists_model_label: ["MR機種"]
  may_apply_to: ["高速機種"]
source_refs:
  - ref_type: lists_item
    list_item_id: "306"
---

# MR 高速 — NL 差動トランス調整後 E-STOP 確認

## 使う場面・対象条件

**高速機** で **NL 差動トランス電圧調整後**（Lists 306）。

## 症状・現象

- （豆知識 — 調整後の取り付け確認）

## ソース要約

### Lists（306）

- 調整後 **一度 E-STOP** を推奨。
- E-STOP 後 **電圧変化なし** → **垂直取付** と判断。
- **変化あり** → **斜め取付** 疑い → **再調整**（Lists）。

## 統合した回答・ノウハウ

[80 CCP 回生](../case-summaries/KH-KM-LD-CCP-REGEN-80.md)・[54 PWFH](../case-summaries/KH-KM-LD-PWFH-PHASE-54.md) は **KM-LD 電源系** — 本件は **MR NL 差動**（別枝）。

## 調査・確認手順

1. 差動トランス **電圧調整** 実施。
2. **E-STOP** 操作。
3. 調整値 **変化の有無**。
4. 変化あり → 取付角度・再調整（Lists）。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **306** | NL 差動 |
| [80](../case-summaries/KH-KM-LD-CCP-REGEN-80.md) | KM-LD CCP |
| [54](../case-summaries/KH-KM-LD-PWFH-PHASE-54.md) | PWFH 相 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §306 |

## 未確認事項

- NL 差動トランス型式別手順。
