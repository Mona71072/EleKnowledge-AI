#!/usr/bin/env bash
# EleKnowledge のロググループに保持期間を設定する（issue #86 の決定）。
#
# 方針（2026-09-09 itai 決定）: 利用価値・監査価値があるものは残す。
#   - Lambda アプリログ            : 365 日（分析価値のある項目は chatlogs / S3 にも保存する前提）
#   - API Gateway 実行ログ         : 90 日（本文を含まず障害切り分け用）
#   - API Gateway アクセスログ枠   : 90 日（現状は未配線・0 バイト）
#   - WAF ログ（有効化後）          : 365 日（本スクリプトの対象外。有効化時に設定）
#
# Lambda のロググループは自動作成済みで SAM テンプレートに無いため、後から
# AWS::Logs::LogGroup を宣言すると「既に存在する」で失敗する。IaC 化（resource import）は後続。
#
# 使い方:
#   AWS_PROFILE=<profile> AWS_REGION=ap-northeast-1 scripts/ops/set-log-retention.sh [--dry-run]
set -euo pipefail

ENV="${ENVIRONMENT:-dev}"
DRY_RUN="${1:-}"
export MSYS_NO_PATHCONV=1

LAMBDA_DAYS=365
APIGW_DAYS=90

LAMBDA_GROUPS=(
  "/aws/lambda/rag-${ENV}"
  "/aws/lambda/chat-${ENV}"
  "/aws/lambda/login-${ENV}"
  "/aws/lambda/signup-${ENV}"
  "/aws/lambda/verify-${ENV}"
  "/aws/lambda/metrics-read-${ENV}"
  "/aws/lambda/metrics-aggregator-${ENV}"
  "/aws/lambda/announcements-read-${ENV}"
  "/aws/lambda/announcements-write-${ENV}"
  "/aws/lambda/announcements-publisher-${ENV}"
  "/aws/lambda/eleknowledge-chat-archive-${ENV}"
  "/aws/lambda/eleknowledge-cognito-domain-guard-${ENV}"
  "/aws/lambda/orchestrator-${ENV}"
  "/aws/lambda/db-search-${ENV}"
  "/aws/lambda/kb-search-cases-${ENV}"
  "/aws/lambda/kb-search-manuals-${ENV}"
  "/aws/lambda/kb-search-materials-${ENV}"
  "/aws/lambda/history-${ENV}"
)

APIGW_GROUPS=(
  "/aws/apigateway/auth-api-${ENV}"
  "/aws/apigateway/chat-api-${ENV}"
  "/aws/apigateway/rag-api-${ENV}"
)

set_retention() {
  local group="$1" days="$2"
  if ! aws logs describe-log-groups --log-group-name-prefix "$group" \
       --query "logGroups[?logGroupName=='${group}'].logGroupName" --output text | grep -q .; then
    echo "skip (not found): $group"
    return
  fi
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "would set $days days: $group"
  else
    aws logs put-retention-policy --log-group-name "$group" --retention-in-days "$days"
    echo "set $days days: $group"
  fi
}

for g in "${LAMBDA_GROUPS[@]}"; do set_retention "$g" "$LAMBDA_DAYS"; done
for g in "${APIGW_GROUPS[@]}"; do set_retention "$g" "$APIGW_DAYS"; done

# API Gateway 実行ログ（サービス管理の自動作成グループ）: 名前に API ID を含むため列挙して設定
while IFS= read -r g; do
  [[ -z "$g" ]] && continue
  set_retention "$g" "$APIGW_DAYS"
done < <(aws logs describe-log-groups --log-group-name-prefix "API-Gateway-Execution-Logs_" \
          --query 'logGroups[].logGroupName' --output text | tr '\t' '\n')

# Lambda の DomainGuard は論理 ID 由来の自動命名のため前方一致で設定
while IFS= read -r g; do
  [[ -z "$g" ]] && continue
  set_retention "$g" "$LAMBDA_DAYS"
done < <(aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/EleKnowledge-${ENV}-phase1-DomainGuardFunction" \
          --query 'logGroups[].logGroupName' --output text | tr '\t' '\n')

echo "done"
