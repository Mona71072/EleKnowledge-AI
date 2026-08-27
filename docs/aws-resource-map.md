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

## Phase 1 - Auth and Base Data

| Resource name | Component type | Purpose | Managed by |
| --- | --- | --- | --- |
| `users-dev` | Cognito User Pool | User authentication and account lifecycle | `phase1-template.yaml` |
| `users-dev-client` | Cognito User Pool Client | Frontend/client auth integration | `phase1-template.yaml` |
| `users-dev` | DynamoDB table | User profile records keyed by `userId` | `phase1-template.yaml` |
| `chatlogs-dev` | DynamoDB table | Chat sessions/messages with user timestamp GSI | `phase1-template.yaml` |
| `documents-dev-${AWS::AccountId}` | S3 bucket | Source documents for RAG and citations | `phase1-template.yaml` |
| `uploads-dev-${AWS::AccountId}` | S3 bucket | Temporary upload area | `phase1-template.yaml` |
| `auth-lambda-dev` | IAM role | Shared execution role for auth Lambda functions | `phase1-template.yaml` |
| `signup-dev` | Lambda function | User signup endpoint handler | `phase1-template.yaml` |
| `login-dev` | Lambda function | User login endpoint handler | `phase1-template.yaml` |
| `verify-dev` | Lambda function | Email verification endpoint handler | `phase1-template.yaml` |
| `auth-api-dev` | API Gateway REST API | `/auth/*` public auth API | `phase1-template.yaml` |
| `/aws/apigateway/auth-api-dev` | CloudWatch Logs log group | API Gateway access/execution logs | `phase1-template.yaml` |

## Phase 2 - RAG and Chat

| Resource name | Component type | Purpose | Managed by |
| --- | --- | --- | --- |
| `kb-dev` | OpenSearch Serverless collection | Vector storage backing Bedrock Knowledge Base | `phase2-template.yaml` |
| `kb-dev-enc` | OpenSearch Serverless encryption policy | Encryption policy for `kb-dev` | `phase2-template.yaml` |
| `kb-dev-net` | OpenSearch Serverless network policy | Network policy for `kb-dev` and dashboards | `phase2-template.yaml` |
| `kb-dev` | IAM role | Bedrock Knowledge Base access to S3/OpenSearch | `phase2-template.yaml` |
| `/eleknowledge/dev/knowledge-base-id` | SSM Parameter | Bedrock Knowledge Base ID placeholder/value | `phase2-template.yaml` |
| `rag-lambda-dev` | IAM role | Shared execution role for RAG and chat Lambda functions | `phase2-template.yaml` |
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

## Not Recreated by Current IaC

| Resource name | Component type | Purpose | Status |
| --- | --- | --- | --- |
| Bedrock Knowledge Base resources | Bedrock | Managed service resources whose IDs are supplied through SSM/parameters | Create or configure after base IaC deployment |
| Bedrock Agent and Alias | Bedrock Agent | Troubleshooting orchestration backend | Create or configure after Phase 3 deployment |
| `sam-test` | CloudFormation/SAM stack | Old test stack | Excluded legacy candidate |
| `troubleshooting-small*` | Lambda/CloudFormation | Old troubleshooting POC | Excluded legacy candidate |
| `rag-*` old APIs | API Gateway | Earlier RAG POC APIs | Excluded legacy candidate |
| Control Tower/Config/CloudTrail/VPC baseline | AWS governance/networking | Account baseline services | Out of EleKnowledge migration scope |
