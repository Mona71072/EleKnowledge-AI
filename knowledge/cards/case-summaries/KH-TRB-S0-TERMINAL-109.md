---
knowledge_id: KH-TRB-S0-TERMINAL-109
kind: case_summary
status: draft
card_version: 1
title: "トランスリアクトル S0 端子増し締めでケーブル脱落"
symptoms:
  - "トランスリアクトル"
  - "TRB2"
  - "S0A"
  - "VFGLB"
  - "増し締め"
  - "端子"
  - "引渡し前点検"
model_scope:
  lists_model_label:
    - "VFGLB"
  product_lines:
    - "AXIEZ"
  machine_room:
    - "MRL"
  model_abbreviations: []
  control_methods:
    - "VFGLB"
  observed_on:
    - "VFGLB"
  may_apply_to:
    - "トランスリアクトル箱 TRB2 端子増し締め確認を行う現場"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "109"
    source_id: evidence-list-trb-s0-terminal-109
---

# トランスリアクトル S0 端子増し締めでケーブル脱落

## 使う場面・対象条件

**引渡し前点検** でトランスリアクトル箱内 **TRB2 の S0A 端子** 増し締めを行うとき。Lists 機種 VFGLB。

## 症状・現象

- 制御盤電源遮断後、S0A 増し締め中に **奥側ケーブル2本のうち1本が端子から脱落**（Lists）

## ソース要約

### Lists（list_item_id 109）

- **原因（報告）**: 端子ボルト **弛み**。
- **対応**: 丸端子へボルト通し固定、マーキング。
- **注意**: 増し締め前に **制御盤で電源遮断必須**。引渡し前点検で **必ず確認**。

### OneNote

- list タイトル **一致页なし**（2026-10-19 スナップショット）。

## 統合した回答・ノウハウ

S0 系端子は弛みがあると、増し締め操作そのもので **既存ケーブルが抜ける**。作業前遮断に加え、増し締め前に **端子状態・ケーブル食込み** を目視し、弛みがあれば脱落リスクを想定する。

## 調査・確認手順

1. 制御盤で電源遮断（Lists 必須）。
2. TRB2 S0A: ボルトトルク/弛み、ケーブル食込み、丸端子状態。
3. 増し締めは脱落を起こさない順序・支持（Lists 事例: 奥側が脱落）。
4. 固定後マーキング（Lists 対応）。

## 関連事例と条件の違い

| 項目 | 109 | 一般的 TR 点検 |
| --- | --- | --- |
| 契機 | 増し締め確認 | 絶縁・温昇等 |

## KB確認に基づく追記

（該当 KB 参照なし — Lists のみ）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §109 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- Lists 添付写真の端子構成（スナップショット未同梱）。
- VFGLB 以外機種への TRB2 同一性。
