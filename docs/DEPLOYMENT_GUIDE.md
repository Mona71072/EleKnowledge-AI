> [!WARNING]
> Legacy deployment guide. Do not use this document for the new AWS account migration to `ap-northeast-1`.
> Use [AWS Migration Runbook](aws-migration-runbook.md) and [AWS Resource Map](aws-resource-map.md) instead.
> This file may still contain old `us-east-1`, `development/staging/production`, and `EleKnowledge-AI-*` resource names.

# 📋 EleKnowledge-AI 環境別デプロイメントガイド

## 概要

このガイドでは、異なる環境（開発、ステージング、本番）でEleKnowledge-AIを構築・デプロイするための手順を説明します。

---

## 環境一覧

| 環境 | 用途 | Bedrock Region | URL | デプロイ頻度 |
|-----|------|----------------|-----|----------|
| **Development** | 開発・機能テスト | us-east-1 | dev.eleknowledge-ai.amplifyapp.com | 毎日 |
| **Staging** | UAT・動作検証 | us-east-1 | staging.eleknowledge-ai.amplifyapp.com | 週次 |
| **Production** | 本番環境 | us-east-1 | eleknowledge-ai.amplifyapp.com | 必要に応じて |

---

## 前提条件

### 必須要件

- ✅ AWS アカウント（環境ごと）
- ✅ AWS CLI v2 インストール
- ✅ AWS SAM CLI インストール
- ✅ Docker インストール（Lambda ローカルテスト用）
- ✅ Git クローン完了
- ✅ IAM ユーザー（適切な権限設定）

### AWS 権限確認

```bash
# 必要な権限をテスト
aws sts get-caller-identity

# 出力例:
# {
#   "UserId": "AIDXXXXXXXXXXXX",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/eleknowledge-dev"
# }
```

### IAM ポリシー例（最小権限）

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "apigateway:*",
        "dynamodb:*",
        "s3:*",
        "cognito-idp:*",
        "bedrock:*",
        "opensearchserverless:*",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:PassRole",
        "iam:GetRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "logs:*",
        "ssm:PutParameter",
        "ssm:GetParameter",
        "kms:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## デプロイメント手順

### Step 1: 環境変数設定

#### AWS CLI プロファイル作成

```bash
# 開発環境用プロファイル
aws configure --profile eleknowledge-dev
# または
aws configure --profile eleknowledge-stg
# または
aws configure --profile eleknowledge-prod
```

#### 環境変数定義ファイル作成

**`infrastructure/sam/parameters-dev.json`:**
```json
{
  "ParameterKey": "Environment",
  "ParameterValue": "development"
},
{
  "ParameterKey": "ProjectName",
  "ParameterValue": "EleKnowledge-AI"
},
{
  "ParameterKey": "AWS Region",
  "ParameterValue": "us-east-1"
},
{
  "ParameterKey": "Phase1StackName",
  "ParameterValue": "EleKnowledge-AI-development-phase1"
},
{
  "ParameterKey": "BedrockModelId",
  "ParameterValue": "anthropic.claude-sonnet-4-20250514-v1:0"
},
{
  "ParameterKey": "RagLambdaTimeout",
  "ParameterValue": "300"
},
{
  "ParameterKey": "RagLambdaMemory",
  "ParameterValue": "1024"
},
{
  "ParameterKey": "ChatLambdaTimeout",
  "ParameterValue": "30"
},
{
  "ParameterKey": "ChatLambdaMemory",
  "ParameterValue": "512"
},
{
  "ParameterKey": "RagApiThrottleBurst",
  "ParameterValue": "20"
},
{
  "ParameterKey": "RagApiThrottleRate",
  "ParameterValue": "5"
},
{
  "ParameterKey": "ChatApiThrottleBurst",
  "ParameterValue": "50"
},
{
  "ParameterKey": "ChatApiThrottleRate",
  "ParameterValue": "10"
},
{
  "ParameterKey": "LogRetentionInDays",
  "ParameterValue": "30"
}
```

**`infrastructure/sam/parameters-stg.json`:**
```json
{
  "ParameterKey": "Environment",
  "ParameterValue": "staging"
},
{
  "ParameterKey": "ProjectName",
  "ParameterValue": "EleKnowledge-AI"
},
{
  "ParameterKey": "AWS Region",
  "ParameterValue": "us-east-1"
},
{
  "ParameterKey": "Phase1StackName",
  "ParameterValue": "EleKnowledge-AI-staging-phase1"
},
{
  "ParameterKey": "BedrockModelId",
  "ParameterValue": "anthropic.claude-sonnet-4-20250514-v1:0"
},
{
  "ParameterKey": "RagLambdaTimeout",
  "ParameterValue": "300"
},
{
  "ParameterKey": "RagLambdaMemory",
  "ParameterValue": "1024"
},
{
  "ParameterKey": "ChatLambdaTimeout",
  "ParameterValue": "30"
},
{
  "ParameterKey": "ChatLambdaMemory",
  "ParameterValue": "512"
},
{
  "ParameterKey": "RagApiThrottleBurst",
  "ParameterValue": "30"
},
{
  "ParameterKey": "RagApiThrottleRate",
  "ParameterValue": "10"
},
{
  "ParameterKey": "ChatApiThrottleBurst",
  "ParameterValue": "100"
},
{
  "ParameterKey": "ChatApiThrottleRate",
  "ParameterValue": "20"
},
{
  "ParameterKey": "LogRetentionInDays",
  "ParameterValue": "60"
}
```

