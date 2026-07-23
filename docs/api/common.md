---
status: production
last-verified: 2026-04-24
related-code: lambda/, infrastructure/
---

# API 共通仕様（エラーハンドリング・スロットリング）

> spec.md §7.4-7.5 から切り出し。全 API 共通のエラーレスポンス形式と API Gateway スロットリング設定をまとめる。

## エラーハンドリング戦略

### バックエンドエラー分類

**1. システムエラー (500系)**
- Lambda実行エラー → CloudWatch Logs記録
- Bedrock API障害 → 3回リトライ（指数バックオフ: 1s, 2s, 4s）
- DynamoDB接続エラー → SDK自動リトライ

**2. ビジネスエラー (400系)**
- 入力検証エラー → 400 Bad Request
- 認証エラー → 401 Unauthorized
- 認可エラー → 403 Forbidden
- リソース上限 → 429 Too Many Requests

### 統一エラーレスポンス形式

```typescript
interface ErrorResponse {
  error: string;           // エラー種別
  message: string;         // ユーザー向けメッセージ
  code: string;            // エラーコード
  timestamp: string;       // ISO 8601
  requestId?: string;      // トレーシング用
}
```

**例:**
```json
{
  "error": "ValidationError",
  "message": "入力内容を確認してください",
  "code": "INVALID_INPUT",
  "timestamp": "2025-10-02T21:30:00Z",
  "requestId": "req-xxxxx"
}
```

### フロントエンドエラー表示

```typescript
interface ErrorDisplay {
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  recoverable: boolean;
  action?: {
    label: string;
    handler: () => void;
  };
}
```

**表示例:**
- "⚠️ 接続エラー - ネットワークを確認してください [再試行]"
- "❌ セッション期限切れ - 再度ログインしてください [ログイン画面へ]"

## API Gateway スロットリング設定

**想定負荷:**
- 同時接続: 20人
- 登録ユーザー: 100人
- 平均クエリ: 10件/人/日 = 1,000件/日 = 約40件/時

**スロットリング設定:**

| API | バースト | 定常レート | 用途 |
|-----|---------|-----------|------|
| 認証API | 50 req/sec | 10 req/sec | ログイン・認証 |
| RAG処理API | 20 req/sec | 5 req/sec | RAGクエリ |
| チャット管理API | 50 req/sec | 10 req/sec | 履歴取得 |

**WAF レート制限:**
- IPベース: 500 req/5min（社内IP全体）
- ユーザーベース: 100 req/5min（1ユーザー）
