# 根拠レコード保全（2026-10-19）

## 実施したこと

- 未コミットの **211件リネーム・189件タイトル短縮** を `git checkout HEAD -- knowledge/drafts` で戻した。`knowledge/drafts/` は curated snapshot としてファイル名・frontmatter を勝手に一括変更しない。
- リネーム時に付与していたトップレベル `list_item_id` は、作業ツリーから抽出し [registry/list-item-to-record.jsonl](./registry/list-item-to-record.jsonl) に退避（211行）。今後の Lists 連携は **registry + evidence_sources 内の明示ID** を正とする。
- Wave1 の統合本文は `knowledge/drafts/` の根拠レコード（ID付きファイル名）に残し、AI向け統合版は `knowledge/cards/` へ移した。

## カード候補へ残した改善（drafts ではない）

- 発生確認機種と適用可能範囲の分離（例: AXIEZ-LINKS で発生、全機種パターンは未確認）
- タイトルから `(IDnnn)` を外した表示（識別は `list_item_id` / `source_refs`）

## 触っていないもの

- コミット済み突き合わせ台帳の **primary 304件** の意味
- `publication_status: not_published` 一括（RAG非対象）
