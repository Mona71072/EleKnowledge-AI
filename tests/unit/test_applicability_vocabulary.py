"""適用範囲の語彙（knowledge/registry/applicability-vocabulary.json）を正本として照合する。

語彙ファイルは APPLICABILITY-TAXONOMY.md をもとに作成し、値の正本として運用する。
次がこの語彙と一致することを確かめる。

- 生成物（scripts/knowledge/generate_vocabulary.py が書く 3 ファイル）が、生成し直した内容と一致すること
- 画面の機種一覧（kb-model-types.generated.mjs → kbModelTypes.ts）と、サーバーの UI_MODEL_FILTERS（app.py）
- ノウハウ検索の機種の別名（knowhow_retrieval.py の MODEL_ALIASES。索引作成側とは既存の同期テストで一致）
- 調査ジョブが質問中の機種を判定する呼び名（senpai_research_understand.py の MODEL_ALIASES）
- テーマカードの model_scope に書かれた値

コード側の値は生成物から import する（WP1、方法 A）。照合はこのファイルで語彙から独立に組み立てた期待値と比べる。

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
FRONTEND_MODELS = ROOT / "frontend/src/data/kb-model-types.generated.mjs"
GENERATOR = ROOT / "scripts/knowledge/generate_vocabulary.py"
RETRIEVAL = ROOT / "lambda/rag/rag-function/knowhow_retrieval.py"
AXES = ("product_lines", "machine_room", "control_methods", "model_abbreviations",
        "guide_systems", "door_families", "door_types")
# 検索の機種フィルタ（knowhow_retrieval.MODEL_ALIASES）が認識しない許容の表記。
# 2026-11-12 itai 決定（WP4）で MELCITY・MELWIDE を別名に足したため、穴は無い。
KNOWN_FILTER_GAPS = []


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


def _generator():
    spec = importlib.util.spec_from_file_location("generate_vocabulary_under_test", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _frontend_models() -> dict:
    text = FRONTEND_MODELS.read_text(encoding="utf-8")
    block = re.search(r"export const KB_MODEL_TYPES = Object\.freeze\(\[(.*?)\]\);", text, re.DOTALL)
    assert block, "KB_MODEL_TYPES not found"
    result = {}
    for value, targets in re.findall(r"value:\s*'([^']+)'.*?targets:\s*(?:Object\.freeze\()?\[([^\]]*)\]", block.group(1), re.DOTALL):
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


def _all_items(vocab: dict) -> list:
    return [e for entries in vocab["axes"].values() for e in entries] + [
        e for entries in vocab["items"].values() for e in entries
    ]


def test_every_item_has_unique_stable_id():
    """項目台帳の ID（知識マップ設計 §4.1）。ID は種類の接頭辞を持ち、重複しない。"""
    vocab = _vocab()
    assert vocab["schema_version"] == 2
    ids = [e["id"] for e in _all_items(vocab)]
    assert len(ids) == len(set(ids)), "ID が重複している"
    assert all(re.match(r"^[a-z_]+:.+", i) for i in ids)


def test_item_relations_point_to_existing_items_with_source():
    """項目同士の関係（R1・R2）は、存在する ID を指し、出典を持つ（知識マップ設計 §4.1 ルール 3）。"""
    vocab = _vocab()
    ids = {e["id"] for e in _all_items(vocab)}
    for entry in _all_items(vocab):
        for relation in entry.get("relations", []):
            assert relation["type"] in ("related", "successor_of"), relation
            assert relation["target"] in ids, f"{entry['id']} → 存在しない ID {relation['target']}"
            assert relation.get("source"), f"{entry['id']} → {relation['target']} に出典が無い"


LAW_LIST = ROOT / "docs/features/development/legal-rag-target-laws.md"
KB_INDEX = ROOT / "knowledge/registry/kb-document-index.jsonl"
KB_REF_RESOLUTION = ROOT / "knowledge/registry/kb-ref-resolution.jsonl"


def _jsonl(path: Path) -> list:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_law_items_match_target_law_list():
    """法令の項目は法令対象一覧（53 件）と一致する。ID は版を含まない e-Gov の法令ID。"""
    folders = set(re.findall(r"`(\d{3}[A-Z0-9]{12}_\d{8}_[A-Z0-9]+)`", LAW_LIST.read_text(encoding="utf-8")))
    laws = _vocab()["items"]["laws"]
    assert {law["current_folder"] for law in laws} == folders
    assert all(law["id"] == "law:" + law["current_folder"].split("_")[0] for law in laws)


def test_kb_value_map_covers_every_kb_value():
    """KB の model_type・category のすべての値に、対応（mapped / all_models / needs_review）が決まっている（§4.8.3）。

    needs_review は未判断であって取扱外ではない。取扱外にするには業務スコープの共同確認が要る。
    """
    vocab = _vocab()
    kb_map = vocab["kb_value_map"]
    ids = {e["id"] for e in _all_items(vocab)}
    rows = _jsonl(KB_INDEX)
    assert {r["catalog_as_of"] for r in rows} == {kb_map["as_of"]}
    elements = {e.strip() for r in rows for e in re.split(r"\s*/\s*", r["model_type"]) if e.strip()}
    categories = {r["category"] for r in rows}
    for key, values in (("model_type", elements), ("category", categories)):
        mapped = {e["kb_value"]: e for e in kb_map[key]}
        assert set(mapped) == values, f"{key}: 対応の無い値 {sorted(values - set(mapped))} / 古い値 {sorted(set(mapped) - values)}"
        for entry in mapped.values():
            assert entry["status"] in ("mapped", "all_models", "needs_review")
            assert bool(entry["maps_to"]) == (entry["status"] == "mapped"), entry
            assert set(entry["maps_to"]) <= ids, entry


def test_card_kb_references_resolve_to_kb_documents():
    """カードの kb_document の解決先（kb-ref-resolution）が、KB の一覧に実在する。"""
    filenames = {r["filename"] for r in _jsonl(KB_INDEX)}
    broken = [
        f"{r['knowledge_id']}: {r['document_number']} → {r['kb_filename']}"
        for r in _jsonl(KB_REF_RESOLUTION)
        if r.get("kb_filename") and r["kb_filename"] not in filenames
    ]
    assert not broken, "KB の一覧に無い資料への解決:\n" + "\n".join(broken)


def test_card_law_references_point_to_law_items():
    """カードの law_rag の law_id は、法令の項目（版を含まない ID）に解決できる。"""
    law_ids = {law["id"] for law in _vocab()["items"]["laws"]}
    unknown = []
    for path in sorted(CARDS.glob("*/*.md")):
        match = re.match(r"---\r?\n(.*?)\r?\n---", path.read_text(encoding="utf-8"), re.DOTALL)
        meta = yaml.safe_load(match.group(1)) or {}
        for ref in meta.get("source_refs") or []:
            if ref.get("ref_type") == "law_rag" and "law:" + str(ref.get("law_id", "")).split("_")[0] not in law_ids:
                unknown.append(f"{path.name}: {ref.get('law_id')}")
    assert not unknown, "法令の項目に無い law_id:\n" + "\n".join(unknown)


# --- コードとの一致 ---------------------------------------------------------------

def test_frontend_model_list_matches_vocabulary():
    expected = {key: tuple(e["ui_filter"]["kb_model_types"]) for key, e in _ui_entries(_vocab()).items()}
    assert _frontend_models() == expected


def test_server_ui_model_filters_match_vocabulary(rag_app):
    expected = {key: tuple(e["ui_filter"]["kb_model_types"]) for key, e in _ui_entries(_vocab()).items()}
    assert rag_app.UI_MODEL_FILTERS == expected


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


def test_question_aliases_match_vocabulary(load_rag_module):
    expected = {key: tuple(e["question_aliases"]) for key, e in _ui_entries(_vocab()).items()}
    understand = load_rag_module("senpai_research_understand_vocab", "senpai_research_understand.py")
    assert understand.MODEL_ALIASES == expected
    # 機種の選択肢はプロンプトにも出す。キーの順は語彙ファイルの順。
    assert " / ".join(expected) + " のいずれか" in understand.SYSTEM_PROMPT


# --- 生成物 ---------------------------------------------------------------------

def test_generated_files_are_up_to_date():
    """生成スクリプトを実行し直した内容が、Git の生成物と一致すること（改行は LF に揃えて比べる）。"""
    stale = _generator().stale_outputs(ROOT)
    assert not stale, "生成物が古い。python scripts/knowledge/generate_vocabulary.py を実行する: " + ", ".join(stale)


def test_generated_files_carry_do_not_edit_header():
    generator = _generator()
    for rel in generator.render_all(_vocab()):
        head = (ROOT / rel).read_text(encoding="utf-8").splitlines()[:2]
        assert "生成物。直接編集しない。元: knowledge/registry/applicability-vocabulary.json。" in head[0], rel
        assert "再生成: python scripts/knowledge/generate_vocabulary.py" in head[1], rel


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
