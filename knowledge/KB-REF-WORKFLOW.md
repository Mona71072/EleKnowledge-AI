# KB 資料確認 → カードへ要約する手順

Lists / OneNote 突合の **後**、共有 KB（Bedrock データソース）上の PDF を確認し、カードの統合回答を **根拠付きで更新** するための流れ。

## 正本

| 種類 | 場所 |
| --- | --- |
| **KB 資料一覧（正本）** | **`docs/kb-metadata-catalog-2026-08-26.md`** — S3 実測 3,745 件（C資料 729 / TI 308 / 据付基準 121 …）。突合は **必ずこの一覧の filename 列** を見る |
| 機械可読索引 | `knowledge/registry/kb-document-index.jsonl`（生成物） |
| 資料番号 → ファイル突合 | `knowledge/registry/kb-ref-resolution.jsonl`（生成物） |
| Wave 突合表 | `knowledge/validation/kb-ref-status-wave1-2.md` |

C 資料・TI・据付基準（SUE-*）など **category** はカタログの章見出し（例: `C資料`、`テクニカルインフォメーション`、`据付基準`）に対応する。

## コマンド（索引更新）

```bash
python3 scripts/knowledge/build_kb_document_index.py
python3 scripts/knowledge/resolve_kb_refs.py
```

カードの `source_refs` に `document_number` を足したあと、上記を再実行する。

## `kb_verify_status`（Must）

| 値 | 意味 |
| --- | --- |
| `pending` | Lists 等から資料名だけ拾った |
| `catalog_matched` | カタログ上の PDF 文件名が特定できた（**本文未読**） |
| `catalog_ambiguous` | 複数候補。人手で `kb_filename` を1つ選ぶ |
| `not_in_catalog` | 2026-08-26 カタログに無い（別表記・未索引・KB 外の可能性） |
| `content_reviewed` | KB/PDF を開き、該当節を読んだ。**要約をカードに反映済み** |

**正式値の断定**は `content_reviewed` 以降のみ。それ以前は Lists/OneNote 由来の記述に留める。

## カードへの書き方

1. `source_refs` の `kb_document` に次を載せる（[CONTRACT.md](./CONTRACT.md) 参照）:
   - `document_number`（業務番号・図番）
   - `kb_filename` / `kb_category`（突合後）
   - `kb_verify_status`
   - `locator`（確認後: 節・ページ）
   - `summary_from_kb`（確認後: 1〜3 文。カード §3 へ転記可）
2. 本文に **「KB確認に基づく追記」** セクションを置き、`content_reviewed` 後に統合回答を更新する。
3. C 資料（`C-*`）は category が `C資料` のファイルを優先。Lists の `C-6-R56.1` のように **カタログ未収載** の場合は `not_in_catalog` のまま止め、RAG 検索または S3 再取得で別名を探す（断定しない）。

## アプリ側（後続）

EleKnowledge の RAG チャット／資料ビューアで該当 PDF に到達したら、同じ `document_number` でカードと突合する。実装は Bedrock KB 連携 PR で行う（本ドキュメントは運用・データ契約のみ）。
