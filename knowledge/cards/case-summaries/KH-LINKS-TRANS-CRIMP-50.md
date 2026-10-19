---
knowledge_id: KH-LINKS-TRANS-CRIMP-50
kind: case_summary
status: draft
card_version: 1
title: "LINKs — トランス結線不良で空回し不可"
symptoms:
  - "空回し"
  - "7SEG"
  - "ROA"
  - "SOA"
  - "P1"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "50"
---

# LINKs — トランス結線不良で空回し不可

## 使う場面・対象条件

**AXIEZ-LINKS** **トランス結線後** **P1 7SEG 不点灯・空回し不可**（Lists 50・重要）。

## 症状・現象

- 7SEG 消灯（Lists）。
- **ROA-R1/SOA-S1/TOA-T1 短絡** で 7SEG 点灯・空回し可（Lists）。

## ソース要約

### Lists（50）

- **原因**: **ROA/SOA 現地結線部潰れ・甘結線** — 修正後 **200 V 相関良好**（Lists）。
- **Notes**: 甘結線のまま運転 → **発煙発火リスク**。**電源遮断** の上確認。電圧異常時は **抜いて端子確認**（Lists）。
- **再発**: 終点 SW **ON 故障** 拾い — OFF 後正常（Q-3688 No11、Lists Notes）。

## 統合した回答・ノウハウ

相関 **ROA-SOA 0V 期待** vs 実測 **68V 等** は **結線不良** の Lists 典型（progress）。

## 調査・確認手順

1. トランス盤・現地結線 **相関電圧**（Lists progress）。
2. 工場側 ROA/SOA/TOA 抜き **現地側のみ** 測定。
3. **潰れ・再結線**。
4. 解消後も不动なら **終点 SW**（Lists Notes）。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **50** | トランス結線 |
| **46** | [仮設逆相 89M](./KH-ME-CH-PHASE-89M-46.md) |
| **87** | RHQ コネクタ |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §50 |

## 未確認事項

- Q-3688 No11 本文。
