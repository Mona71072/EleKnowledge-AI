# AWS 権限調査レポート — `datautl-bple-mebs` / `datautl-bple-mebs-gyoumu012` プロファイル

> 調査日: 2026-06-04  
> アカウント ID: `<DEV_ACCOUNT_ID>`（実際の値は各自のローカル設定・AWS コンソールで確認する）  
> リージョン: `ap-northeast-1`（東京）

---

## 1. 呼び出し元 ID

| 項目 | 値 |
|------|-----|
| UserId | `AROA2UMKUUBNZM2FCI5OR:itai-yu` |
| Account | `<DEV_ACCOUNT_ID>`（実際の値は各自のローカル設定・AWS コンソールで確認する） |
| ARN | `arn:aws:sts::<DEV_ACCOUNT_ID>:assumed-role/AWSReservedSSO_datautl-bple-mebs_16773c9fde39ceeb/itai-yu` |
| 認証方式 | AWS SSO (SAML フェデレーション) |
| セッション最大時間 | 43,200 秒（12 時間） |

---

## 2. アタッチされたポリシー（3 件）

### 2-1. `AdministratorAccess`（AWS 管理ポリシー）

```json
{ "Effect": "Allow", "Action": "*", "Resource": "*" }
```

**意味**: 全 AWS サービス・全リソースへのフル権限。  
ただし後述の IP 制限ポリシー（Deny）が上書きするため、**許可リスト外 IP からは実質的に全操作不可**。

---

### 2-2. `datautl-prd-security-iam-policy-bple-mebs`（カスタム）

```json
{ "Effect": "Allow", "NotAction": "*", "Resource": "*" }
```

**意味**: `NotAction: "*"` = 「全アクション以外を許可」→ 実質 **何も許可しない**（ノーオプポリシー）。  
`AdministratorAccess` に対して追加・削減ともに影響なし。冗長ポリシー。

---

### 2-3. `datautl-prd-security-iam-policy-share`（カスタム・Deny）

```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "NotIpAddress": { "aws:SourceIp": [ ... ] },
    "Bool": { "aws:ViaAWSService": "false" },
    "StringNotLike": { "aws:userAgent": "*exec-env/CloudShell*" }
  }
}
```

**意味**: 以下をすべて満たす場合、全操作を **Deny（明示的拒否）**:

- リクエスト元 IP が許可リストに含まれない
- かつ AWS サービス経由ではない（`ViaAWSService: false`）
- かつ CloudShell からではない

#### 許可 IP リスト

| CIDR / IP | 備考 |
|-----------|------|
| `27.0.3.144/28` | 16 アドレス |
| `15.248.5.4/32` | |
| `39.110.205.170/32` | |
| `133.165.186.43/32` | |
| `219.166.164.110/32` | |
| `210.143.35.0/26` | 64 アドレス |
| `192.218.140.236/32` ～ `192.218.140.241/32` | 6 アドレス |
| `210.172.233.198/32` | |
| `210.172.233.219/32` | |
| `210.172.233.220/32` | |
| `203.178.81.200/32` | |
| `118.238.4.182/32` | |
| `123.253.152.1/32` | |
| `140.82.207.28/32` | |
| `150.195.209.132/32` | |

#### 調査時の自 IP

| 項目 | 値 | 許可リスト該当 |
|------|-----|--------------|
| 現在の Public IP | `192.218.140.240` | ✅ 該当 |

**→ 調査時点では IP 制限を通過しており、AdministratorAccess の全権限が有効。**

---

## 3. 実効権限まとめ

```
AdministratorAccess（Allow: *）
  ↕
datautl-prd-security-iam-policy-share（条件付き Deny: *）
```

| 接続元 | 実効権限 |
|--------|---------|
| 許可 IP からの直接アクセス | **全サービス・全リソースに対してフルアクセス** |
| 許可 IP 外からの直接アクセス | **全操作が Deny（実質アクセス不能）** |
| AWS サービス経由（Lambda 実行等） | 制限なし（ViaAWSService 条件が除外） |
| CloudShell からのアクセス | 制限なし（CloudShell 条件が除外） |

---

## 4. 東京リージョン（ap-northeast-1）の既存リソース

### 4-1. S3 バケット（24 件）

