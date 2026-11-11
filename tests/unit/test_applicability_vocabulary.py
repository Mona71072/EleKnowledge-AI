"""適用範囲の語彙（knowledge/registry/applicability-vocabulary.json）を正本として照合する。

語彙ファイルは APPLICABILITY-TAXONOMY.md をもとに作成し、値の正本として運用する。
次がこの語彙と一致することを確かめる。

- 画面の機種一覧（frontend/src/data/kbModelTypes.ts）と、サーバーの UI_MODEL_FILTERS（app.py）
- ノウハウ検索の機種の別名（knowhow_retrieval.py の MODEL_ALIASES。索引作成側とは既存の同期テストで一致）
- 調査ジョブが質問中の機種を判定する呼び名（senpai_research_understand.py の MODEL_ALIASES）
- テーマカードの model_scope に書かれた値

症状・部位・条件（symptoms / conditions）と、原文を写す欄（lists_model_label など）は対象外。
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import unicodedata
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
VOCAB_PATH = ROOT / "knowledge/registry/applicability-vocabulary.json"
CARDS = ROOT / "knowledge/cards"
FRONTEND_MODELS = ROOT / "frontend/src/data/kbModelTypes.ts"
RAG_APP = ROOT / "lambda/rag/rag-function/app.py"
RETRIEVAL = ROOT / "lambda/rag/rag-function/knowhow_retrieval.py"
UNDERSTAND = ROOT / "lambda/rag/rag-function/senpai_research_understand.py"
AXES = ("product_lines", "machine_room", "control_methods", "model_abbreviations",
        "guide_systems", "door_families", "door_types")
# 2026-11-11 時点で、検索の機種フィルタ（knowhow_retrieval.MODEL_ALIASES）が認識しない許容の表記。
KNOWN_FILTER_GAPS = ["MELCITY", "MELWIDE"]


def _vocab() -> dict:
    return json.loads(VOCAB_PATH.read_text(encoding="utf-8"))


def _norm(value: str) -> str:
    return unicodedata.normalize("NFKC", value).lower().strip()


def _retrieval():
    spec = importlib.util.spec_from_file_location("knowhow_retrieval_vocab", RETRIEVAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ui_entries(vocab: dict) -> dict:
    return {e["ui_filter"]["key"]: e for e in vocab["axes"]["product_lines"] if e.get("ui_filter")}


def _py_tuple_map(path: Path, name: str) -> dict:
    """`NAME = { 'KEY': ('a', 'b'), ... }` を読む（Lambda を import せずに照合するため）。"""
    text = path.read_text(encoding="utf-8")
    block = re.search(rf"^{name} = \{{(.*?)^\}}", text, re.DOTALL | re.MULTILINE)
    assert block, f"{name} not found in {path.name}"
    result = ast.literal_eval("{" + block.group(1) + "}")
    assert result, f"{name} is empty in {path.name}"
    return {key: tuple(values) for key, values in result.items()}


def _frontend_models() -> dict:
    text = FRONTEND_MODELS.read_text(encoding="utf-8")
    block = re.search(r"export const ALL_MODEL_TYPES[^=]*=\s*\[(.*?)\];", text, re.DOTALL)
    assert block, "ALL_MODEL_TYPES not found"
    result = {}
    for value, targets in re.findall(r"value:\s*'([^']+)'.*?targets:\s*\[([^\]]*)\]", block.group(1), re.DOTALL):
        result[value] = tuple(re.findall(r"'([^']+)'", targets))
    return result


def _card_scopes():
    for path in sorted(CARDS.glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.match(r"---\r?\n(.*?)\r?\n---", text, re.DOTALL)
        assert match, f"frontmatter not found: {path.name}"
        meta = yaml.safe_load(match.group(1)) or {}
        yield path, (meta.get("model_scope") or {})


# --- 語彙ファイルそのもの -------------------------------------------------------

def test_vocabulary_has_all_axes_and_unique_terms():
    vocab = _vocab()
    assert set(vocab["axes"]) == set(AXES)
    for axis, entries in vocab["axes"].items():
        seen = {}
        for entry in entries:
            for term in [entry["value"], *entry.get("admitted", []), *entry.get("deprecated", [])]:
                assert term not in seen, f"{axis}: '{term}' が '{seen[term]}' と '{entry['value']}' に重複"
                seen[term] = entry["value"]


def test_misplaced_entries_point_to_known_values():
    vocab = _vocab()
    for item in vocab["misplaced"]:
        assert item["axis"] in AXES
        if item["move_to_axis"] is not None:
            targets = {e["value"] for e in vocab["axes"][item["move_to_axis"]]}
            assert item["move_to_value"] in targets, f"{item['value']} の移し先 {item['move_to_value']} が語彙に無い"


def test_related_values_exist_in_their_axes():
    vocab = _vocab()
    for entry in vocab["axes"]["product_lines"]:
        for axis, values in (entry.get("related") or {}).items():
            known = {e["value"] for e in vocab["axes"][axis]}
            missing = set(values) - known
            assert not missing, f"{entry['value']} の related.{axis} に語彙に無い値: {sorted(missing)}"


# --- コードとの一致 ---------------------------------------------------------------

def test_frontend_model_list_matches_vocabulary():
    expected = {key: tuple(e["ui_filter"]["kb_model_types"]) for key, e in _ui_entries(_vocab()).items()}
    assert _frontend_models() == expected


def test_server_ui_model_filters_match_vocabulary():
    expected = {key: tuple(e["ui_filter"]["kb_model_types"]) for key, e in _ui_entries(_vocab()).items()}
    assert _py_tuple_map(RAG_APP, "UI_MODEL_FILTERS") == expected


def test_retrieval_model_aliases_match_vocabulary():
    module = _retrieval()
    expected = {
        key: {_norm(v) for v in e["ui_filter"]["kb_model_types"] + e["ui_filter"]["extra_card_aliases"]}
        for key, e in _ui_entries(_vocab()).items()
    }
    assert {key: set(values) for key, values in module.MODEL_ALIASES.items()} == expected
    labels = _vocab()["generic_labels"]
    assert module.GENERIC_ELEVATOR_LABEL == labels["elevator"]
    assert module.GENERIC_ESCALATOR_LABEL == labels["escalator"]


def test_question_aliases_match_vocabulary():
    expected = {key: tuple(e["question_aliases"]) for key, e in _ui_entries(_vocab()).items()}
    assert _py_tuple_map(UNDERSTAND, "MODEL_ALIASES") == expected


# --- カードとの一致 ---------------------------------------------------------------

def test_card_model_scope_values_are_in_vocabulary():
    """カードの model_scope の値は、語彙（正式・許容・非推奨）か、置き場違いの一覧にあること。

    新しい値を使う前に、itai・mona が語彙ファイルへ追加する。
    """
    vocab = _vocab()
    known = {
        axis: {t for e in entries for t in [e["value"], *e.get("admitted", []), *e.get("deprecated", [])]}
        for axis, entries in vocab["axes"].items()
    }
    for item in vocab["misplaced"]:
        known[item["axis"]].add(item["value"])
    unknown = []
    for path, scope in _card_scopes():
        for axis in AXES:
            values = scope.get(axis) or []
            values = values if isinstance(values, list) else [values]
            for value in values:
                if str(value) not in known[axis]:
                    unknown.append(f"{path.relative_to(ROOT).as_posix()}: {axis}={value}")
    assert not unknown, "語彙に無い値（語彙ファイルへ追加するか、カードを直す）:\n" + "\n".join(unknown)


def test_admitted_product_spellings_recognized_by_retrieval_are_declared():
    """許容の表記のうち、検索の機種フィルタが認識しないものを一覧にして固定する。

    ここに出た表記のカードは、確認済み（scope_status: verified）にしても機種で絞り込まれない。
    コードの別名へ足すか、カードの表記を正式な値に直したら、この一覧から外す。
    """
    module = _retrieval()
    recognized = {v for values in module.MODEL_ALIASES.values() for v in values}
    gaps = sorted(
        term
        for e in _vocab()["axes"]["product_lines"]
        if e.get("ui_filter")
        for term in e.get("admitted", [])
        if _norm(term) not in recognized
    )
    assert gaps == KNOWN_FILTER_GAPS
