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
- **カテゴリ未指定時**: `category` の**許可リスト**（実カテゴリ全10種 = `CATEGORY_MAP` の値 = `ALLOWED_CATEGORY_VALUES`）を**常時適用**する。ユーザー視点では従来どおり「未指定＝全検索」だが、web-crawler（GenU ドキュメント）・quick-start（引用 presign 不能バケット）データソース由来のノイズ文書と `TEST` 文書は category が許可リスト外のため遮断される。カテゴリ指定時も許可リスト外の値は通らない。根拠: [verification-2026-08-26-kb-vqv-metadata.md](../verification-2026-08-26-kb-vqv-metadata.md)（PR #55）。
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
| `site_agent` | 現場代理人業務マニュアル | 現場代理人業務マニュアル |
| `quality_mgmt` | 品質管理業務マニュアル | 品質管理業務マニュアル |
| `w_doc` | W資料 | W資料 |

- `site_agent`（30件）/ `quality_mgmt`（7件）は 2026-08-26 実測で実在を確認し、チャット UI に掲載（`UI_CATEGORY_KEYS`）。旧記載「カタログ 0 件のため非掲載」は誤りだった。`site_agent` はうち2件（GM-01-03-A / GM-01-29-A）がテキスト層なしスキャン PDF で KB 未索引のため検索可能実数は **28件**（差し替えは issue #53 で所有側へ依頼済み）。
- `w_doc`（5件）は全件が取扱機種スコープ対象外のため、スコープフィルタ併用時にチップ選択で 0 件になる既知問題あり（業務判断待ち。verification-2026-08-26 §5.1）。
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
- カテゴリ未指定時は内部で本命（C/TI/据付基準）を先に retrieve し、弱ければ全資料（実カテゴリ10種の許可リスト内）へ拡大（`priorityExpanded`）。ユーザーが category を選んでいる場合はそれを尊重。
- 直前アシスタントが聞き返しのとき、追記ターンの検索クエリは**直前のユーザー質問と結合**する（保存・表示する `query` は利用者の今回入力のまま）。
- `priorityExpanded`: 本命→全資料へ拡大したとき `true`。診断用フィールド（チャット UI では未表示）。
- `mode`: API 上は `normal` \| `spec` を受け付ける。現行チャット UI は常に `normal`。`spec` は **非推奨**で、サーバ側で `normal` に正規化し、カテゴリ未指定時は本命（`spec`/`tech_info`/`std`）を強制する。
- `sourceUri` は `s3://` ではなく**プリサイン HTTPS URL**。
- `sourceDocuments[].category` / `modelType` は実 KB メタデータ由来、`hasImage` は当該チャンクに IMAGE が含まれるか。
