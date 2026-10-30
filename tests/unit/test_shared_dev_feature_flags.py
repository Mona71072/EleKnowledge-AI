from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _setting(text: str, name: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(name)}:\s*['\"]?([^\s'\"#]+)", text, re.MULTILINE)
    return match.group(1).lower() if match else None


def test_amplify_shared_dev_keeps_knowledge_workbench_disabled() -> None:
    amplify = (ROOT / "amplify.yml").read_text(encoding="utf-8")
    assert _setting(amplify, "NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH") == "false"


def test_sam_prototype_resource_flags_default_off() -> None:
    template = (ROOT / "infrastructure/sam/phase2-template.yaml").read_text(encoding="utf-8")
    for name in ("KnowhowEnabled", "SenpaiSynthesisEnabled", "SenpaiFieldReportsEnabled", "SenpaiResearchEnabled"):
        block = re.search(rf"^  {name}:\n(?P<body>(?:^    .*\n|^\n)*)", template, re.MULTILINE)
        assert block, f"{name} parameter is missing"
        assert re.search(r"^    Default:\s*['\"]false['\"]\s*$", block.group("body"), re.MULTILINE), name
