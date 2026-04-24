# チャット管理API

> spec.md §7.3 から切り出し。Phase 2 のチャットセッション管理エンドポイントを記載する。

**Base URL:** `https://zzzzz.execute-api.us-east-1.amazonaws.com/prod`

## GET /chat/sessions
セッション一覧取得

**Response:**
```json
{
  "sessions": [
    {
      "sessionId": "session_xxxxx",
      "title": "配線に関する質問",
      "createdAt": "2025-10-01T10:00:00Z",
      "lastMessageTime": "2025-10-02T15:30:00Z",
      "messageCount": 12,
      "daysUntilDeletion": 28
    }
  ]
}
```
