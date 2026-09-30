---
status: draft
last-verified: 2026-09-30
related-code: frontend/package.json, frontend/package-lock.json, infrastructure/sam/, lambda/
---

# 技術スタック

> 最終検証: 2026-09-30 — package manifest / lockfile と SAM runtime を照合。AWS のモデル設定は開発環境に限られ、production の実環境確認は未実施のため draft とする。

## フロントエンド

| 技術 | リポジトリ上の指定 | 用途 |
|---|---|---|
| Next.js | `^15.5.24` | App Router |
| React / React DOM | `19.1.0` | UI |
| AWS Amplify | `^6.15.7` | Cognito 認証統合 |
| Axios | `^1.13.2` | API 通信 |
| Tailwind CSS | `^4` | スタイリング |
| TypeScript | `^5` | 型検査 |

バージョンは `frontend/package.json` の指定範囲であり、環境ごとのデプロイ済み成果物を示すものではない。

## バックエンド・AWS

| 技術 | 用途 |
|---|---|
| AWS SAM / Lambda Python 3.13 | 認証・RAG・チャット・管理 API の handler |
| API Gateway REST API | Cognito 認証と Lambda API の公開 |
| Amazon Cognito User Pool | ユーザー認証・JWT 発行 |
| Amazon DynamoDB | ユーザー、チャット履歴、管理・集計データ |
| Amazon S3 / Glue / Athena | チャットアーカイブと分析 |
| Amazon CloudWatch / SNS | ログ、メトリクス、アラーム、通知 |
| AWS WAF | Regional Web ACL による API の IP / rate 制御 |
| AWS Amplify Hosting | Next.js フロントエンド配信 |

## AI / ML

- Amazon Bedrock Knowledge Base が RAG 検索を提供する。
- 開発環境では 2026-09-30 時点の RAG Lambda が `global.anthropic.claude-sonnet-5` を参照していた。モデルは環境設定で指定されるため、他環境へ一般化しない。
- Bedrock Agent を使うトラブルシューティングの AWS リソースは確認済みだが、利用者向け E2E は未確認。
- Knowledge Base の embedding model は今回再確認していない。過去のモデル名を現行環境へ適用しない。

## 関連ドキュメント

- [architecture/overview.md](architecture/overview.md) — システム全体図
- [architecture/components.md](architecture/components.md) — コンポーネント構成
- [security.md](security.md) — セキュリティ設計
- [aws-resource-map.md](aws-resource-map.md) — AWS 実環境と IaC の確認記録
