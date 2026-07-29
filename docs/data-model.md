---
status: production
last-verified: 2026-07-29
related-code: infrastructure/, lambda/rag/, lambda/chat/
---

# データモデル

> 出典: 旧 [spec.md](../spec.md) §6（PR #10 で本ファイルに切り出し）  
> **正本の補足:** API 契約は [`docs/api/rag.md`](./api/rag.md) / [`docs/api/chat.md`](./api/chat.md)。  
> 本ページの S3 パス例など古い記述がある場合は API／コードを優先する。

## DynamoDB テーブル設計

### users テーブル

```typescript
{
  userId: string;           // Partition Key (Cognito Sub)
  email: string;            // Email
  username: string;         // ユーザー名
  createdAt: string;        // 作成日時（ISO 8601）
  lastLoginAt: string;      // 最終ログイン
  role: 'admin' | 'user';   // ロール
}
```

### eleknowledge-chatlogs テーブル（ホットウィンドウ）

```typescript
{
  sessionId: string;        // Partition Key
  messageId: string;        // Sort Key (ULID)
  userId: string;           // ユーザーID（GSI）
  role: 'user' | 'assistant' | 'product_wish';
  content: string;          // メッセージ内容
  timestamp: string;        // タイムスタンプ
  citations?: string[];     // 引用（AIのみ・レガシー）
  sourceDocuments?: object[]; // ソース文書（AI）
  // --- 2026-07-29 RAG 応答メタ（assistant）---
  responseType?: 'clarify' | 'pages' | 'not_found';
  pageCandidates?: object[];
  clarifyQuestions?: string[];
  queryFilters?: object;    // 当時の機種・カテゴリ等
  // --- フィードバック ---
  feedback?: 'good' | 'bad';
  feedbackReason?: 'wrong_doc' | 'unresolved' | 'bad_answer' | 'other' | 'wrong_page';
  // wrong_page は旧データのみ（新規 PUT 拒否）。unresolved は「資料が悪い」決め打ちではなく failures で振り分け
  feedbackComment?: string;
  feedbackAt?: string;
  deleted?: boolean;        // 論理削除
  ttl: number;              // TTL（保存時から約60日。Stream→S3 で保全）
}
```

**GSI (Global Secondary Index):**
- userId-timestamp-index: ユーザーごとの履歴取得

失敗一覧（`GET /chat/admin/failures`）は失敗専用 GSI を持たず Scan + Filter（試用初期向け）。詳細は [`docs/api/chat.md`](./api/chat.md)。

## S3 バケット構成

> 実バケット名／プレフィックスは環境の CloudFormation / SSM を正とする。  
> 下記は概念メモ。KB 再利用構成の詳細は phase2 KB レポート等を参照。

### Knowledge Base 用ドキュメント

本番／開発の Knowledge Base が参照するドキュメントバケット（既存 KB 再利用）。

### アップロード／アーカイブ

- 一時アップロード用プレフィックス（環境依存）
- chatlogs Stream → S3 アーカイブ（TTL 物理削除前の保全）

## データライフサイクル管理

### チャット履歴の保管期間

**ポリシー（現行コード）:**
- ホットウィンドウ: 保存時から **約60日**（DynamoDB TTL）
- 物理削除前に Stream → S3 アーカイブで保全
- UI: 各セッションに残り日数を表示しうる

**実装（RAG 保存時）:**
```python
# lambda/rag/rag-function/app.py
ttl_timestamp = int(time.time()) + (60 * 24 * 60 * 60)  # 60 days
```
