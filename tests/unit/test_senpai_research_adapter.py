"""rag-function（app.py）の検索・生成・ノウハウを調査ジョブへつなぐアダプターのテスト。

app.py は CRLF のまま編集せず import して使う。ここでは Bedrock / KB を偽物に差し替え、
アダプターが既存の関数を再利用して、契約どおりの根拠データ（evidence）に変換することを確認する。
"""
import copy
import json

import pytest

import test_senpai_research_support as support

KB_BUCKET = "kbbucket"
SECRET = "固有質問ZZZQ"


@pytest.fixture
def ctx(rag_app, monkeypatch):
    module = support.load_module("senpai_research_rag.py")
    module.set_app(rag_app)
    monkeypatch.setattr(rag_app, "KB_SOURCE_BUCKET", KB_BUCKET)
    monkeypatch.setattr(rag_app, "KB_SOURCE_PREFIX", "docs/")
    monkeypatch.setattr(rag_app, "RERANK_MODEL_ARN", "")
    agent = FakeAgent()
    monkeypatch.setattr(rag_app, "bedrock_agent", agent)
    return module, rag_app, agent


class FakeAgent:
    def __init__(self):
        self.calls = []
        self.by_kb = {}
        self.default = []

    def retrieve(self, **kwargs):
        self.calls.append(kwargs)
        results = self.by_kb.get(kwargs["knowledgeBaseId"], self.default)
        return {"retrievalResults": copy.deepcopy(results)}


def _chunk(doc="TI-1.pdf", page=3, text="ドア調整の本文", score=0.8, model=("AXIEZ-LINKs",),
           category="テクニカルインフォメーション"):
    return {
        "content": {"type": "TEXT", "text": text},
        "metadata": {
            "x-amz-bedrock-kb-source-uri": f"s3://{KB_BUCKET}/docs/{doc}",
            "x-amz-bedrock-kb-document-page-number": page,
            "title": doc.removesuffix(".pdf"), "category": category, "model_type": list(model),
        },
        "score": score,
    }


def _law_chunk(provision="第三十五条", score=0.7, source_url="https://laws.e-gov.go.jp/law/abc"):
    return {
        "content": {"type": "TEXT", "text": "昇降機の構造は政令で定める。"},
        "metadata": {
            "source_type": "law", "status": "current", "document_granularity": "provision_unit",
            "x-amz-bedrock-kb-source-uri": "s3://lawbucket/kb/egov/325AC0000000201/20250401/main/00035.txt",
            "law_id": "325AC0000000201", "law_title": "建築基準法", "law_number": "昭和二十五年法律第二百一号",
            "provision_reference": provision, "provision_type": "main",
            "effective_date": "2025-04-01", "source_url": source_url,
        },
        "score": score,
    }


# ---------------------------------------------------------------- 技術資料

def test_search_tech_reuses_rag_retrieval_and_maps_evidence(ctx):
    module, app, agent = ctx
    agent.default = [_chunk(), _chunk("TI-2.pdf", 5, "別資料", 0.5)]
    deps = module.RagDeps()
    result = deps.search_tech("ＬＩＮＫｓ　ドア 異音", None)
    first = result["evidence"][0]
    assert first == {
        "kind": "tech", "docKey": f"s3://{KB_BUCKET}/docs/TI-1.pdf", "documentName": "TI-1.pdf",
        "title": "TI-1", "pageNumber": 3, "sourceUri": f"s3://{KB_BUCKET}/docs/TI-1.pdf",
        "text": "ドア調整の本文", "score": pytest.approx(0.8)}
    assert result["hits"] == 2 and result["topScores"][0] == pytest.approx(0.8)
    # 検索語は既存の正規化（NFKC・空白）を通る
    assert agent.calls[0]["retrievalQuery"]["text"] == "LINKs ドア 異音"


