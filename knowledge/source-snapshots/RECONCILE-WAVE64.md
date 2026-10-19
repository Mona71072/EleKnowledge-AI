---
snapshot_type: "reconciliation_wave_log"
wave: 64
generated_on: "2026-10-19"
---

# Wave 64（OneNote 統合・監査）

## 新規テーマ

なし。**累計 Wave テーマ: 395**。

## 実施

### 1. 自動付与の停止（候補台帳化）

- `attach_onenote_title_hits.py` / `sync_onenote_sections.py` / `attach_onenote_from_drafts.py` — **既定は候補・registry のみ**。カード更新は **`--apply`**
- タイトル候補: `registry/onenote-attach-candidates-title.jsonl`（121 件、未 apply）

### 2. OneNote 1,039 頁分類

- `classify_onenote_pages.py` → `registry/onenote-page-catalog.jsonl`
- content **635** / cross_topic **201** / empty **176** / hybrid **15** / index **12**

### 3. 監査台帳

- `build_onenote_audit_ledger.py` → `onenote-card-audit.jsonl` + **`onenote-wave61-63-audit.jsonl`**
- カード上の参照 + Wave 61 title / 62 extended / 63 draft + title **候補**を突合

### 4. 是正

- `apply_onenote_page_roles.py` — **53** カードに catalog 由来 `page_role`
- `normalize_onenote_index_sections.py` — **16** カード §3 を navigation 化
- `page_role: body` → **`content`** に統一（5 ファイル）

### 5. クラスタ要約（パイロット）

| クラスタ | カード | 内容 |
| --- | --- | --- |
| SCU / エレコール | [228](../cards/practice-guides/KH-SCU20-CONN-TEST-228.md) | 索引頁 navigation + 233/149 相互リンク |
| ESC SVFC | [326](../cards/case-summaries/KH-ESC-SVFC-STEP-CHAIN-GAP-326.md), [325](../cards/case-summaries/KH-ESC-SVFC-P2-FWR-TOGGLE-325.md), [298](../cards/case-summaries/KH-ESC-SVFC-UVW-WIRING-298.md) | 326 のみ content 頁要約。325/298 は Lists 正 + クラスタリンク |
| 戸・DOB | [403](../cards/case-summaries/KH-VFGLF-DOR-DOB-403.md) | 408/424/432 相互リンク（本文複製なし） |

### 6. 公開経路設計

- [card-kb-two-tier-retrieval.md](../../docs/features/development/card-kb-two-tier-retrieval.md)（development ドラフト）
- [CONTRACT.md](../CONTRACT.md) — OneNote 役割・`page_role`・候補 attach 運用

## registry

- `build_registry.py`: **repair 0**（実行時点）
- 詳細件数: `registry/onenote-card-audit-summary.json`

## 次

- Wave 61 候補 **121** 件の監査（`recommended_action` に従い `--apply` または手動 curate）
- 拡張 prefix hit **手動検証**（`manual_verify_prefix`）
- §384 / 227 統合、未検出 ~108 の grep 探索
