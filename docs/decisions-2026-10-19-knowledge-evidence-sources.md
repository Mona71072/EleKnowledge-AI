---
status: draft
last-verified: 2026-10-19
related-code:
  - knowledge/CONTRACT.md
  - knowledge/cards/_SOURCE-LEGEND.md
---

# 知識地図の「出典」と照合作業（2026-10-19）

## 決定

- **参照元（出典）**は次の **4 種類**（写し索引 `draft_record` は除く）。
  1. **Lists** — Microsoft Lists の `list_item_id`（**カード・索引・§8 では §番号 / `list_item_id` のみ書く**）
  2. **OneNote** — `onenote_id`
  3. **KB** — 共有 KB（Bedrock）上の PDF。`document_number` → カタログ `docs/kb-metadata-catalog-*.md` で `kb_filename` を解決 → 本文確認後 `content_reviewed`（手順: `knowledge/KB-REF-WORKFLOW.md`）
  4. **法令 RAG** — `law_id`（本家 `legal-rag-target-laws.md`）。手順: `knowledge/LAW-RAG-REF-WORKFLOW.md`
- **照合正本（執筆者が開くファイル）**は [CONTRACT.md](../knowledge/CONTRACT.md)「照合作業」の表に **1 か所だけ**書く。`首都工_…_初期スナップショット.md` や `onenote-*.md` の **フルパスを、テーマカード §8・法令索引・registry まとめの related-code に繰り返さない**（出典の正は `list_item_id` / `onenote_id` 等のフィールド）。
- `record_id`（`knowledge/drafts`）は **Vault 写し・照合用**。出典の代わりにしない。カード本文の「正式資料・元情報」では **Lists / OneNote / KB の表を先**に書き、`draft_record` は任意で別記。
- **`list_item_id` と `record_id` を混同しない。** 例: `417` は Lists 項目番号。`case-elv-vfglf-…-id417` は draft の安定 ID（末尾の `-id417` は照合ヒントであり、ユーザー向け出典表記にしない）。
- タイトル・見出しに `(ID417)` / `Lists ID417` を **入れない**。番号は YAML フィールドのみ。

## OneNote `onenote_id` の正本と略称（2026-10-19 追記）

- **正本（機械・監査・ingest）**は常に **フル `onenote_id`**（`{uuid}:{page}`）。載せる場所: カード `source_refs`、スナップショット frontmatter、`registry/onenote-id-index.json` / `card-source-links.jsonl`。**`:156` だけを `source_refs` に書かない。**
- **§8・人向け表記**はフル ID、`uuid…:page`、または **`4f038f2a…:1` 型の省略**可。クリック URL やスナップショットパスは §8 に必須としない（正本は frontmatter）。
- **§3 / §6 の本文**では、**同じノートブック UUID が文脈で分かるとき**（当該カードの `source_refs`、または直前に書いたフル ID）に **`:156` など page  suffix だけ**の略称を使ってよい。**AI・執筆者は略称を必ずフル ID に解釈**し、`onenote-page-catalog.jsonl` / `onenote-id-index.json` / 当該カードの `source_refs` で突合する。
- **`:page` は UUID 横断で一意ではない**（別ノートブックにも `:156` がありうる）。略称だけ渡されたときは **registry で uuid を確定**してから編集・リンク・監査する。文脈不明なら略称を増やさず **フル ID を書く**。
- 他カードへ「同索引」と書くときは、**そのカードが `source_refs` で持つ `onenote_id`**、または **Lists テーマカードへの Markdown リンク**を優先する（索引タイトル一覧の転記は [CONTRACT.md](../knowledge/CONTRACT.md) の `page_role: index` どおり禁止）。

## 作業手順（Must）

テーマカード・draft を新規／更新するとき:

1. **Lists** — 上記スナップショットで `## Lists item ID {n}` 節を開き、カードの統合回答と突合する。
2. **OneNote** — `knowledge/source-snapshots/onenote/` をタイトル・キーワードで検索し、該当ページの `onenote_id` を `source_refs` に載せる。該当なしは表で「—」。
3. **KB** — Lists / OneNote の資料番号を `document_number` に載せ、`build_kb_document_index.py` / `resolve_kb_refs.py` でカタログ突合。**PDF 本文を読む前に正式値を断定しない**（`kb_verify_status` が `content_reviewed` になるまで）。
4. C 資料（`C-*`）・TI・据付基準（`SUE-*`）も同じ。カタログ未収載は `not_in_catalog` で止め、RAG/再索引で別名探索（後続）。
5. 上記 1〜4 を満たすまで、出典を draft のみで完結させない。

## 確認者

- mona（会話合意）。itai レビューは knowledge 共同確認 PR で。
