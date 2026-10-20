---
status: draft
last-verified: "2026-10-20"
related-code:
  - scripts/knowledge/build_onenote_jump_index.py
  - knowledge/registry/onenote-jump-index.jsonl
  - knowledge/registry/card-onenote-jumps.jsonl
  - knowledge/source-snapshots/onenote/HIERARCHY.json
---

# OneNote ジャンプ（EleKnowledge で回答に届く順）

アプリ RAG は現状 **PDF KB のみ**。カード ingest は未実装。いまの正本はテーマカード + この索引。

生成: `python3 scripts/knowledge/build_onenote_jump_index.py`

階層は Vault パス推定（`HIERARCHY.json`）。notebook / section / 页順は未確定。索引頁の**他テーマタイトルはカードに写さない**。

## 開き方

1. 症状・機種で **テーマカード**を開く（[cards/INDEX.md](../cards/INDEX.md)）。回答の第一候補はカード **§4**。
2. frontmatter の `onenote_id` を `card-onenote-jumps.jsonl` で引く。
3. `answer_mode` に従う。

| mode | 何を開くか | 回答になるもの |
| --- | --- | --- |
| `read_this_page` | `cited_snapshot_file` | その頁が **content / cross_topic**。`child_content_pages` があれば続けて開く |
| `navigate_to_child_content` | `answer_pages` の子 content | 引用頁は目次。本文は子頁 |
| `use_citing_cards` | `same_page_cards` とカード §6 | 子 content が無い索引。同 `onenote_id` のテーマカードが回答 |
| `navigation_only` | スナップショットは確認用 | キュレーション済み回答が無い。タイトルから手順を作らない |

4. 手順の断定は PDF（`kb_verify_status: content_reviewed` のあと）。`pending` / `catalog_ambiguous` の間はカードと OneNote 本文頁まで。

## 2026-10-20 生成値

| 指標 | 値 |
| --- | ---: |
| 階層页 | 1039 |
| `read_this_page` | 836 |
| `navigate_to_child_content` | 87 |
| `use_citing_cards` | 13 |
| `navigation_only` | 103 |
| OneNote を frontmatter に持つカード | 66 |
| カードから引用されている頁 | 52 |

カード 657 枚のうち OneNote 引用は 66。残りは Lists 要約が回答で、OneNote ジャンプは無い。

## 例

| カード | 引用 | mode | 回答の開き方 |
| --- | --- | --- | --- |
| 392 本スロー | `:156` hybrid | `use_citing_cards` | §4 + §6（同頁カード）。索引本文は転記しない |
| 415 ELSGW | `:106` content | `read_this_page` | `onenote-15fdf4b73ce899ff2c9eee95.md` のあと子 `:107` `:108` |
| 調整ハブ `:99` | hybrid | `navigate_to_child_content` | 子 content 9 頁（ID とスナップショット名のみ） |

## アプリに載せるとき

[card-kb-two-tier-retrieval.md](../../docs/features/development/card-kb-two-tier-retrieval.md) の順: カード KB → この jump → PDF KB。`navigation_only` と index 頁を引用チャンクにしない。
