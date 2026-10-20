---

knowledge_id: KH-MRL-SOFT-MNT-170
kind: practice_guide
status: draft
card_version: 1
title: "ソフト MNT — 投入・解除と発報回避"
symptoms:
  - "ソフトMNT"
  - "ブロックサイン"
  - "保守合理化"
  - "R/M戻し忘れ"
  - "#29"
model_scope:
  lists_model_label: ["MRL機種"]
  machine_room: ["MRL"]
source_refs:
  - ref_type: lists_item
    list_item_id: "170"
  - ref_type: onenote_page
    onenote_id: "51232edc-3051-4d66-b01e-2e33ee73bc9c:1"
    page_role: content
---
# ソフト MNT — 投入・解除と発報回避

## 使う場面・対象条件

**引渡し後是正** で **P1=R/M のまま #29 遮断** — **警報盤・警備臨場** リスク（Lists 170）。

## 症状・現象

- **保守担当不在** の是正作業（Lists 要旨）。

## ソース要約

### Lists（170）

- **投入**: 自動モードで **自階釦+引戸内 UP/DN 同時押し** → ブザー・階床点滅 → ソフト MNT（Lists）。
- **解除**: **戸開+戸閉同押し** → 通常点灯 → **R/M**（Lists）。
- **Notes**: **R/M 戻し忘れ** — AUTO で MNT **120 分**で内部 R/M 化・監視盤異常灯有効（Lists）。タイマリセット手順あり。**VFGLB/GF** ソフトメンテ解除（最下階自動 **開閉 2 秒同押し** 等）。

### OneNote（`51232edc-3051-4d66-b01e-2e33ee73bc9c:1`）

- **Lists 170 と整合**: 引渡し後是正で **P1=R/M のまま #29 遮断** → 警報盤/警備臨場リスク。**ソフト MNT** で回避。
- **投入/解除手順**は Lists 170 が正（自階+引戸内 UP/DN 同押し → 解除は **最下階** 戸開+戸閉同押し等 — OneNote も同趣旨）。
- **保守合理化 S/W** 要（OneNote リンク先）。


## 統合した回答・ノウハウ

[173 ハードメンテ残留](../case-summaries/KH-VFGLB-MAINT-MODE-FLICKER-173.md)・[186 見守り](./KH-VFGLF-REMOTE-WATCH-186.md) — **170** は **ソフト MNT** で **トグル MNT 回避**。

## 調査・確認手順

1. **保守合理化 S/W** 有無。
2. 是正前 **ソフト MNT 投入**（Lists）。
3. 警備連携物件は **事前連絡**（Lists 発報例）。
4. 作業後 **解除→R/M**。

## 関連事例と条件の違い

| カード | 備考 |
| --- | --- |
| **170** | ソフト MNT |
| [173](../case-summaries/KH-VFGLB-MAINT-MODE-FLICKER-173.md) | ハード MNT |
| [175](../case-summaries/KH-VFGLB-ARES-SERVICE-STOP-175.md) | ARES+休止 |

## KB確認に基づく追記

（該当なし）

## 正式資料・元情報

| 種別 | 参照 |
| --- | --- |
| Lists | §170 |
| OneNote | 51232edc-3051-4d66-b01e-2e33ee73bc9c:1 |

## 未確認事項

- 機種別ソフトメンテ解除 UI（Lists Notes 抜粋のみ）。
