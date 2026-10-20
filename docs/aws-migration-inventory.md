---
status: draft
last-verified: 2026-08-21
related-code: infrastructure/sam/, amplify.yml
---

# AWS Migration Inventory

> 最終検証: 2026-10-20 — 冒頭のタグ説明と同日反映記録への案内を照合。移行対象一覧は再検証していない。

EleKnowledge resources to recreate in the new AWS account on `ap-northeast-1`.
Resource ownership should be identified with tags, not long names:

- `Project=EleKnowledge`
- `ManagedBy=SAM`

SAM templates no longer declare the legacy `Env` resource tag; the `Environment` parameter still selects the deployment environment. The 2026-10-19 read found Env on 108 resources and each new cost key on 99 of that result set. These counts are historical; see the dated follow-up below for the explicit 10/20 updates. This inventory does not authorize bulk tag changes.

Use [AWS Migration Runbook](aws-migration-runbook.md) for the end-to-end deployment and verification procedure.
See [AWS Resource Map](aws-resource-map.md) for the resource name, component type, and purpose table.

## Tag follow-up (2026-10-20)

> 最終検証: 2026-10-20 — タグ適用・読み戻し証跡と移行範囲の未決事項を照合。移行対象一覧全体は再検証していない。

The seven existing dev stacks corresponding to PR #193 completed Env-tag removal. The 19 resources outside those stacks were also checked for the new cost keys, and the dedicated law KB stack's missing keys were added. This cost-tag assignment is not approval to add the law KB, its data, or other resources to the migration scope. Keep the scope review in the next section pending. See [the operation record](ops-cost-allocation-tags.md#2026-10-20のaws反映追加確認) for counts, preservation checks, remaining Env tags, and unverified billing activation.

## Migration Target

> 最終検証: 2026-10-19 — AWS CLI 読み取り専用確認（東京リージョンのCloudFormation。データ内容・機能E2Eは未確認）

The Phase 1–3 `dev` stacks already exist in the inspected AWS account and were `UPDATE_COMPLETE` on 2026-10-19. The documented “create an empty dev environment” instruction is a migration target for a different/new account, not a description of the current environment. A separate live stack, `eleknowledge-law-kb-dev`, was also `UPDATE_COMPLETE`; it is not yet included in the Phase 1–3 inventory and needs migration-scope review. The `eleknowledge-legal-rag-dev` stack was `ROLLBACK_COMPLETE` and must not be treated as deployed.

Data migration scope remains out of scope for this inventory. This snapshot is limited to CloudFormation status and does not verify data completeness or service health.

## IaC Managed Resources

Phase 1:

- Cognito user pool/client: `users-dev`
- DynamoDB: `users-dev`, `chatlogs-dev`
- S3: `documents-dev-${AWS::AccountId}`, `uploads-dev-${AWS::AccountId}`
- Lambda: `signup-dev`, `login-dev`, `verify-dev`
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
