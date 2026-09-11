"""保持期間スクリプトの対象選定が EleKnowledge の対象環境に限定されることを検証する（PR #92 レビュー指摘）。"""
import importlib.util
import os

BASE = os.path.join(os.path.dirname(__file__), "../..")
spec = importlib.util.spec_from_file_location(
    "set_log_retention", os.path.normpath(os.path.join(BASE, "scripts/ops/set_log_retention.py")))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


EXISTING = {
    "/aws/lambda/rag-dev", "/aws/lambda/chat-dev", "/aws/lambda/rag-prd",
    "/aws/lambda/otherapp-worker", "/aws/lambda/EleKnowledge-dev-phase1-DomainGuardFunction-abc123",
    "/aws/apigateway/rag-api-dev", "/aws/apigateway/rag-api-prd",
    "API-Gateway-Execution-Logs_aaaa111111/dev",   # rag-api-dev
    "API-Gateway-Execution-Logs_bbbb222222/dev",   # other app (same stage name)
    "API-Gateway-Execution-Logs_cccc333333/prd",   # rag-api-prd
    "API-Gateway-Execution-Logs_aaaa111111/prd",   # EleKnowledge api id but different stage
}
APIS = {"aaaa111111": "rag-api-dev", "bbbb222222": "otherapp-api-dev", "cccc333333": "rag-api-prd"}


def test_only_eleknowledge_dev_groups_selected():
    targets = dict(mod.select_targets("dev", EXISTING, APIS))
    assert targets == {
        "/aws/lambda/rag-dev": 365,
        "/aws/lambda/chat-dev": 365,
        "/aws/lambda/EleKnowledge-dev-phase1-DomainGuardFunction-abc123": 365,
        "/aws/apigateway/rag-api-dev": 90,
        "API-Gateway-Execution-Logs_aaaa111111/dev": 90,
    }


def test_other_apps_and_other_envs_untouched():
    selected = {g for g, _ in mod.select_targets("dev", EXISTING, APIS)}
    for untouched in (
        "/aws/lambda/rag-prd", "/aws/lambda/otherapp-worker", "/aws/apigateway/rag-api-prd",
        "API-Gateway-Execution-Logs_bbbb222222/dev", "API-Gateway-Execution-Logs_cccc333333/prd",
        "API-Gateway-Execution-Logs_aaaa111111/prd",
    ):
        assert untouched not in selected


def test_missing_groups_are_skipped():
    assert mod.select_targets("dev", set(), APIS) == []
