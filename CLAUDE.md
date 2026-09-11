# Claude Code instructions

@AGENTS.md

共通ルールの正本は `AGENTS.md`（上で読み込み済み）。本ファイルには要点と「どこを見に行くか」だけを置き、詳細は必要になったときに参照先を読むこと。

## 最重要（要約 — 正本は AGENTS.md）

- `status: production` のドキュメントは**ユーザーの事前確認なしに編集しない**
- PR は base `develop`・日本語・細かめ。`main` へは develop 経由のみ
- ドキュメント更新時は検証日を更新。**部分検証なら frontmatter の `last-verified` は進めず、セクション見出し直下に `> 最終検証: YYYY-MM-DD — <検証方法・範囲>` を置く**。ファイル移動は `git mv`

## 情報の場所

| 知りたいこと | 参照先 |
|---|---|
| 仕様の索引 | [spec.md](spec.md) → トピック別に `docs/` へ分割。各ファイルの frontmatter（`status` / `last-verified` / `related-code`）で扱いを判断 |
| 稼働中／開発中の機能仕様 | `docs/features/production/` ／ `docs/features/development/` |
| アーキテクチャ・API・データモデル | `docs/architecture/` ／ `docs/api/` ／ `docs/data-model.md` |
| デプロイ | `docs/deployment.md` |
| RAG 機種絞り込み（取扱機種スコープ・KB model_type 対応） | `docs/rag-model-filter-mapping.md`（自動生成。正本は `lambda/rag/rag-function/app.py`） |
| KB メタデータ実測カタログ | `docs/kb-metadata-catalog-2026-07-29.md` |
| タスク履歴・過去の経緯 | `docs/task-history.md` |