| バケット名 | 用途 |
|-----------|------|
| `aws-glue-libs-<DEV_ACCOUNT_ID>-ap-northeast-1` | Glue ライブラリ |
| `cdk-hnb659fds-assets-<DEV_ACCOUNT_ID>-ap-northeast-1` | CDK アセット（東京） |
| `cdk-hnb659fds-assets-<DEV_ACCOUNT_ID>-us-east-1` | CDK アセット（バージニア） |
| `chat-history-data-inst-<DEV_ACCOUNT_ID>-ap-northeast-1` | チャット履歴 |
| `codepipeline-ap-northeast-1-*` | CodePipeline アーティファクト |
| `datautl-prd-gyoumu012-apne1-s3-bucket-accesslog` | アクセスログ（gyoumu012） |
| `datautl-prd-gyoumu012-apne1-s3-bucket-cloudformation` | CloudFormation テンプレート |
| `datautl-prd-gyoumu012-apne1-s3-bucket-waflog` | WAF ログ |
| `datautl-prd-gyoumu012-usea1-s3-bucket-cloudformation` | CloudFormation（バージニア） |
| `generativeaiusecasesstack-*` | GenAI ユースケース各種 |
| `meta-info-extract-inst-*` | メタ情報抽出 |
| `rag-data-source-inst-*` | RAG データソース（複数） |
| `ragknowledgebasestackinst-*` | RAG ナレッジベース |
| `ti-bucket-inst-*` | TI データ |
| `videotmpbucketstackinstdap-*` | 動画一時バケット |

### 4-2. Lambda 関数（19 件）

| 関数名 | 概要 |
|--------|------|
| `ModelTypeExtract-INST` | モデル種別抽出 |
| `MetaInfoExtract-INST` | メタ情報抽出 |
| `KeywordExtract-INST` | キーワード抽出 |
| `S3IncrementalCopy-INST` | S3 差分コピー |
| `deploy-MAI-Box-INST` | MAI Box デプロイ |
| `GenerativeAiUseCasesStack-*` | GenAI ユースケース群 |
| `RagKnowledgeBaseStackINST-*` | RAG ナレッジベース関連 |
| `VideoTmpBucketStackINSTDa-*` | 動画処理 |

### 4-3. CloudFormation スタック（15 件）

