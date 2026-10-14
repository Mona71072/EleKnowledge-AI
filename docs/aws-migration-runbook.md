---
status: draft
last-verified: 2026-08-27
related-code: infrastructure/sam/, amplify.yml, docs/aws-resource-map.md
---

# AWS Migration Runbook

This is the canonical runbook for recreating an empty EleKnowledge `dev` environment in a new AWS account on `ap-northeast-1`.

Use [AWS Resource Map](aws-resource-map.md) for resource names and purposes. Older deployment guides still describe the previous `us-east-1` / `EleKnowledge-AI-development-*` environment and must not be used for this migration.

## 0. Preconditions

- AWS CLI and SAM CLI are installed.
- The target AWS profile points to the new AWS account.
- Bedrock model access is enabled in `ap-northeast-1`.
- Data migration is intentionally out of scope.
- Run commands from the repository root.

Set shell variables:

```powershell
$Profile = "<new-account-profile>"
$Region = "ap-northeast-1"
$Env = "dev"
$Project = "EleKnowledge"
```

Confirm the target account before deploying:

```powershell
aws sts get-caller-identity --profile $Profile
```

## 1. Validate and Build

```powershell
sam validate --region $Region --template-file infrastructure/sam/phase1-template.yaml
sam validate --region $Region --template-file infrastructure/sam/phase2-template.yaml
sam validate --region $Region --template-file infrastructure/sam/phase3-template.yaml

sam build --template-file infrastructure/sam/phase1-template.yaml --build-dir .aws-sam/phase1 --cached
sam build --template-file infrastructure/sam/phase2-template.yaml --build-dir .aws-sam/phase2 --cached
sam build --template-file infrastructure/sam/phase3-template.yaml --build-dir .aws-sam/phase3 --cache-dir .aws-sam/phase3-cache --cached
```

### 1-1. Artifacts bucket — do NOT use `--resolve-s3`

`--resolve-s3` cannot work in this account. It creates the `aws-sam-cli-managed-default` stack, whose
`SamCliSourceBucket` sets a public-access block, and the organization SCP
(`arn:aws:organizations::<ORG_MANAGEMENT_ACCOUNT_ID>:policy/o-jjrd939pt4/service...`。`<ORG_MANAGEMENT_ACCOUNT_ID>` は実際の値を各自のローカル設定・AWS コンソールで確認する) **explicitly denies
`s3:PutBucketPublicAccessBlock` for every principal**, including this SSO role. The stack fails with:

```
User: .../AWSReservedSSO_datautl-bple-mebs_.../itai-yu is not authorized to perform:
s3:PutBucketPublicAccessBlock ... with an explicit deny in a service control policy
```

and is left in `ROLLBACK_COMPLETE`, which blocks every later `--resolve-s3` attempt. This is the same
SCP that forced the removal of `PublicAccessBlockConfiguration` from the document/upload buckets
(commit `e01bddf`).

Create a plain artifacts bucket once, and pass it with `--s3-bucket` from then on. `aws s3 mb` does not
call `PutBucketPublicAccessBlock`, and since April 2023 S3 blocks public access on new buckets by
default anyway, so the bucket is still private.

```powershell
# <DEV_ACCOUNT_ID> は実際の値を各自のローカル設定・AWS コンソールで確認して置き換える
$ArtifactsBucket = "eleknowledge-sam-artifacts-$Env-<DEV_ACCOUNT_ID>-$Region"
aws s3 mb "s3://$ArtifactsBucket" --region $Region --profile $Profile

# If aws-sam-cli-managed-default is stuck in ROLLBACK_COMPLETE, delete it so SAM stops retrying it:
aws cloudformation delete-stack --stack-name aws-sam-cli-managed-default --region $Region --profile $Profile
```

Every `sam deploy` below uses `--s3-bucket $ArtifactsBucket` instead of `--resolve-s3`.

## 2. Deploy Phase 1

Creates Cognito, base DynamoDB tables, document/upload buckets, auth Lambda functions, and `auth-api-dev`.

```powershell
sam deploy `
  --template-file infrastructure/sam/phase1-template.yaml `
  --stack-name "$Project-$Env-phase1" `
  --region $Region `
  --profile $Profile `
  --s3-bucket $ArtifactsBucket `
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM `
  --parameter-overrides "Environment=$Env" "ProjectName=$Project"
```

Capture Phase 1 outputs:

```powershell
aws cloudformation describe-stacks `
  --stack-name "$Project-$Env-phase1" `
  --region $Region `
  --profile $Profile `
  --query "Stacks[0].Outputs[].{Key:OutputKey,Value:OutputValue}" `
  --output table
```

Required outputs for later steps:

- `AuthApiUrl`
- `CognitoUserPoolId`
- `CognitoClientId`
- `DocumentsBucketName`

