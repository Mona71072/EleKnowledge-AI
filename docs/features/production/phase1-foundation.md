---
status: draft
phase: 1
last-verified: 2026-08-21
related-code: frontend/src/app/, lambda/auth/, infrastructure/sam/phase1-template.yaml
---

# Phase 1: 基盤整備 — 旧仕様（再検証中）

> **現行仕様としての使用注意:** この文書は実装例・セッションやトークンの記述を含め、現行コードとの全面照合が終わっていない。認証 API の契約は [API 仕様](../../api/auth.md)、実際の実装は `lambda/auth/` と `infrastructure/sam/phase1-template.yaml` を参照する。Phase 1 の AWS スタックが存在することは確認済みだが、この文書の各機能の E2E 確認を意味しない。

> 最終検証: 2026-09-30 — frontmatter / 索引と開発環境の Phase 1 stack の存在を部分照合。本文全体および認証 E2E は未検証。

> 本ドキュメントは [spec.md](../../../spec.md) §3.1 から切り出された Phase 1 の機能仕様です。
> 全体索引は [spec.md](../../../spec.md) を参照してください。

## 認証システム【完成】

**Phase 1実装機能:**
- ✅ ユーザー登録（サインアップ）※メール確認完了後は自動ログインしてホーム画面へ遷移（同一ブラウザセッション内のみ。別タブ・リロード後はログイン画面へ）
- ✅ ログイン・ログアウト
- ✅ パスワードリセット
- MFA（多要素認証）— 現在の User Pool 設定を未確認。提供機能として保証しない。

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

**過去の設計値（現行設定は未確認）:**
この文書に残るパスワード要件、セッション期限、失敗回数制限は現行 User Pool の設定値として扱わない。現行契約は [認証 API 仕様](../../api/auth.md) と Cognito / frontend の実設定を確認する。

**トークン管理:**
トークン期限、保存方法、自動更新タイミングの過去記述は現行仕様として保証しない。現行の認証 API 契約は [認証 API 仕様](../../api/auth.md)、クライアント実装は `frontend/` を参照する。

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

## IP 制限・WAF

> 最終検証: 2026-09-30 — AWS の Regional Web ACL と API 関連付けの存在を確認。ルール詳細・ログ配信・通知の全体検証ではない。

この仕様書に残っていた Amplify WAF 手順、IP 範囲、閾値、費用見積もり、WAF ログ・通知の説明は現行手順として撤回する。開発環境では Regional Web ACL と API 関連付けを確認したが、EleKnowledge 用 WAF ログ配信・アラーム・専用 SNS 通知は確認できなかった。現在の IaC 定義と実環境の差は [AWS Resource Map](../../aws-resource-map.md) と [WAF 実施計画](../development/2026-09-18-security-observability-plan.md) を参照する。
