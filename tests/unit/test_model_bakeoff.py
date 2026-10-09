"""モデル比較スクリプトの料金と Retrieve キャッシュ。"""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/eval/run_model_bakeoff.py"
SPEC = importlib.util.spec_from_file_location("model_bakeoff_test", SCRIPT)
BAKEOFF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BAKEOFF)


def test_luna_pricing_uses_global_short_and_long_context_rates():
    assert BAKEOFF.price_for("global.openai.gpt-6-luna", input_tokens=100) == (0.10, 0.50)
    assert BAKEOFF.price_for("global.openai.gpt-6-luna", input_tokens=272000) == (0.10, 0.50)
    assert BAKEOFF.price_for("global.openai.gpt-6-luna", input_tokens=272001) == (0.20, 0.75)
    assert "Bedrock の cache 単価は未確認" in BAKEOFF.price_note(
        "global.anthropic.claude-sonnet-5"
    )


def test_luna_cost_includes_cached_input_tokens():
    usage = {
        "inputTokens": 2,
        "cacheReadInputTokens": 2851,
        "cacheWriteInputTokens": 0,
        "outputTokens": 344,
    }
    assert BAKEOFF.estimate_cost_usd("global.openai.gpt-6-luna", usage) == pytest.approx(0.00020071)
    assert usage["inputTokens"] + usage["cacheReadInputTokens"] == 2853


def test_luna_cost_uses_long_context_rates_for_cached_tokens():
    usage = {
        "inputTokens": 2,
        "cacheReadInputTokens": 272000,
        "cacheWriteInputTokens": 0,
        "outputTokens": 344,
    }
    assert BAKEOFF.estimate_cost_usd("global.openai.gpt-6-luna", usage) == pytest.approx(0.0056984)


def test_sonnet_cost_marks_bedrock_cache_rates_unconfirmed_and_excludes_them():
    usage = {
        "inputTokens": 1000,
        "cacheReadInputTokens": 2000,
        "cacheWriteInputTokens": 3000,
        "outputTokens": 1000,
    }
    assert BAKEOFF.estimate_cost_usd(
        "global.anthropic.claude-sonnet-5", usage
    ) == 0.012
    assert BAKEOFF.cache_cost_status("global.anthropic.claude-sonnet-5") == "未確認"
    note = BAKEOFF.price_note("global.anthropic.claude-sonnet-5")
    assert "未確認" in note
    assert "含めない" in note


def test_luna_cache_write_uses_published_rate_without_rounding_total():
    usage = {
        "inputTokens": 1,
        "cacheReadInputTokens": 0,
        "cacheWriteInputTokens": 2,
        "outputTokens": 0,
    }
    assert BAKEOFF.estimate_cost_usd("global.openai.gpt-6-luna", usage) == pytest.approx(0.00000035)


def test_luna_long_context_boundary_uses_total_input_tokens():
    at_boundary = {
        "inputTokens": 271999,
        "cacheReadInputTokens": 0,
        "cacheWriteInputTokens": 1,
        "outputTokens": 0,
    }
    over_boundary = {**at_boundary, "cacheWriteInputTokens": 2}
    assert BAKEOFF.total_input_tokens(at_boundary) == 272000
    assert BAKEOFF.estimate_cost_usd("global.openai.gpt-6-luna", at_boundary) == pytest.approx(0.027200025)
    assert BAKEOFF.total_input_tokens(over_boundary) == 272001
    assert BAKEOFF.estimate_cost_usd("global.openai.gpt-6-luna", over_boundary) == pytest.approx(0.0544003)


