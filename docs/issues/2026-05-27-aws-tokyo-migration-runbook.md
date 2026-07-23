# AWS東京リージョン移行作業の歩き方に沿って新環境を構築する

## 背景

AWS環境を新アカウントの東京リージョン（`ap-northeast-1`）へ移行するため、事前準備としてIaC・命名規則・リソース一覧・移行ランブックを整備した。

今回の移行では、旧環境のような `EleKnowledge-AI-development-*` の冗長なリソース名を避け、プロジェクト識別はタグで行う。

- `Project=EleKnowledge`
- `Env=dev` / `Env=prd`
- `ManagedBy=SAM`

移行作業そのものは後日実施する。

## 参照ドキュメント

- `docs/aws-migration-runbook.md`
  - 移行作業の正規手順
  - Phase1 → Phase2 → Bedrock設定 → Phase3 → Amplify設定 → Smoke Test の順番を記載
- `docs/aws-resource-map.md`
  - リソース名、コンポーネント種別、用途、管理元テンプレートの一覧
- `docs/aws-migration-inventory.md`
  - 移行対象、移行対象外候補、後続入力値の整理

旧手順書は `us-east-1` / `EleKnowledge-AI-*` 前提が残るため、今回の移行では使わない。

## 移行作業の歩き方

1. 新AWSアカウントの作業用プロファイルを用意し、`ap-northeast-1` を対象リージョンにする。
2. Bedrockのモデルアクセスを東京リージョンで有効化する。
3. `sam validate` / `sam build` で Phase1/2/3 を検証する。
4. Phase1をデプロイし、Cognito、DynamoDB、S3、Auth APIを作成する。
5. Phase2を `KnowledgeBaseId=pending` でデプロイし、OpenSearch Serverless、RAG/Chat API、SSMを作成する。
6. Bedrock Knowledge Base / Agent を作成し、必要なIDを控える。
7. `/eleknowledge/dev/knowledge-base-id` を更新し、Phase2を実IDで再デプロイする。
8. Phase3を実ID付きでデプロイし、Troubleshooting APIと関連Lambdaを作成する。
9. Amplify環境変数をCloudFormation Outputsから設定し、再ビルドする。
10. Signup/Login、RAG、Troubleshooting、History、CloudWatch LogsをSmoke Testする。

## 受け入れ条件

- `docs/aws-migration-runbook.md` の手順に沿って新アカウントの `dev` 空環境を作成できる。
- CloudFormation OutputsとAmplify環境変数の対応が明確である。
- Bedrock Knowledge Base / Agent ID の反映手順が明確である。
- Smoke Test項目がすべて確認済みになる。
- 旧 `us-east-1` / `EleKnowledge-AI-*` 手順を使わずに移行できる。

## GitHub Issue

- https://github.com/yukiworkspace/EleKnowledge-AI/issues/20
