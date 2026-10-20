---
snapshot_type: "reconciliation_wave_log"
wave: 3
generated_on: "2026-10-19"
review_status: unreviewed
publication_status: not_published
---

# 体系化 Wave 3（重要・高から3テーマ）

Wave2 候補どおり **UPS / P1·7SEG / 巻上機ビス**。Lists §節 + OneNote スナップショット統合。KB は filename 突合のみ（`content_reviewed` 前）。

| list_item_id | 重要度 | テーマ | knowledge_id | draft 写し（参照のみ） | カード |
| --- | --- | --- | --- | --- | --- |
| 350 | 重要 | UPS 不作動・監視盤優先 | KH-UPS-PEAK-SERVICE-350 | [ELV3_UPS群管理親ページ_参照記録.md](../drafts/ELV3_UPS群管理親ページ_参照記録.md) | [KH-UPS-PEAK-SERVICE-350.md](../cards/practice-guides/KH-UPS-PEAK-SERVICE-350.md) |
| 151 | 重要 | P1 不良で 7SEG/WDT 消灯 | （primary draft 未紐付） | [KH-P1-7SEG-WDT-151.md](../cards/case-summaries/KH-P1-7SEG-WDT-151.md) |
| 137 | ↑高 | ロープカバー取付ビス首下 | （primary draft 未紐付） | [KH-HOIST-SCREW-LENGTH-137.md](../cards/case-summaries/KH-HOIST-SCREW-LENGTH-137.md) |

## OneNote 突合メモ

| list | OneNote |
| --- | --- |
| 350 | 本文 `a556a262-…:1`（BE28 等）、確認手順 `1e0ad6f4-…:1`、索引 `…:145` |
| 151 | タイトル完全一致页なし |
| 137 | 索引 `c3cbdf09-…:131`（PM040MR 首下表なし言及） |

## 横断ツール

- `python3 scripts/knowledge/match_onenote_titles.py` → [lists-onenote-title-hits.jsonl](../registry/lists-onenote-title-hits.jsonl)（390 件中 **165** 件が OneNote タイトル hit、2026-10-19 実行）

## 次（Wave 4 候補）

- 高/重要で **カード未作成**: reconcile-summary の `high_importance_unmatched_lists`（13）を ledger と照合
- 同一タイトル横断: list **1/2**（かご内振動）
- 保留解除待ち: **413**, **14**, **349** 等（Lists 伏せ字）
