---
knowledge_id: KH-VFGLF-R03-PIT-WIRE-226
kind: case_summary
status: draft
card_version: 1
title: "R03 昇降路幹線損傷 — ダウン呼び常時・BP ヒューズ・29 ライン"
symptoms:
  - "R03"
  - "ピットツナギ"
  - "SSD"
  - "BPヒューズ"
  - "29ライン"
  - "420"
  - "VFGLF"
model_scope:
  lists_model_label:
    - "VFGLF"
  machine_room:
    - "MRL"
  control_methods:
    - "VFGLF"
  observed_on:
    - "VFGLF"
  may_apply_to:
    - "OH 後ダウン呼び常時・BP 飛び・29 不入"
  excludes: []
  scope_note: "Lists ↑高。建築ビス損傷は他機種も（Notes）"
source_refs:
  - ref_type: lists_item
    list_item_id: "226"
---

# R03 昇降路幹線損傷 — ダウン呼び常時・BP ヒューズ・29 ライン

## 使う場面・対象条件

**VFGLF** **オーバーホール前後** に **①ダウン呼び常時 ②BP ヒューズ ③29 ライン** 複合。**Lists ↑高**。

## 症状・現象

- 手動で **ダウン呼び自動**、**UP 不可**
- **ELD 投入 + MCB** で **BP ヒューズ** — MELD/停電灯/地震計不可
- **29 不入**（ピット SW/DOT、Lists）

## ソース要約

### Lists（226）

- **原因**: **R03（制御盤～ピットツナギ）** **建築ボードビス断線**（添付参照）。
- **①**: DRT **B9 SSD** 48V 常時 — **B9/B10 と 420 導通** 等、PS1 抜差しで一時改善も **SSD/SSU 単体断線** 残存例。
- **②**: **B48V と 400 導通** → 地絡・ヒューズ。
- **③**: **70EDB 不通** → ピット SW 無電圧。
- **Notes**: LINKs 限らず **昇降路幹線** で同様リスク。

### OneNote

- タイトル一致索引なし。

## 統合した回答・ノウハウ

複合症状は **R03 一括損傷** を疑い Lists progress の **DRT/PS1/PID ピン** 切り分け。**176**（N00 アース）とは別経路。[217 P15 干渉](./KH-VFGLF-P15-CABLE-CAGE-217.md) は **クリアランス** 別軸。

## 調査・確認手順

1. ダウン呼び常時 — **DRT B9** 48V、**420 導通**（Lists ①）。
2. BP ヒューズ — **PS1 A1/B1** B48V–400 導通（Lists ②）。
3. 29 — **70EDB DRT A2–PID B1**（Lists ③）。
4. R03 沿い **物理損傷**（ビス等）。

## 関連事例と条件の違い

| list | 焦点 |
| --- | --- |
| **226** | **R03 幹線** 物理損傷 |
| [197](./KH-VFGLF-SSC-JGS-CR1-197.md) | SSC・420 |
| **176** | **N00 アース** 531 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §226（添付） |
| OneNote | なし |
| KB | なし |

## 未確認事項

- 添付図のリポジトリ同梱有無。
