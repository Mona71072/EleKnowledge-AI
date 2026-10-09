---
status: draft
last-verified: 2026-09-02
related-code: infrastructure/sam/, frontend/src/, lambda/
---

# アーキテクチャ概要

> 最終検証: 2026-09-30 — リポジトリの SAM / frontend / Lambda と、同日確認した開発環境の CloudFormation 構成を照合。production 環境と Phase 3 の利用者向け E2E は未確認のため、本書は draft とする。

## 開発環境の構成

```text
利用者
  │ HTTPS
  ▼
AWS Amplify Hosting (Next.js App Router)
  │ Cognito User Pool の JWT
  ▼
API Gateway REST API
  ├─ Cognito 認証・RAG・チャット・管理 API
  ├─ Regional WAF Web ACL（API の IP / rate 制御）
  └─ Lambda (Python 3.13)
       ├─ 認証・ユーザー管理 ───────────────► Cognito / DynamoDB
       ├─ RAG ─────────────────────────────► Bedrock Knowledge Base / Bedrock model
       ├─ チャット・履歴 ───────────────────► DynamoDB chatlogs
       ├─ お知らせ・日次 KPI ───────────────► DynamoDB / EventBridge
       └─ Phase 3 troubleshooting ─────────► Bedrock Agent / DynamoDB
            (AWS リソースを確認。利用者向け E2E は未確認)

チャット履歴: DynamoDB Streams ─► archive Lambda ─► S3 ─► Glue / Athena
運用監視: CloudWatch Logs / metrics / alarms ─► SNS email
```

上図は開発環境の構成スナップショットである。Amplify の `develop` ブランチでは自動ビルドが有効だった。開発環境の RAG Lambda は `global.anthropic.claude-sonnet-5` を参照していたが、モデル設定は環境ごとに確認する。

## WAF・監視の状態

Regional Web ACL と API の関連付けは確認済み。一方、EleKnowledge 向け WAF ログ配信、WAF アラーム、専用通知 SNS は確認できていない。SAM テンプレートに記載があっても、環境で確認するまでは構成図上の実装済みリソースとみなさない。詳細は [AWS Resource Map](../aws-resource-map.md) を参照。

## ネットワーク境界

> 最終検証: 2026-09-02 — AWS 実査（VPC / NAT Gateway / Lambda VpcConfig）。

VPC、NAT Gateway、Private Subnet は存在せず、Lambda に `VpcConfig` は設定されていない。Lambda は VPC 外で実行される。ネットワークの確認記録と設計上の影響は [security.md](../security.md) を参照。

## 関連ドキュメント

- [components.md](components.md) — コンポーネントと役割
- [../tech-stack.md](../tech-stack.md) — 技術スタック
- [../security.md](../security.md) — 認証・暗号化・ネットワーク制御
- [../data-model.md](../data-model.md) — DynamoDB / S3 のデータモデル
- [../aws-resource-map.md](../aws-resource-map.md) — AWS リソースと IaC / 実環境の差
