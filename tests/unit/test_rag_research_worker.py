import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = ROOT / "lambda" / "rag" / "rag-function"
sys.path.insert(0, str(RAG_DIR))
SPEC = importlib.util.spec_from_file_location("research_worker_test", RAG_DIR / "research_worker.py")
research_worker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = research_worker
SPEC.loader.exec_module(research_worker)


def _result(uri, text, model_type="AXIEZ", score=0.8):
    return {
        "score": score,
        "content": {"text": text},
        "metadata": {"uri": uri, "model_type": model_type, "page": "4"},
    }


def test_parse_model_json_accepts_fenced_json_only():
    assert research_worker.parse_model_json('```json\n{"claims": []}\n```') == {"claims": []}
    assert research_worker.parse_model_json("not json") is None


def test_normalize_plan_falls_back_to_two_queries():
    plan = research_worker.normalize_plan({}, "火管の動作は？", lambda value: value + " 火災管制")

    assert len(plan["searches"]) == 2
    assert plan["searches"][0]["query"] == "火管の動作は？"
    assert plan["searches"][1]["query"] == "火管の動作は？ 火災管制"


def test_select_evidence_applies_threshold_dedup_and_per_document_limit():
    results = [
        _result("s3://bucket/a.pdf", f"same {index}") for index in range(5)
    ] + [
        _result("s3://bucket/a.pdf", "same 0"),
        _result("s3://bucket/b.pdf", "weak", score=0.2),
        _result("s3://bucket/c.pdf", "valid"),
    ]

    selected = research_worker.select_research_evidence(
        results, lambda item: item["content"]["text"], "uri"
    )

    assert len(selected) == 4
    assert [item["id"] for item in selected] == ["E1", "E2", "E3", "E4"]
    assert sum(item["uri"].endswith("a.pdf") for item in selected) == 3
    assert all(item["text"] != "weak" for item in selected)


def test_claim_validation_rejects_unknown_evidence_and_model_mismatch():
    evidence = [{
        "id": "E1", "metadata": {"model_type": "AXIEZ"}, "uri": "s3://b/a.pdf",
        "text": "値は10です", "score": 0.9,
    }]
    claims = [
        {"text": "値は10", "evidenceIds": ["E1"], "modelType": "AXIEZ", "section": "model"},
        {"text": "値は20", "evidenceIds": ["E2"], "modelType": "AXIEZ", "section": "model"},
        {"text": "別機種", "evidenceIds": ["E1"], "modelType": "NEXCUBE", "section": "model"},
    ]

    valid, rejected = research_worker.validate_claims(claims, evidence)

    assert [claim["claimId"] for claim in valid] == ["C1"]
    assert [claim["claimId"] for claim in rejected] == ["C2", "C3"]


def test_run_research_runs_plan_search_synthesis_and_verification():
    model_outputs = iter([
        json.dumps({
            "kind": "comparison", "risk": "low", "models": ["AXIEZ"],
            "searches": [
                {"query": "AXIEZ 制御仕様", "purpose": "仕様"},
                {"query": "AXIEZ 据付資料", "purpose": "手順"},
            ],
        }, ensure_ascii=False),
        json.dumps({
            "claims": [{
                "text": "制御仕様を確認できます", "evidenceIds": ["E1"],
                "modelType": "AXIEZ", "section": "conclusion",
            }],
            "unknownPoints": [],
        }, ensure_ascii=False),
        json.dumps({"supportedClaims": ["C1"], "unsupportedClaims": []}),
    ])
    search_queries = []

    def invoke_generation(*args, **kwargs):
        return next(model_outputs), {}, "end_turn"

    def query_knowledge_base(query, **kwargs):
        search_queries.append(query)
        suffix = "a" if len(search_queries) % 2 else "b"
        return {"retrievalResults": [_result(f"s3://bucket/{suffix}.pdf", f"根拠 {suffix}")]}

    fake_app = SimpleNamespace(
        BEDROCK_MODEL_ID="global.anthropic.claude-sonnet-5",
        bedrock_runtime=object(),
        invoke_generation=invoke_generation,
        expand_query_abbreviations=lambda value: value,
        query_knowledge_base=query_knowledge_base,
        merge_retrieval_results=lambda *groups: [item for group in groups for item in group],
        chunk_text=lambda item: item["content"]["text"],
        KB_PROFILE=SimpleNamespace(source_uri_key="uri"),
        extract_citations_from_selected=lambda items: (["a.pdf"], [{"documentName": "a.pdf"}]),
        extract_page_number=lambda metadata: 4,
    )
    progress_events = []

    result = research_worker.run_research(
        fake_app, "AXIEZの制御仕様は？", {},
        progress=lambda *args, **kwargs: progress_events.append((args, kwargs)),
        deadline=research_worker.time.monotonic() + 60,
    )

    assert len(search_queries) == 3
    assert result["research"]["searchCount"] == 3
    assert result["research"]["evidenceCount"] == 2
    assert result["research"]["claims"][0]["text"] == "制御仕様を確認できます"
    assert "■結論" in result["content"]
    assert [event[0][0] for event in progress_events] == [
        "planning", "searching", "searching", "searching", "searching",
        "selecting", "synthesizing", "checking",
    ]
    assert [event[1]["done"] for event in progress_events if event[0][0] == "searching"] == [0, 1, 2, 3]


