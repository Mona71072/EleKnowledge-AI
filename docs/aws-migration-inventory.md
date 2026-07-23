---
status: draft
last-verified: 2026-05-27
related-code: infrastructure/sam/, amplify.yml
---

# AWS Migration Inventory

EleKnowledge resources to recreate in the new AWS account on `ap-northeast-1`.
Resource ownership should be identified with tags, not long names:

- `Project=EleKnowledge`
- `Env=dev` or `Env=prd`
- `ManagedBy=SAM`

Use [AWS Migration Runbook](aws-migration-runbook.md) for the end-to-end deployment and verification procedure.
See [AWS Resource Map](aws-resource-map.md) for the resource name, component type, and purpose table.

## Migration Target

Create an empty `dev` environment first. Data migration is out of scope for this phase.

## IaC Managed Resources

Phase 1:

- Cognito user pool/client: `users-dev`
- DynamoDB: `users-dev`, `chatlogs-dev`
- S3: `documents-dev-${AWS::AccountId}`, `uploads-dev-${AWS::AccountId}`
- Lambda: `signup-dev`, `login-dev`, `verify-dev`, `forgot-password-dev`, `confirm-password-reset-dev`
- API Gateway: `auth-api-dev`
- IAM role: `auth-lambda-dev`

Phase 2:

- OpenSearch Serverless collection: `kb-dev`
- Bedrock Knowledge Base ID placeholder: `/eleknowledge/dev/knowledge-base-id`
- Lambda: `rag-dev`, `chat-dev`
- API Gateway: `rag-api-dev`, `chat-api-dev`
- IAM roles: `kb-dev`, `rag-lambda-dev`

Phase 3:

- DynamoDB: `sites-dev`, `sessions-dev`
- Lambda: `orchestrator-dev`, `db-search-dev`, `kb-search-cases-dev`, `kb-search-manuals-dev`, `kb-search-materials-dev`, `history-dev`
- API Gateway: `troubleshooting-api-dev`
- SSM: `/eleknowledge/dev/agent-id`, `/eleknowledge/dev/agent-alias-id`
- IAM role: `troubleshooting-lambda-dev`

## Excluded Legacy Candidates

Do not recreate these in the new IaC unless a later review finds a live dependency:

- `sam-test`
- old `rag-*` API resources
- `troubleshooting-small` and `orchestractor-ver1`
- individual POC Lambda functions such as `rag-upload-poc` and `pdf-split*`
- Control Tower, Config, CloudTrail, and VPC baseline resources

## Post Deploy Inputs

After Phase 2/3 deployment, replace `pending` parameter values with actual Bedrock resource IDs:

- Bedrock Knowledge Base IDs
- Bedrock Agent ID
- Bedrock Agent Alias ID

Then update Amplify environment variables from CloudFormation Outputs.
