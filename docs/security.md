# セキュリティ

> 出典: 旧 [spec.md](../spec.md) §5（PR #10 で本ファイルに切り出し）

## 認証・認可

**認証方式:**
- AWS Cognito User Pool
- JWT（JSON Web Token）ベース
- Access Token（1時間）+ Refresh Token（30日）

**認可:**
- API Gateway Cognito Authorizer
- Lambdaでユーザー権限チェック
- リソースベースのアクセス制御

## データ暗号化

**転送時の暗号化:**
- すべての通信はHTTPS（TLS 1.2以上）
- API Gateway → Lambda: AWS内部通信（暗号化済み）

**保管時の暗号化:**
- DynamoDB: AWS管理キー（デフォルト暗号化）
- S3: SSE-S3（サーバーサイド暗号化）
- Secrets Manager: AWS KMS暗号化

## ネットワークセキュリティ

**VPC構成:**
- Private Subnet内にLambda配置
- NAT Gateway経由で外部API接続
- Security Groupで通信制限

**IP制限:**
- AWS WAF IP Set: 192.168.28.0/24
- 社内ネットワークからのみアクセス可能

## 環境変数管理

**機密情報の保護:**
- すべての機密情報は`.env`ファイルで管理
- `.env`は`.gitignore`に記載（Git管理外）
- 本番環境はAWS Secrets Managerで管理

**環境変数の種類:**
```bash
# AWS設定
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=xxxxx

# Cognito
COGNITO_USER_POOL_ID=xxxxx
COGNITO_CLIENT_ID=xxxxx

# Bedrock
BEDROCK_KB_ID=xxxxx
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-xxxxx

# DynamoDB
DYNAMODB_USERS_TABLE=eleknowledge-users
DYNAMODB_CHATLOGS_TABLE=eleknowledge-chatlogs

# S3
S3_DOCUMENTS_BUCKET=eleknowledge-documents
```

## 入力検証

**バックエンド検証:**
- すべてのユーザー入力をサニタイゼーション
- XSS対策: HTMLエスケープ
- SQLインジェクション対策: パラメータ化クエリ（DynamoDB）
- 入力長制限: 最大文字数制限

**フロントエンド検証:**
- React Hook Formでバリデーション
- 型安全性（TypeScript）
- CSRFトークン（必要に応じて）

## 関連ドキュメント

- [architecture/overview.md](architecture/overview.md) — ネットワーク構成図
- [tech-stack.md](tech-stack.md) — Cognito / WAF / Secrets Manager のバージョン
- [data-model.md](data-model.md) — データ保管時の暗号化対象
