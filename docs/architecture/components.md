---
status: draft
last-verified: 2026-09-30
related-code: frontend/src/, lambda/, infrastructure/sam/
---

# コンポーネント構成

> 最終検証: 2026-09-30 — frontend の route / package manifest、SAM テンプレート、Lambda 配置を確認。AWS 確認は開発環境のみのため、production 適用確認までは draft とする。

システム全体図は [overview.md](overview.md)、API の公開契約は [RAG API](../api/rag.md)・[チャット API](../api/chat.md)・[認証 API](../api/auth.md)を参照。

## フロントエンド

- Next.js App Router で認証、RAG チャット、履歴、管理画面を提供する。
- AWS Amplify Hosting が配信し、開発環境の `develop` ブランチは自動ビルドが有効だった。
- トラブルシューティング画面のコードは存在するが、AWS リソースの存在だけでは利用者向け E2E の確認にならない。

## API・バックエンド

> 最終検証: 2026-10-05 — develop の SAM runtime 定義を照合（主要 stack と旧式 troubleshooting template の差を確認）

- API Gateway REST API が認証、RAG、チャット、トラブルシューティング、お知らせ・KPI API を受け付ける。
- 認証は Cognito User Pool と JWT を使う。API 側で JWT の subject を用いて利用者データを分離する。
- 主要な SAM stack の Lambda runtime は Python 3.13。旧式の `infrastructure/sam/phase3-troubleshooting-small.yaml` は Python 3.8 を指定している。各 stack / handler の詳細は `infrastructure/sam/` と `lambda/` を参照する。
- トラブルシューティングの API・Lambda・データテーブルは開発環境に存在した。利用者向け提供状態は未確認として扱う。

## AI・データ

- RAG は Amazon Bedrock Knowledge Base と Bedrock の生成モデルを利用する。モデル ID は環境設定で変わる。
- チャット履歴は DynamoDB `chatlogs` に保存し、Streams から S3 アーカイブへ連携する。アーカイブは Glue / Athena で参照する。
- お知らせと KPI は DynamoDB を利用する。KPI aggregator の実装は日次の UTC 集計であり、設計中の KPI v2 と区別する。

## 運用

- CloudWatch Logs、メトリクス、アラーム、Logs Insights 保存クエリを使う。
- 2026-09-30 の開発環境観測と `origin/develop` の IaC 定義には件数差がある。WAF ログ等の未反映リソースを運用済みと扱わない。
- 差分・検証範囲・未確認事項は [AWS Resource Map](../aws-resource-map.md) と [運用ランブック](../ops-runbook.md) に記録する。

## 関連ドキュメント

- [overview.md](overview.md) — システム全体図
- [../tech-stack.md](../tech-stack.md) — バージョン込みの技術スタック
- [../data-model.md](../data-model.md) — データストアのスキーマ詳細