## 3. Deploy Phase 2

Creates the RAG/chat Lambda functions, `rag-api-dev`, `chat-api-dev`, and `/eleknowledge/dev/knowledge-base-id`.

This stack **no longer creates an OpenSearch Serverless collection or a Knowledge Base service role** — Phase 2 reuses the existing Knowledge Base (see section 4). `KnowledgeBaseId` has a default value in `phase2-template.yaml` and is constrained by `AllowedPattern`; the old `KnowledgeBaseId=pending` two-pass flow is gone, because deploying with `pending` silently produced a `rag-dev` that returned zero results for every query. The template default is **not** authoritative for the running environment — always confirm the deployed value as described below.

> **⚠️ Template default vs. deployed value.** `DF9XUCSPDM` is the **default value in
> `phase2-template.yaml`**; the deployed stack `EleKnowledge-dev-phase2` and the live `rag-dev`
> Lambda both used **`KnowledgeBaseId=VQV81CNYU4`** (`generative-ai-use-cases-jpinstd`, TEXT
> ingestion) **as of 2026-08-26** (`DF9XUCSPDM`'s MULTIMODAL parsing yields IMAGE chunks the app
> cannot consume yet). Both are point-in-time facts, not permanent rules.
> **Before any full `sam deploy`, look up the KB ID currently approved and deployed** — the
> deployed CloudFormation Parameter and/or the `rag-dev` `KNOWLEDGE_BASE_ID` environment variable —
> **and pass it explicitly**, otherwise the deploy silently repoints the KB to the template
> default. For a first-time deployment (no existing stack), use the KB ID currently approved for
> the environment (see section 4). Facts and rationale:
> `docs/verification-2026-08-26-kb-vqv-metadata.md`.

```powershell
# Confirm the currently deployed KB ID first (cross-check the rag-dev
# KNOWLEDGE_BASE_ID environment variable if in doubt)
$KbId = aws cloudformation describe-stacks `
  --stack-name "$Project-$Env-phase2" `
  --region $Region `
  --profile $Profile `
  --query "Stacks[0].Parameters[?ParameterKey=='KnowledgeBaseId'].ParameterValue" `
  --output text

sam deploy `
  --template-file infrastructure/sam/phase2-template.yaml `
  --stack-name "$Project-$Env-phase2" `
  --region $Region `
  --profile $Profile `
  --s3-bucket $ArtifactsBucket `
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM `
  --parameter-overrides "Environment=$Env" "ProjectName=$Project" "KnowledgeBaseId=$KbId"
```

> **If `$Project-$Env-phase2` is already deployed with the old template**, split the change into two
> deployments: first remove only the three `KnowledgeBase*` Outputs, deploy, and confirm success —
> CloudFormation fails safely with `Export cannot be deleted as it is in use` if anything still
> imports them. Only then remove the collection/policies/role in a second deployment. Doing both at
> once risks `UPDATE_ROLLBACK_FAILED`.

Capture Phase 2 outputs:

```powershell
aws cloudformation describe-stacks `
  --stack-name "$Project-$Env-phase2" `
  --region $Region `
  --profile $Profile `
  --query "Stacks[0].Outputs[].{Key:OutputKey,Value:OutputValue}" `
  --output table
