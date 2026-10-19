---
snapshot_type: "reconciliation_wave_log"
wave: 62
generated_on: "2026-10-19"
---

# Wave 62（OneNote 同期・拡張索引）

## 新規テーマ

なし。**累計 Wave テーマ: 395**。

## 実施

- `scripts/knowledge/sync_onenote_sections.py`
  - frontmatter の `onenote_page` と §3 **### OneNote** を **273 カード**で同期（「タイトル一致索引なし」解消）
  - **拡張索引**（Lists ID in body / タイトル先頭一致）: **+15** → [lists-onenote-extended-hits.jsonl](../registry/lists-onenote-extended-hits.jsonl)
  - スナップショット未検出: **123** カードに「**タイトル一致・ID 索引未検出**」を明記（Lists のみ運用）
- **障害**: 初回 write で FM 閉じ `---` が note 行に連結 → `build_registry` が cards **168** まで落ちた
- **復旧**: `scripts/knowledge/fix_card_frontmatter_closing.py`（**288** ファイル）— 以後 sync は `\n---\n` 形式で write

## registry（復旧後）

- `card-source-links`: **765** 行、repair **0**

## OneNote カバレッジ（概算）

| 種別 | 件数 |
| --- | --- |
| frontmatter に `onenote_page` | 292+（127 title + 15 extended + 既存） |
| 未検出明記（Lists のみ） | ~123 |

## 次

- Vault / キーワード grep で **未検出 123** を個別探索（別 Wave）
- §384、227 duplicate、ledger
