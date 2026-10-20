---
knowledge_id: KH-KM-LD-CCP-REGEN-80
kind: case_summary
status: draft
card_version: 1
title: "KM-LD — CCP 未投入で回生スロー不可"
symptoms:
  - "WOS"
  - "回生コンバーター"
  - "CCP"
  - "15m/min"
  - "スロー"
model_scope:
  lists_model_label: ["KM-LD"]
  machine_room: ["MR"]
source_refs:
  - ref_type: lists_item
    list_item_id: "80"
---

# KM-LD — CCP 未投入で回生スロー不可

## 使う場面・対象条件

**KM-LD** **WOS** で **回生コンバーター使用時 15 m/min スロー不可**、**8 m/min（非回生）では可**（Lists 80）。

## 症状・現象

- 回生 ON → スロー不可；回生 OFF → 8 m/min で可（Lists）。

## ソース要約

### Lists（80）

- **原因**: 制御盤 **CCP ブレーカー未投入** — 投入で回生付き運転可能（Lists）。
- **Notes**: CCP 投入必要性が **資料に明記なし** → 連メモ展開・資料改定依頼（Lists）。
- **progress**: 回生盤配線・NVA/NVB/NVC・相関・48V・C1 RSW 等確認履歴（Lists）。

## 統合した回答・ノウハウ

WOS 回生スロー不可は **CCP 投入** を Lists 上の第一確認。**配線・通信** は progress 参照、手順断定は KB 待ち。

## 調査・確認手順

1. **CCP ブレーカー** 投入状態。
2. 回生 ON/OFF で **8 vs 15 m/min** 切り分け。
3. Lists progress の **コネクタ・48V・C1** 項目（必要時）。
4. PT.14 図面ピン（Lists — KB 未レビュー）。

## 関連事例と条件の違い

| テーマ | 備考 |
| --- | --- |
| **80** | CCP＋回生 |
| **54** | [PWFH 逆相](./KH-KM-LD-PWFH-PHASE-54.md) |
| [116](./KH-KM-LD-L20A-GROUND-116.md) | KM-LD 地絡 |
| [306](../practice-guides/KH-MR-NL-DIFF-TRANS-ESTOP-306.md) | MR NL 差動（別系） |
| [287](./KH-KM-LD-REGEN-LID-SW-NVA-287.md) | 回生フタ SW |

## KB確認に基づく追記

（該当 KB 未指定）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §80 |

## 未確認事項

- CCP 記載の正式 C／連絡メモ改定結果。
