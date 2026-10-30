#!/usr/bin/env python3
"""Lint every SAM/CloudFormation template and fail on findings outside a narrow legacy allowlist."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "infrastructure" / "sam"

# cfn-lint 1.46.0's CloudFormation schema lags the documented Bedrock MANAGED
# Knowledge Base/connector properties. Keep each exception tied to its exact
# resource path and expected message; a new or moved finding remains a failure.
ALLOWLIST = {
    (
        "infrastructure/sam/legal-rag-kb-template.yaml",
        "E3030",
        ("Resources", "LawKnowledgeBase", "Properties", "KnowledgeBaseConfiguration", "Type"),
        "'MANAGED' is not one of",
    ),
    (
        "infrastructure/sam/legal-rag-kb-template.yaml",
        "E3002",
        ("Resources", "LawKnowledgeBase", "Properties", "KnowledgeBaseConfiguration", "ManagedKnowledgeBaseConfiguration"),
        "Additional properties are not allowed (",
    ),
    (
        "infrastructure/sam/legal-rag-kb-template.yaml",
        "E3030",
        ("Resources", "CurrentLawsDataSource", "Properties", "DataSourceConfiguration", "Type"),
        "'MANAGED_KNOWLEDGE_BASE_CONNECTOR' is not one of",
    ),
    (
        "infrastructure/sam/legal-rag-kb-template.yaml",
        "E3002",
        ("Resources", "CurrentLawsDataSource", "Properties", "DataSourceConfiguration", "ManagedKnowledgeBaseConnectorConfiguration"),
        "Additional properties are not allowed (",
    ),
    # This template is explicitly documented as an old POC; do not mistake it
    # for the active Phase 3 stack. Its Python 3.8 runtime is not deployable.
    (
        "infrastructure/sam/phase3-troubleshooting-small.yaml",
        "E2533",
        ("Resources", "TroubleshootingSmallOrchestratorFunction", "Properties", "Runtime"),
        "Runtime 'python3.8' was deprecated",
    ),
}


def main() -> int:
    templates = sorted(TEMPLATES.glob("*.yaml"))
    if not templates:
        print(f"No SAM templates found under {TEMPLATES}", file=sys.stderr)
        return 2

    seen = set()
    unexpected = []
    for template in templates:
        result = subprocess.run(
            ["cfn-lint", "--format", "json", str(template)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode not in (0, 1, 2):
            print(result.stderr, file=sys.stderr)
            return result.returncode
        try:
            findings = json.loads(result.stdout or "[]")
        except json.JSONDecodeError as error:
            print(f"Could not parse cfn-lint JSON for {template}: {error}", file=sys.stderr)
            return 2
        if result.returncode != 0 and not findings:
            print(
                f"cfn-lint exited {result.returncode} without JSON findings for {template}: {result.stderr.strip()}",
                file=sys.stderr,
            )
            return 1

        for finding in findings:
            key = (
                Path(finding["Filename"]).resolve().relative_to(ROOT).as_posix(),
                finding["Rule"]["Id"],
                tuple(finding["Location"]["Path"]),
                finding["Message"],
            )
            exact = next((allowed for allowed in ALLOWLIST if (
                key[0], key[1], key[2]
            ) == allowed[:3] and key[3].startswith(allowed[3])), None)
            if exact:
                seen.add(exact)
                print(f"KNOWN LIMITATION: {key[0]} {key[1]} {'/'.join(key[2])}: {key[3]}")
            else:
                unexpected.append(f"{key[0]} {key[1]} {'/'.join(key[2])}: {key[3]}")

    missing = ALLOWLIST - seen
    if unexpected or missing:
        if unexpected:
            print("Unexpected cfn-lint findings:", file=sys.stderr)
            print("\n".join(unexpected), file=sys.stderr)
        if missing:
            print("Previously known findings changed; review and update the narrow allowlist:", file=sys.stderr)
            print("\n".join(f"{item[0]} {item[1]} {'/'.join(item[2])}" for item in sorted(missing)), file=sys.stderr)
        return 1

    print(f"PASS: {len(templates)} templates linted; {len(seen)} documented limitations matched exactly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
