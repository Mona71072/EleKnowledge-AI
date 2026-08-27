---
status: production
phase: 2
last-verified: 2026-08-26
related-code: lambda/rag/, frontend/src/app/chat/
---

# RAG処理API

> spec.md §7.2 から切り出し。Phase 2 の RAG クエリエンドポイントを記載する。

**Base URL:** Phase 2 `RagApiUrl` output, e.g. `https://{api-id}.execute-api.{region}.amazonaws.com/{env}`

## POST /rag/query
RAGクエリ実行

**Request:**
```json
{
  "sessionId": "session_xxxxx",
  "userId": "user_xxxxx",
  "query": "火災管制運転の動作は？",
  "mode": "normal",
  "filters": { "category": "spec", "modelType": "AXIEZ" }
}
```

- `mode`: `normal`（標準 RAG）| `spec`（仕様確認モード）。実装 [app.py](../../lambda/rag/rag-function/app.py) 参照。
- `filters.category`: フロント側の**安定キー**（`drawing` / `spec` / `tech_info` / `incident` / `qsheet` / `std` / `note` 等）。サーバー側 `CATEGORY_MAP` が実 KB の `category` メタデータ値へ変換する。安定キー・KB実値・UI表示ラベルの対応は下表参照。
- **カテゴリ未指定時**: カテゴリフィルタなし（**全資料対象**）。フロントの初期状態も未選択＝全検索。チップで選んだときだけ絞り込む。
- `filters.modelType`: `model_type`（多値）に対する**部分一致**（`AXIEZ` は `AXIEZ-LINKs` にも一致する）。機種を指定した場合でも、全機種共通文書は常に検索対象に含める（**選択機種 OR `*` OR `general` OR 空文字**）。カタログ上の `model_type` 空欄は全機種共通を意味する。空文字フィルタの本番確認は [verify-checklist-2026-07-29-kb-filter.md](../verify-checklist-2026-07-29-kb-filter.md)。
- `mode: spec` のとき `category` はサーバー側 `SPEC_CATEGORIES`（`C資料` / `テクニカルインフォメーション` / `据付基準`）で上書きされる。
- **検索方式**: Knowledge Base の `overrideSearchType` は環境変数 `RAG_SEARCH_TYPE` で制御する（既定 `HYBRID` / `SEMANTIC` に切替可、不正値は `HYBRID` にフォールバック）。HYBRID はベクトル類似に加えキーワード/全文一致を併用し、型式コード・エラーコードのような完全一致寄りの語の取りこぼしを減らす。

### `filters.category` 対応表

| 安定キー (API) | KB 実 `category` 値 | UI 表示ラベル |
|---|---|---|
| `drawing` | 据付場用図 | 据付場用図 |
| `spec` | C資料 | C資料 |
| `tech_info` | テクニカルインフォメーション | TI |
| `incident` | 災害事例集 | 災害事例集 |
| `qsheet` | Qシート | Qシート |
| `std` | 据付基準 | 据付基準 |
| `note` | 据付ノート | 据付ノート |
| `w_doc` | W資料 | W資料 |

`site_agent` / `quality_mgmt` は API `CATEGORY_MAP` に残すが、現行 KB カタログ 0 件のため **チャット UI には出さない**（`UI_CATEGORY_KEYS`）。

**Response:**
```json
{
  "sessionId": "session_xxxxx",
  "sessionTitle": "火災管制運転について",
  "userMessageId": "msg_user_xxxxx",
  "aiMessageId": "msg_ai_xxxxx",
  "responseType": "pages",
  "clarifyQuestions": [],
  "pageCandidates": [
    {
      "documentName": "C-18-....pdf",
      "category": "C資料",
      "modelType": "AXIEZ",
      "pageNumber": 42,
      "sourceUri": "https://...",
      "relevance": 0.81,
      "snippet": "..."
    }
  ],
  "content": "（短い整理。clarify/not_found では定型文）",
  "sourceDocuments": [
    {
      "documentName": "配線マニュアルv2.pdf",
      "sourceUri": "https://<bucket>.s3.<region>.amazonaws.com/...?X-Amz-Signature=...",
      "category": "C資料",
      "modelType": "AXIEZ",
      "pageNumber": 42,
      "hasImage": true,
      "relevance": 0.95
    }
  ],
  "priorityExpanded": false
}
```

- `responseType`: `clarify`（検索せず聞き返し）/ `pages`（候補あり）/ `not_found`（弱い検索で作文停止）。実装理由は [impl-log-2026-07-29-clarify-and-page.md](../impl-log-2026-07-29-clarify-and-page.md)。
- `pageCandidates`: UI 上部用。`pageNumber` は KB メタにあるときだけ付与（無ければキー省略＝ページ不明）。`not_found` 時は最大2件の参考候補に `lowConfidence: true` を付ける（作文はしない）。
- `clarifyQuestions`: `clarify` 時の追加質問リスト。
- カテゴリ未指定時の**本命優先 2 段階 retrieve は 2026-08-26 に一時停止**（少数カテゴリが全検索でヒットしない副作用のため。mona 了承済み）。現在は未指定時も常に単一の retrieve（対象は実カテゴリ10種の許可リスト内）。後継方式の検討は [issue #61](https://github.com/yukiworkspace/EleKnowledge-AI/issues/61)。ユーザーが category を選んでいる場合はそれを尊重（従来どおり）。
- 直前アシスタントが聞き返しのとき、追記ターンの検索クエリは**直前のユーザー質問と結合**する（保存・表示する `query` は利用者の今回入力のまま）。
- `priorityExpanded`: 本命→全資料へ拡大したとき `true` だった診断用フィールド（チャット UI では未表示）。優先 retrieve 停止中は**常に `false`**（API 互換のためフィールドは残置）。
- `mode`: API 上は `normal` \| `spec` を受け付ける。現行チャット UI は常に `normal`。`spec` は **非推奨**で、サーバ側で `normal` に正規化し、カテゴリ未指定時は本命（`spec`/`tech_info`/`std`）を強制する。
- `sourceUri` は `s3://` ではなく**プリサイン HTTPS URL**。
- `sourceDocuments[].category` / `modelType` は実 KB メタデータ由来、`hasImage` は当該チャンクに IMAGE が含まれるか。
