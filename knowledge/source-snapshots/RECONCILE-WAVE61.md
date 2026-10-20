---
snapshot_type: "reconciliation_wave_log"
wave: 61
generated_on: "2026-10-19"
---

# Wave 61（OneNote タイトル一致 — 索引付け）

## 新規テーマ

なし。**累計 Wave テーマ: 395**。

## 実施

- `scripts/knowledge/attach_onenote_title_hits.py` — [lists-onenote-title-hits.jsonl](../registry/lists-onenote-title-hits.jsonl) の **165** Lists 項のうち、カードに `onenote_page` が無かった **127** 件へ:
  - frontmatter `source_refs` に **1 件**（先頭 hit の `onenote_id`）
  - §3 `### OneNote` — スナップショット文件名・**本文未転載**
- **タイトル hit ありで OneNote 未参照: 0**
- 残 **95** カードの「タイトル一致索引なし」= **Lists タイトルが OneNote 本文に無い** 節（別探索要）

## registry

- `card-source-links`: **760** 行（+127 onenote）
- repair **0**

## 次

- OneNote **手動 grep / match** で残 95+α
- §384、227 統合、ledger unmatched
