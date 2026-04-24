---
status: production
phase: 2
last-verified: 2026-04-24
related-code: lambda/rag/
---

# RAG処理API

> spec.md §7.2 から切り出し。Phase 2 の RAG クエリエンドポイントを記載する。

**Base URL:** `https://yyyyy.execute-api.us-east-1.amazonaws.com/prod`

## POST /rag/query
RAGクエリ実行

**Request:**
```json
{
  "sessionId": "session_xxxxx",
  "query": "配線の接続方法は？",
  "filters": {
    "documentType": "manual",
    "product": "ProductA"
  }
}
```

**Response:**
```json
{
  "messageId": "msg_xxxxx",
  "content": "配線の接続方法は...",
  "citations": ["doc1.pdf", "doc2.pdf"],
  "sourceDocuments": [
    {
      "documentName": "配線マニュアルv2.pdf",
      "sourceUri": "s3://...",
      "relevance": 0.95
    }
  ],
  "timestamp": "2025-10-02T21:30:00Z"
}
```
