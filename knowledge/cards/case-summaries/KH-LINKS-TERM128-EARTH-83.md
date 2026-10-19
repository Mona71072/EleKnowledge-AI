---
knowledge_id: KH-LINKS-TERM128-EARTH-83
kind: case_summary
status: draft
card_version: 1
title: "LINKs — 128番 BOON 誤アースで絶縁不良"
symptoms:
  - "絶縁不良"
  - "メガ"
  - "128番"
  - "BOON"
  - "アース"
model_scope:
  lists_model_label: ["AXIEZ-LINKS"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "83"
---

# LINKs — 128番 BOON 誤アースで絶縁不良

## 使う場面・対象条件

**AXIEZ-LINKS** 調整時 **制御回路メガ ~0.2 MΩ**（Lists 83・多発注意）。

## 症状・現象

- 制御回路 **絶縁不良**（Lists）。

## ソース要約

### Lists（83）

- **原因**: ターミナル **128 番（BOON／MELD−）** に **H10/H20 アース線を誤挿** — BOON 線がアースに見えるため（Lists）。
- **対応**: アースを **正しいアース端子** へ → 絶縁良好（Lists progress）。
- **Notes**: 神奈川・関越・東京で同型 → **据付注意喚起**（Lists）。

## 統合した回答・ノウハウ

SF 1次不良→ **MB5 経路** で **128 番** を必ず目視。**BOON とアースの混同** が Lists 上の典型。

## 調査・確認手順

1. SF **1次側** メガ。
2. M1 **MB5(N00)** 抜き差しで切り分け（Lists progress）。
3. **128 番** BOON vs H10/H20 アースの有無。
4. 正規アース端子へ結線。

## 関連事例と条件の違い

| list | 備考 |
| --- | --- |
| **83** | 128 番誤配 |
| **101** | MELD±逆 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §83 |

## 未確認事項

- 端子配列の現行 C 図（添付写真参照 — 未転記）。
