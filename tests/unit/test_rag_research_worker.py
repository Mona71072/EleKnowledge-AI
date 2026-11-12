import importlib.util
import json
import re
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


def _fake_app(outputs, results, handled=()):
    return SimpleNamespace(
        BEDROCK_MODEL_ID="global.anthropic.claude-sonnet-5", bedrock_runtime=object(),
        invoke_generation=lambda *args, **kwargs: (next(outputs), {}, None),
        expand_query_abbreviations=lambda value: value,
        query_knowledge_base=lambda *args, **kwargs: {"retrievalResults": results},
        merge_retrieval_results=lambda *groups: [item for group in groups for item in group],
        chunk_text=lambda item: item["content"]["text"],
        KB_PROFILE=SimpleNamespace(source_uri_key="uri"),
        HANDLED_MODEL_TYPES=frozenset(handled),
        extract_citations_from_selected=lambda items: (["safety.pdf"], [{"documentName": "safety.pdf"}]),
    )


def _run(app, question="質問"):
    return research_worker.run_research(
        app, question, {}, progress=lambda *args, **kwargs: None,
        deadline=research_worker.time.monotonic() + 60,
    )


def _plan(risk="low", domain="other"):
    return json.dumps({"kind": "procedure", "risk": risk, "domain": domain, "models": [], "searches": [
        {"query": "検索1", "purpose": "手順"}, {"query": "検索2", "purpose": "確認"},
    ]}, ensure_ascii=False)


def _evidence(eid, model_type, name=None, version=None):
    return {
        "id": eid, "uri": f"s3://b/{name or eid}.pdf", "text": "本文", "score": 0.9,
        "metadata": {"model_type": model_type, "x-amz-bedrock-kb-document-page-number": 3.0},
        "common": research_worker.is_common_model(model_type), "version": version,
    }


def test_high_risk_supported_conclusion_is_shown_under_escalation_with_status(monkeypatch):
    # G5: 裏付けの取れた結論は消さず「判断は確認先で行う」欄に「裏付けあり」で置く。未確認の結論は件数だけ。
    monkeypatch.delenv(research_worker.ESCALATION_CONTACTS_ENV, raising=False)
    outputs = iter([
        _plan(risk="high", domain="safety"),
        json.dumps({"claims": [
            {"text": "手順書の確認が必要です", "evidenceIds": ["E1"], "modelType": None, "section": "conclusion"},
            {"text": "作業できます", "evidenceIds": ["E1"], "modelType": None, "section": "conclusion"},
        ], "unknownPoints": []}, ensure_ascii=False),
        json.dumps({"supportedClaims": ["C1"], "unsupportedClaims": ["C2"]}),
    ])
    result = _run(_fake_app(outputs, [_result("s3://bucket/safety.pdf", "手順の確認が必要です")]),
                  "この状態で作業しても安全ですか？")

    content = result["content"]
    assert "■判断は確認先で行う" in content
    assert "手順書の確認が必要です（safety.pdf）［裏付けあり］" in content
    assert "裏付けを確認できていない結論の候補: 1 件" in content
    assert "作業できます" not in content
    assert "■結論" not in content
    assert "確認先（安全）: 未設定" in content
    assert result["research"]["unsupportedClaimCount"] == 1
    assert "作業できます" not in json.dumps(result["research"], ensure_ascii=False)


def test_rejected_claim_text_is_not_shown():
    # G4: 照合で否定された主張の本文は回答にも research にも残さない。
    outputs = iter([
        _plan(),
        json.dumps({"claims": [
            {"text": "値は10です", "evidenceIds": ["E1"], "modelType": "AXIEZ", "section": "conclusion"},
            {"text": "値は99です", "evidenceIds": ["E1"], "modelType": "AXIEZ", "section": "conclusion"},
        ], "unknownPoints": ["据付寸法"]}, ensure_ascii=False),
        json.dumps({"supportedClaims": ["C1"], "unsupportedClaims": ["C2"]}),
    ])
    result = _run(_fake_app(outputs, [_result("s3://bucket/a.pdf", "値は10")]))

    assert "値は10です" in result["content"]
    assert "値は99です" not in result["content"]
    assert "値は99です" not in json.dumps(result["research"], ensure_ascii=False)
    assert "裏付けを確認できなかった記述が 1 件" in result["content"]
    assert "- 据付寸法" in result["content"]


