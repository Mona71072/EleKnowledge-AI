---
knowledge_id: KH-ALL-MEGA-FIRE-PANEL-162
kind: practice_guide
status: draft
card_version: 1
title: "絶縁抵抗 500V — 火報盤基板直取込みで焼損"
symptoms:
  - "絶縁抵抗"
  - "メガー"
  - "火報盤"
  - "53番"
  - "410"
  - "FECA"
  - "官検"
model_scope:
  lists_model_label:
    - "全エレ機種"
  machine_room: []
  observed_on: []
  may_apply_to:
    - "信号回路 53 番等で DC500V メガー後、火報盤警報鳴り続け"
  excludes: []
  scope_note: "duplicate primary: case-elv-insulation-test-fire-alarm-panel-board-damage-id162"
source_refs:
  - ref_type: lists_item
    list_item_id: "162"
---

# 絶縁抵抗 500V — 火報盤基板直取込みで焼損

## 使う場面・対象条件

**調整・官検** で **信号回路（53 番 400 等）** の **絶縁抵抗試験** を行うとき。**全エレ機種**（Lists）。

## 症状・現象

- DC15V OK 後 **DC500V** 測定 → **0Ω 近傍**、**客先火報盤焼損・警報鳴り続け**（Lists）

## ソース要約

### Lists（162）

- **原因**: 無電圧 A 接点想定だが **基板直出力** — **DC500V が火報盤基板を損傷**。
- **指示**: 15V でグラつく／500V で 0Ω 落ち → **410/FECA 等客先接点を切離** してから 500V。**火報屋確認**、リレー追加検討。
- **Notes**: ホーチキ等 **基板直取込** 注意（能美・ニッタン等も増加、23/2/16）。C 資料改定依頼済（Lists）。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

「A 接点＝リレー出力」と決めつけない。**162** は **メガー前の接点切離** と **メーカー仕様** 確認。詳細手順は **elv-insulation-resistance-test-review-hold** 索引ではなく Lists + 将来 KB。

## 調査・確認手順

1. 試験対象回路（53 番等）と **客先火報接点** 経路。
2. **DC15V → DC500V** の段階と読み（Lists パターン）。
3. 異常時 **客先接点切離** 後再測定。
4. **火報業者** へ盤状態確認。

## 関連事例と条件の違い

| テーマ | 162 |
| --- | --- |
| 試験 | **絶縁抵抗** |
| 307 | 電源線 IR（別 list） |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §162（添付） |
| OneNote | なし |
| KB | C 資料改定（pending） |

## 未確認事項

- 全メーカー一覧（Lists「その他未確認」）。
