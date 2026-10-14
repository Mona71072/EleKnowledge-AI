---
status: draft
last-verified: 2026-08-21
related-code: infrastructure/sam/, amplify.yml
---

# AWS Resource Map

EleKnowledge resources are identified by tags, not by a shared name prefix:

- `Project=EleKnowledge`
- `Env=dev` or `Env=prd`
- `ManagedBy=SAM`

The names below use `dev` as the example environment. For production, replace `-dev` and `/dev/` with `-prd` and `/prd/`.

Use [AWS Migration Runbook](aws-migration-runbook.md) for deployment order, Bedrock ID updates, and Amplify environment variable setup.

## Development environment observation (2026-09-30)

> 最終検証: 2026-09-30 — AWS CLI 読み取り専用確認（東京リージョンの開発環境。通知到達と機能 E2E は未確認）

This is a time-bounded observation, not a guarantee of current state. The AWS environment and the current `origin/develop` templates did not match in every resource count.

| Area | AWS observation | `origin/develop` IaC / limitation |
| --- | --- | --- |
| Core and monitoring stacks | The Phase 1/2, troubleshooting, archive, monitoring, WAF, and announcements/metrics stacks were present and `UPDATE_COMPLETE`. | Stack presence does not prove that every user-facing flow is usable. |
| CloudWatch monitoring | The monitoring stack had 27 alarms and 6 saved Logs Insights queries. Across EleKnowledge alarms, 28 were `OK` with actions enabled. Two monitoring SNS email subscriptions were confirmed. | `monitoring-template.yaml` defines 26 alarms, 3 query definitions, and 2 metric filters. Resolve the stack/template difference before describing the deployed set as reproducible from `develop`. |
| Budget notification | A budget notification was present. | It is not defined in the current monitoring SAM template; notification delivery was not tested. |
| KPI aggregation | Daily and hourly EventBridge rules were enabled and targeted the aggregator. `metrics-dev` TTL was disabled. | `announcements-monitoring-template.yaml` defines only the daily schedule. The aggregator code processes the previous UTC day on each invocation; an enabled hourly rule does not mean hourly KPI aggregation is implemented. |
| WAF | The regional Web ACL and API associations were present. No EleKnowledge WAF log delivery, WAF alarm, or dedicated WAF notification topic was found. The single regional logging configuration was for another Web ACL. | `security-waf-template.yaml` defines S3 logging and WAF alarms/notifications, but those resources were absent from the deployed stack. Treat them as IaC-defined, not deployed. |
| Phase 3 | Troubleshooting stack, API, Lambda functions, and tables were present. | User-facing availability and end-to-end behavior were not verified. See the development specification and sequence document. |

These observations do not include delivery tests for SNS/Budget notifications or a user-facing E2E test. Do not copy account IDs, email addresses, or other secret values into this inventory.

## Phase 1 - Auth and Base Data

> 最終検証: 2026-10-04 — SAMテンプレートとLambdaのAWS API呼出しを照合（実環境未確認）

| Resource name | Component type | Purpose | Managed by |
| --- | --- | --- | --- |
| `users-dev` | Cognito User Pool | User authentication and account lifecycle | `phase1-template.yaml` |
| `users-dev-client` | Cognito User Pool Client | Frontend/client auth integration | `phase1-template.yaml` |
| `users-dev` | DynamoDB table | User profile records keyed by `userId` | `phase1-template.yaml` |
| `chatlogs-dev` | DynamoDB table | Chat sessions/messages with user timestamp GSI | `phase1-template.yaml` |
| `documents-dev-${AWS::AccountId}` | S3 bucket | Source documents for RAG and citations | `phase1-template.yaml` |
| `uploads-dev-${AWS::AccountId}` | S3 bucket | Temporary upload area | `phase1-template.yaml` |
| `auth-lambda-dev` | IAM role | signup: usersテーブルへの`PutItem` | `phase1-template.yaml` |
| `auth-login-lambda-dev` | IAM role | login: usersテーブルへの`UpdateItem` | `phase1-template.yaml` |
| `auth-verify-lambda-dev` | IAM role | verify: CloudWatch Logsのみ | `phase1-template.yaml` |
| `signup-dev` | Lambda function | User signup endpoint handler | `phase1-template.yaml` |
| `login-dev` | Lambda function | User login endpoint handler | `phase1-template.yaml` |
| `verify-dev` | Lambda function | Email verification endpoint handler | `phase1-template.yaml` |
| `auth-api-dev` | API Gateway REST API | `/auth/*` public auth API | `phase1-template.yaml` |
| `/aws/apigateway/auth-api-dev` | CloudWatch Logs log group | API Gateway access/execution logs | `phase1-template.yaml` |

## Phase 2 - RAG and Chat

> 最終検証: 2026-10-04 — SAMテンプレートとLambdaのAWS API呼出しを照合（実環境未確認）

