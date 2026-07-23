---
status: production
last-verified: 2026-04-24
related-code: frontend/package.json, lambda/, infrastructure/
---

# 技術スタック

> 出典: 旧 [spec.md](../spec.md) §4（PR #10 で本ファイルに切り出し）

## フロントエンド

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| Framework | Next.js | 14.x | App Router、SSR/SSG |
| UI Library | React | 18.x | コンポーネント開発 |
| スタイリング | Tailwind CSS | 3.x | ユーティリティファースト |
| UI Components | shadcn/ui | latest | 再利用可能コンポーネント |
| 状態管理 | Zustand | 4.x | 軽量状態管理 |
| フォーム | React Hook Form | 7.x | フォーム検証 |
| HTTP Client | Axios | 1.x | API通信 |
| 認証 | AWS Amplify | 6.x | Cognito統合 |

## バックエンド

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| Lambda Runtime | Python | 3.11 | RAG処理、DB操作 |
| Lambda Runtime | Node.js | 18.x | 認証処理 |
| API Gateway | REST API | v1 | APIエンドポイント |
| 認証 | AWS Cognito | - | ユーザー管理 |
| パッケージ管理 | pip / npm | - | 依存関係管理 |

## AI/ML

| カテゴリ | 技術 | モデル | 用途 |
|---------|------|--------|------|
| LLM | Amazon Bedrock | Claude 4 Sonnet | RAG応答生成 |
| Embedding | Amazon Bedrock | Titan Embeddings G1 | ベクトル化 |
| Vector DB | OpenSearch Serverless | - | Knowledge Base |
| Multi-Agent | Bedrock Agent | - | 複雑タスク処理（Phase 3） |

## インフラ

| カテゴリ | サービス | 用途 |
|---------|---------|------|
| ホスティング | AWS Amplify | フロントエンド配信 |
| セキュリティ | AWS WAF | IP制限、攻撃防御 |
| データベース | DynamoDB | ユーザー、チャット履歴 |
| ストレージ | S3 | ドキュメント保存 |
| シークレット | Secrets Manager | API Key管理 |
| ログ | CloudWatch Logs | ログ集約 |
| 監視 | CloudWatch | メトリクス、アラート |

## 関連ドキュメント

- [architecture/overview.md](architecture/overview.md) — システム全体図
- [architecture/components.md](architecture/components.md) — コンポーネント構成
- [security.md](security.md) — セキュリティ設計
