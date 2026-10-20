---
status: development
last-verified: 2026-10-15
related-code: scripts/ops/apply_cost_allocation_tags.py, infrastructure/sam/
---

# コスト配分タグのリソース別台帳

## この台帳の位置づけ

2026-10-15のAWSタグ反映後に再読取で検証した104件を、検証結果と計画の一致を確認して一覧化した。対象は東京（`ap-northeast-1`）。本書作成時にAWSへ再照会・変更はしていないため、以後の変更を自動的に反映する一覧ではない。全AWSリソースや請求明細を網羅する台帳でもない。

タグの定義・分類基準・承諾記録・有効化依頼の正本は [コスト配分タグの運用](ops-cost-allocation-tags.md)。本書はその定義を適用したリソース別の確認記録であり、運用ルールを重複定義しない。

## 表の読み方と証拠

- **全104件共通:** `gyoumu012Project=ele-knowledge`。
- 各表の `Component` は `gyoumu012Component`、`Usage` は `gyoumu012Usage` の実際に検証した値を表す。旧タグを含む全タグ一覧ではない。
- 台帳IDはARNのSHA-256先頭12桁から作成した識別子。AWSのリソースIDではない。リソース再作成でARNが変われば台帳IDも変わる。
- アカウントID・完全なARN・生成IDは共有版に載せない。`<account-id>` / `<generated-suffix>` は表示上の置換であり、AWS名を変更したものではない。API・KB等は用途名・論理IDで表示する。
- 正確なARNとの対応はローカルの未追跡 `eval-results/cost-tags/final-plan.json`、検証成功と既存タグ保持は `final-plan-results.json` で照合する。これらは内部情報を含むためGitへ追加しない。別端末の担当者はAWSから再取得する。
- 「スタックタグ」は計画に保存されたCloudFormation由来タグによる所有根拠。コードへのリンクは管理元の参照であり、今回そのテンプレートをAWSへデプロイ済みという意味ではない。管理元が確認できないものはその旨を残す。

## 分類別の件数

| Component | 件数 | Usage |
|---|---:|---|
| `rag` | 9 | `shared` |
| `legal-rag` | 2 | `development` |
| `monitoring` | 38 | `shared` |
| `shared` | 35 | `shared` |
| `troubleshooting` | 12 | `development` |
| `announcements` | 8 | `shared` |

合計104件。Usage別は `shared` 90件、`development` 14件、`user` 0件。件数はリソース数であり、費用の割合ではない。

## rag

通常RAGの処理・資料・検索設定・専用ログ。既存推論プロファイルも分類するが、現在の生成推論費がそこへ帰属するとは扱わない。