def test_summary_and_question_rows_report_cache_split_and_unrounded_costs():
    models = [("luna", "global.openai.gpt-6-luna")]
    answer = {
        "latencySec": 1.0,
        "inputTokens": 1,
        "cacheReadInputTokens": 2,
        "cacheWriteInputTokens": 3,
        "totalInputTokens": 6,
        "outputTokens": 4,
        "estCostUsd": 0.0000009,
        "cacheCostStatus": "AWS公式モデルカードの単価を適用",
        "stopReason": "end_turn",
        "text": "回答",
    }
    rows = [{"id": "Q1", "query": "質問", "gate": "pages", "answers": {"luna": answer}}]
    summary = BAKEOFF.summarize(rows, models)
    assert summary["luna"]["avgTotalInputTokens"] == 6
    assert summary["luna"]["totalEstCostUsd"] == 0.0000009

    markdown = BAKEOFF.render_markdown(
        rows, models, summary, {"date": "2026-10-04", "kbId": "kb"},
    )
    assert "通常入力 1 / cache read 2 / cache write 3 / 総入力 6" in markdown
    assert "金額は参考概算（実請求とは未照合）" in markdown
    assert "0.00000090" in markdown  # 表示時のみ丸める


def test_missing_usage_is_not_counted_as_zero_in_question_or_summary():
    model_id = "global.openai.gpt-6-luna"
    models = [("luna", model_id)]
    successful_answer = {
        "inputTokens": 100,
        "cacheReadInputTokens": 20,
        "cacheWriteInputTokens": 5,
        "totalInputTokens": 125,
        "outputTokens": 10,
        "estCostUsd": 0.00002,
        "text": "回答あり",
    }
    rows = [
        {"id": f"Q{i}", "query": f"質問{i}", "gate": "pages", "answers": {
            "luna": dict(successful_answer) if i < 30 else {
                "error": "generation failed", "text": "[生成エラー] RuntimeError: failed",
                "totalInputTokens": None,
            },
        }}
        for i in range(1, 33)
    ]

    assert BAKEOFF.total_input_tokens({}) is None
    summary = BAKEOFF.summarize(rows, models)["luna"]
    assert summary["usageCount"] == 29
    assert summary["avgInputTokens"] == 100
    assert summary["avgTotalInputTokens"] == 125
    assert summary["totalEstCostUsd"] == pytest.approx(29 * 0.00002)

    markdown = BAKEOFF.render_markdown(
        rows, models, {"luna": summary}, {"date": "2026-10-04", "kbId": "kb"},
    )
    assert "29/32" in markdown
    assert "通常入力 - / cache read - / cache write - / 総入力 - / 出力 -" in markdown


def test_generation_exception_records_missing_usage_as_none():
    def fail_generation(*args, **kwargs):
        raise RuntimeError("generation failed")

    mod = SimpleNamespace(
        normalize_mode_and_filters=lambda mode, filters: (mode, filters),
        needs_clarify=lambda query, filters, _context: (False, []),
        is_weak_retrieval=lambda results, mode: False,
        select_retrieval_results=lambda results, mode: results,
        build_page_candidates=lambda results, max_items: [],
        generate_response_with_claude=fail_generation,
        invoke_generation=lambda *args, **kwargs: ("", {}, None),
    )
    helpers = SimpleNamespace(
        run_normal_retrieve=lambda _mod, query, filters: ([{"page": 1}], False, False),
    )
    row = BAKEOFF.run_question(
        mod, helpers, {"id": "Q1", "query": "質問"},
        [("luna", "global.openai.gpt-6-luna")],
    )

    answer = row["answers"]["luna"]
    for key in (
        "inputTokens", "cacheReadInputTokens", "cacheWriteInputTokens",
        "totalInputTokens", "outputTokens",
    ):
        assert answer[key] is None


def test_sonnet_report_marks_cache_charge_unconfirmed():
    model_id = "global.anthropic.claude-sonnet-5"
    rows = [{"id": "Q1", "query": "質問", "gate": "pages", "answers": {
        "sonnet5": {
            "inputTokens": 10, "cacheReadInputTokens": 20,
            "cacheWriteInputTokens": 30, "totalInputTokens": 60,
            "outputTokens": 5, "estCostUsd": 0.000045,
            "cacheCostStatus": "未確認", "text": "回答",
        },
    }}]
    summary = BAKEOFF.summarize(rows, [("sonnet5", model_id)])
    markdown = BAKEOFF.render_markdown(
        rows, [("sonnet5", model_id)], summary,
        {"date": "2026-10-04", "kbId": "kb"},
    )
    assert "cache料金未確認・金額に含めず" in markdown
    assert "5分 cache write $2.50" in markdown


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
