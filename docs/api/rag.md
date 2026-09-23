---
status: production
phase: 2
last-verified: 2026-09-09
related-code: lambda/rag/, frontend/src/app/chat/
---

# RAG処理API

> spec.md §7.2 から切り出し。Phase 2 の RAG クエリエンドポイントを記載する。

**Base URL:** Phase 2 `RagApiUrl` output, e.g. `https://{api-id}.execute-api.{region}.amazonaws.com/{env}`

## POST /rag/query

> 最終検証: 2026-09-22 — #84 実装（応答はフォールバック、sessionTitle は非同期が初めて書く）

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
- **カテゴリ未指定時**: `category` の**許可リスト**（実カテゴリ全10種 = `CATEGORY_MAP` の値 = `ALLOWED_CATEGORY_VALUES`）を**常時適用**する。ユーザー視点では従来どおり「未指定＝全検索」だが、web-crawler（GenU ドキュメント）・quick-start（引用 presign 不能バケット）データソース由来のノイズ文書と `TEST` 文書は category が許可リスト外のため遮断される。カテゴリ指定時も許可リスト外の値は通らない。根拠: [verification-2026-08-26-kb-vqv-metadata.md](../verification-2026-08-26-kb-vqv-metadata.md)（PR #55）。
- `filters.modelType`: UI 機種絞り込み項目（6項目）。サーバー側 `UI_MODEL_FILTERS` が対象機種へ展開し（例 `AXIEZ` → `AXIEZ` / `AXIEZ(KE-WF・KE-HF)` / `駅舎エレ`）、`model_type` に対する **`listContains`（リスト要素の完全一致）** の `orAll` で検索前に絞り込む。KB の `model_type` は list 型 / string 型が混在するが、string 型はスカラー＝単要素リスト扱いで `listContains` に一致する（2026-08-26 実機確認）。旧実装の `stringContains`（部分一致。`AXIEZ` が `AXIEZ-LINKs` にも一致していた）は廃止。機種を指定した場合でも、全機種共通文書（`model_type` が `*` / `general`）は常に検索対象に含める（**展開機種 OR `*` OR `general`**）。空文字・空配列・キー欠落は実データ 0 件のため空文字句は持たない。加えて取得後に要素完全一致の post-filter と取扱機種スコープ（`HANDLED_MODEL_TYPES`）を安全弁として適用する。根拠: [verification-2026-08-26-kb-vqv-metadata.md](../verification-2026-08-26-kb-vqv-metadata.md) §4/§5.4（PR #55）、[rag-model-filter-mapping-2026-08-26.md](../rag-model-filter-mapping-2026-08-26.md) §1/§4（PR #54）。
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
| `site_agent` | 現場代理人業務マニュアル | 現場代理人業務マニュアル |
| `quality_mgmt` | 品質管理業務マニュアル | 品質管理業務マニュアル |
| `w_doc` | W資料 | （UI 非掲載・業務判断待ち） |

- `site_agent`（30件）/ `quality_mgmt`（7件）は 2026-08-26 実測で実在を確認し、チャット UI に掲載（`UI_CATEGORY_KEYS`）。旧記載「カタログ 0 件のため非掲載」は誤りだった。`site_agent` はうち2件（GM-01-03-A / GM-01-29-A）がテキスト層なしスキャン PDF で KB 未索引のため検索可能実数は **28件**（差し替えは issue #53 で所有側へ依頼済み）。
- `w_doc`（5件）は全件が取扱機種スコープ対象外のため、スコープフィルタ併用時にチップ選択で 0 件になることを実機確認（2026-08-26）。業務判断（W資料機種の HANDLED 追加 or スコープ例外化）が出るまで **UI 非掲載**（`UI_CATEGORY_KEYS` から除外）。API 上は引き続き有効なキーで、`CATEGORY_MAP` / 許可リストには残る（verification-2026-08-26 §5.1）。
- KB 実 `category` にはこのほか `TEST`（ゴミ・1件）が存在するが、許可リスト外のため常時遮断される。

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
- `sessionTitle`: **セッション最初のやりとりのみ**付く履歴一覧用の見出し。応答 JSON では質問文を切り詰めたフォールバックを返す。DynamoDB の `sessionTitle` は初回の put では書かない。
  - 見出し生成は回答返却後の非同期 Lambda タスクで行う。Bedrock の接続・本文読取は、通常回答・聞き返し・該当なしの応答時間に入れない。生成後は、同一 `userId` で `sessionTitle` がまだ無い最初の user メッセージだけを更新する。
  - 初回 put にフォールバックを書いておくと、`attribute_not_exists(sessionTitle)` が外れ、LLM 見出しが保存されない。一覧は質問の先頭 50 文字のままになる。
  - モデルは `SESSION_TITLE_MODEL_ID`（未設定時は `BEDROCK_MODEL_ID`）。Sonnet 5 系では `temperature` を送らず `thinking: {type: disabled}` を指定し、本文生成と同じ互換形式を使う。
  - `SESSION_TITLE_LLM=false` や非同期起動の失敗のあいだ、一覧は優先順 2（最初のユーザー質問。フォールバックと同じ切り詰め）になる。Bedrock 例外・空応答のときは、非同期タスクがフォールバック文字列を `sessionTitle` として書く。見出し生成の失敗で回答は落とさない。
  - **SECURITY:** 質問文は `<question>` タグで囲み、システムプロンプトで資料扱いを明示する。タスクは同一LambdaのIAM権限でのみ起動される。
  - 現行チャット UI はこのフィールドを直接使わず、一覧 API を再取得して表示する。

