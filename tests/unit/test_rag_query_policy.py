"""Parity tests for the extracted pure query policy module."""
import importlib.util
import os
import sys

import pytest

BASE = os.path.join(os.path.dirname(__file__), "../..")
RAG_DIR = os.path.normpath(os.path.join(BASE, "lambda/rag/rag-function"))


def _load(name: str, filename: str):
    path = os.path.join(RAG_DIR, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def modules():
    os.environ.setdefault("CHATLOGS_TABLE", "test-chatlogs")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    return _load("rag_query_policy_legacy", "app.py"), _load("rag_query_policy_new", "query_policy.py")


@pytest.mark.parametrize(
    "text",
    [
        "  ＡＸＩＥＺ　 火管  ",
        "現調で寸法が合わない",
        "地震管制の条件は？",
        "",
    ],
)
def test_normalize_query_text_matches_existing_behavior(modules, text):
    legacy, new = modules
    assert new.normalize_query_text(text) == legacy.normalize_query_text(text)


@pytest.mark.parametrize(
    "text",
    ["火管の動作", "震管", "現調で確認", "未知語", ""],
)
def test_abbreviation_expansion_matches_existing_behavior(modules, text):
    legacy, new = modules
    assert new.expand_query_abbreviations(text) == legacy.expand_query_abbreviations(text)


@pytest.mark.parametrize(
    "query,filters,history",
    [
        ("振動がする", {}, []),
        ("振動がする", {"modelType": "AXIEZ"}, []),
        ("かごが振動する", {"modelType": "AXIEZ"}, []),
        ("地震管制で最寄階に停止する条件は？", {}, []),
        (
            "かご、走行中です",
            {},
            [
                {"role": "user", "content": "異音がする"},
                {"role": "assistant", "content": "該当ページを探すために教えてください\n1. 機種"},
            ],
        ),
    ],
)
def test_clarification_decision_matches_existing_behavior(modules, query, filters, history):
    legacy, new = modules
    assert new.needs_clarify(query, filters, history) == legacy.needs_clarify(query, filters, history)


def test_followup_composition_matches_existing_behavior(modules):
    legacy, new = modules
    history = [
        {"role": "user", "content": "エレベーターから異音がする"},
        {"role": "assistant", "content": legacy.CLARIFY_MARKER + "\n1. 機種"},
    ]
    assert new.compose_search_query("かご、走行中です", history) == legacy.compose_search_query(
        "かご、走行中です", history
    )


@pytest.mark.parametrize(
    "mode,filters",
    [
        ("normal", {}),
        ("spec", {}),
        ("spec", {"category": "drawing", "modelType": "AXIEZ"}),
        ("unknown", {"category": []}),
    ],
)
def test_mode_normalization_matches_existing_behavior(modules, mode, filters):
    legacy, new = modules
    assert new.normalize_mode_and_filters(mode, filters) == legacy.normalize_mode_and_filters(mode, filters)


@pytest.mark.parametrize(
    "filters",
    [{}, {"category": "drawing"}, {"category": ["spec", "std"]}],
)
def test_not_found_copy_matches_existing_behavior(modules, filters):
    legacy, new = modules
    assert new.build_not_found_content(filters) == legacy.build_not_found_content(filters)
