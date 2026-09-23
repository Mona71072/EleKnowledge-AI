#!/usr/bin/env python3
"""EleKnowledge のロググループに保持期間を設定する（issue #86 の決定）。

方針（2026-09-09 itai 決定）: 利用価値・監査価値があるものは残す。
  - Lambda アプリログ          : 365 日
  - API Gateway 実行ログ       : 90 日（本文を含まず障害切り分け用）
  - API Gateway アクセスログ枠 : 90 日

対象は **EleKnowledge の関数名 / API 名で明示的に限定** する（同一リージョンの他システム・
別環境のロググループには触れない。PR #92 レビュー指摘）。

使い方:
  AWS_PROFILE=<profile> AWS_REGION=ap-northeast-1 python scripts/ops/set_log_retention.py --env dev [--dry-run]
"""
from __future__ import annotations

import argparse
import sys

LAMBDA_DAYS = 365
APIGW_DAYS = 90

# 関数名（{env} を置換）。ロググループは /aws/lambda/<name>
LAMBDA_FUNCTION_NAMES = [
    "rag-{env}", "chat-{env}", "login-{env}", "signup-{env}", "verify-{env}",
    "metrics-read-{env}", "metrics-aggregator-{env}",
    "announcements-read-{env}", "announcements-write-{env}", "announcements-publisher-{env}",
    "eleknowledge-chat-archive-{env}", "eleknowledge-cognito-domain-guard-{env}",
    "orchestrator-{env}", "db-search-{env}", "kb-search-cases-{env}", "kb-search-manuals-{env}",
    "kb-search-materials-{env}", "history-{env}",
]
# 論理 ID 由来の自動命名（前方一致）
LAMBDA_GROUP_PREFIXES = ["/aws/lambda/EleKnowledge-{env}-phase1-DomainGuardFunction"]
# REST API 名（{env} を置換）。実行ログは API-Gateway-Execution-Logs_<apiId>/<stage>
API_NAMES = [
    "auth-api-{env}", "chat-api-{env}", "rag-api-{env}",
    "announcements-monitoring-api-{env}", "troubleshooting-api-{env}",
]
# 明示宣言済みのアクセスログ枠
APIGW_ACCESS_LOG_GROUPS = [
    "/aws/apigateway/auth-api-{env}", "/aws/apigateway/chat-api-{env}", "/aws/apigateway/rag-api-{env}",
]


def select_targets(env: str, existing_groups: set[str], rest_apis: dict[str, str]) -> list[tuple[str, int]]:
    """(ロググループ名, 保持日数) の一覧を返す。存在しないグループは含めない。

    rest_apis: {apiId: apiName}
    """
    targets: list[tuple[str, int]] = []
    for name in LAMBDA_FUNCTION_NAMES:
        g = f"/aws/lambda/{name.format(env=env)}"
        if g in existing_groups:
            targets.append((g, LAMBDA_DAYS))
    for prefix in LAMBDA_GROUP_PREFIXES:
        p = prefix.format(env=env)
        for g in sorted(existing_groups):
            if g.startswith(p):
                targets.append((g, LAMBDA_DAYS))
    for g in APIGW_ACCESS_LOG_GROUPS:
        gg = g.format(env=env)
        if gg in existing_groups:
            targets.append((gg, APIGW_DAYS))
    wanted_api_names = {n.format(env=env) for n in API_NAMES}
    for api_id, api_name in sorted(rest_apis.items()):
        if api_name not in wanted_api_names:
            continue
        g = f"API-Gateway-Execution-Logs_{api_id}/{env}"
        if g in existing_groups:
            targets.append((g, APIGW_DAYS))
    return targets


def load_aws_state(region: str):
    import boto3
    logs = boto3.client("logs", region_name=region)
    apigw = boto3.client("apigateway", region_name=region)
    groups: set[str] = set()
    for page in logs.get_paginator("describe_log_groups").paginate():
        groups.update(g["logGroupName"] for g in page.get("logGroups", []))
    apis: dict[str, str] = {}
    for page in apigw.get_paginator("get_rest_apis").paginate():
        apis.update({a["id"]: a["name"] for a in page.get("items", [])})
    return logs, groups, apis


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--env", default="dev")
    p.add_argument("--region", default="ap-northeast-1")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)

    logs, groups, apis = load_aws_state(a.region)
    targets = select_targets(a.env, groups, apis)
    for group, days in targets:
        if a.dry_run:
            print(f"would set {days} days: {group}")
        else:
            logs.put_retention_policy(logGroupName=group, retentionInDays=days)
            print(f"set {days} days: {group}")
    print(f"done ({len(targets)} groups)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
