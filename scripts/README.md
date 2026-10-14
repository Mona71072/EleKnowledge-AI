# scripts

`bedrock-*.json`（直下）の `<ACCOUNT_ID>` は実アカウント ID に置換してから IAM ポリシーとして適用する。
`deploy_lambdas.py` はアカウント ID を `AWS_ACCOUNT_ID` 環境変数、未設定なら `aws sts get-caller-identity` から取得する。
