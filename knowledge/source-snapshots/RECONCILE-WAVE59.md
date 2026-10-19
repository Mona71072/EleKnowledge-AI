---
snapshot_type: "reconciliation_wave_log"
wave: 59
generated_on: "2026-10-19"
---

# Wave 59（関連表リンク一括）

## 新規テーマ

なし。**累計 Wave テーマ: 395**。

## 実施

- 新規 `scripts/knowledge/fix_related_list_links.py` — `list-item-to-card.jsonl` を正として、`| **NNN** |` を `[NNN](相対path)` に変換（**当該カード自身の list ID** は除外）。
- **duplicate primary** 優先: §227 → `KH-ALL-SMOKE-FIRE-SERVICE-MELD-227`、§154 → `KH-MRL-SMOKE-SHAFT-SENSOR-154`。
- **143 ファイル / 162 置換**。残り約 10 件は **自リスト ID 行**（384 on 384 等）または **同一行に既リンク**（392↔7/27）で意図的スキップ。
- 手動追記: 286 の 384 列、392 の 7/27 行、373→99 リンク `./` 修正。

## registry

- `build_registry.py` — repair **0**

## 次（Wave 60+）

- リンク表記 `(KH-*.md)` の `./` 統一（任意・108 行級 — 表示は通る）
- §384 Lists 原因全文
- OneNote / ledger unmatched
