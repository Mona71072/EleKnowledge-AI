# コンポーネント構成

> 出典: 旧 [spec.md](../../spec.md) §2.2（PR #10 で本ファイルに切り出し）

システム全体図は [overview.md](overview.md) を参照。

## フロントエンド

- **Framework:** Next.js 14 (App Router)
- **UI Library:** Tailwind CSS + shadcn/ui
- **状態管理:** React Context API / Zustand
- **ホスティング:** AWS Amplify Hosting

## バックエンド

- **API Gateway:** 3つの独立したREST API
- **Lambda Runtime:** Python 3.11 / Node.js 18
- **認証:** AWS Cognito User Pool

## AI/ML

- **LLM:** Amazon Bedrock Claude 4.5 Haiku
- **Vector Store:** Amazon Bedrock Knowledge Base
- **Multi-Agent:** Amazon Bedrock Agent (Phase 3)

## データストア

- **User DB:** Amazon DynamoDB (users)
- **Chat History:** Amazon DynamoDB (eleknowledge-chatlogs)
- **Sites DB:** Amazon DynamoDB(sites)
- **Document Storage:** Amazon S3

## 関連ドキュメント

- [overview.md](overview.md) — システム全体図（ネットワーク〜AWSサービス）
- [../tech-stack.md](../tech-stack.md) — バージョン込みの技術スタック
- [../data-model.md](../data-model.md) — データストアのスキーマ詳細
