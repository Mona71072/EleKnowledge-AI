#!/usr/bin/env python3
"""Plan, add and verify Ele-Knowledge cost tags without changing workloads.

The plan is account-bound. Existing classification conflicts stop the operation.
Snapshots and results contain internal ARNs: keep them in an ignored directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

KEYS = ("gyoumu012Project", "gyoumu012Component", "gyoumu012Usage")
PROJECT_VALUES = {"EleKnowledge", "EleKnowledge-AI"}
COMPONENTS = {
    "rag", "legal-rag", "monitoring", "shared", "troubleshooting", "announcements",
}
USAGES = {"development", "user", "shared"}


def component_for(arn: str, tags: dict[str, str]) -> str:
    """Classify only resources whose project ownership was already established."""
    name = arn.lower()
    stack = tags.get("aws:cloudformation:stack-name", "").lower()
    logical = tags.get("aws:cloudformation:logical-id", "").lower()
    if ":cloudwatch:" in name or ":alarm:" in name:
        return "monitoring"
    if (
        "law" in stack or "legal-rag" in name
        or "lawrag" in tags.get("Purpose", "").lower()
    ):
        return "legal-rag"
    if (
        "troubleshooting" in stack
        or re.search(
            r"(?:function:|/aws/lambda/)(orchestrator|kb-search-|db-search-|"
            r"history-|troubleshooting-small)", name,
        )
        or re.search(r"table/(sites|sessions)-dev$", name)
    ):
        return "troubleshooting"
    if (
        any(word in name for word in (
            "metrics-", "metrics/", "metrics-dev", "analytics", "athena", "alerts-",
        ))
        or stack == "eleknowledge-monitoring-dev" or "metrics" in logical
    ):
        return "monitoring"
    if (
        logical in {"appapi", "appapistage", "appapiloggroup"}
        or "/aws/apigateway/announcements-monitoring-api-" in name
    ):
        return "shared"
    if "announcements" in name or "announcements" in logical:
        return "announcements"
    if (
        any(word in name for word in (
            "function:rag-", "/aws/lambda/rag-", "rag-api-",
            "application-inference-profile/", "documents-dev-", "/knowledge-base-id",
        ))
        or logical in {
            "ragfunction", "ragapi", "ragapistage", "documentsbucket", "ragapiloggroup",
        }
    ):
        return "rag"
    return "shared"


def skip_reason(arn: str) -> str | None:
    """Avoid CloudFormation updates and children with inherited table tags."""
    if ":cloudformation:" in arn:
        return "stack metadata: use normal IaC deployment"
    if ":dynamodb:" in arn and "/stream/" in arn:
        return "stream inherits parent table tags"
    if ":budgets:" in arn:
        return "budget metadata has no resource usage cost"
    return None


def desired_tags(
    component: str, default_usage: str, poc_usage: str,
) -> dict[str, str]:
    usage = (
        poc_usage if component in {"legal-rag", "troubleshooting"} else default_usage
    )
    return dict(zip(KEYS, ("ele-knowledge", component, usage)))


def validate_resource(resource: dict, account: str) -> None:
    arn = resource["arn"]
    parts = arn.split(":", 5)
    if len(parts) != 6 or parts[0] != "arn" or parts[4] not in {"", account}:
        raise ValueError("Resource ARN does not belong to the expected account")
    if skip_reason(arn):
        raise ValueError("Unsafe or inherited resource in apply plan")
    wanted = resource["desired"]
    if (
        set(wanted) != set(KEYS) or wanted[KEYS[0]] != "ele-knowledge"
        or wanted[KEYS[1]] not in COMPONENTS or wanted[KEYS[2]] not in USAGES
    ):
        raise ValueError("Invalid cost tag vocabulary")
    before = resource["before"]
    if "Project" in before and before["Project"] not in PROJECT_VALUES:
        raise ValueError("Conflicting legacy project ownership")
    if (
        before.get("Project") not in PROJECT_VALUES
        and before.get(KEYS[0]) != "ele-knowledge"
        and not resource.get("owner") and not resource.get("owner_stack")
    ):
        raise ValueError("Project ownership not established")
    for key, value in wanted.items():
        if key in before and before[key] != value:
            raise ValueError(f"Existing classification conflict: {key}")


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )


def read_tags(session, region: str, arn: str) -> dict[str, str]:
    """Read exact ARN tags, including services not supported by GetResources."""
    service = arn.split(":")[2]
    if service == "apigateway":
        return session.client("apigateway", region_name=region).get_tags(
            resourceArn=arn,
        )["tags"]
    if service == "bedrock":
        api = "bedrock-agent" if ":knowledge-base/" in arn else "bedrock"
        client = session.client(api, region_name=region)
        response = (
            client.list_tags_for_resource(resourceArn=arn)
            if api == "bedrock-agent"
            else client.list_tags_for_resource(resourceARN=arn)
        )
        rows = response["tags"]
        if isinstance(rows, dict):
            return rows
        return {t["key"]: t["value"] for t in rows}
    if service == "s3":
        rows = session.client("s3", region_name=region).get_bucket_tagging(
            Bucket=arn.split(":::", 1)[1],
        )["TagSet"]
        return {t["Key"]: t["Value"] for t in rows}
    if service == "logs":
        return session.client("logs", region_name=region).list_tags_for_resource(
            resourceArn=arn,
        )["tags"]
    if service == "lambda":
        return session.client("lambda", region_name=region).list_tags(
            Resource=arn,
        )["Tags"]
    if service == "dynamodb":
        tags = {}
        client = session.client("dynamodb", region_name=region)
        request = {"ResourceArn": arn}
        while True:
            response = client.list_tags_of_resource(**request)
            tags.update({t["Key"]: t["Value"] for t in response["Tags"]})
            if not response.get("NextToken"):
                return tags
            request["NextToken"] = response["NextToken"]
    client = session.client("resourcegroupstaggingapi", region_name=region)
    response = client.get_resources(ResourceARNList=[arn])
    rows = response["ResourceTagMappingList"]
    if len(rows) != 1 or rows[0]["ResourceARN"] != arn:
        raise ValueError("Resource could not be re-read; success is unconfirmed")
    return {t["Key"]: t["Value"] for t in rows[0]["Tags"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--expected-account", required=True)
    parser.add_argument(
        "--regions", nargs="+",
        default=["ap-northeast-1", "us-east-1", "ap-northeast-3"],
    )
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--default-usage", choices=sorted(USAGES), default="shared")
    parser.add_argument("--poc-usage", choices=sorted(USAGES), default="development")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true")
    action.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    import boto3
    session = boto3.Session(profile_name=args.profile)
    account = session.client("sts").get_caller_identity()["Account"]
    if account != args.expected_account:
        raise ValueError("Authenticated account does not match expected account")
    if args.apply or args.verify:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        if plan["account"] != account:
            raise ValueError("Plan belongs to a different account")
        for resource in plan["resources"]:
            validate_resource(resource, account)
        # Preflight all resources before the first write.
        live_tags = {}
        for resource in plan["resources"] if args.apply else []:
            current = read_tags(session, resource["region"], resource["arn"])
            live_tags[resource["arn"]] = current
            if current.get("Project") != resource["before"].get("Project"):
                raise ValueError("Project ownership changed since planning")
            if resource.get("owner"):
                owner_tags = read_tags(
                    session, resource["region"], resource["owner"],
                )
                if owner_tags.get("Project") not in PROJECT_VALUES:
                    raise ValueError("Parent workload project ownership changed")
            if resource.get("owner_stack"):
                client = session.client(
                    "cloudformation", region_name=resource["region"],
                )
                stack = client.describe_stacks(
                    StackName=resource["owner_stack"],
                )["Stacks"][0]
                tags = {t["Key"]: t["Value"] for t in stack.get("Tags", [])}
                members = client.list_stack_resources(
                    StackName=resource["owner_stack"],
                )["StackResourceSummaries"]
                owned_member = any(
                    r["before"].get("Project") in PROJECT_VALUES
                    and r["before"].get("aws:cloudformation:stack-id")
                    == stack["StackId"]
                    for r in plan["resources"]
                )
                if (
                    tags.get("Project") not in PROJECT_VALUES and not owned_member
                ) or not any(
                    m.get("PhysicalResourceId") == resource["physical_id"]
                    for m in members
                ):
                    raise ValueError("CloudFormation ownership not established")
            if args.apply and any(
                k in current and current[k] != v
                for k, v in resource["desired"].items()
            ):
                raise ValueError("Live classification conflicts with the plan")
        results = []
        result_path = args.plan.with_name(args.plan.stem + "-results.json")
        for resource in plan["resources"]:
            entry = {
                "arn": resource["arn"], "region": resource["region"],
                "desired": resource["desired"],
            }
            try:
                current = live_tags.get(resource["arn"], {})
                needs_write = args.apply and any(
                    current.get(k) != v for k, v in resource["desired"].items()
                )
                if needs_write:
                    service = resource["arn"].split(":")[2]
                    if service == "bedrock":
                        if ":knowledge-base/" in resource["arn"]:
                            client = session.client(
                                "bedrock-agent", region_name=resource["region"],
                            )
                            client.tag_resource(
                                resourceArn=resource["arn"],
                                tags=resource["desired"],
                            )
                        else:
                            client = session.client(
                                "bedrock", region_name=resource["region"],
                            )
                            client.tag_resource(
                                resourceARN=resource["arn"],
                                tags=[
                                    {"key": k, "value": v}
                                    for k, v in resource["desired"].items()
                                ],
                            )
                    else:
                        client = session.client(
                            "resourcegroupstaggingapi",
                            region_name=resource["region"],
                        )
                        response = client.tag_resources(
                            ResourceARNList=[resource["arn"]],
                            Tags=resource["desired"],
                        )
                        if response.get("FailedResourcesMap"):
                            raise RuntimeError(
                                json.dumps(response["FailedResourcesMap"]),
                            )
                if needs_write or not args.apply:
                    current = read_tags(
                        session, resource["region"], resource["arn"],
                    )
                entry["verified"] = all(
                    current.get(k) == v for k, v in resource["desired"].items()
                )
                # Never silently remove or alter a pre-existing unrelated tag.
                entry["preserved"] = all(
                    current.get(k) == v
                    for k, v in resource["before"].items() if k not in KEYS
                )
            except Exception as exc:
                entry.update(verified=False, error=str(exc))
            results.append(entry)
            save(result_path, {"account": account, "results": results})
        failed = [
            r for r in results
            if not r["verified"] or not r.get("preserved", False)
        ]
        print(json.dumps({
            "total": len(results), "verified": len(results) - len(failed),
            "failed": len(failed), "results_file": str(result_path),
        }))
        return bool(failed)
    resources, skipped = [], []
    for region in args.regions:
        client = session.client("resourcegroupstaggingapi", region_name=region)
        discovered = {}
        filters = [
            {"Key": "Project", "Values": sorted(PROJECT_VALUES)},
            {"Key": KEYS[0], "Values": ["ele-knowledge"]},
        ]
        for tag_filter in filters:
            for page in client.get_paginator("get_resources").paginate(
                TagFilters=[tag_filter],
            ):
                for row in page["ResourceTagMappingList"]:
                    discovered[row["ResourceARN"]] = row
        for row in discovered.values():
            arn = row["ResourceARN"]
            tags = {t["Key"]: t["Value"] for t in row["Tags"]}
            reason = skip_reason(arn)
            if reason:
                skipped.append({"arn": arn, "reason": reason})
                continue
            component = component_for(arn, tags)
            resources.append({
                "arn": arn, "region": region, "before": tags,
                "desired": desired_tags(
                    component, args.default_usage, args.poc_usage,
                ),
            })
        # SAM-generated REST APIs/stages are not always tagged. Establish
        # ownership through a tagged stack rather than resource name alone.
        cloudformation = session.client("cloudformation", region_name=region)
        existing_arns = {r["arn"] for r in resources}
        known_stack_ids = {
            r["before"].get("aws:cloudformation:stack-id")
            for r in resources if r["region"] == region
            and r["before"].get("Project") in PROJECT_VALUES
        }
        for stack_page in cloudformation.get_paginator("describe_stacks").paginate():
            for stack in stack_page["Stacks"]:
                stack_tags = {
                    t["Key"]: t["Value"] for t in stack.get("Tags", [])
                }
                if (
                    stack_tags.get("Project") not in PROJECT_VALUES
                    and stack["StackId"] not in known_stack_ids
                ):
                    continue
                members = []
                for member_page in cloudformation.get_paginator(
                    "list_stack_resources",
                ).paginate(StackName=stack["StackId"]):
                    members.extend(member_page["StackResourceSummaries"])
                api_ids = {
                    m["LogicalResourceId"]: m["PhysicalResourceId"]
                    for m in members
                    if m["ResourceType"] == "AWS::ApiGateway::RestApi"
                }
                for member in members:
                    kind = member["ResourceType"]
                    logical = member["LogicalResourceId"]
                    physical = member.get("PhysicalResourceId")
                    if kind == "AWS::ApiGateway::RestApi":
                        suffix = f"/restapis/{physical}"
                    elif kind == "AWS::ApiGateway::Stage":
                        api_id = api_ids.get(logical.removesuffix("Stage"))
                        if not api_id:
                            continue
                        suffix = f"/restapis/{api_id}/stages/{physical}"
                    else:
                        continue
                    arn = f"arn:aws:apigateway:{region}::{suffix}"
                    if arn in existing_arns:
                        continue
                    tags = read_tags(session, region, arn)
                    if tags.get("Project", "EleKnowledge") not in PROJECT_VALUES:
                        raise ValueError("Stack API has conflicting ownership")
                    comp = component_for(arn, {
                        "aws:cloudformation:stack-name": stack["StackName"],
                        "aws:cloudformation:logical-id": logical,
                    })
                    resources.append({
                        "arn": arn, "region": region, "before": tags,
                        "desired": desired_tags(
                            comp, args.default_usage, args.poc_usage,
                        ),
                        "owner_stack": stack["StackId"],
                        "physical_id": physical,
                    })
                    existing_arns.add(arn)
        # Logs can exist without any tag and are absent from GetResources.
        # Match exact log group names to already-owned Lambda/API resources.
        parents = {}
        for resource in resources:
            if resource["region"] != region:
                continue
            arn = resource["arn"]
            if ":lambda:" in arn and ":function:" in arn:
                name = "/aws/lambda/" + arn.split(":function:", 1)[1]
                parents[name] = resource
            elif ":apigateway:" in arn and re.fullmatch(
                r"/restapis/[^/]+", arn.split(":", 5)[5],
            ):
                api_id = arn.rsplit("/", 1)[1]
                parents[f"API-Gateway-Execution-Logs_{api_id}/dev"] = resource
        logs = session.client("logs", region_name=region)
        existing = {r["arn"]: r for r in resources}
        for page in logs.get_paginator("describe_log_groups").paginate():
            for group in page["logGroups"]:
                parent = parents.get(group["logGroupName"])
                if parent is None:
                    continue
                arn = group.get("logGroupArn") or group["arn"].removesuffix(":*")
                wanted = parent["desired"].copy()
                if arn in existing:
                    existing[arn]["desired"] = wanted
                else:
                    tags = logs.list_tags_for_resource(resourceArn=arn)["tags"]
                    if "Project" in tags and tags["Project"] not in PROJECT_VALUES:
                        raise ValueError("Workload log has conflicting project tag")
                    resources.append({
                        "arn": arn, "region": region, "before": tags,
                        "desired": wanted, "owner": parent["arn"],
                    })
    for resource in resources:
        validate_resource(resource, account)
    plan = {
        "account": account,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resources": resources, "skipped": skipped,
    }
    save(args.plan, plan)
    print(json.dumps({
        "resources": len(resources), "skipped": len(skipped),
        "components": dict(Counter(r["desired"][KEYS[1]] for r in resources)),
        "usages": dict(Counter(r["desired"][KEYS[2]] for r in resources)),
    }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"Cost tag operation stopped: {error}", file=sys.stderr)
        sys.exit(1)