| スタック名 | ステータス |
|-----------|-----------|
| `GenerativeAiUseCasesStackINSTD` | UPDATE_COMPLETE |
| `RagKnowledgeBaseStackINSTD` | CREATE_COMPLETE |
| `VideoTmpBucketStackINSTDap-northeast-1` | CREATE_COMPLETE |
| `CDKToolkit` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-EventbridgeStack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-TmpS3Stack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-LibS3Stack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-SecretsmanagerStack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-BackupStack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-SnsStack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-LogS3Stack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-AthenaStack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-WafStack-*` | CREATE_COMPLETE |
| `datautl-prd-gyoumu012-stack-KmsStack-*` | CREATE_COMPLETE |

### 4-4. Bedrock

| 項目 | 内容 |
|------|------|
| ナレッジベース | 3 件（ACTIVE） |
| | `generative-ai-use-cases-jpinstd` |
| | `rag-data-source-for-mai-box-inst-markdown` |
| | `generative-ai-use-cases-jp-inst-fmp` |
| 利用可能モデル（主要） | Claude Sonnet 4.6 / Claude Opus 4.7/4.8 / Claude Haiku 4.5 等 |

### 4-5. その他リソース

| サービス | リソース |
|---------|---------|
| **Athena** | ワークグループ 2 件（`datautl-prd-gyoumu012-wg`, `primary`） |
| **KMS** | カスタマー管理キー 4 件 |
| **Secrets Manager** | `datautl-prd-gyoumu012-secretsmanager-001`（1 件） |
| **SNS** | トピック 3 件（`datautl-prd-gyoumu012-sns-001/002/003`） |
| **EventBridge** | ルール 4 件（backup-rule: DISABLED, health-rule: ENABLED, securityhub-rule: ENABLED, codepipeline: DISABLED） |
| **AWS Backup** | Vault 2 件（日次・半年 EC2 バックアップ用） |
| **WAFv2** | WebACL 2 件（GenAI 用 + gyoumu012 用） |
| **EC2** | インスタンスなし |
| **Glue** | ジョブなし（ライブラリ用 S3 のみ） |
| **CloudWatch Alarms** | なし（現時点） |

---

## 5. `datautl-bple-mebs-gyoumu012` プロファイルとの比較

### 5-1. 基本情報

| 項目 | `datautl-bple-mebs` | `datautl-bple-mebs-gyoumu012` |
|------|---------------------|-------------------------------|
| UserId | `AROA2UMKUUBNZM2FCI5OR:itai-yu` | `AROA2UMKUUBNYJFODFIVJ:itai-yu` |
| ARN | `.../AWSReservedSSO_datautl-bple-mebs_.../itai-yu` | `.../AWSReservedSSO_datautl-bple-mebs-gyoumu012_.../itai-yu` |
| アカウント | `<DEV_ACCOUNT_ID>` | `<DEV_ACCOUNT_ID>`（同一） |
| セッション最大時間 | 43,200 秒 | 43,200 秒 |

### 5-2. ポリシー比較

| ポリシー | `mebs` | `mebs-gyoumu012` | 内容 |
|---------|--------|-----------------|------|
| `AdministratorAccess` | ✅ | ✅ | 全権限 |
| `datautl-prd-security-iam-policy-share` | ✅ | ✅ | IP 制限 Deny（共通） |
| `datautl-prd-security-iam-policy-bple-mebs` | ✅ | ❌ | `NotAction: "*"` → ノーオプ |
| `datautl-prd-security-iam-policy-bple-mebs-gyoumu012` | ❌ | ✅ | `NotAction: "*"` → ノーオプ |

### 5-3. アクセス可能リソースの比較

| サービス | `mebs` 件数 | `gyoumu012` 件数 | 差異 |
|---------|------------|----------------|------|
| S3 バケット | 24 | 24 | なし |
| Lambda 関数 | 19 | 19 | なし |
| CloudFormation スタック | 15 | 15 | なし |

### 5-4. 結論：両プロファイルの実効権限は同一

```
同一アカウント (<DEV_ACCOUNT_ID>) 上の異なる SSO ロール
  → AdministratorAccess（共通）
  → IP 制限 Deny（共通・同一ポリシー）
  → カスタムポリシーは名前違いのノーオプ（実質差なし）
```

**2 つのプロファイルで見えるリソースも操作できる内容も同一。**  
用途の使い分けは IAM ポリシーではなく **命名規則・運用規約レベル**で管理されている。

- `datautl-bple-mebs` → アカウント全体の管理・GenAI / RAG 系リソース操作
- `datautl-bple-mebs-gyoumu012` → `gyoumu012` サブシステム（datautl-prd-gyoumu012-stack 群）の操作に使用する運用上の慣習

---

## 6. 制限・注意事項

1. **IP ホワイトリスト必須**: 許可リスト外 IP（社外ネット等）からは全操作が Deny される。VPN 接続または社内ネットワーク経由が必須。
2. **セッショントークン有効期限**: `aws_session_token` は一時クレデンシャル。有効期限（最大 12 時間）後は再認証が必要。
3. **Organizations SCP**: 管理アカウント（`<ORG_MANAGEMENT_ACCOUNT_ID>`）レベルで SCP が適用されている可能性があるが、メンバーアカウントからは確認不可。
4. **グローバルリソース**: IAM はグローバルサービスのため、`--region` 指定不要。
5. **Athena データベース**: `datautl-prd-gyoumu012-wg` ワークグループに紐づくデータベースは現時点で未作成（空）。

---

## 7. 移行作業に向けた確認事項

- [x] IAM 権限: AdministratorAccess あり → CDK デプロイ・リソース作成・削除すべて可能
- [x] 東京リージョン: S3 / Lambda / Bedrock / Athena / KMS 等の主要インフラ確認済み
- [x] IP 制限: 現在の接続 IP（`192.218.140.240`）は許可リスト内
- [x] `datautl-bple-mebs-gyoumu012` プロファイルの権限調査完了 → `mebs` と実効権限は同一
- [ ] VPC / サブネット構成の確認（EC2 未使用のため現時点では不要の可能性あり）
- [ ] Organizations SCP の内容確認（管理アカウント権限保有者に問い合わせ）
- [ ] Cross-account アクセスが必要な場合は AssumeRole 設定を確認
