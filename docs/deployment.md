---
status: production
last-verified: 2026-04-24
related-code: infrastructure/, amplify.yml, samconfig.toml
---

# 🚀 デプロイ構成

> 本ドキュメントは [spec.md](../spec.md) §8 から切り出された詳細仕様です。

## 1. AWSリージョン戦略

**プライマリリージョン:** us-east-1（米国東部バージニア北部）

**選定理由:**
1. ✅ Bedrock Claude 4の最新機能が最初に利用可能
2. ✅ 新サービス・機能の提供が最速
3. ✅ サービス障害時のAWSサポートが最も充実
4. ✅ コスト面で有利（一部サービス）

**考慮事項:**
- ⚠️ レイテンシー: 日本から約150ms（許容範囲内）
- ⚠️ データレジデンシー: 社内データが米国に保存
- ⚠️ コンプライアンス: 法的要件確認済み

**将来的な拡張:**
- マルチリージョン展開は当面予定なし
- DR（災害復旧）は同リージョン内AZ冗長化で対応

## 2. 環境構成

| 環境 | 用途 | URL | ブランチ |
|-----|------|-----|---------|
| Development | 開発・テスト | dev.eleknowledge-ai.amplifyapp.com | develop |
| Production | 本番 | eleknowledge-ai.amplifyapp.com | main |

## 3. CI/CD

**Amplify Hosting自動デプロイ:**
1. Gitプッシュ検知
2. ビルド実行（Next.js build）
3. テスト実行
4. デプロイ（成功時のみ）
5. 通知（Slack）

**Lambda デプロイ:**
- AWS SAM / Serverless Framework
- GitHub Actions経由でデプロイ
- Blue/Green デプロイ（本番）

## 4. インフラ as Code【完成】

**使用ツール:**
- ✅ AWS CloudFormation
- ✅ AWS SAM（phase1-template.yaml）
- Terraform（将来検討）

**Phase 1 SAM テンプレート実装内容:**
- ✅ Cognito User Pool作成
- ✅ Cognito User Pool Client設定
- ✅ DynamoDB テーブル設定（users、chatlogs）
- ✅ S3 バケット設定（documents、uploads）
- ✅ Lambda実行ロール・ポリシー定義
- ✅ Lambda関数デプロイ設定
- ✅ API Gateway設定（CORS、スロットリング、ログ出力）
- ✅ CloudWatch Logs設定（30日保管）

## 5. コスト試算

**月間想定コスト（20人同時接続、100人登録、1日平均10クエリ）**

| サービス | 項目 | 想定使用量 | 月額概算（USD） |
|---------|------|-----------|----------------|
| **AI/ML** |
| Bedrock Claude 4 | 入力トークン | 60万トークン | $1.80 |
| Bedrock Claude 4 | 出力トークン | 20万トークン | $3.00 |
| Knowledge Base | ベクトル検索 | 6,000クエリ | $3.00 |
| **データベース** |
| DynamoDB | 読み込み | 2万RCU | $2.50 |
| DynamoDB | 書き込み | 6,000WCU | $3.00 |
| **ホスティング** |
| Amplify Hosting | ビルド・配信 | 20GB転送 | $3.00 |
| **コンピューティング** |
| Lambda | 実行時間 | 2万GB-秒 | $0.33 |
| API Gateway | リクエスト | 2万リクエスト | $0.07 |
| **セキュリティ** |
| WAF | 基本+ルール | 5ルール | $10.00 |
| WAF | リクエスト | 2万リクエスト | $0.01 |
| **ストレージ** |
| S3 | ストレージ | 10GB | $0.23 |
| **その他** |
| CloudWatch | ログ・メトリクス | 標準 | $2.00 |
| **合計** | | | **$28.94/月** |

**年間コスト:** 約**$347（約48,000円）**

**コスト最適化施策:**
1. DynamoDB On-Demand → Provisioned（安定稼働後）
2. Lambda予約済みキャパシティ（高頻度実行時）
3. S3 Intelligent-Tiering活用
4. CloudWatch Logs保管期間最適化
