"""モデル比較スクリプトの料金と Retrieve キャッシュ。"""

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/eval/run_model_bakeoff.py"
SPEC = importlib.util.spec_from_file_location("model_bakeoff_test", SCRIPT)
BAKEOFF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BAKEOFF)


def test_luna_pricing_uses_global_short_and_long_context_rates():
    assert BAKEOFF.price_for("global.openai.gpt-6-luna", input_tokens=100) == (0.10, 0.50)
    assert BAKEOFF.price_for("global.openai.gpt-6-luna", input_tokens=272000) == (0.10, 0.50)
    assert BAKEOFF.price_for("global.openai.gpt-6-luna", input_tokens=272001) == (0.20, 0.75)
    assert BAKEOFF.price_note("global.anthropic.claude-sonnet-5") == (
        "Anthropic 公式 $2/$10、Bedrock 単価は請求で確認"
    )


def test_retrieval_save_and_load_excludes_answers_and_restores_results(tmp_path):
    retrieval_results = [{"x": 1}]
    rows = [{"id": "q1", "query": "question", "gate": "pages",
             "retrievalResults": retrieval_results, "answers": {"luna": {"text": "answer"}}}]
    path = tmp_path / "retrieval.json"
    BAKEOFF.save_retrieval(path, rows)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert "answers" not in saved[0]
    loaded = BAKEOFF.load_retrieval(path)
    assert loaded["q1"]["retrievalResults"] == retrieval_results
    assert "answers" not in loaded["q1"]
