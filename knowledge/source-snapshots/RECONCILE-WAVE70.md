---
snapshot_type: "reconciliation_wave_log"
wave: 70
generated_on: "2026-10-19"
---

# Wave 70（392 索引整理 + 本スロー網 + PDF 候補 + ドア連携）

## OneNote 反映

- **392** — §3 索引表を削除 → **navigation のみ**；§6 に **`:156` 同页テーマ** をカードリンク化（176/87/90/414/407/63/81 等）
- **`normalize_onenote_index_sections.py`** — **13** カード（別索引ブロック除去 + navigation 簡略化）
- **`build_onenote_pdf_kb_candidates.py`** — **136** 件 → `onenote-pdf-kb-candidates.jsonl`（C/TI/EA ヒント、すべて pending）

## §6 クラスタ連携

- **`append_cluster_related_rows.py --apply`** — **403/160/105** ドア・戸短・CLT 行（8 ファイル更新）
- **414 ↔ 392**、**87 → 392**、**407 → 414/392/ハブ**

## registry

- `build_registry.py`: **repair 0**, cards **657**

## 残

- `onenote-pdf-kb-candidates.jsonl` → `resolve_kb_refs.py` バッチ（未実行）
- Lists **§384** 全文、カード KB ingest
- hybrid **`:156`** 本文要約（Lists 既存カード優先 — 追加要約不要方針）

## 次

- Wave 71: **55/342/139** 本スロー DN 群の §6 相互リンク、ハブ表への PSL 系追記
- duplicate_matches ledger（変更なし）
