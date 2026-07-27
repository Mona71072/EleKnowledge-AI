---
status: production
phase: 2
last-verified: 2026-07-27
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
- `filters.category`: フロント側の**安定キー**（`drawing` / `spec` / `tech_info` / `incident` / `qsheet` / `std` / `note`）。サーバー側 `CATEGORY_MAP` が実 KB の `category` メタデータ値へ変換する。安定キー・KB実値・UI表示ラベルの対応は下表参照。
- `filters.modelType`: `model_type`（多値）に対する**部分一致**（`AXIEZ` は `AXIEZ-LINKs` にも一致する）。機種を指定した場合でも、`model_type` が `*` / `general`（全機種共通）の文書は常に検索対象に含める（**選択機種 OR `*` OR `general`**）。これにより据付基準など全機種向け文書が機種選択時に除外されない。
- `mode: spec` のとき `category` はサーバー側 `SPEC_CATEGORIES`（`C資料` / `テクニカルインフォメーション`）で上書きされる。
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

**Response:**
```json
{
  "sessionId": "session_xxxxx",
  "sessionTitle": "火災管制運転について",
  "userMessageId": "msg_user_xxxxx",
  "aiMessageId": "msg_ai_xxxxx",
  "content": "火災管制運転の動作は...",
  "sourceDocuments": [
    {
      "documentName": "配線マニュアルv2.pdf",
      "sourceUri": "https://<bucket>.s3.<region>.amazonaws.com/...?X-Amz-Signature=...",
      "category": "spec",
      "modelType": "AXIEZ",
      "hasImage": true,
      "relevance": 0.95
    }
  ]
}
```

- `sourceUri` は `s3://` ではなく**プリサイン HTTPS URL**（`presign_source_uri`、既定 3600 秒）。
- `sourceDocuments[].category` / `modelType` は実 KB メタデータ（`category` / `model_type`）由来、`hasImage` は当該チャンクに IMAGE が含まれるか。