| 台帳ID | サービス | リソース識別名 | Component | Usage | 管理元・分類根拠 |
|---|---|---|---|---|---|
| `CT-953ee78fb599` | API Gateway | `rag-api-dev / REST API` | `rag` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `RagApi`（スタックタグ） |
| `CT-ee976b7724fb` | API Gateway | `rag-api-dev / stage: dev` | `rag` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `RagApiStage`（スタックタグ） |
| `CT-cee204a7cdac` | Bedrock | `EleKnowledge-rag-dev-sonnet5-20260909（推論プロファイル・現在の生成経路は未使用）` | `rag` | `shared` | 既存推論プロファイル / AWS名とProjectタグを確認（管理テンプレート未収録） |
| `CT-08cf3cbafaca` | Lambda | `rag-dev` | `rag` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `RagFunction`（スタックタグ） |
| `CT-9efa515a5181` | CloudWatch Logs | `/aws/apigateway/rag-api-dev` | `rag` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `RagApiLogGroup`（スタックタグ） |
| `CT-ea7712fdc983` | CloudWatch Logs | `/aws/lambda/rag-dev` | `rag` | `shared` | Lambdaのログ / [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `RagFunction`（スタックタグ） |
| `CT-67abc58911bc` | CloudWatch Logs | `API実行ログ / rag-api-dev / dev` | `rag` | `shared` | API実行ログ / [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `RagApi`（スタックタグ） |
| `CT-30ae96e0f77e` | S3 | `documents-dev-<account-id>` | `rag` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `DocumentsBucket`（スタックタグ） |
| `CT-1836bbef9e70` | SSM Parameter | `/eleknowledge/dev/knowledge-base-id` | `rag` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `KnowledgeBaseIdParameter`（スタックタグ） |

## legal-rag

法令専用Knowledge Baseと法令資料バケット。ユーザーが確認したPoC開発専用の分類。

| 台帳ID | サービス | リソース識別名 | Component | Usage | 管理元・分類根拠 |
|---|---|---|---|---|---|
| `CT-f6be3f4015bc` | Bedrock | `法令専用Knowledge Base（LawKnowledgeBase）` | `legal-rag` | `development` | `eleknowledge-law-kb-dev` / `LawKnowledgeBase`（既存スタック。テンプレート未収録） |
| `CT-dce860505ef1` | S3 | `eleknowledge-legal-rag-dev-lawdatabucket-<generated-suffix>` | `legal-rag` | `development` | 法令専用保持バケット / 旧Project値・役割を確認（管理テンプレート未収録） |

## monitoring

監視アラーム、集計処理、分析保存先。監視対象がRAGやPoCでも、リソース自身の役割で監視に分類する。

| 台帳ID | サービス | リソース識別名 | Component | Usage | 管理元・分類根拠 |
|---|---|---|---|---|---|
| `CT-8c3c9079a3d7` | Athena | `eleknowledge-analytics-dev` | `monitoring` | `shared` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-d8dbecbdaf32` | CloudWatch Alarm | `EleKnowledge-dev-P1-amplify-5xx` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `AmplifyHosting5xxAlarm`（スタックタグ） |
| `CT-3f0fe775a656` | CloudWatch Alarm | `EleKnowledge-dev-P1-app-api-5xx` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `AppApi5xxAlarm`（スタックタグ） |
| `CT-19093f66c480` | CloudWatch Alarm | `EleKnowledge-dev-P1-auth-api-5xx` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `AuthApi5xxAlarm`（スタックタグ） |
| `CT-1dcafd91a424` | CloudWatch Alarm | `EleKnowledge-dev-P1-chat-api-5xx` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `ChatApi5xxAlarm`（スタックタグ） |
| `CT-3682fa883895` | CloudWatch Alarm | `EleKnowledge-dev-P1-chat-archive-errors` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `ArchiveErrorsAlarm`（スタックタグ） |
| `CT-7aa8a4b15e1f` | CloudWatch Alarm | `EleKnowledge-dev-P1-chat-error-lines` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `ChatErrorLinesAlarm`（スタックタグ） |
| `CT-5c42e961a777` | CloudWatch Alarm | `EleKnowledge-dev-P1-chat-throttles` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `ChatThrottlesAlarm`（スタックタグ） |
| `CT-ad83afa29799` | CloudWatch Alarm | `EleKnowledge-dev-P1-cognito-email-errors` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `CognitoEmailErrorAlarm`（スタックタグ） |
| `CT-0e36090dd96b` | CloudWatch Alarm | `EleKnowledge-dev-P1-cognito-signups-45-per-day` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `CognitoSignups45Alarm`（スタックタグ） |
| `CT-48fa57c6fed7` | CloudWatch Alarm | `EleKnowledge-dev-P1-cognito-signups-50-per-day` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `CognitoSignups50Alarm`（スタックタグ） |
| `CT-df5d9ac11632` | CloudWatch Alarm | `EleKnowledge-dev-P1-login-throttles` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `LoginThrottlesAlarm`（スタックタグ） |
| `CT-7b03428618b4` | CloudWatch Alarm | `EleKnowledge-dev-P1-rag-api-5xx` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `RagApi5xxAlarm`（スタックタグ） |
| `CT-25dc2d8742e9` | CloudWatch Alarm | `EleKnowledge-dev-P1-rag-duration-max` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `RagDurationMaxAlarm`（スタックタグ） |
| `CT-4545a3a57dfd` | CloudWatch Alarm | `EleKnowledge-dev-P1-rag-error-lines` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `RagErrorLinesAlarm`（スタックタグ） |
| `CT-5cc8e8d48849` | CloudWatch Alarm | `EleKnowledge-dev-P1-rag-throttles` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `RagThrottlesAlarm`（スタックタグ） |
| `CT-7280c2b91250` | CloudWatch Alarm | `EleKnowledge-dev-P1-troubleshooting-api-5xx` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `TroubleshootingApi5xxAlarm`（スタックタグ） |
| `CT-4e4813d90f5b` | CloudWatch Alarm | `EleKnowledge-dev-P2-announcements-publisher-errors` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `AnnouncementsPublisherErrorsAlarm`（スタックタグ） |
| `CT-698c75ef5db1` | CloudWatch Alarm | `EleKnowledge-dev-P2-auth-api-4xx-spike` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `AuthApi4xxSpikeAlarm`（スタックタグ） |
| `CT-0d1e8add718e` | CloudWatch Alarm | `EleKnowledge-dev-P2-chat-api-4xx-spike` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `ChatApi4xxSpikeAlarm`（スタックタグ） |
| `CT-2372aa8cdce7` | CloudWatch Alarm | `EleKnowledge-dev-P2-chatlogs-read-throttle` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `ChatLogsReadThrottleAlarm`（スタックタグ） |
| `CT-5f84153ca8fc` | CloudWatch Alarm | `EleKnowledge-dev-P2-chatlogs-write-throttle` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `ChatLogsWriteThrottleAlarm`（スタックタグ） |
| `CT-e1cba96abfd0` | CloudWatch Alarm | `EleKnowledge-dev-P2-cognito-signups-40-per-day` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `CognitoSignups40Alarm`（スタックタグ） |
| `CT-70c19914a0c4` | CloudWatch Alarm | `EleKnowledge-dev-P2-metrics-aggregator-errors` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `MetricsAggregatorErrorsAlarm`（スタックタグ） |
| `CT-0dbe4c9b118f` | CloudWatch Alarm | `EleKnowledge-dev-P2-metrics-schedule-failed` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `MetricsScheduleFailedAlarm`（スタックタグ） |
| `CT-22881c9a95cf` | CloudWatch Alarm | `EleKnowledge-dev-P2-rag-api-4xx-spike` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `RagApi4xxSpikeAlarm`（スタックタグ） |
| `CT-ace4551f9031` | CloudWatch Alarm | `EleKnowledge-dev-P2-rag-duration-p90` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `RagDurationP90Alarm`（スタックタグ） |
| `CT-d55cedae8f40` | CloudWatch Alarm | `EleKnowledge-dev-P2-sessions-write-throttle` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `SessionsWriteThrottleAlarm`（スタックタグ） |
| `CT-e14286fd5f59` | DynamoDB | `metrics-dev` | `monitoring` | `shared` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-ca647719a5b7` | EventBridge | `EleKnowledge-dev-cognito-email-errors` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `CognitoEmailErrorRule`（スタックタグ） |
| `CT-fc77bfdb45c3` | EventBridge | `metrics-daily-agg-dev` | `monitoring` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `MetricsAggregatorFunctionDailySchedule`（スタックタグ） |
| `CT-645da6733d12` | EventBridge | `metrics-hourly-agg-dev` | `monitoring` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `MetricsAggregatorFunctionHourlySchedule`（スタックタグ） |
| `CT-b2b76c6aa3c9` | Lambda | `metrics-aggregator-dev` | `monitoring` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `MetricsAggregatorFunction`（スタックタグ） |
| `CT-e514abd52e62` | Lambda | `metrics-read-dev` | `monitoring` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `MetricsReadFunction`（スタックタグ） |
| `CT-5d3aaeffe11d` | CloudWatch Logs | `/aws/lambda/metrics-aggregator-dev` | `monitoring` | `shared` | Lambdaのログ / [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `MetricsAggregatorFunction`（スタックタグ） |
| `CT-0445c6b3f0b3` | CloudWatch Logs | `/aws/lambda/metrics-read-dev` | `monitoring` | `shared` | Lambdaのログ / [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `MetricsReadFunction`（スタックタグ） |
| `CT-e308df06c379` | S3 | `eleknowledge-athena-results-dev-<account-id>` | `monitoring` | `shared` | [chat-archive-template.yaml](../infrastructure/sam/chat-archive-template.yaml) / `AthenaResultsBucket`（スタックタグ） |
| `CT-4393f3a96408` | SNS | `eleknowledge-alerts-dev` | `monitoring` | `shared` | [monitoring-template.yaml](../infrastructure/sam/monitoring-template.yaml) / `AlertTopic`（スタックタグ） |

## shared

認証・画面・チャット履歴・共通API・配布資材などの共通基盤。開発とユーザー利用の内訳はこのタグだけでは分離しない。

| 台帳ID | サービス | リソース識別名 | Component | Usage | 管理元・分類根拠 |
|---|---|---|---|---|---|
| `CT-edcf1bb2d324` | Amplify | `Ele-Knowledgeフロントエンド（対象アプリ1件）` | `shared` | `shared` | Amplify管理 / 旧Projectタグを確認 |
| `CT-24b22e3358ee` | API Gateway | `announcements-monitoring-api-dev / REST API` | `shared` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AppApi`（スタックタグ） |
| `CT-ef50008be607` | API Gateway | `announcements-monitoring-api-dev / stage: dev` | `shared` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AppApiStage`（スタックタグ） |
| `CT-d28f1f6949f5` | API Gateway | `auth-api-dev / REST API` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `AuthApi`（スタックタグ） |
| `CT-58acdd1a9897` | API Gateway | `auth-api-dev / stage: dev` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `AuthApiStage`（スタックタグ） |
| `CT-e703bb8d253c` | API Gateway | `chat-api-dev / REST API` | `shared` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `ChatApi`（スタックタグ） |
| `CT-bbb7207a6824` | API Gateway | `chat-api-dev / stage: dev` | `shared` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `ChatApiStage`（スタックタグ） |
| `CT-69102cb75ff3` | Cognito | `users-dev (CognitoUserPool)` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `CognitoUserPool`（スタックタグ） |
| `CT-69fd2425c3ce` | DynamoDB | `chatlogs-dev` | `shared` | `shared` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-5b7e07806bf8` | DynamoDB | `users-dev` | `shared` | `shared` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-4c0196628893` | EventBridge | `eleknowledge-chat-archive-dev-failure-notification` | `shared` | `shared` | [chat-archive-template.yaml](../infrastructure/sam/chat-archive-template.yaml) / `ArchiveFailureEventRule`（スタックタグ） |
| `CT-057cc09fffc2` | Lambda | `ArchiveFunctionChatLogsStream（イベントソースマッピング）` | `shared` | `shared` | [chat-archive-template.yaml](../infrastructure/sam/chat-archive-template.yaml) / `ArchiveFunctionChatLogsStream`（スタックタグ） |
| `CT-56369ee16973` | Lambda | `EleKnowledge-dev-phase1-DomainGuardFunction-<generated-suffix>` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `DomainGuardFunction`（スタックタグ） |
| `CT-55919acdcc76` | Lambda | `chat-dev` | `shared` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `ChatManagementFunction`（スタックタグ） |
| `CT-736a27bb8d2a` | Lambda | `eleknowledge-chat-archive-dev` | `shared` | `shared` | [chat-archive-template.yaml](../infrastructure/sam/chat-archive-template.yaml) / `ArchiveFunction`（スタックタグ） |
| `CT-dbfbce728844` | Lambda | `login-dev` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `LoginFunction`（スタックタグ） |
| `CT-7dcfd86a0862` | Lambda | `signup-dev` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `SignupFunction`（スタックタグ） |
| `CT-909362d20cdd` | Lambda | `verify-dev` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `VerifyFunction`（スタックタグ） |
| `CT-634d814f44d8` | CloudWatch Logs | `/aws/apigateway/announcements-monitoring-api-dev` | `shared` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AppApiLogGroup`（スタックタグ） |
| `CT-1a15aede2494` | CloudWatch Logs | `/aws/apigateway/auth-api-dev` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `ApiGatewayLogGroup`（スタックタグ） |
| `CT-cd5740f250be` | CloudWatch Logs | `/aws/apigateway/chat-api-dev` | `shared` | `shared` | [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `ChatApiLogGroup`（スタックタグ） |
| `CT-78115c6d9e1e` | CloudWatch Logs | `/aws/lambda/EleKnowledge-dev-phase1-DomainGuardFunction-<generated-suffix>` | `shared` | `shared` | Lambdaのログ / [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `DomainGuardFunction`（スタックタグ） |
| `CT-bd17e92448dc` | CloudWatch Logs | `/aws/lambda/chat-dev` | `shared` | `shared` | Lambdaのログ / [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `ChatManagementFunction`（スタックタグ） |
| `CT-24cad6a00566` | CloudWatch Logs | `/aws/lambda/eleknowledge-chat-archive-dev` | `shared` | `shared` | Lambdaのログ / [chat-archive-template.yaml](../infrastructure/sam/chat-archive-template.yaml) / `ArchiveFunction`（スタックタグ） |
| `CT-53978b16ad91` | CloudWatch Logs | `/aws/lambda/eleknowledge-cognito-domain-guard-dev` | `shared` | `shared` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-9fdefb6e947c` | CloudWatch Logs | `/aws/lambda/login-dev` | `shared` | `shared` | Lambdaのログ / [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `LoginFunction`（スタックタグ） |
| `CT-13c46e70e27c` | CloudWatch Logs | `API実行ログ / announcements-monitoring-api-dev / dev` | `shared` | `shared` | API実行ログ / [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AppApi`（スタックタグ） |
| `CT-b9f224e17792` | CloudWatch Logs | `API実行ログ / auth-api-dev / dev` | `shared` | `shared` | API実行ログ / [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `AuthApi`（スタックタグ） |
| `CT-7be3fe80dea8` | CloudWatch Logs | `API実行ログ / chat-api-dev / dev` | `shared` | `shared` | API実行ログ / [phase2-template.yaml](../infrastructure/sam/phase2-template.yaml) / `ChatApi`（スタックタグ） |
| `CT-51892927fa92` | S3 | `eleknowledge-chat-archive-dev-<account-id>` | `shared` | `shared` | [chat-archive-template.yaml](../infrastructure/sam/chat-archive-template.yaml) / `ArchiveBucket`（スタックタグ） |
| `CT-3081e48f127f` | S3 | `eleknowledge-sam-artifacts-dev-<account-id>-ap-northeast-1` | `shared` | `shared` | 作業時の配布設定と所有アカウントを照合。現在は[共有設定例](../infrastructure/sam/samconfig-monitoring.example.toml)から未追跡ローカル設定を作成 |
| `CT-03382a58c764` | S3 | `uploads-dev-<account-id>` | `shared` | `shared` | [phase1-template.yaml](../infrastructure/sam/phase1-template.yaml) / `UploadsBucket`（スタックタグ） |
| `CT-49f4cd26a408` | SSM Parameter | `/eleknowledge/dev/bedrock-unit-price` | `shared` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `BedrockUnitPriceParameter`（スタックタグ） |
| `CT-3b52844a1518` | WAFv2 | `ipset` | `shared` | `shared` | [security-waf-template.yaml](../infrastructure/sam/security-waf-template.yaml) / `AllowedIPSet`（スタックタグ） |
| `CT-363e25e59788` | WAFv2 | `webacl` | `shared` | `shared` | [security-waf-template.yaml](../infrastructure/sam/security-waf-template.yaml) / `RegionalWebAcl`（スタックタグ） |

## troubleshooting

トラブルシューティングの処理・API・専用テーブル・Agent参照設定。ユーザーが確認したPoC開発専用の分類。

| 台帳ID | サービス | リソース識別名 | Component | Usage | 管理元・分類根拠 |
|---|---|---|---|---|---|
| `CT-2d8f964fc7af` | API Gateway | `troubleshooting-api-dev / REST API` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `TroubleshootingApi`（スタックタグ） |
| `CT-6c76c3457cd6` | API Gateway | `troubleshooting-api-dev / stage: dev` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `TroubleshootingApiStage`（スタックタグ） |
| `CT-fe5066fc21d5` | DynamoDB | `sessions-dev` | `troubleshooting` | `development` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-93fdb90c9d53` | DynamoDB | `sites-dev` | `troubleshooting` | `development` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-54be4018a900` | Lambda | `db-search-dev` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `DBSearchFunction`（スタックタグ） |
| `CT-05a69df71b54` | Lambda | `history-dev` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `HistoryFunction`（スタックタグ） |
| `CT-a9085572577f` | Lambda | `kb-search-cases-dev` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `KBSearch1Function`（スタックタグ） |
| `CT-9365062ac9b3` | Lambda | `kb-search-manuals-dev` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `KBSearch2Function`（スタックタグ） |
| `CT-15ae812aa4ee` | Lambda | `kb-search-materials-dev` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `KBSearch3Function`（スタックタグ） |
| `CT-0dba1cbd7bb7` | Lambda | `orchestrator-dev` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `OrchestratorFunction`（スタックタグ） |
| `CT-72cd07da347d` | SSM Parameter | `/eleknowledge/dev/agent-alias-id` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `AgentAliasIdParameter`（スタックタグ） |
| `CT-5abe97131bce` | SSM Parameter | `/eleknowledge/dev/agent-id` | `troubleshooting` | `development` | [phase3-template.yaml](../infrastructure/sam/phase3-template.yaml) / `AgentIdParameter`（スタックタグ） |

## announcements

お知らせの保存・公開・読取・更新と専用ログ。監視との共用APIはshared表に記載する。

| 台帳ID | サービス | リソース識別名 | Component | Usage | 管理元・分類根拠 |
|---|---|---|---|---|---|
| `CT-6f3e2fe0d686` | DynamoDB | `announcements-dev` | `announcements` | `shared` | 既存リソース / 名前・役割・旧Projectタグで分類（管理スタック未確認） |
| `CT-d685353e1cd5` | EventBridge | `announcements-promote-dev` | `announcements` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AnnouncementsPublisherFunctionEveryFiveMinutes`（スタックタグ） |
| `CT-c71dfec39ae4` | Lambda | `announcements-publisher-dev` | `announcements` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AnnouncementsPublisherFunction`（スタックタグ） |
| `CT-4445a6142e11` | Lambda | `announcements-read-dev` | `announcements` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AnnouncementsReadFunction`（スタックタグ） |
| `CT-cadeb59fce3c` | Lambda | `announcements-write-dev` | `announcements` | `shared` | [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AnnouncementsWriteFunction`（スタックタグ） |
| `CT-6871aa359525` | CloudWatch Logs | `/aws/lambda/announcements-publisher-dev` | `announcements` | `shared` | Lambdaのログ / [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AnnouncementsPublisherFunction`（スタックタグ） |
| `CT-9a28b4e5cf49` | CloudWatch Logs | `/aws/lambda/announcements-read-dev` | `announcements` | `shared` | Lambdaのログ / [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AnnouncementsReadFunction`（スタックタグ） |
| `CT-71cb99ca2bb8` | CloudWatch Logs | `/aws/lambda/announcements-write-dev` | `announcements` | `shared` | Lambdaのログ / [announcements-monitoring-template.yaml](../infrastructure/sam/announcements-monitoring-template.yaml) / `AnnouncementsWriteFunction`（スタックタグ） |

## 直接付与から除外した対象

| 対象 | 件数 | 扱い |
|---|---:|---|
| CloudFormationスタック本体 | 7 | 更新の誘発を避けて直接書込しない。スタックタグは通常デプロイで反映 |
| DynamoDB Stream | 2 | 親テーブル側のタグで扱う。台帳の独立付与件数には含めない |
| AWS Budgetsの予算メタデータ | 1 | 今回のリソース費分類の直接付与対象外 |

外部所有の共有KB・S3・検索基盤は、他システムへの影響と配賦方法が未確認のため対象外。IAM等の非課金メタデータも網羅していない。

## 更新・差分確認の手順

1. デプロイ後と月次に、運用文書の手順でAWSの計画・検証結果を新しいファイル名で取得する。失敗・未検証行を確認済みとして台帳へ取り込まない。
2. ARN由来の台帳IDで前回と比較し、追加・削除・タグ値変更・管理元変更を確認する。AWSで見つからないだけで廃止と判断せず、取得範囲や権限も確認する。
3. 新規・共用・管理元不明のリソースは分類根拠を確認する。分類を変える場合は合意内容を運用文書へ記録してからAWSとIaCを更新する。
4. 検証済みのタグ値、件数、管理元を本書へ反映し、104件という初期件数を固定値として使い続けない。検証日も実際の確認範囲に従って更新する。
5. 全表を再検証したときだけfrontmatterの日付を更新する。一部の確認では該当節へ検証マーカーを置き、文書全体の日付を進めない。

管理部門によるコスト配分タグ有効化と請求への反映は、リソースタグ検証とは別に確認する。管理元未確認の項目は、所有スタックの実査等で根拠が得られた時点で補完する。