def test_run_research_returns_non_compositional_answer_without_evidence():
    plan = json.dumps({"kind": "single", "risk": "low", "models": [], "searches": [
        {"query": "質問の検索", "purpose": "直接"}, {"query": "質問の検索2", "purpose": "補助"},
    ]}, ensure_ascii=False)
    outputs = iter([plan])
    fake_app = SimpleNamespace(
        BEDROCK_MODEL_ID="model", bedrock_runtime=object(),
        invoke_generation=lambda *args, **kwargs: (next(outputs), {}, None),
        expand_query_abbreviations=lambda value: value,
        query_knowledge_base=lambda *args, **kwargs: {"retrievalResults": []},
        merge_retrieval_results=lambda *groups: [],
        chunk_text=lambda item: item["content"]["text"],
        KB_PROFILE=SimpleNamespace(source_uri_key="uri"),
        extract_page_number=lambda metadata: None,
    )

    result = research_worker.run_research(
        fake_app, "質問", {}, progress=lambda *args, **kwargs: None,
        deadline=research_worker.time.monotonic() + 60,
    )

    assert result["research"]["evidenceCount"] == 0
    assert "作文" not in result["content"]
    assert "根拠資料は見つかりませんでした" in result["content"]


def test_high_risk_question_does_not_present_a_conclusion_claim():
    outputs = iter([
        json.dumps({"kind": "procedure", "risk": "high", "models": [], "searches": [
            {"query": "安全な作業方法", "purpose": "手順"},
            {"query": "作業可否", "purpose": "確認"},
        ]}, ensure_ascii=False),
        json.dumps({"claims": [{
            "text": "作業できます", "evidenceIds": ["E1"],
            "modelType": None, "section": "conclusion",
        }], "unknownPoints": []}, ensure_ascii=False),
        json.dumps({"supportedClaims": ["C1"], "unsupportedClaims": []}),
    ])
    fake_app = SimpleNamespace(
        BEDROCK_MODEL_ID="global.anthropic.claude-sonnet-5", bedrock_runtime=object(),
        invoke_generation=lambda *args, **kwargs: (next(outputs), {}, None),
        expand_query_abbreviations=lambda value: value,
        query_knowledge_base=lambda *args, **kwargs: {"retrievalResults": [
            _result("s3://bucket/safety.pdf", "手順の確認が必要です")
        ]},
        merge_retrieval_results=lambda *groups: [item for group in groups for item in group],
        chunk_text=lambda item: item["content"]["text"],
        KB_PROFILE=SimpleNamespace(source_uri_key="uri"),
        extract_citations_from_selected=lambda items: (["safety.pdf"], [{"documentName": "safety.pdf"}]),
        extract_page_number=lambda metadata: 1,
    )

    result = research_worker.run_research(
        fake_app, "この状態で作業しても安全ですか？", {},
        progress=lambda *args, **kwargs: None,
        deadline=research_worker.time.monotonic() + 60,
    )

    assert result["research"]["claims"] == []
    assert "作業できます" in result["research"]["unsupportedClaims"]
    assert "■確認先・エスカレーション" in result["content"]