---
status: draft
last-verified: 2026-07-01
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

## 2. Deploy Phase 1

Creates Cognito, base DynamoDB tables, document/upload buckets, auth Lambda functions, and `auth-api-dev`.

```powershell
sam deploy `
  --template-file infrastructure/sam/phase1-template.yaml `
  --stack-name "$Project-$Env-phase1" `
  --region $Region `
  --profile $Profile `
  --resolve-s3 `
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

Creates OpenSearch Serverless resources, RAG/chat Lambda functions, `rag-api-dev`, `chat-api-dev`, and `/eleknowledge/dev/knowledge-base-id`.

Use `KnowledgeBaseId=pending` for the first empty deployment. Replace it after the Bedrock Knowledge Base is created.

```powershell
sam deploy `
  --template-file infrastructure/sam/phase2-template.yaml `
  --stack-name "$Project-$Env-phase2" `
  --region $Region `
  --profile $Profile `
  --resolve-s3 `
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM `
  --parameter-overrides "Environment=$Env" "ProjectName=$Project" "KnowledgeBaseId=pending"
```

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
- `KnowledgeBaseCollectionArn`
- `KnowledgeBaseCollectionEndpoint`
- `KnowledgeBaseRoleArn`
- `KnowledgeBaseIdParameterName`

## 4. Configure Bedrock

Create or configure Bedrock Knowledge Bases and Bedrock Agent in `ap-northeast-1` using the Phase 1 document bucket and Phase 2 OpenSearch/IAM outputs.

Create brand-new Knowledge Bases for this environment. Do not reuse or repoint any Knowledge Base, OpenSearch Serverless collection, or S3 bucket already owned by other departments (for example the GenU environment's Knowledge Bases) — those serve a different purpose and must not be modified.

At minimum, collect these IDs:

- General RAG Knowledge Base ID
- Trouble cases Knowledge Base ID
- Troubleshooting manuals Knowledge Base ID
- C-materials Knowledge Base ID
- Bedrock Agent ID
- Bedrock Agent Alias ID

Update the SSM parameter for the general RAG Knowledge Base:

```powershell
aws ssm put-parameter `
  --name "/eleknowledge/$Env/knowledge-base-id" `
  --value "<general-kb-id>" `
  --type String `
  --overwrite `
  --region $Region `
  --profile $Profile
```

Redeploy Phase 2 so `rag-dev` receives the real `KNOWLEDGE_BASE_ID` environment variable:

```powershell
sam deploy `
  --template-file infrastructure/sam/phase2-template.yaml `
  --stack-name "$Project-$Env-phase2" `
  --region $Region `
  --profile $Profile `
  --resolve-s3 `
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM `
  --parameter-overrides "Environment=$Env" "ProjectName=$Project" "KnowledgeBaseId=<general-kb-id>"
```

## 5. Deploy Phase 3

Creates troubleshooting tables, Lambda functions, `troubleshooting-api-dev`, and Bedrock Agent ID parameters.

```powershell
sam deploy `
  --template-file infrastructure/sam/phase3-template.yaml `
  --stack-name "troubleshooting-$Env" `
  --region $Region `
  --profile $Profile `
  --resolve-s3 `
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
