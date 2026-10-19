---
snapshot_type: "reconciliation_wave_log"
wave: 69
generated_on: "2026-10-19"
---

# Wave 69（Wave 68 適用 + テンプレ是正）

## 実施

### Wave 68 未適用分の反映

- **INDEX** — `§据付・試験・調整（横断入口）` 追加（ハブ・本スロー・LV 戸・官検 419）
- `append_adjustment_hub_links.py --apply` — **27** ファイルに **調整・試験（入口）** 行（419 / CM-LB 戸短 / 160 含む）
- スクリプト — `## 関連事例` 表もハブ追記対象に拡張

### OneNote 反映（content / cross）

- **419** — §3 **OneNote navigation**（`onenote-6ff82bf…`、C-7-C3600-J 正本明記）
- **414** — §6 欠落を補完 + ハブ行（本スロー後 421）

### テンプレ

- `## 関連事例` → `## 関連事例と条件の違い` — **9** カード一括（ESC/MRL/VFGR 等）

## registry

- `build_registry.py`: **repair 0**, cards **657**

## 残

- **392** §3 索引表 — CONTRACT「索引他テーマ転記禁止」とギャップ（要 navigation 簡略化 Wave）
- **414** 等 — frontmatter OneNote `:156` 未付与（索引参照は本文のみ）
- Lists **§384** 全文、カード KB **ingest**

## 次

- Wave 70: `:153` / `:156` 配下 PDF → `document_number` 候補台帳（KB 突合のみ、断定なし）
- `normalize_onenote_index_sections.py` 対象を 392 等 hybrid に限定適用検討
