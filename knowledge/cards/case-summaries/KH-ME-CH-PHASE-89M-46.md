---
knowledge_id: KH-ME-CH-PHASE-89M-46
kind: case_summary
status: draft
card_version: 1
title: "ME-CH — 逆相で 89M 振動・空回し不可"
symptoms:
  - "空回し"
  - "D89"
  - "#29"
  - "89M"
  - "5番コンタクタ"
model_scope:
  lists_model_label: ["ME-CH"]
source_refs:
  - ref_type: lists_item
    list_item_id: "46"
---

# ME-CH — 逆相で 89M 振動・空回し不可

## 使う場面・対象条件

**ME-CH** **空回し** で **#29 は入るが D89 不入・#5 不入**（Lists 46）。

## 症状・現象

- **89M 入り切り繰返し**（正常時は励磁維持→D89 ON）（Lists）。
- エラー例: 011, 012, 311, 631, 64D/E/F, A43, A52, E35/E36, E45/E46 等（Lists）。

## ソース要約

### Lists（46）

- **原因**: **仮設分電盤 R/T 逆相** — 客先側 **絶縁トランス** 等で **P1 にエラー出ず**（Lists）。
- **教訓**: 昇降機だけでなく **外部電源・施錠盤** も疑う（Lists Notes）。

## 統合した回答・ノウハウ

相順系は **KM-LD 回生** [54](./KH-KM-LD-PWFH-PHASE-54.md)・**トランス** [50](./KH-LINKS-TRANS-CRIMP-50.md)・**LINKs 盤 U/V** [10](./KH-LINKS-UV-PHASE-FREE-RUN-10.md) と **症状が似る** — **89M/D89** は ME-CH 空回しの Lists 固有切り口。

## 調査・確認手順

1. #29 vs **D89** vs **#5**。
2. **89M** 励磁状態。
3. **仮設分電 RST 相順**（Lists — progress 保留部分は転記しない）。
4. P1 エラーと客先側電源の切り分け。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **46** | 89M・仮設逆相 |
| [54](./KH-KM-LD-PWFH-PHASE-54.md) | PWFH・回生 15m |
| [50](./KH-LINKS-TRANS-CRIMP-50.md) | ROA/SOA 結線 |
| [10](./KH-LINKS-UV-PHASE-FREE-RUN-10.md) | LINKs U/V |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §46 |

## 未確認事項

- Lists progress（情報管理保留の有無はスナップショット確認）。
