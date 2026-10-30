import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validation" / "lint_sam_templates.py"
SPEC = importlib.util.spec_from_file_location("lint_sam_templates", SCRIPT)
lint_sam_templates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lint_sam_templates)


def test_nonzero_linter_exit_without_json_findings_fails(tmp_path, monkeypatch):
    root = tmp_path
    template_dir = root / "infrastructure" / "sam"
    template_dir.mkdir(parents=True)
    expected_by_file = {}
    for relative, rule_id, location, message_prefix in lint_sam_templates.ALLOWLIST:
        template = root / relative
        template.parent.mkdir(parents=True, exist_ok=True)
        template.touch(exist_ok=True)
        expected_by_file.setdefault(relative, []).append({
            "Filename": str(template),
            "Rule": {"Id": rule_id},
            "Location": {"Path": list(location)},
            "Message": message_prefix + " documented schema value",
        })

    extra = template_dir / "unexpected.yaml"
    extra.touch()
    monkeypatch.setattr(lint_sam_templates, "ROOT", root)
    monkeypatch.setattr(lint_sam_templates, "TEMPLATES", template_dir)

    def fake_run(command, **_kwargs):
        template = Path(command[-1])
        relative = template.relative_to(root).as_posix()
        if relative == "infrastructure/sam/unexpected.yaml":
            return type("Result", (), {"returncode": 1, "stdout": "[]", "stderr": "lint failed"})()
        findings = expected_by_file.get(relative, [])
        return type("Result", (), {"returncode": 1 if findings else 0, "stdout": json.dumps(findings), "stderr": ""})()

    monkeypatch.setattr(lint_sam_templates.subprocess, "run", fake_run)

    assert lint_sam_templates.main() == 1