def test_search_tech_passes_the_model_filter_to_the_knowledge_base(ctx):
    module, app, agent = ctx
    agent.default = [_chunk()]
    module.RagDeps().search_tech("ドア異音", "AXIEZ-LINKs")
    kb_filter = agent.calls[0]["retrievalConfiguration"]["vectorSearchConfiguration"]["filter"]
    assert "AXIEZ-LINKs" in json.dumps(kb_filter, ensure_ascii=False)
    agent.calls.clear()
    module.RagDeps().search_tech("ドア異音", None)
    kb_filter = agent.calls[0]["retrievalConfiguration"]["vectorSearchConfiguration"]["filter"]
    assert "AXIEZ-LINKs" not in json.dumps(kb_filter, ensure_ascii=False)


def test_search_tech_drops_low_score_markdown_and_unopenable_sources(ctx):
    module, app, agent = ctx
    other_bucket = _chunk("X.pdf")
    other_bucket["metadata"]["x-amz-bedrock-kb-source-uri"] = "s3://elsewhere/docs/X.pdf"
    agent.default = [_chunk("note.md"), other_bucket, _chunk("Low.pdf", score=0.1), _chunk("Ok.pdf")]
    result = module.RagDeps().search_tech("ドア異音", None)
    assert [e["documentName"] for e in result["evidence"]] == ["Ok.pdf"]


def test_search_tech_omits_page_when_unknown(ctx):
    module, app, agent = ctx
    chunk = _chunk()
    chunk["metadata"].pop("x-amz-bedrock-kb-document-page-number")
    agent.default = [chunk]
    assert module.RagDeps().search_tech("ドア異音", None)["evidence"][0]["pageNumber"] is None


def test_search_tech_expands_abbreviations_only_when_nothing_selected(ctx):
    module, app, agent = ctx
    responses = [[], [_chunk()]]

    def retrieve(**kwargs):
        agent.calls.append(kwargs)
        return {"retrievalResults": copy.deepcopy(responses[len(agent.calls) - 1])}

    agent.retrieve = retrieve
    claims = []
    result = module.RagDeps().search_tech("火管 試験", None, claim_search=lambda: claims.append(1) or True)
    assert len(agent.calls) == 2 and claims == [1]  # 追加の検索は予算を確保してから
    assert agent.calls[1]["retrievalQuery"]["text"] == "火災管制 試験"
    assert len(result["evidence"]) == 1


def test_search_tech_skips_expansion_when_budget_refuses(ctx):
    module, app, agent = ctx
    agent.default = []
    result = module.RagDeps().search_tech("火管 試験", None, claim_search=lambda: False)
    assert len(agent.calls) == 1 and result["evidence"] == []


def test_search_tech_does_not_expand_when_results_exist(ctx):
    module, app, agent = ctx
    agent.default = [_chunk()]
    module.RagDeps().search_tech("火管 試験", None, claim_search=lambda: pytest.fail("no extra call needed"))
    assert len(agent.calls) == 1


# ---------------------------------------------------------------- 法令