- カテゴリ未指定時の**本命優先 2 段階 retrieve は 2026-08-26 に一時停止**（少数カテゴリが全検索でヒットしない副作用のため。mona 了承済み）。現在は未指定時も常に単一の retrieve（対象は実カテゴリ10種の許可リスト内）。後継方式の検討は [issue #61](https://github.com/yukiworkspace/EleKnowledge-AI/issues/61)。ユーザーが category を選んでいる場合はそれを尊重（従来どおり）。
- 直前アシスタントが聞き返しのとき、追記ターンの検索クエリは**直前のユーザー質問と結合**する（保存・表示する `query` は利用者の今回入力のまま）。
- `priorityExpanded`: 本命→全資料へ拡大したとき `true` だった診断用フィールド（チャット UI では未表示）。優先 retrieve 停止中は**常に `false`**（API 互換のためフィールドは残置）。
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
GET /rag/document?uri=s3%3A%2F%2F<bucket>%2Fdocs%2F....pdf&s=<sessionId>&m=<messageId>
Authorization: Bearer <IdToken>
```

> 最終検証: 2026-09-11 — `s` / `m` と 500 応答の形は実装 PR #111 のコードと突合（実環境は未デプロイ）

- `s`（sessionId）と `m`（messageId）は任意。**どの回答の引用から開いたか**を記録するためで、フロントの `/doc?uri=…&s=&m=` が引き継ぐ。両方あり、かつ `s` が呼び出し元の所有セッションなら、該当の assistant 行に `documentOpens` を加算し `lastOpenedAt` を記録する（到達ファネル「資料を開いた」。設計 [design-2026-09-10-dashboard-v2.md](../design-2026-09-10-dashboard-v2.md) §4.3 I3）。無くても文書は開ける。CloudWatch には `document_open` の構造化行（文書名のみ）が出る

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

---

## 500 応答の形と構造化ログ（2026-09-11）

> 最終検証: 2026-09-11 — 実装 PR #111 のコードと突合（実環境は未デプロイ）

`POST /rag/query` の 500 は AWS のエラーメッセージを返さず、一般化した本文と API Gateway のリクエスト ID だけを返す。

```json
{ "error": "InternalServerError", "message": "処理に失敗しました。時間をおいて再度お試しください。", "requestId": "<apiRequestId>" }
```

CloudWatch Logs には 1 リクエスト 1 行の構造化行が出る（本文・質問文は含まない）。

| event | 主な項目 | 用途 |
|---|---|---|
| `rag_request` | `apiRequestId`, `statusCode`, `sessionId`, `messageId`, `responseType`, `pageCandidates`, `sourceDocuments`, `latencyMs` | アクセスログの `requestId` と結合（保存クエリ `request-by-id`） |
| `rag_error` | `apiRequestId`, `stage`（retrieve / generate / save / history）, `errorCode`, `errorMessage`, `latencyMs` | 500 の段階と原因 |
| `document_open` | `apiRequestId`, `sessionId`, `messageId`, `documentName` | 資料到達の追跡 |
| `reformulation` | `sessionId`, `messageId` | 直前の回答に言い換えの印（`reformulatedAt`）を付けた |