def test_verification_failure_hides_all_claim_text():
    # G4: 照合できないときは全主張の本文を出さず件数だけ。
    def outputs():
        yield _plan()
        yield json.dumps({"claims": [
            {"text": "値は10です", "evidenceIds": ["E1"], "modelType": None, "section": "conclusion"},
        ], "unknownPoints": []}, ensure_ascii=False)
        raise RuntimeError("check unavailable")

    result = _run(_fake_app(outputs(), [_result("s3://bucket/a.pdf", "値は10")]))

    assert "値は10です" not in result["content"]
    assert "照合ができなかったため、1 件の記述を表示していません" in result["content"]
    assert result["research"]["verificationStatus"] == "unavailable"
    assert result["research"]["claims"] == []


def test_plan_failure_is_treated_as_high_risk():
    # G6
    plan = research_worker.normalize_plan({}, "質問", lambda value: value)
    assert plan["risk"] == "high"
    assert plan["domain"] == "other"
    assert research_worker.normalize_plan({"risk": "unknown"}, "質問", lambda value: value)["risk"] == "high"


def test_model_match_is_exact_not_substring():
    # G1: AXIEZ の主張は AXIEZ-LINKs の資料では裏付けられない。
    evidence = [_evidence("E1", "AXIEZ-LINKs"), _evidence("E2", ["AXIEZ(KE-WF・KE-HF)"]), _evidence("E3", "駅舎エレ")]
    claims = [
        {"text": "a", "evidenceIds": ["E1"], "modelType": "AXIEZ", "section": "model"},
        {"text": "b", "evidenceIds": ["E2"], "modelType": "AXIEZ", "section": "model"},
        {"text": "c", "evidenceIds": ["E1"], "modelType": "AXIEZ-LINKs", "section": "model"},
        {"text": "d", "evidenceIds": ["E2"], "modelType": "駅舎エレ", "section": "model"},
        {"text": "e", "evidenceIds": ["E1"], "modelType": "架空の機種", "section": "model"},
        {"text": "f", "evidenceIds": ["E2"], "modelType": "アクシーズ", "section": "model"},
        {"text": "g", "evidenceIds": ["E1", "E2"], "modelType": "AXIEZ", "section": "model"},
    ]

    valid, rejected = research_worker.validate_claims(claims, evidence)

    assert [claim["text"] for claim in valid] == ["b", "c", "f"]
    assert [claim["text"] for claim in rejected] == ["a", "d", "e", "g"]


def test_handled_model_values_are_known_models():
    evidence = [_evidence("E1", "メルシティ"), _evidence("E2", "斜行エレベーター")]
    claims = [{"text": "x", "evidenceIds": ["E2"], "modelType": "斜行エレベーター", "section": "model"}]

    assert research_worker.validate_claims(claims, evidence)[0] == []
    valid, _ = research_worker.validate_claims(claims, evidence, handled_models=("斜行エレベーター",))
    assert [claim["text"] for claim in valid] == ["x"]


def test_common_document_supports_model_claim_and_is_labelled():
    # G2: 共通資料は機種付きの主張を裏付けてよい。根拠一覧に「共通資料」と表示する。
    evidence = [_evidence("E1", ["*"], name="共通要領"), _evidence("E2", "AXIEZ", name="AXIEZ仕様")]
    claims = [{"text": "共通の値です", "evidenceIds": ["E1", "E2"], "modelType": "AXIEZ", "section": "model"}]

    valid, rejected = research_worker.validate_claims(claims, evidence)
    content = research_worker.format_research_answer(
        searches=2, evidence=evidence, claims=valid, unknown_points=[], unsupported=rejected,
        elapsed_seconds=1, risk="low",
    )

    assert [claim["text"] for claim in valid] == ["共通の値です"]
    assert "- 共通要領.pdf p.3（共通資料）" in content
    assert "- AXIEZ仕様.pdf p.3" in content.splitlines()


def test_unlabelled_claim_mixing_models_is_rejected():
    # G3
    evidence = [_evidence("E1", "AXIEZ"), _evidence("E2", "NEXCUBE"), _evidence("E3", "general")]
    claims = [
        {"text": "混在", "evidenceIds": ["E1", "E2"], "modelType": None, "section": "conclusion"},
        {"text": "単一", "evidenceIds": ["E1", "E3"], "modelType": None, "section": "conclusion"},
    ]

    valid, rejected = research_worker.validate_claims(claims, evidence)

    assert [claim["text"] for claim in valid] == ["単一"]
    assert [claim["text"] for claim in rejected] == ["混在"]