```

Required outputs:

- `RagApiUrl`
- `ChatApiUrl`
- `KnowledgeBaseIdParameterName`

(`KnowledgeBaseCollectionArn` / `KnowledgeBaseCollectionEndpoint` / `KnowledgeBaseRoleArn` were removed along with the self-hosted vector store.)

## 4. Configure Bedrock

Configure the Bedrock Knowledge Bases and the Bedrock Agent in `ap-northeast-1`. Phase 2 reuses an
existing Knowledge Base (see the exception below) and no longer emits OpenSearch/IAM outputs; the
Phase 3 Knowledge Bases still need to be created against the Phase 1 document bucket.

> **Exception for Phase 2 (approved 2026-07-17; superseded in practice — see 2026-08-26 note).**
> Phase 2 was planned to **reuse the existing Knowledge Base
> `DF9XUCSPDM`** (`generative-ai-use-cases-jp-inst-fmp`), together with its data source `WQ4ED5IFOP`,
> its OpenSearch Serverless collection `k9p9daatgyg5pvbhf85h`, and its S3 data-source bucket
> `ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb` (prefix `docs/`).
> **As of 2026-08-26 the deployed environment instead reuses `VQV81CNYU4`**
> (`generative-ai-use-cases-jpinstd`, data source `KHPV3CNKOU`, **same S3 bucket and prefix**);
> the read-only rules below apply identically to it. See
> `docs/verification-2026-08-26-kb-vqv-metadata.md` for both KBs' data sources and the decision.
> The knowledge itself is identical to what EleKnowledge needs — the differentiation is the end user,
> the UI, and how that knowledge is surfaced — so duplicating 3,693 PDFs into a second KB would only
> add storage, embedding, and sync cost.
>
> Owner approval has been obtained, but these remain **shared assets**, so the reuse is
> **strictly read-only**:
> - `phase2-template.yaml` grants `s3:GetObject` on the data-source bucket and **never `s3:PutObject`**.
> - Never call a write API on the KB, its data source, or the collection. **Never run a Sync.**
> - `phase2-template.yaml` no longer creates an OpenSearch Serverless collection or a KB service role.
>
> For Phase 3 (which needs four separate Knowledge Bases) the rule below still applies until a
> separate decision is recorded.

For everything other than the Phase 2 exception above: create brand-new Knowledge Bases for this environment. Do not reuse or repoint any Knowledge Base, OpenSearch Serverless collection, or S3 bucket already owned by other departments (for example the GenU environment's Knowledge Bases) — those serve a different purpose and must not be modified.

At minimum, collect these IDs:

- General RAG Knowledge Base ID — **Phase 2: `VQV81CNYU4` as deployed at the 2026-08-26 verification (reused, see the note above)**
- Trouble cases Knowledge Base ID
- Troubleshooting manuals Knowledge Base ID
- C-materials Knowledge Base ID
- Bedrock Agent ID
- Bedrock Agent Alias ID

For Phase 2 nothing further is needed: the Knowledge Base ID (`VQV81CNYU4` as deployed — see the
2026-08-26 note above) is passed at deploy time and the stack writes it to the `rag-dev` environment
variable. (The Lambda reads the environment variable, not SSM. Note: as of 2026-08-26 the SSM
parameter `/eleknowledge/dev/knowledge-base-id` does **not** exist in the account — this paragraph
previously overstated it; whether to recreate it or drop it from the template is an open item.)

Verify the reused Knowledge Base actually answers before moving on (`$KbId` = the confirmed
deployed KB ID from section 3):

```powershell
aws bedrock-agent-runtime retrieve `
  --knowledge-base-id $KbId `
  --retrieval-query '{\"text\":\"火災管制運転\"}' `
  --retrieval-configuration '{\"vectorSearchConfiguration\":{\"numberOfResults\":5,\"filter\":{\"equals\":{\"key\":\"category\",\"value\":\"C資料\"}}}}' `
  --region $Region --profile $Profile --query 'length(retrievalResults)'
```

A non-zero count is required. Note the KB metadata keys are `category` / `model_type` / `filename` /
`file_path` — the older `document` / `product` / `model` keys do not exist and always match nothing.

## 5. Deploy Phase 3

Creates troubleshooting tables, Lambda functions, `troubleshooting-api-dev`, and Bedrock Agent ID parameters.

```powershell
sam deploy `
  --template-file infrastructure/sam/phase3-template.yaml `
  --stack-name "troubleshooting-$Env" `
  --region $Region `
  --profile $Profile `
  --s3-bucket $ArtifactsBucket `
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM `
  --parameter-overrides `
    "Environment=$Env" `
    "ProjectName=$Project" `
    "BedrockRegion=$Region" `
    "KnowledgeBaseId=<general-kb-id>" `
    "TroubleCasesKnowledgeBaseId=<trouble-cases-kb-id>" `
    "TroubleshootingManualKnowledgeBaseId=<manuals-kb-id>" `
    "CMaterialKnowledgeBaseId=<materials-kb-id>" `
    "AgentId=<agent-id>" `
    "AgentAliasId=<agent-alias-id>"
```

If Agent IDs change later, update SSM and redeploy Phase 3 with the same values:

```powershell
aws ssm put-parameter --name "/eleknowledge/$Env/agent-id" --value "<agent-id>" --type String --overwrite --region $Region --profile $Profile
aws ssm put-parameter --name "/eleknowledge/$Env/agent-alias-id" --value "<agent-alias-id>" --type String --overwrite --region $Region --profile $Profile
```

Capture Phase 3 outputs:

```powershell
aws cloudformation describe-stacks `
  --stack-name "troubleshooting-$Env" `
  --region $Region `
  --profile $Profile `
  --query "Stacks[0].Outputs[].{Key:OutputKey,Value:OutputValue}" `
  --output table
```

Required output:

- `TroubleshootingApiUrl`: base URL ending in `/{env}/troubleshooting`; the frontend appends `/analyze` and `/history`.

## 6. Create Amplify App

This account has no existing Amplify app for EleKnowledge, so the app must be created before environment variables can be configured. Skip this step if an app was already created in a previous run.

```powershell
aws amplify list-apps --region $Region --profile $Profile --query "apps[].{Name:name,AppId:appId,DefaultDomain:defaultDomain}" --output table
```

If no matching app exists, create one and connect the `develop` branch (or the branch designated for this environment):

