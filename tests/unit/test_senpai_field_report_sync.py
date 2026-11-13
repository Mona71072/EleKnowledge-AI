"""「結果を残す」の語彙が Lambda・フロントエンド・キュー生成の 3 か所で一致することを確認する。"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VOCAB = ROOT / "lambda/rag/senpai-field-report/field_report_vocab.py"
FRONTEND_REPORT = ROOT / "frontend/src/lib/knowledge-senpai-field-report.mjs"
FRONTEND_CHAT = ROOT / "frontend/src/lib/knowledge-senpai-chat.mjs"
FRONTEND_MODELS = ROOT / "frontend/src/data/kb-model-types.generated.mjs"
QUEUE_SCRIPT = ROOT / "scripts/knowledge/build_scope_review_queue.py"
RETRIEVAL = ROOT / "lambda/rag/rag-function/knowhow_retrieval.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _js_set(path: Path, name: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"const {name} = (?:Object\.freeze\()?new Set\(\[(.*?)\]\)", text, re.DOTALL)
    assert match, f"{name} not found in {path.name}"
    return re.findall(r"'([^']+)'", match.group(1))


def test_reactions_match_everywhere_in_order():
    vocab = _load(VOCAB, "field_report_vocab_sync")
    queue = _load(QUEUE_SCRIPT, "scope_queue_field_report_sync")
    assert list(vocab.REACTIONS) == _js_set(FRONTEND_REPORT, "FIELD_REPORT_REACTIONS")
    assert list(vocab.REACTIONS) == list(queue.FIELD_REPORT_REACTIONS)


def test_review_states_match_everywhere_and_start_unconfirmed():
    vocab = _load(VOCAB, "field_report_vocab_sync_states")
    queue = _load(QUEUE_SCRIPT, "scope_queue_field_report_sync_states")
    assert list(vocab.REVIEW_STATES) == _js_set(FRONTEND_REPORT, "FIELD_REPORT_REVIEW_STATES")
    assert list(vocab.REVIEW_STATES) == list(queue.FIELD_REPORT_REVIEW_STATES)
    assert vocab.INITIAL_REVIEW_STATE == vocab.REVIEW_STATES[0] == "unconfirmed"
    assert set(queue.OPEN_REVIEW_STATES) == {"unconfirmed", "awaiting_review"}


def test_model_types_match_ui_filters_and_retrieval_aliases():
    vocab = _load(VOCAB, "field_report_vocab_sync_models")
    retrieval = _load(RETRIEVAL, "knowhow_retrieval_field_report_sync")
    # 画面の機種一覧と SENPAI_MODEL_TYPES は、語彙ファイルから生成した kb-model-types.generated.mjs を使う。
    generated = FRONTEND_MODELS.read_text(encoding="utf-8")
    ui_values = re.findall(r"value: '([^']+)'", generated)
    keys = re.search(r"export const KB_MODEL_KEYS = Object\.freeze\(\[(.*?)\]\);", generated)
    assert keys, "KB_MODEL_KEYS not found"
    assert set(vocab.MODEL_TYPES) == set(retrieval.MODEL_ALIASES)
    assert set(vocab.MODEL_TYPES) == set(ui_values)
    assert set(vocab.MODEL_TYPES) == set(re.findall(r"'([^']+)'", keys.group(1)))
    assert "export const SENPAI_MODEL_TYPES = new Set(KB_MODEL_KEYS);" in FRONTEND_CHAT.read_text(encoding="utf-8")


def test_text_limits_match_between_lambda_and_frontend():
    vocab = _load(VOCAB, "field_report_vocab_sync_limits")
    text = FRONTEND_REPORT.read_text(encoding="utf-8")
    assert f"FIELD_REPORT_FINDING_MAX = {vocab.FINDING_MAX_CHARS};" in text
    assert f"FIELD_REPORT_CONDITION_MAX = {vocab.CONDITION_MAX_CHARS};" in text
