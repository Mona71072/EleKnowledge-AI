---
knowledge_id: KH-ALL-VHP-LANDING-OPEN-91
kind: practice_guide
status: draft
card_version: 1
title: "VHP 仕様 — ランディングオープン（LO）しない"
symptoms:
  - "VHP"
  - "ランディングオープン"
  - "LO"
  - "戸開阻止"
  - "アナウンス"
model_scope:
  lists_model_label:
    - "VFGLF・VFGLB・VFGH"
  control_methods:
    - "VFGLF"
    - "VFGLB"
    - "VFGH"
  observed_on: []
  scope_note: "Lists Model は複数制御。機種略称は物件品目で確認"
  may_apply_to:
    - "全自動で LO しない・視覚障害者仕様"
  excludes: []
source_refs:
  - ref_type: lists_item
    list_item_id: "91"
  - ref_type: onenote_page
    onenote_id: "699d1f86-7ec0-478d-8a09-77cf8b36da45:1"
    page_role: hybrid
    note: "LO/VHP — Lists 91 リンク（同頁に RSRL 一般論あり）"
---

# VHP 仕様 — ランディングオープン（LO）しない

## 使う場面・対象条件

**VFGLF/VFGLB/VFGH** **視覚障害者仕様（VHP）** で **ランディングオープン（LO）が動かない**（Lists 91）。LINKs は LO 標準だが **VHP 時は戸開阻止** 優先。

## 症状・現象

- 全自動で **LO 不動作**（Lists — 故障ではなく仕様）。

## ソース要約

### Lists（91）

- **原因**: VHP で **アナウンス発報中は戸開阻止**。
  - **戸開アナウンス** 完了前の戸開開始を防ぐ。
  - **階床アナウンス** — JEAS-515E に従い到着前に完了 → **戸開阻止** → **LO しない場合あり**。
- **二か国語等** で待ち時間長期化注意。
- **対応**: 現場代理人経由 **営業設計** に設計思想確認（Lists）。

### OneNote（`:1` — LO 節のみ）

- **LINKs は LO 標準**、**AXIEZ は LO 適用不可**（OneNote 一般論）。
- **Lists 91 同一タイトル**（VHP 時 LO しない）リンク — **原因・対応は Lists 91**（アナウンス中戸開阻止）。
- 同頁 **RSRL/DCRL** リレベル一般論は **91 本文に転記しない**（別テーマ）。

## 統合した回答・ノウハウ

LO 不具合と断定せず **VHP + アナウンス状態** を確認。**91** はエレ横断（Lists Model 3 系）。

## 調査・確認手順

1. VHP 仕様の有無。
2. 戸開/階床アナウンス **鳴動中** か。
3. 営業設計確認（Lists 指示）。

## 関連事例と条件の違い

| テーマ | 備考 |
| --- | --- |
| **91 LO しない** | **仕様**（VHP 戸開阻止） |
| **399 チャイム** | 乗場 ST **S/W** 信号更新 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §91 |
| OneNote | なし |
| KB | 要目資料（Lists 抜粋のみ — pending） |

## 未確認事項

- 機種別パラメータ差 — KB 未照合。
