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
      "sourceUri": "s3://<bucket>/docs/.../C-18-....pdf",
      "relevance": 0.81,
      "snippet": "..."
    }
  ],
  "content": "（短い整理。clarify/not_found では定型文）",
  "sourceDocuments": [
    {
      "documentName": "配線マニュアルv2.pdf",
      "sourceUri": "s3://<bucket>/docs/.../配線マニュアルv2.pdf",
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
- カテゴリ未指定時は内部で本命（C/TI/据付基準）を先に retrieve し、弱ければ全資料へ拡大（`priorityExpanded`）。ユーザーが category を選んでいる場合はそれを尊重。
- 直前アシスタントが聞き返しのとき、追記ターンの検索クエリは**直前のユーザー質問と結合**する（保存・表示する `query` は利用者の今回入力のまま）。
- `priorityExpanded`: 本命→全資料へ拡大したとき `true`。診断用フィールド（チャット UI では未表示）。
- `mode`: API 上は `normal` \| `spec` を受け付ける。現行チャット UI は常に `normal`。`spec` は **非推奨**で、サーバ側で `normal` に正規化し、カテゴリ未指定時は本命（`spec`/`tech_info`/`std`）を強制する。
- `sourceUri` の形式は環境変数 `CITATION_URI_MODE`（SAM パラメータ `CitationUriMode`）で切り替える（PR #50 の段階移行スイッチ）。
  - `s3`（移行完了後）: **raw の `s3://` URI** を保存・返却する。認証なしで開ける URL を DynamoDB に残さないためで、実 URL はユーザーが開く瞬間にフロントの中継ページ `/doc` → `GET /rag/document` で都度発行する。
  - `presigned`（既定・移行互換）: 従来どおり**プリサイン HTTPS URL**（TTL は `PRESIGNED_URL_EXPIRES_IN`、既定 300 秒）。受付（`GET /rag/document` と `/doc`）だけを先に本番反映し、デプロイ済みフロントを壊さないためのモード。受付の実機確認とフロント反映の完了後に `s3` へ切り替える。
- **旧履歴リンクの扱い**: #50 以前に保存された署名付き URL（期限切れで AccessDenied になっていたもの）は、フロントの `documentHref()` が S3 の URL と判定できれば bucket/key を `s3://` に逆変換して `/doc` 経由の都度発行に乗せ替える（過去履歴の引用が復活し、DynamoDB に残る発行済み URL が流出しても認証必須の導線に置き換わる）。S3 と判定できない https URL のみ従来どおり素通し。
- `sourceDocuments[].category` / `modelType` は実 KB メタデータ由来、`hasImage` は当該チャンクに IMAGE が含まれるか。

## GET /rag/document

引用文書の解決エンドポイント（PR #50）。`s3://` URI を、実際に開ける短命の署名付き URL に都度変換する。

**Request:** `GET /rag/document?uri=s3%3A%2F%2F<bucket>%2Fdocs%2F...pdf`（要 Cognito 認証。フロントは中継ページ `/doc` から呼ぶ）

**Response:**
```json
{ "url": "https://<bucket>.s3.<region>.amazonaws.com/...?X-Amz-Signature=...", "expiresIn": 300 }
```

- 認証: API Gateway の Cognito Authorizer + ハンドラ内のクレーム確認。未認証は `401`（フロントの `/doc` が `next` 付きでログイン画面へ誘導し、ログイン後に復帰する。戻り先は `safeNextPath()` でオープンリダイレクト検査）。
- 許可対象は **KB データソースバケットの prefix 配下と DocumentsBucket のみ**（`is_allowed_document_uri()`）。許可外・不正な URI は区別せず `400`（バケット構成を外部に教えないため）。presign 失敗は `502`（内部例外文は返さない）。
- 応答には `Cache-Control: no-store` を付与し、署名付き URL をキャッシュに残さない。
