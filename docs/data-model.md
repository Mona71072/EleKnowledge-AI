---
status: production
last-verified: 2026-04-24
related-code: infrastructure/, lambda/
---

# データモデル

> 出典: 旧 [spec.md](../spec.md) §6（PR #10 で本ファイルに切り出し）

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

### eleknowledge-chatlogs テーブル

```typescript
{
  sessionId: string;        // Partition Key
  messageId: string;        // Sort Key (ULID)
  userId: string;           // ユーザーID（GSI）
  role: 'user' | 'assistant';
  content: string;          // メッセージ内容
  timestamp: string;        // タイムスタンプ
  citations?: string[];     // 引用（AIのみ）
  sourceDocuments?: object[]; // ソース文書
  feedback?: string;        // フィードバック
  ttl: number;              // TTL（30日後削除）
}
```

**GSI (Global Secondary Index):**
- userId-timestamp-index: ユーザーごとの履歴取得

## S3 バケット構成

### eleknowledge-documents（Knowledge Base用）

```
eleknowledge-documents/
├── manuals/              # マニュアル
├── policies/             # 規定・ポリシー
├── reports/              # 報告書
└── specifications/       # 仕様書
```

### eleknowledge-uploads（一時アップロード用）

```
eleknowledge-uploads/
├── tmp/                  # 一時ファイル（24時間で削除）
└── processed/            # 処理済みファイル
```

## データライフサイクル管理

### チャット履歴の保管期間

**ポリシー:**
- 保管期間: 最終更新から**30日間**
- 自動削除: DynamoDB TTL機能で実装
- UI表示: 各セッションに残り日数を表示

**実装:**
```python
# TTL設定（メッセージ保存時）
ttl_timestamp = int(time.time()) + (30 * 24 * 60 * 60)  # 30日後

item = {
    'sessionId': session_id,
    'messageId': message_id,
    'content': content,
    'timestamp': datetime.now().isoformat(),
    'ttl': ttl_timestamp  # TTL属性
}
```

**UI表示例:**
```typescript
// 残り日数の計算と表示
const daysUntilDeletion = calculateDaysUntilDeletion(session.ttl);
// "あと15日で削除されます"
```

### S3 ドキュメントのライフサイクル

**ライフサイクルポリシー:**
- 30日: Standard → Glacier（アーカイブ）
- 90日: Glacier → Deep Archive
- 1年: 削除（ポリシーに基づく）

**一時ファイル:**
- tmp/ 配下: 24時間で自動削除

### 削除通知

**通知設定:**
- 削除7日前: メール通知（オプション）
- 削除1日前: UI内通知バナー表示

## 関連ドキュメント

- [architecture/components.md](architecture/components.md) — データストアのコンポーネント概要
- [security.md](security.md) — 暗号化・アクセス制御
- [tech-stack.md](tech-stack.md) — DynamoDB / S3 のサービス諸元
