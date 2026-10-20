---
snapshot_type: "reconciliation_wave_log"
wave: 56
generated_on: "2026-10-19"
---

# Wave 56（保留 § 索引 + 連携是正）

## 新規（情報管理保留 — 索引カードのみ）

| list | knowledge_id | 連携 |
| --- | --- | --- |
| 390 | [KH-MRL-UCMP-SEISMIC-INDEX-390](../cards/practice-guides/KH-MRL-UCMP-SEISMIC-INDEX-390.md) | **227** / **79** |
| 337 | [KH-ALL-MILAI-HATCHING-337](../cards/practice-guides/KH-ALL-MILAI-HATCHING-337.md) | **311** / **333** |
| 335 | [KH-LINKS-BPS-SWITCH-335](../cards/practice-guides/KH-LINKS-BPS-SWITCH-335.md) | **395** |
| 253 | [KH-VFGLF-GROUP-WIRING-SAVE-MODE-253](../cards/practice-guides/KH-VFGLF-GROUP-WIRING-SAVE-MODE-253.md) | **384** / **371** / **373** |

**累計 Wave テーマ: 395**（Wave1–56、+4）。

## 連携是正（既存カード）

| 変更 | 内容 |
| --- | --- |
| **179** | **122** 未カード表記 → リンク |
| **122** | **179** / **363** リンク |
| **384** | **371** / **253** リンク |
| **371** | **384** / **253** リンク |

## スナップショット Lists § 状態

| 状態 | 件数 |
| --- | --- |
| **§ 節あり（390）** | 全 ID に `list_item_id` カードあり |
| **保留** | 253/335/337/390 本文保留・索引化済 |
| **384** | cause 未完 — 既存カードで索引 |
| **番号ギャップ** | 1–390 のうち **47** 番号はスナップショットに節なし |

## 次

- `python3 scripts/knowledge/build_reconcile_ledger.py` で summary 再生成
- Lists **384** cause 追記後 §3 更新
- draft↔card 一致率（reconcile-summary）の更新確認
