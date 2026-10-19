---
knowledge_id: KH-ALL-HALL-CHIME-SIGNAL-399
kind: case_summary
status: draft
card_version: 1
title: "乗場チャイム — AECH/AIL 同時適用で意図しない DN 音"
symptoms:
  - "電子音チャイム"
  - "AECH"
  - "AIL"
  - "乗場ステーション"
  - "500msec"
model_scope:
  lists_model_label:
    - "全エレ機種"
  observed_on: []
  may_apply_to:
    - "かご待機階で乗場釦時、標準チャイムが鳴らない・変な音"
  excludes: []
  scope_note: "全エレ Lists ラベル — 機種別 S/W は稲電見解参照"
source_refs:
  - ref_type: lists_item
    list_item_id: "399"
---

# 乗場チャイム — AECH/AIL 同時適用で意図しない DN 音

## 使う場面・対象条件

**乗場電子音チャイム（AECH）** と **即時予報（AIL）** **同時適用** で、かご待機階の乗場釦時に **標準チャイムが鳴らない**（Lists 399）。

## 症状・現象

- 到着予報後 **意図しないダウン音** 等（Lists 稲電見解）。

## ソース要約

### Lists（399）

- **机理**: かご待機階で上呼び → ①到着予報 → ②アップ音試行。①信号残存 + ② → **①&② = ③ダウン音**（Lists Notes 信号表）。
- **稲電見解**: 乗場 ST→チャイム **500ms ON** 仕様。制御盤→乗場 ST 信号が 500ms 内更新時、**前出力 OFF してから更新** が正 — **当該 S/W で OFF 処理漏れ**。

### OneNote

- なし。

## 統合した回答・ノウハウ

硬配線故障ではなく **ST S/W 更新処理** 論点（Lists）。**91**（VHP 戸開阻止）と混同しない。

## 調査・確認手順

1. AECH + AIL 同時適用か。
2. かご待機階・上呼び再現。
3. 稲電/開発 **S/W 修正** 有無（Lists 対応済み — 横展開確認）。

## 関連事例と条件の違い

| list | 内容 |
| --- | --- |
| **399** | チャイム **信号合成** |
| **91** | **VHP** LO |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §399 |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 修正 S/W の機種展開 — Lists のみ。