```powershell
aws amplify create-app `
  --name "eleknowledge-$Env" `
  --region $Region `
  --profile $Profile `
  --platform WEB

aws amplify create-branch `
  --app-id "<app-id-from-create-app-output>" `
  --branch-name "develop" `
  --region $Region `
  --profile $Profile
```

Amplify Hosting needs a connection to the source repository (GitHub) to build automatically. Either:

- Connect the repository via the Amplify Console (one-time OAuth authorization), or
- Use `aws amplify create-webhook` for manual/CI-triggered builds without a direct repository connection.

Confirm `amplify.yml` at the repository root is picked up as the build spec; it already defines the `frontend/` monorepo build path and output directory.

## 7. Configure Amplify Environment Variables

Set these in Amplify Hosting for the new app/branch:

| Variable | Value source |
| --- | --- |
| `NEXT_PUBLIC_AWS_REGION` | `ap-northeast-1` |
| `NEXT_PUBLIC_API_URL` | Phase 1 `AuthApiUrl` |
| `NEXT_PUBLIC_RAG_API_URL` | Phase 2 `RagApiUrl` |
| `NEXT_PUBLIC_CHAT_API_URL` | Phase 2 `ChatApiUrl` |
| `NEXT_PUBLIC_TROUBLESHOOTING_API_URL` | Phase 3 `TroubleshootingApiUrl` base URL |
| `NEXT_PUBLIC_COGNITO_USER_POOL_ID` | Phase 1 `CognitoUserPoolId` |
| `NEXT_PUBLIC_COGNITO_CLIENT_ID` | Phase 1 `CognitoClientId` |

For CLI-based updates, first find the Amplify app and branch:

```powershell
aws amplify list-apps --region $Region --profile $Profile --query "apps[].{Name:name,AppId:appId,DefaultDomain:defaultDomain}" --output table
aws amplify list-branches --app-id "<app-id>" --region $Region --profile $Profile --query "branches[].branchName" --output table
```

Then update the branch environment variables:

```powershell
$AmplifyEnvVars = "NEXT_PUBLIC_AWS_REGION=$Region,NEXT_PUBLIC_API_URL=<auth-api-url>,NEXT_PUBLIC_RAG_API_URL=<rag-api-url>,NEXT_PUBLIC_CHAT_API_URL=<chat-api-url>,NEXT_PUBLIC_TROUBLESHOOTING_API_URL=<troubleshooting-api-url>,NEXT_PUBLIC_COGNITO_USER_POOL_ID=<user-pool-id>,NEXT_PUBLIC_COGNITO_CLIENT_ID=<client-id>"

aws amplify update-branch `
  --app-id "<app-id>" `
  --branch-name "<branch-name>" `
  --region $Region `
  --profile $Profile `
  --environment-variables $AmplifyEnvVars
```

Trigger a new Amplify build after updating variables.

## 8. Smoke Test

Run these checks before handing the environment to users:

- Sign up a test user.
- Log in and confirm Cognito tokens are issued.
- Call the RAG API from the frontend and confirm it reaches `rag-dev`.
- Call troubleshooting analyze from the frontend and confirm it reaches `orchestrator-dev`.
- Open troubleshooting history and confirm `history-dev` reads from `sessions-dev`.
- Check CloudWatch logs for Lambda errors.

Useful commands:

```powershell
aws lambda list-functions --region $Region --profile $Profile --query "Functions[?ends_with(FunctionName, '-$Env')].FunctionName" --output table
aws dynamodb list-tables --region $Region --profile $Profile --output table
aws ssm get-parameters-by-path --path "/eleknowledge/$Env" --region $Region --profile $Profile --output table
```

## 9. Do Not Use Legacy Assets

Do not recreate these unless a later dependency review explicitly requires them:

- `sam-test`
- old `rag-*` API resources
- `troubleshooting-small*`
- individual POC Lambda functions
- Control Tower, Config, CloudTrail, and VPC baseline resources

## 10. Existing dev: law-chat pre-release

> 最終検証: 2026-10-09 — PR #155 / #156、developコード、Amplify job 64、RAG有効化設定と実配信画面を照合。develop公開反映・カードからの法令画面遷移を確認。

既存devへ法令チャットを反映する場合、空環境の再構築を行わず[法令プレリリース手順](legal-chat-prerelease.md)を使用する。`NEXT_PUBLIC_LAW_RAG_ENABLED`はdevelopブランチのカード表示条件、`LawRagEnabled` / `LawKnowledgeBaseId`はPhase 2のサーバー設定であり、それぞれ読み戻して確認する。Lambda / SAMはitaiが既存パラメータと他テーマの反映を保持した変更セットで実施する。文書更新やPRマージだけでAWS反映完了とは扱わず、追加Syncや旧stack / bucketの削除・importをこの手順に含めない。
