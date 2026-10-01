---
status: production
phase: 1
last-verified: 2026-08-21
related-code: frontend/src/app/, lambda/auth/
---

# Phase 1: 基盤整備（2ヶ月）【完成】

> 本ドキュメントは [spec.md](../../../spec.md) §3.1 から切り出された Phase 1 の機能仕様です。
> 全体索引は [spec.md](../../../spec.md) を参照してください。

## 認証システム【完成】

**Phase 1実装機能:**
- ✅ ユーザー登録（サインアップ）※メール確認完了後は自動ログインしてホーム画面へ遷移（同一ブラウザセッション内のみ。別タブ・リロード後はログイン画面へ）
- ✅ ログイン・ログアウト
- ✅ パスワードリセット
- ✅ MFA（多要素認証）※オプション

**将来的な拡張（Phase 4以降）:**
- SAML 2.0統合（社内IdP連携）
- OIDC統合（Google Workspace等）
- Cognito Identity Providerとして統合

**技術実装:**
```typescript
// AWS Cognito統合
import { Auth } from 'aws-amplify';

// サインアップ
const signUp = async (email: string, password: string) => {
  await Auth.signUp({
    username: email,
    password,
    attributes: {
      email
    }
  });
};

// ログイン
const signIn = async (email: string, password: string) => {
  const user = await Auth.signIn(email, password);
  return user;
};
```

**セキュリティ要件:**
- パスワード: 8文字以上、大文字・小文字・数字・記号必須
- セッション有効期限: 24時間
- 失敗回数制限: 5回でアカウントロック（15分）

**トークン管理:**
- **Access Token:** 1時間（短命）
- **Refresh Token:** 24時間（セッション有効期限と一致）
- **ID Token:** 1時間
- **自動リフレッシュ:** 有効期限5分前に自動更新
- **トークン保存:** localStorage（開発環境）/ httpOnly Cookie（本番推奨）

**CORS設定:**
```typescript
// API Gateway CORS設定
{
  "allowedOrigins": [
    "https://eleknowledge.amplifyapp.com",
    "http://localhost:3000" // 開発環境のみ
  ],
  "allowedMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  "allowedHeaders": ["Content-Type", "Authorization"],
  "allowCredentials": true,
  "maxAge": 3600
}
```

## ホーム画面【完成】

**機能:**
- ✅ ログイン後のランディングページ
- ✅ 3つの主要機能への導線
- ✅ ユーザー情報表示
- ✅ 開発モード（認証スキップ機能）搭載
- ✅ インフォモーダル機能（Knowledge Base説明、質問例表示）
- ✅ レスポンシブデザイン対応

**UI構成:**
```
┌─────────────────────────────────────────────┐
│  EleKnowledge                  👤 user@... │
├─────────────────────────────────────────────┤
│                                             │
│  🤖 RAGチャット                              │
│  技術資料・マニュアルの検索と質問応答         │
│  [開始する →]                                │
│                                             │
│  🔧 トラブルシューティング  🚧 開発中         │
│  現場トラブルの原因分析と対処方法提案         │
│  [準備中]                                    │
│                                             │
│  ✅ 品質書類チェック  🚧 開発中               │
│  技評の自動判定　　　　　　　　                │
│  [準備中]                                    │
│                                             │
└─────────────────────────────────────────────┘
```

**画面遷移:**
```
ログイン → ホーム画面
         ├─ RAGチャット画面
         ├─ トラブルシューティング画面（開発中表示）
         └─ 品質書類チェック画面（開発中表示）
```

## IP制限設定

**AWS Amplify WAF v2統合機能（2024年追加）:**

2024年にAmplifyがWAF直接統合機能を追加したため、CloudFront経由の追加設定は不要です。

**実装手順:**
1. Amplifyコンソール → App settings → Access control
2. WAF ACLを作成・アタッチ
3. IPセットルールで社内IPを許可

**許可IPリスト:**
```bash
x.x.x.0/32    # 社内ネットワーク（20人同時接続想定）
```

**WAFルール設定:**

| 優先度 | ルール名 | タイプ | 設定内容 |
|-------|---------|--------|---------|
| 1 | IP許可リスト | IP Set | x.x.x.0/32のみ許可 |
| 2 | レート制限（IP） | Rate-based | 500 req/5min/IP |
| 3 | レート制限（全体） | Rate-based | 2000 req/5min |
| 4 | SQLインジェクション | Managed Rule | AWS-AWSManagedRulesSQLiRuleSet |
| 5 | 共通攻撃防御 | Managed Rule | AWS-AWSManagedRulesCommonRuleSet |

**コスト:**
- WAF基本料金: $5/月
- ルール単価: $1/月 × 5ルール = $5/月
- リクエスト単価: $0.60/100万リクエスト
- **月間想定:** 約$11/月（2万リクエスト想定）

**監視:**
- CloudWatch Logsでブロックログ記録
- ブロック回数が閾値超過時にアラート通知
