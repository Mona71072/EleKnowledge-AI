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

The seven existing dev stacks corresponding to PR #193 completed Env-tag removal. The 19 resources outside those stacks were also checked for the new cost keys, and the dedicated law KB stack's missing keys were added. This cost-tag assignment is not approval to add the law KB, its data, or other resources to the migration scope. The subsequent scope agreement is recorded in the next section. See [the operation record](ops-cost-allocation-tags.md#2026-10-20のaws反映追加確認) for counts, preservation checks, remaining Env tags, and unverified billing activation.

## Migration Target

> 最終検証: 2026-10-19 — AWS CLI 読み取り専用確認（東京リージョンのCloudFormation。データ内容・機能E2Eは未確認）

The Phase 1–3 `dev` stacks already exist in the inspected AWS account and were `UPDATE_COMPLETE` on 2026-10-19. The documented “create an empty dev environment” instruction is a migration target for a different/new account, not a description of the current environment. A separate live stack, `eleknowledge-law-kb-dev`, was also `UPDATE_COMPLETE`; its inclusion in migration scope was agreed by mona on 2026-10-21 and by itai in the 2026-10-22 user request (see the decision below). The `eleknowledge-legal-rag-dev` stack was `ROLLBACK_COMPLETE` and must not be treated as deployed.

Data migration scope remains out of scope for this inventory. This snapshot is limited to CloudFormation status and does not verify data completeness or service health.

## 移行範囲の合意とitai検証資源（2026-10-22）

> 最終検証: 2026-10-22 — PR #194のmona回答と本ユーザー依頼、itai b9076cbdの実施記録を照合。AWS再実査・移行実行なし。

- 決定者・確認者: mona（2026-10-21の[明示回答](https://github.com/yukiworkspace/EleKnowledge-AI/pull/194#issuecomment-6304277103)）、itai（2026-10-22の修正依頼）。稼働中の法令KBスタック `eleknowledge-law-kb-dev` 1件をPhase1〜3に加えた移行対象として記載し、コスト配分対象 `legal-rag / development` とする。根拠は10/19のUPDATE_COMPLETE観測と10/20のKB・データソース不変／タグ確認。
- 対象外: `eleknowledge-legal-rag-dev`（ROLLBACK_COMPLETE）1スタックは移行対象外のまま保持。関連バケット等の独立した現存資源を削除する判断ではない。検索・表示・利用対象の追加／除外は今回0件。法令RAG利用者の接続・データは変更しない。
- 移行の実行・データ移行・KB同期・原本の削除は今回行わない。対象データ量、移行手順、担当、切替・復旧条件は実行前の確認として残す。
- itai専用のPhase2・KB v2・共通知識スタックとAmplify itaiは、今回の正式移行対象へ自動追加しない。[リソースマップのitai追補](aws-resource-map.md#itai専用検証環境の追補2026-10-22)で検証環境として棚卸しする。10/20の110件には含まれない。


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

## 法令KB（追加の移行対象）

> 最終検証: 2026-10-22 — 上記共同合意と10/20の保存記録を照合。構成・データの新規実査なし。

- `eleknowledge-law-kb-dev`: 稼働中の専用スタック。LawKnowledgeBaseと既存データソースの設定・実体IDが10/20のタグ補完前後で不変だったことを確認した記録がある。
- タグ分類: `gyoumu012Project=ele-knowledge` / `gyoumu012Component=legal-rag` / `gyoumu012Usage=development`。スタック・KBは19件の追加確認と重複するため加算しない。
- 元のデータS3・検索基盤等の移行依存、対象文書件数、データの保持・コピー・切替手順は未確定。スタック1件の追加を、すべての関連資源・データを移行済みとする根拠にしない。


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
