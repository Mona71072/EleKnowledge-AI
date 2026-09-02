---
status: production
last-verified: 2026-08-21
related-code: infrastructure/, lambda/, waf-rules.json
---

# セキュリティ

> 出典: 旧 [spec.md](../spec.md) §5（PR #10 で本ファイルに切り出し）

## 認証・認可

**認証方式:**
- AWS Cognito User Pool
- JWT（JSON Web Token）ベース
- Access Token（1時間）+ Refresh Token（24時間）

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

> 最終検証: 2026-09-02 — AWS 実査（VPC / NAT Gateway / Lambda `VpcConfig`）。§IP 制限 は本検証の対象外

### 現行の実体

**Lambda は VPC 外で実行される。** VPC・NAT Gateway は存在しない。

| 項目 | 実測値 |
|---|---|
| VPC | 0 件（デフォルト VPC も存在しない） |
| NAT Gateway | 0 件 |
| Lambda の `VpcConfig` | 全 42 関数で未設定（`rag-dev` / `chat-dev` を含む） |
| IaC 上の定義 | `infrastructure/` 配下に `VpcConfig` / `NatGateway` / `AWS::EC2::VPC` の記述なし（0 件） |

実査コマンド（リージョン `ap-northeast-1`。読み取りのみ）:

```bash
aws ec2 describe-vpcs           --region ap-northeast-1
aws ec2 describe-nat-gateways   --region ap-northeast-1
aws lambda list-functions       --region ap-northeast-1 --query 'Functions[].{Name:FunctionName,Vpc:VpcConfig.VpcId}'
```

したがって Lambda のアウトバウンド通信に経路上の制限はない。現状の外向き通信は
AWS API（Bedrock / DynamoDB / S3）宛のみで、インターネット上の第三者ドメインへ
能動的に通信する処理は存在しない。

### VPC 構成【未実装・将来構想】

> ⚠️ **以下は将来の拡張候補であり、2026-09-02 時点で実装されていない。**
> 実装済みの統制として扱わないこと。将来 VPC 化する際の設計意図として記載を残す。

- Private Subnet 内に Lambda を配置
- NAT Gateway 経由で外部 API へ接続
- Security Group で通信制限

**VPC 化を判断する際の材料**

VPC なし構成のトレードオフ:

| | VPC なし（現行） | VPC + NAT（将来構想） |
|---|---|---|
| アウトバウンドの記録・追跡 | VPC Flow Logs がなく**追跡不可** | Flow Logs で追跡可能 |
| egress の宛先制限 | **なし**（侵害時のデータ持ち出し経路が無制御） | Security Group / NAT で宛先を限定可能 |
| 常時コスト | NAT Gateway 課金なし | NAT Gateway の時間課金が発生 |
| Lambda コールドスタート | ENI 割り当てなし | ENI 割り当て分の増加 |

**外部インターネットへ能動的に通信する処理を追加する場合は、この構成の是非を先に判断すること。**
（例: 外部 API からのデータ取り込み。→ issue #79）

### IP 制限

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