@pytest.fixture
def law_on(ctx, monkeypatch):
    module, app, agent = ctx
    monkeypatch.setattr(app, "ENVIRONMENT", "dev")
    monkeypatch.setattr(app, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(app, "LAW_KNOWLEDGE_BASE_ID", "LAWKB12345")
    monkeypatch.setattr(app, "LAW_DATA_BUCKET_NAME", "")
    return module, app, agent


def test_law_is_unavailable_unless_dev_flag_and_kb_are_configured(ctx, monkeypatch):
    module, app, agent = ctx
    monkeypatch.setattr(app, "LAW_RAG_ENABLED", "false")
    assert module.RagDeps().law_available is False
    monkeypatch.setattr(app, "ENVIRONMENT", "prod")
    monkeypatch.setattr(app, "LAW_RAG_ENABLED", "true")
    monkeypatch.setattr(app, "LAW_KNOWLEDGE_BASE_ID", "LAWKB12345")
    assert module.RagDeps().law_available is False


def test_search_law_returns_only_egov_citable_provisions(law_on):
    module, app, agent = law_on
    assert module.RagDeps().law_available is True
    agent.by_kb["LAWKB12345"] = [_law_chunk(), _law_chunk("第三十六条", 0.6, source_url="https://evil.example/x")]
    result = module.RagDeps().search_law("昇降機 構造")
    assert [e["provision"] for e in result["evidence"]] == ["第三十五条"]
    law = result["evidence"][0]
    assert law["kind"] == "law" and law["lawTitle"] == "建築基準法"
    assert law["effectiveDate"] == "2025-04-01"
    assert law["sourceUrl"] == "https://laws.e-gov.go.jp/law/abc"
    assert law["text"].startswith("昇降機")
    assert result["hits"] == 2
    assert agent.calls[0]["knowledgeBaseId"] == "LAWKB12345"


def test_search_law_raises_when_disabled(ctx):
    module, app, agent = ctx
    with pytest.raises(Exception):
        module.RagDeps().search_law("昇降機")


# ---------------------------------------------------------------- モデル呼び出し

def test_call_model_uses_understand_model_for_the_small_steps(ctx, monkeypatch, capsys):
    module, app, agent = ctx
    calls = []

    def fake_invoke(client, model_id, system_prompt, messages, **kwargs):
        calls.append((model_id, system_prompt, messages, kwargs))
        return "出力", {'inputTokens': 123, 'outputTokens': 45, 'prompt': 'secret text'}, "end_turn"

    monkeypatch.setattr(app, "invoke_generation", fake_invoke)
    monkeypatch.setattr(app, "BEDROCK_MODEL_ID", "jp.anthropic.claude-sonnet-5-5-20260601-v1:0")
    monkeypatch.setenv("SENPAI_UNDERSTAND_MODEL_ID", "jp.anthropic.claude-haiku-4-5-20251001-v1:0")
    deps = module.RagDeps()
    assert deps.call_model("understand", "sys", "user", 700) == "出力"
    assert deps.call_model("sufficiency", "sys", "user", 500) == "出力"
    assert deps.call_model("synthesize", "sys", "user", 3000) == "出力"
    assert [c[0] for c in calls] == [
        "jp.anthropic.claude-haiku-4-5-20251001-v1:0", "jp.anthropic.claude-haiku-4-5-20251001-v1:0",
        "jp.anthropic.claude-sonnet-5-5-20260601-v1:0"]
    assert calls[0][2] == [{"role": "user", "content": "user"}]
    assert calls[0][3]["max_tokens"] == 700 and calls[0][3]["ensure_ascii"] is False
    logs = capsys.readouterr().out
    assert '"inputTokens":123' in logs and '"outputTokens":45' in logs
    assert 'secret text' not in logs and '出力' not in logs


def test_understand_model_falls_back_to_main_model_when_unset(ctx, monkeypatch):
    module, app, agent = ctx
    seen = []
    monkeypatch.setattr(app, "invoke_generation",
                        lambda client, model_id, *a, **k: seen.append(model_id) or ("x", {}, None))
    monkeypatch.setattr(app, "BEDROCK_MODEL_ID", "jp.anthropic.claude-haiku-4-5-20251001-v1:0")
    monkeypatch.setenv("SENPAI_UNDERSTAND_MODEL_ID", "")
    module.RagDeps().call_model("understand", "s", "u", 100)
    assert seen == ["jp.anthropic.claude-haiku-4-5-20251001-v1:0"]


def test_worker_clients_have_a_single_attempt_and_finite_wait(ctx, monkeypatch):
    import boto3
    module, app, _agent = ctx
    calls = []
    def client(service, **kwargs):
        calls.append((service, kwargs['config']))
        return object()
    monkeypatch.setattr(boto3, 'client', client)
    monkeypatch.setattr(app, 'bedrock_agent', app.bedrock_agent)
    monkeypatch.setattr(app, 'bedrock_runtime', app.bedrock_runtime)
    module.RagDeps().configure_worker_clients()
    assert {s for s, c in calls} == {'bedrock-runtime', 'bedrock-agent-runtime'}
    assert all(c.retries == {'total_max_attempts': 1} and c.read_timeout == 40 and c.connect_timeout == 5
               for s, c in calls)


# ---------------------------------------------------------------- ノウハウ

def _index(*cards):
    return {"schemaVersion": 1, "indexVersion": "sha256:" + "a" * 64,
            "generatedAt": "2026-10-20T00:00:00Z", "cards": list(cards)}


def _kcard(kid="KH-AX-001", title="かご走行中の振動", scope=("AXIEZ",), doc="TI-2024-017"):
    import hashlib
    body = "## 症状\nかごが走行中に振動する。\n\n## 対策\n締結状態を確認する。"
    return {"knowledgeId": kid, "cardVersion": 2, "sha256": hashlib.sha256(body.encode()).hexdigest(),
            "title": title, "status": "draft", "usage": "navigation_only", "body": body,
            "searchTerms": ["振動", "走行中", "かご"],
            "sourceRefs": [{"ref_type": "kb_document", "document_number": doc}],
            "modelScope": {"model_abbreviations": list(scope)}}


@pytest.fixture
def knowhow_on(ctx, monkeypatch):
    module, app, agent = ctx
    monkeypatch.setattr(app, "KNOWHOW_ENABLED", True)
    monkeypatch.setattr(app, "KNOWHOW_INDEX_BUCKET", "indexbucket")
    monkeypatch.setattr(app, "KNOWHOW_INDEX_KEY", "knowhow/index.json")
    monkeypatch.setattr(app, "DOCUMENTS_BUCKET", "docs-bucket")
    return module, app, agent


def test_knowhow_availability_follows_the_rag_feature_flag(ctx, knowhow_on, monkeypatch):
    module, app, agent = knowhow_on
    assert module.RagDeps().knowhow_available is True
    monkeypatch.setattr(app, "KNOWHOW_ENABLED", False)
    assert module.RagDeps().knowhow_available is False
    monkeypatch.setattr(app, "KNOWHOW_ENABLED", True)
    monkeypatch.setattr(app, "KNOWHOW_INDEX_BUCKET", "docs-bucket")  # 公開バケットと同居は拒否
    assert module.RagDeps().knowhow_available is False


def test_search_knowhow_returns_cards_hints_and_model_fit(knowhow_on, monkeypatch):
    module, app, agent = knowhow_on
    monkeypatch.setattr(app, "load_index", lambda **kw: _index(_kcard()))
    found = module.RagDeps().search_knowhow(["かごが走行中に振動"], "AXIEZ")
    assert found["status"] == "matched"
    card = found["cards"][0]
    assert card["knowledgeId"] == "KH-AX-001" and card["cardVersion"] == 2
    assert card["status"] == "draft" and card["modelFit"] == "matched"
    assert "## 症状" in card["body"]
    assert found["hints"] == ["TI-2024-017"]


def test_search_knowhow_merges_multiple_queries_without_duplicates(knowhow_on, monkeypatch):
    module, app, agent = knowhow_on
    monkeypatch.setattr(app, "load_index", lambda **kw: _index(_kcard(), _kcard("KH-AX-002", "かごの振動 別事例")))
    found = module.RagDeps().search_knowhow(["かごが走行中に振動", "かご 振動 走行中"], None)
    ids = [c["knowledgeId"] for c in found["cards"]]
    assert len(ids) == len(set(ids)) and 1 <= len(ids) <= 3


def test_managed_adapter_forwards_budget_and_keeps_kb_hints(knowhow_on, monkeypatch):
    module, app, _agent = knowhow_on
    monkeypatch.setenv("KNOWHOW_BACKEND", "managed")
    monkeypatch.setattr(app, "load_index", lambda **_kw: _index(_kcard()))
    claims = []

    def retrieve(index, query, model_type=None, claim_search=None, max_matches=3):
        assert claim_search()
        return {"matches": index["cards"]}

    monkeypatch.setattr(app, "retrieve_cards", retrieve)
    deps = module.RagDeps()
    assert deps.knowhow_uses_remote
    found = deps.search_knowhow(["振動"], "AXIEZ", claim_search=lambda: claims.append(1) or True)
    assert claims == [1] and found["hints"] == ["TI-2024-017"]
    with pytest.raises(module.KnowhowUnavailable):
        deps.search_knowhow(["振動"], "AXIEZ")


@pytest.mark.parametrize("backend", ["local", "managed"])
def test_knowhow_selection_preserves_a_later_query_top_candidate(knowhow_on, monkeypatch, backend):
    module, app, _agent = knowhow_on
    monkeypatch.setenv("KNOWHOW_BACKEND", backend)
    cards = [_kcard(f"KH-SYNTHETIC-{number}", doc=f"DOC-{number}") for number in range(4)]
    monkeypatch.setattr(app, "load_index", lambda **_kwargs: _index(*cards))
    calls = []

    def retrieve(index, query, model_type=None, claim_search=None, max_matches=3):
        calls.append(query)
        if backend == "managed":
            assert claim_search()
        return {"matches": cards[:3] if query == "first" else [cards[3], cards[1]]}

    monkeypatch.setattr(app, "search_index" if backend == "local" else "retrieve_cards", retrieve)
    claims = []
    found = module.RagDeps().search_knowhow(
        ["first", "second"], None, claim_search=lambda: claims.append(1) or True)
    assert [card["knowledgeId"] for card in found["cards"]] == [
        "KH-SYNTHETIC-0", "KH-SYNTHETIC-3", "KH-SYNTHETIC-1", "KH-SYNTHETIC-2"]
    assert found["candidateIdsByQuery"] == [
        ["KH-SYNTHETIC-0", "KH-SYNTHETIC-1", "KH-SYNTHETIC-2"],
        ["KH-SYNTHETIC-3", "KH-SYNTHETIC-1"]]
    assert found["hints"] == ["DOC-0", "DOC-3", "DOC-1", "DOC-2"]
    assert calls == ["first", "second"]
    assert len(claims) == (2 if backend == "managed" else 0)


def test_knowhow_merged_cards_keep_the_combined_body_budget(knowhow_on, monkeypatch):
    module, app, _agent = knowhow_on
    monkeypatch.setenv("KNOWHOW_BACKEND", "local")
    cards = [_kcard(f"KH-SYNTHETIC-{number}") for number in range(4)]
    for card, size in zip(cards, [9000, 1000, 1000, 9000]):
        card["body"] = "x" * size
    monkeypatch.setattr(app, "load_index", lambda **_kwargs: _index(*cards))
    monkeypatch.setattr(app, "search_index", lambda index, query, model_type=None, **kw: {
        "matches": cards[:3] if query == "first" else [cards[3]]})
    found = module.RagDeps().search_knowhow(["first", "second"], None)
    assert sum(len(card["body"]) for card in found["cards"]) <= 16000
    assert [card["knowledgeId"] for card in found["cards"]] == [
        "KH-SYNTHETIC-0", "KH-SYNTHETIC-1", "KH-SYNTHETIC-2"]


def test_search_knowhow_raises_unavailable_when_the_index_cannot_be_read(knowhow_on, monkeypatch):
    module, app, agent = knowhow_on

    def broken(**kw):
        raise app.KnowhowIndexError("bad")

    monkeypatch.setattr(app, "load_index", broken)
    with pytest.raises(module.KnowhowUnavailable):
        module.RagDeps().search_knowhow(["振動"], None)


# ---------------------------------------------------------------- ログ

def test_adapter_logs_never_contain_queries_or_text(ctx, capsys):
    module, app, agent = ctx
    agent.default = [_chunk(text=f"本文{SECRET}")]
    module.RagDeps().search_tech(f"質問{SECRET}", None)
    captured = capsys.readouterr()
    assert SECRET not in captured.out and SECRET not in captured.err