**`infrastructure/sam/parameters-prod.json`:**
```json
{
  "ParameterKey": "Environment",
  "ParameterValue": "production"
},
{
  "ParameterKey": "ProjectName",
  "ParameterValue": "EleKnowledge-AI"
},
{
  "ParameterKey": "AWS Region",
  "ParameterValue": "us-east-1"
},
{
  "ParameterKey": "Phase1StackName",
  "ParameterValue": "EleKnowledge-AI-production-phase1"
},
{
  "ParameterKey": "BedrockModelId",
  "ParameterValue": "anthropic.claude-sonnet-4-20250514-v1:0"
},
{
  "ParameterKey": "RagLambdaTimeout",
  "ParameterValue": "300"
},
{
  "ParameterKey": "RagLambdaMemory",
  "ParameterValue": "2048"
},
{
  "ParameterKey": "ChatLambdaTimeout",
  "ParameterValue": "30"
},
{
  "ParameterKey": "ChatLambdaMemory",
  "ParameterValue": "1024"
},
{
  "ParameterKey": "RagApiThrottleBurst",
  "ParameterValue": "100"
},
{
  "ParameterKey": "RagApiThrottleRate",
  "ParameterValue": "20"
},
{
  "ParameterKey": "ChatApiThrottleBurst",
  "ParameterValue": "500"
},
{
  "ParameterKey": "ChatApiThrottleRate",
  "ParameterValue": "50"
},
{
  "ParameterKey": "LogRetentionInDays",
  "ParameterValue": "90"
}
```

### Step 2: Phase 1 デプロイ

```bash
# 環境変数設定
export ENVIRONMENT=development  # または staging, production
export AWS_PROFILE=eleknowledge-dev
export REGION=us-east-1

# Phase 1 ビルド
cd infrastructure/sam
sam build --template phase1-template.yaml --use-container

# Phase 1 デプロイ
sam deploy \
  --stack-name EleKnowledge-AI-${ENVIRONMENT}-phase1 \
  --profile ${AWS_PROFILE} \
  --region ${REGION} \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    "Environment=${ENVIRONMENT}" \
    "ProjectName=EleKnowledge-AI"
```

**デプロイ確認:**
```bash
# CloudFormation スタック状態確認
aws cloudformation describe-stacks \
  --stack-name EleKnowledge-AI-${ENVIRONMENT}-phase1 \
  --profile ${AWS_PROFILE} \
  --region ${REGION} \
  --query 'Stacks[0].StackStatus'

# 期待値: CREATE_COMPLETE または UPDATE_COMPLETE
```

### Step 3: Phase 2 デプロイ

```bash
# Phase 2 ビルド
sam build --template phase2-template.yaml --use-container

# Phase 2 デプロイ（パラメータファイル使用）
sam deploy \
  --stack-name EleKnowledge-AI-${ENVIRONMENT}-phase2 \
  --profile ${AWS_PROFILE} \
  --region ${REGION} \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides file://parameters-${ENVIRONMENT}.json
```

**デプロイ確認:**
```bash
# CloudFormation Outputs確認
aws cloudformation describe-stacks \
  --stack-name EleKnowledge-AI-${ENVIRONMENT}-phase2 \
  --profile ${AWS_PROFILE} \
  --region ${REGION} \
  --query 'Stacks[0].Outputs'
```

### Step 4: Knowledge Base 手動設定

```bash
# 1. AWS Bedrock コンソール上で Knowledge Base を作成
# 2. 作成後、Knowledge Base ID を取得
# 例: KB_ELEKNOWLEDGE_001

# 3. Phase 2 SAM テンプレートのパラメータを確認
sam deploy \
  --stack-name EleKnowledge-AI-${ENVIRONMENT}-phase2 \
  --profile ${AWS_PROFILE} \
  --region ${REGION} \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    "BedrockKnowledgeBaseId=KB_ELEKNOWLEDGE_001" \
    file://parameters-${ENVIRONMENT}.json

# 注: Knowledge Base ID は環境変数として Lambda 関数に自動設定されます
# Lambda 関数内では KNOWLEDGE_BASE_ID 環境変数から取得可能です
```

**Knowledge Base 作成手順:**
1. AWS Bedrock コンソール → Knowledge Base → Create Knowledge Base
2. 名前: `eleknowledge-${ENVIRONMENT}-kb`
3. Data Source: S3 バケット (`eleknowledge-${ENVIRONMENT}-documents`)
4. メタデータ設定: ドキュメントのタイプ、製品、モデル等を設定
5. 同期実行
6. Knowledge Base ID を控える（デプロイ時に使用）