def test_evidence_records_hash_and_version_and_rejects_mixed_versions():
    # G7: 本文のハッシュと版を持つ。同じ資料名で版が違う根拠を 1 つの主張にまとめない。
    results = [
        {"score": 0.9, "content": {"text": "本文A"}, "metadata": {"uri": "s3://b/x.pdf", "rev": "2"}},
        {"score": 0.8, "content": {"text": "本文B"}, "metadata": {"uri": "s3://b/x.pdf"}},
    ]
    selected = research_worker.select_research_evidence(
        results, lambda item: item["content"]["text"], "uri", version_key="rev",
    )
    assert selected[0]["version"] == "2" and selected[1]["version"] is None
    assert selected[0]["textHash"] == research_worker.hashlib.sha256("本文A".encode("utf-8")).hexdigest()
    assert research_worker.select_research_evidence(
        results, lambda item: item["content"]["text"], "uri",
    )[0]["version"] is None

    evidence = [_evidence("E1", "*", name="x", version="1"), _evidence("E2", "*", name="x", version="2")]
    claims = [{"text": "v", "evidenceIds": ["E1", "E2"], "modelType": None, "section": "conclusion"}]
    assert research_worker.validate_claims(claims, evidence)[0] == []

    summary = research_worker.research_evidence_summary(evidence)
    assert summary[0] == {"id": "E1", "documentName": "x.pdf", "page": 3, "modelScope": "common",
                          "textHash": None, "version": "1"}


def test_escalation_contacts_from_config(monkeypatch):
    # G8
    assert research_worker.load_escalation_contacts("") == {}
    assert research_worker.load_escalation_contacts("not json") == {}
    assert research_worker.load_escalation_contacts('["x"]') == {}
    assert research_worker.load_escalation_contacts(
        json.dumps({"legal": " 法務\n担当 ", "unknown": "x", "safety": 1}, ensure_ascii=False)
    ) == {"legal": "法務 担当"}

    monkeypatch.setenv(research_worker.ESCALATION_CONTACTS_ENV, json.dumps({"legal": "法務担当"}, ensure_ascii=False))
    result = _run(_fake_app(iter([_plan(risk="high", domain="legal")]), []))
    assert "確認先（法令）: 法務担当" in result["content"]


def test_answer_shows_document_names_not_evidence_ids():
    # G9: 根拠ID は本文に出さず、資料名とページをコードで付ける。主張中の括弧書き ID は取り除く。
    evidence = [_evidence("E1", "AXIEZ", name="TI-1158"), _evidence("E2", "AXIEZ", name="TI-1158")]
    claims = [
        {"text": "値は10です（E1/E2）", "evidenceIds": ["E1", "E2"], "modelType": "AXIEZ", "section": "conclusion"},
        {"text": "異常コード(E12)を確認", "evidenceIds": ["E1"], "modelType": None, "section": "conclusion"},
    ]

    valid, rejected = research_worker.validate_claims(claims, evidence)
    content = research_worker.format_research_answer(
        searches=2, evidence=evidence, claims=valid, unknown_points=[], unsupported=rejected,
        elapsed_seconds=1, risk="low",
    )

    assert "- AXIEZ: 値は10です（TI-1158.pdf p.3）" in content
    assert "異常コード(E12)を確認（TI-1158.pdf p.3）" in content
    assert valid[0]["evidenceIds"] == ["E1", "E2"]
    assert re.search(r"\bE[12]\b", content) is None
    assert content.count("- TI-1158.pdf p.3") == 1


def test_common_model_value_in_claim_is_treated_as_no_model():
    # 実機確認（2026-11-12）で、モデルが共通資料の model_type「general」をそのまま書き、正しい主張が全件落ちた。
    evidence = [_evidence("E1", "general"), _evidence("E2", ["general"]), _evidence("E3", "AXIEZ")]
    claims = [
        {"text": "a", "evidenceIds": ["E1"], "modelType": "general", "section": "conclusion"},
        {"text": "b", "evidenceIds": ["E2", "E3"], "modelType": "*", "section": "conclusion"},
        {"text": "c", "evidenceIds": ["E1"], "modelType": "全エレ機種", "section": "conclusion"},
    ]

    valid, rejected = research_worker.validate_claims(claims, evidence)

    assert [claim["text"] for claim in valid] == ["a", "b", "c"]
    assert all(claim["modelType"] is None for claim in valid)
    assert rejected == []
