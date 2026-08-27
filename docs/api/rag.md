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
      "sourceUri": "s3://<bucket>/docs/C-18-....pdf",
      "relevance": 0.81,
      "snippet": "..."
    }
  ],
  "content": "（短い整理。clarify/not_found では定型文）",
  "sourceDocuments": [
    {
      "documentName": "配線マニュアルv2.pdf",
      "sourceUri": "s3://<bucket>/docs/配線マニュアルv2.pdf",
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
- `sourceUri` の形式は環境変数 `CITATION_URI_MODE`（SAM パラメータ `CitationUriMode`）で切り替える（デプロイ順を壊さないための段階移行スイッチ）。
  - `s3`（移行完了後の姿。上の例）: **`s3://` URI**。プリサイン HTTPS URL は応答にも DynamoDB にも含めない。フロントは `documentHref()` で中継ページ `/doc?uri=...` へのリンクに変換し、クリック時に `GET /rag/document` で実 URL を都度発行する。
  - `presigned`（既定・移行互換）: 従来どおり**プリサイン HTTPS URL**（TTL は `PresignedUrlExpiresIn`、既定 300 秒）。受付（`GET /rag/document` と `/doc`）だけを先に本番反映しても、デプロイ済みフロントを壊さないためのモード。受付の実機確認とフロント反映（Amplify）の完了後に `s3` へ切り替える。
- 旧データ（プリサイン URL が保存済みの履歴。期限切れで AccessDenied になっていたもの）もフロント側で `s3://` に逆変換して同じ導線に乗せる（過去履歴の引用が復活し、DynamoDB に残る発行済み URL が流出しても認証必須の導線に置き換わる）。S3 と判定できない https URL のみ素通し。
- `sourceDocuments[].category` / `modelType` は実 KB メタデータ由来、`hasImage` は当該チャンクに IMAGE が含まれるか。

---

## GET /rag/document

引用文書の実体を開くための**短命プリサイン URL を都度発行する**エンドポイント。チャット応答の `sourceUri`（`s3://` URI）を、開く瞬間にだけ有効な HTTPS URL に解決する。呼び出し元は中継ページ `/doc`（`frontend/src/lib/documents.ts` の `resolveDocumentUrl`）。

**認証:** Cognito Authorizer 必須（未ログインは API Gateway / ハンドラで 401）。これにより引用リンクを共有されても、開けるのは登録ユーザーのみ。未ログイン時はフロントの `/doc` が `next` 付きでログイン画面へ誘導し、ログイン後に復帰する（戻り先は `safeNextPath()` で正規化・origin 検証するオープンリダイレクト対策済み。`frontend/src/lib/safe-next-path.mjs`）。

**Request:**

```text
GET /rag/document?uri=s3%3A%2F%2F<bucket>%2Fdocs%2F....pdf
Authorization: Bearer <IdToken>
```

**Response (200):**

```json
{
  "url": "https://<bucket>.s3.<region>.amazonaws.com/docs/....pdf?X-Amz-Signature=...",
  "expiresIn": 300
}
```

- `Cache-Control: no-store` を付与（プリサイン URL をキャッシュに残さない）
- TTL は `PresignedUrlExpiresIn`（テンプレート既定 **300 秒**）。経緯は [decisions-2026-08-26-presigned-url-ttl.md](../decisions-2026-08-26-presigned-url-ttl.md)

**エラー:**

| status | error | 条件 |
|---|---|---|
| 400 | `InvalidDocumentUri` | `s3://` でない / bucket・key 欠落 / キーに `..` を含む / 許可外バケット（KB データソースの prefix 配下と documents バケット以外）。**存在するバケット名を外部に教えないため、これらは区別せず 400 に丸める** |
| 401 | `Unauthorized` | 未認証 |
| 502 | `PresignFailed` | S3 プリサイン発行の失敗 |

**期限切れプリサイン URL の想定挙動（設計）:**

- 正規導線では期限切れに遭遇しない設計（保存・共有されるのは `/doc` リンクのみ。URL は開く瞬間に発行し、その場で使い捨てる）
- それでも発行済み URL に期限後アクセスした場合（タブのリロード・ブラウザ履歴・コピーされた URL）、リクエストはブラウザ → S3 に直行しアプリは経路上に存在しないため、**S3 が素の 403 XML（`AccessDenied` / `Request has expired`）を返すのが想定動作**。アプリ側でのエラーページ表示や再発行リダイレクトは構造的に不可能
- **復旧導線はチャットの引用リンクを再クリック**（都度発行で新しい URL が出る）
- 既知エッジ: ブラウザ PDF ビューアはレンジリクエストで逐次読み込むため、大きい PDF を 5 分超閲覧すると未読ページの取得が失敗しうる（表示済みページは影響なし。復旧は同上）
