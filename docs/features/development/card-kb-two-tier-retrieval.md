---
status: development
last-verified: 2026-10-19
related-code:
  - lambda/rag/rag-function/app.py
  - knowledge/cards/
---

# 承認カード KB と PDF KB の二段検索（設計ドラフト）

> 最終検証: 2026-10-19 — コード読取（RAG Lambda）+ knowledge パイプライン未実装の確認

## 背景

- 本番 RAG は **S3 上の PDF** を Bedrock Knowledge Base で検索する（`lambda/rag/rag-function/app.py`）。
- `knowledge/cards/*.md` の **ingest・承認・公開パイプラインは未実装**。カードはすべて `status: draft` が既定。
- OneNote **索引頁**をカード本文にそのまま載せると、将来カードを KB 化した際に HYBRID 検索で**別テーマ語の誤ヒット**が起きうる。

## 推奨構成

```text
自然文クエリ
  →（1）承認済みカード専用 KB — 切り分け・適用条件・手順要約
  → カードの source_refs から正式層へ誘導
  →（2）既存 PDF KB — 図番・据付基準・TI/C 等
  → 引用・資料候補表示
```

| 層 | 中身 | 公開条件 |
| --- | --- | --- |
| カード KB | 固定 9 見出し、`approved` + allowlist | CI: スキーマ・`page_role`・出典・条件差 |
| PDF KB | 現行どおり S3 `docs/documents/` | 既存メタデータ・カテゴリフィルタは**母集団絞り込みのみ** |

## 公開対象外

- `status: draft`
- OneNote `page_role: index` / `empty_or_attachment_only` を**内容根拠**にした要約（navigation リンクのみ可）
- URL omitted のみで本文根拠が取れない頁

## フォールバック

カード KB で該当テーマに到達できない場合は **現行 PDF HYBRID 検索**へ。カテゴリ・機種フィルタは retrieve 前の filter のみ（RAG 本体は常に自然文 + チャンク本文検索）。

## アプリ表示（案）

- カード題名・適用条件・正式資料リンク（`kb_document` / Lists § / OneNote navigation）
- 索引頁を回答引用として見せない

## 評価（3 点）

1. 症状の自然文から **該当カード**へ到達できるか
2. 索引頁の**別テーマ語**で誤カードが上位にならないか
3. カードから **正式 PDF**へ到達できるか

## 実装メモ（未着手）

- カード → S3/Bedrock 同期ジョブ、allowlist、`approved` 遷移 API
- Lambda: カード retrieve → PDF retrieve の順序制御
- CI: `build_registry.py` + `page_role` + 固定見出し検証