### Step 5: Amplify デプロイ

```bash
# Amplify コンソールから手動設定または CLI使用

# Amplify CLI使用例（オプション）
amplify init  # 初回のみ
amplify push  # デプロイ
```

---

## 環境別の設定差分

### パフォーマンス設定

| 項目 | Development | Staging | Production |
|------|------------|---------|-----------|
| RAG Lambda Memory | 1024 MB | 1024 MB | 2048 MB |
| Chat Lambda Memory | 512 MB | 512 MB | 1024 MB |
| RAG API Burst | 20 req/s | 30 req/s | 100 req/s |
| RAG API Rate | 5 req/s | 10 req/s | 20 req/s |
| Logs Retention | 30日 | 60日 | 90日 |

### コスト試算

| 環境 | 月間コスト（概算） | 用途 |
|-----|------------|------|
| Development | $15-20 | 開発・テスト |
| Staging | $20-25 | UAT・検証 |
| Production | $30-40 | 本番稼働 |

---

## ロールバック手順

### 特定リソースのロールバック

```bash
# CloudFormation スタック削除（全リソース削除）
aws cloudformation delete-stack \
  --stack-name EleKnowledge-AI-${ENVIRONMENT}-phase2 \
  --profile ${AWS_PROFILE} \
  --region ${REGION}

# DynamoDB テーブルのみ保護したい場合
# SAM テンプレート内で RetentionPolicy: Retain を設定
```

### 部分的なリソース更新

```bash
# 特定パラメータのみ更新
sam deploy \
  --stack-name EleKnowledge-AI-${ENVIRONMENT}-phase2 \
  --profile ${AWS_PROFILE} \
  --region ${REGION} \
  --no-fail-on-empty-changeset \
  --parameter-overrides \
    "RagLambdaMemory=2048" \
    "RagApiThrottleRate=10"
```

---

## トラブルシューティング

### Lambda デプロイエラー

**エラー:** `Unable to upload artifact`

**原因:** コード量が大きすぎる

**解決策:**
```bash
# Lambda レイヤー使用検討
# または
# メモリ削減・コード最適化
```

### Knowledge Base 検索エラー

**エラー:** `Access Denied to OpenSearch`

**原因:** IAM ロールの権限不足

**解決策:**
```bash
# KnowledgeBaseRole のポリシー確認
aws iam get-role-policy \
  --role-name EleKnowledge-AI-${ENVIRONMENT}-kb-role \
  --policy-name OpenSearchAccess
```

### Bedrock API 制限エラー

**エラー:** `ThrottlingException`

**原因:** Bedrock API レート制限到達

**解決策:**
```bash
# 待機時間を設定（Lambda 内のリトライロジック）
# または
# Bedrock リクエスト制限申請
```

---

## モニタリング・メンテナンス

### CloudWatch ダッシュボード作成

```bash
# メトリクス監視スクリプト
aws cloudwatch put-metric-dashboard \
  --dashboard-name EleKnowledge-AI-${ENVIRONMENT} \
  --dashboard-body file://dashboard-config.json
```

### ログ分析

```bash
# CloudWatch Logs Insights クエリ例
aws logs start-query \
  --log-group-name /aws/lambda/EleKnowledge-AI-${ENVIRONMENT}-rag \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | stats count() by @message'
```

---

## チェックリスト

### デプロイ前

- [ ] AWS アカウント確認
- [ ] IAM 権限確認
- [ ] Bedrock リージョン確認
- [ ] パラメータファイル確認

### デプロイ中

- [ ] Phase 1 デプロイ完了確認
- [ ] Phase 1 出力値取得
- [ ] Phase 2 デプロイ完了確認
- [ ] Knowledge Base 作成・同期

### デプロイ後

- [ ] API エンドポイント動作確認
- [ ] Lambda 関数ログ確認
- [ ] DynamoDB テーブル確認
- [ ] Amplify デプロイ完了確認

---

## 環境間のデータ移行

### DynamoDB バックアップ復元

```bash
# 開発環境からステージング環境へ復元
aws dynamodb create-backup \
  --table-name eleknowledge-development-chatlogs \
  --backup-name eleknowledge-dev-backup-$(date +%s)

# バックアップからテーブル復元
aws dynamodb restore-table-from-backup \
  --target-table-name eleknowledge-staging-chatlogs \
  --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/eleknowledge-development-chatlogs/backup/01234567890123-abcdefgh
```

### S3 ドキュメント同期

```bash
# 開発環境から本番環境へドキュメント複製
aws s3 sync \
  s3://eleknowledge-development-documents/ \
  s3://eleknowledge-production-documents/ \
  --profile eleknowledge-dev
```

---

**最終更新:** 2026-01-22  
**対応バージョン:** Phase 2 以降