| Resource name | Component type | Purpose | Managed by |
| --- | --- | --- | --- |
| `kb-dev` | OpenSearch Serverless collection | Vector storage backing Bedrock Knowledge Base | `phase2-template.yaml` |
| `kb-dev-enc` | OpenSearch Serverless encryption policy | Encryption policy for `kb-dev` | `phase2-template.yaml` |
| `kb-dev-net` | OpenSearch Serverless network policy | Network policy for `kb-dev` and dashboards | `phase2-template.yaml` |
| `kb-dev` | IAM role | Bedrock Knowledge Base access to S3/OpenSearch | `phase2-template.yaml` |
| `/eleknowledge/dev/knowledge-base-id` | SSM Parameter | Bedrock Knowledge Base ID placeholder/value | `phase2-template.yaml` |
| `rag-lambda-dev` | IAM role | RAG: Bedrock Retrieve/InvokeModel/Rerank、chatlogsの検索・書込み、対象S3のGetObject、非同期自己呼出し | `phase2-template.yaml` |
| `chat-lambda-dev` | IAM role | chat: chatlogsのQuery/Scan/書込み。GSIは`userId-timestamp-index`のみ | `phase2-template.yaml` |
| `rag-dev` | Lambda function | RAG query processing with Bedrock | `phase2-template.yaml` |
| `chat-dev` | Lambda function | Chat session/message management | `phase2-template.yaml` |
| `rag-api-dev` | API Gateway REST API | Authenticated RAG query API | `phase2-template.yaml` |
| `chat-api-dev` | API Gateway REST API | Authenticated chat management API | `phase2-template.yaml` |
| `/aws/apigateway/rag-api-dev` | CloudWatch Logs log group | RAG API Gateway logs | `phase2-template.yaml` |
| `/aws/apigateway/chat-api-dev` | CloudWatch Logs log group | Chat API Gateway logs | `phase2-template.yaml` |

## Phase 3 - Troubleshooting

| Resource name | Component type | Purpose | Managed by |
| --- | --- | --- | --- |
| `troubleshooting-lambda-dev` | IAM role | Shared execution role for troubleshooting Lambda functions | `phase3-template.yaml` |
| `sites-dev` | DynamoDB table | Site/equipment lookup keyed by `constructionNumber` | `phase3-template.yaml` |
| `sessions-dev` | DynamoDB table | Troubleshooting sessions with TTL and `userId-timestamp-index` | `phase3-template.yaml` |
| `orchestrator-dev` | Lambda function | Main troubleshooting orchestration and Bedrock Agent invocation | `phase3-template.yaml` |
| `db-search-dev` | Lambda function | Site database search helper | `phase3-template.yaml` |
| `kb-search-cases-dev` | Lambda function | Trouble case Knowledge Base search helper | `phase3-template.yaml` |
| `kb-search-manuals-dev` | Lambda function | Troubleshooting manual Knowledge Base search helper | `phase3-template.yaml` |
| `kb-search-materials-dev` | Lambda function | C-material Knowledge Base search helper | `phase3-template.yaml` |
| `history-dev` | Lambda function | Troubleshooting history read API handler | `phase3-template.yaml` |
| `troubleshooting-api-dev` | API Gateway REST API | Authenticated troubleshooting analyze/history API | `phase3-template.yaml` |
| `/eleknowledge/dev/agent-id` | SSM Parameter | Bedrock Agent ID placeholder/value | `phase3-template.yaml` |
| `/eleknowledge/dev/agent-alias-id` | SSM Parameter | Bedrock Agent Alias ID placeholder/value | `phase3-template.yaml` |

## Frontend and Deployment Settings

