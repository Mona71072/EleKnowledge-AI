---
status: production
phase: 2
last-verified: 2026-07-17
related-code: lambda/rag/
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
- `filters.category`: フロント側の**安定キー**（`drawing` / `spec` / `tech_info` / `incident` / `qsheet` / `std` / `note`）。サーバー側 `CATEGORY_MAP` が実 KB の `category` メタデータ値へ変換する。
- `filters.modelType`: **部分一致**（`AXIEZ` は `AXIEZ-LINKs` にも一致する）。
- `mode: spec` のとき `category` はサーバー側 `SPEC_CATEGORIES`（`C資料` / `テクニカルインフォメーション`）で上書きされる。

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