| Name | Component type | Purpose | Managed by |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_AWS_REGION` | Amplify environment variable | Frontend AWS region, default `ap-northeast-1` | `amplify.yml` |
| `NEXT_PUBLIC_API_URL` | Amplify environment variable | Auth API base URL from Phase 1 output | `amplify.yml` |
| `NEXT_PUBLIC_RAG_API_URL` | Amplify environment variable | RAG API base URL from Phase 2 output | `amplify.yml` |
| `NEXT_PUBLIC_CHAT_API_URL` | Amplify environment variable | Chat API base URL from Phase 2 output | `amplify.yml` |
| `NEXT_PUBLIC_TROUBLESHOOTING_API_URL` | Amplify environment variable | Troubleshooting API base URL from Phase 3 `TroubleshootingApiUrl`; frontend appends `/analyze` and `/history` | `amplify.yml` |
| `NEXT_PUBLIC_COGNITO_USER_POOL_ID` | Amplify environment variable | Cognito User Pool ID from Phase 1 output | `amplify.yml` |
| `NEXT_PUBLIC_COGNITO_CLIENT_ID` | Amplify environment variable | Cognito User Pool Client ID from Phase 1 output | `amplify.yml` |

## Additional Stacks (added 2026-07-21 to 2026-09-09)

> 最終検証: 2026-10-05 — develop の SAM 定義と 2026-09-30 AWS 読み取り専用観測記録を照合（WAF 関連付け数は実環境未確認）

| Stack | Template | Key resources |
|---|---|---|
| `announcements-monitoring-dev` | `infrastructure/sam/announcements-monitoring-template.yaml` | DynamoDB `announcements-dev`, `metrics-dev` (TTL disabled in the 2026-09-30 observation); Lambda `announcements-read/write/publisher-dev`, `metrics-read-dev`, `metrics-aggregator-dev`; API `announcements-monitoring-api-dev` (`GET /admin/metrics`, announcements routes); AWS had daily and hourly metrics rules enabled plus `announcements-promote-dev` (5 min). Current `develop` template defines only the daily metrics rule. |
| `eleknowledge-chat-archive-dev` | `infrastructure/sam/chat-archive-template.yaml` | Lambda `eleknowledge-chat-archive-dev` (chatlogs stream -> S3); S3 `eleknowledge-chat-archive-dev-<account>` (versioned; OnFailure invocation records), `eleknowledge-athena-results-dev-<account>`; EventBridge→SNS failure notification; Athena workgroup `eleknowledge-analytics-dev`; Glue `eleknowledge_analytics.chatlogs_archive` |
| `eleknowledge-security-waf-dev` | `infrastructure/sam/security-waf-template.yaml` | WAFv2 regional `EleKnowledge-dev-RegionalWebAcl` + IPSet. IaC defines associations with 5 REST API stages; the 2026-09-30 AWS observation confirmed API associations but did not establish their count. |
| `eleknowledge-monitoring-dev` | `infrastructure/sam/monitoring-template.yaml` | AWS observation: SNS `eleknowledge-alerts-dev` (2 confirmed email subscriptions), 27 CloudWatch alarms, 6 saved Logs Insights queries. Current `develop` template: 26 alarms, 2 metric filters, 3 query definitions. See the dated observation above and [runbook](ops-runbook.md); notification delivery was not tested. |

### Lambda execution roles

> 最終検証: 2026-10-09 — #166/#169のSAM定義とLambda呼出し権限を照合（#169変更セットの適用前、実環境未確認）

| Lambda execution role | 権限範囲 |
| --- | --- |
| `eleknowledge-chat-archive-dev-role` | DynamoDB Streams読取り（chatlogs stream ARN）、専用アーカイブバケット内のS3 `PutObject`（`s3:ResourceAccount` で自アカウントに限定）と `ListBucket`（OnFailure送信先に必要） |
| `metrics-aggregator-dev` | chatlogs `Scan`、metricsテーブル`PutItem`、CloudWatch `GetMetricStatistics` |
| `metrics-read-dev` | metricsテーブルの`scope-metricDate-index`に対する`Query` |

Not in IaC: the AWS budget notification and the Bedrock application inference profile referenced by the operational records. The 2026-09-30 read-only observation found the development RAG Lambda configured for `global.anthropic.claude-sonnet-5`; do not infer the state of other environments from this. Log group retention is set by `scripts/ops/set_log_retention.py` (Lambda 365 d / API Gateway 90 d).

## Not Recreated by Current IaC

| Resource name | Component type | Purpose | Status |
| --- | --- | --- | --- |
| Bedrock Knowledge Base resources | Bedrock | Managed service resources whose IDs are supplied through SSM/parameters | Create or configure after base IaC deployment |
| Bedrock Agent and Alias | Bedrock Agent | Troubleshooting orchestration backend | Create or configure after Phase 3 deployment |
| `sam-test` | CloudFormation/SAM stack | Old test stack | Excluded legacy candidate |
| `troubleshooting-small*` | Lambda/CloudFormation | Old troubleshooting POC | Excluded legacy candidate |
| `rag-*` old APIs | API Gateway | Earlier RAG POC APIs | Excluded legacy candidate |
| Control Tower/Config/CloudTrail/VPC baseline | AWS governance/networking | Account baseline services | Out of EleKnowledge migration scope |

## Law chat: develop pre-release addition

> 最終検証: 2026-10-09 — develop `b8070f56`の法令SAM定義とPR #155 / #156を照合。今回のAWS実リソース読取りは未実施。

法令専用KBは`infrastructure/sam/legal-rag-kb-template.yaml`、データ保存の定義は`legal-rag-data-template.yaml` / `legal-rag-data-import-template.yaml`、RAGへの接続は`phase2-template.yaml`にある。過去のdev記録では独立KB stackが保持済みbucketを参照する。定義の存在をbucket import済み・現在のAWS反映済みと扱わない。

通常KBとは別の`LAW_KNOWLEDGE_BASE_ID`を使い、`ENVIRONMENT=dev`・`LAW_RAG_ENABLED=true`・KB IDありで許可する。データ・IAM・KMS・コードの現況は[プレリリース手順](legal-chat-prerelease.md)に沿って読み戻し、[確認記録](verification-2026-10-09-legal-chat-prerelease.md)に残す。過去のリソースIDやgate状態を現在値として転記しない。
