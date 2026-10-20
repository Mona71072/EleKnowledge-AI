"""Scoring behaviour of the Senpai know-how retrieval (bounded, IDF-weighted, normalised)."""
import hashlib
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "lambda/rag/rag-function/knowhow_retrieval.py"


def _module():
    spec = importlib.util.spec_from_file_location("knowhow_scoring_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _card(knowledge_id, title, terms=(), body="", scope=None):
    body = body or f"## 症状\n{title}\n\n## 対策\n手順に従う。"
    return {
        "knowledgeId": knowledge_id,
        "cardVersion": 1,
        "sha256": hashlib.sha256(body.encode()).hexdigest(),
        "title": title,
        "status": "draft",
        "usage": "navigation_only",
        "body": body,
        "searchTerms": [title, *terms],
        "sourceRefs": [{"ref_type": "lists_item", "list_item_id": "1"}],
        "modelScope": scope or {},
    }


def _index(*cards):
    return {
        "schemaVersion": 1,
        "indexVersion": "sha256:" + "b" * 64,
        "generatedAt": "2026-10-21T00:00:00Z",
        "cards": list(cards),
    }


def _generic_index():
    return _index(
        _card("KH-G-001", "エラーコードの見方", ["エラー", "3桁"]),
        _card("KH-G-002", "ヘルスエアーの立上げ不良 タイマーリレー誤品", ["ヘルスエア"]),
        _card("KH-G-003", "ドア異音の確認", ["異音", "ドア"]),
        _card("KH-G-004", "巻上機ロープカバーの確認", ["巻上機"]),
        _card("KH-G-005", "照度の確認方法", ["照度"]),
    )


def _ids(result):
    return [card["knowledgeId"] for card in result["matches"]]


def test_scores_are_bounded_between_zero_and_one():
    module = _module()
    code_card = _card("KH-C-001", "エラー421 TI-1406 戸開不能", ["421", "TI-1406", "VFGLF"],
                      body="421 TI-1406 VFGLF " * 20)
    index = _index(code_card, *_generic_index()["cards"])
    queries = ["エラー421 TI-1406 VFGLF 戸開不能", "421", "ドア異音の確認", "給与明細の見方",
               "x" * 50, "戸開不能" * 100]
    for query in queries:
        for score, _card_ in module.rank_cards(index, query):
            assert 0.0 <= score <= 1.0


@pytest.mark.parametrize("query", ["給与明細の見方", "パソコンが起動しない", "今日の天気を教えて", "昼ご飯のおすすめは"])
def test_unrelated_queries_are_not_found_despite_shared_generic_words(query):
    module = _module()

    result = module.search_index(_generic_index(), query)

    assert result["status"] == "not_found" and result["matches"] == []


@pytest.mark.parametrize("query", ["教えてください", "できない", "について", "ください"])
def test_stopword_only_query_is_not_found(query):
    module = _module()
    index = _index(_card("KH-S-001", "教えてください資料", ["できない", "について"]))

    assert module.search_index(index, query)["status"] == "not_found"


@pytest.mark.parametrize("query", [
    "たいまーりれー", "タイマリレー", "ﾀｲﾏｰﾘﾚｰ", "ヘルスエア タイマーリレー", "へるすえあー",
])
def test_katakana_hiragana_halfwidth_and_long_vowel_variants_match(query):
    module = _module()

    assert _ids(module.search_index(_generic_index(), query))[:1] == ["KH-G-002"]


def test_hiragana_card_text_matches_katakana_query():
    module = _module()
    index = _index(_card("KH-H-001", "戸閉時のがたつき", ["がたつき"]), *_generic_index()["cards"])

    assert _ids(module.search_index(index, "ガタツキ"))[:1] == ["KH-H-001"]


def test_alias_dictionary_maps_katakana_product_names_to_card_vocabulary():
    module = _module()
    index = _index(
        _card("KH-A-001", "LINKs ブレーキスイッチ設定不良", ["LINKs"]),
        _card("KH-A-002", "NEXCUBE 品質確認", ["NEXCUBE"]),
        *_generic_index()["cards"],
    )

    assert _ids(module.search_index(index, "リンクス ブレーキスイッチ"))[:1] == ["KH-A-001"]
    assert _ids(module.search_index(index, "ネクスキューブ 品質"))[:1] == ["KH-A-002"]


def test_exact_error_code_ranks_the_card_with_that_code_first():
    module = _module()
    index = _index(
        _card("KH-E-031", "ドア駆動基板エラー31", ["エラー31", "31"],
              body="## 症状\nエラーが出る。エラー表示の確認。エラー履歴。"),
        _card("KH-E-421", "かご上の伝送異常", ["421", "CAN"]),
        _card("KH-E-204", "U-CAN 異常 エラー204", ["204"], body="## 症状\nエラーエラーエラー"),
        *_generic_index()["cards"],
    )

    assert _ids(module.search_index(index, "エラー421"))[:1] == ["KH-E-421"]
    assert _ids(module.search_index(index, "421"))[:1] == ["KH-E-421"]
    assert _ids(module.search_index(index, "エラー31"))[:1] == ["KH-E-031"]


def test_idf_downweights_a_word_present_in_every_card():
    module = _module()
    index = _index(
        _card("KH-I-001", "巻上機の確認"),
        _card("KH-I-002", "ロープの確認"),
        _card("KH-I-003", "照度の確認"),
        _card("KH-I-004", "ドアの確認"),
        _card("KH-I-005", "非常灯の確認"),
    )
    scores = {card["knowledgeId"]: score for score, card in module.rank_cards(index, "巻上 確認")}

    # 確認 is in all five cards (no information); 巻上 only in one.
    assert scores["KH-I-001"] > 0.5
    assert scores["KH-I-002"] < scores["KH-I-001"] / 2


def test_relative_gate_drops_candidates_far_below_the_top_score():
    module = _module()
    assert module.RELATIVE_SCORE_GATE == 0.7
    index = _index(
        _card("KH-R-001", "ドア異音調整手順"),
        _card("KH-R-002", "ドア異音調整手順の記録"),
        _card("KH-R-003", "ドア異音の記録簿"),
        _card("KH-R-004", "巻上機の点検"),
        _card("KH-R-005", "照度測定"),
    )
    query = "ドア異音調整手順"
    scores = {card["knowledgeId"]: score for score, card in module.rank_cards(index, query)}
    assert module.MIN_MATCH_SCORE <= scores["KH-R-003"] < 0.7 * scores["KH-R-001"]

    ids = _ids(module.search_index(index, query))

    assert ids[0] == "KH-R-001" and "KH-R-002" in ids
    assert "KH-R-003" not in ids


def test_threshold_constant_is_in_the_roc_selected_range():
    module = _module()
    assert 0.18 <= module.MIN_MATCH_SCORE <= 0.22
    assert module.MAX_MATCHES == 3


def test_scores_and_order_are_deterministic_and_independent_of_card_order():
    module = _module()
    cards = _generic_index()["cards"]
    forward = module.rank_cards(_index(*cards), "ドア 異音 確認")
    again = module.rank_cards(_index(*cards), "ドア 異音 確認")
    reverse = module.rank_cards(_index(*reversed(cards)), "ドア 異音 確認")

    assert [(s, c["knowledgeId"]) for s, c in forward] == [(s, c["knowledgeId"]) for s, c in again]
    assert [(s, c["knowledgeId"]) for s, c in forward] == [(s, c["knowledgeId"]) for s, c in reverse]


def test_card_features_are_computed_once_per_index_and_not_reused_for_other_indexes(monkeypatch):
    module = _module()
    calls = []
    original = module._build_card_features
    monkeypatch.setattr(module, "_build_card_features", lambda card: calls.append(1) or original(card))
    index = _generic_index()

    module.search_index(index, "ドア 異音")
    first = len(calls)
    module.search_index(index, "巻上機 確認")
    assert len(calls) == first == len(index["cards"])

    changed = _index(_card("KH-G-003", "全く別のタイトル 異音"), *index["cards"][:2])
    result = module.search_index(changed, "全く別のタイトル")
    assert _ids(result)[:1] == ["KH-G-003"]


def test_long_natural_sentence_still_finds_its_card_despite_filler_ngrams():
    module = _module()
    fillers = [_card(f"KH-F-{n:03d}", f"{name}の資料") for n, name in enumerate(
        ["巻上機", "照度", "非常灯", "秤装置", "緩衝器", "ガバナ", "レール", "ロープ", "終点スイッチ",
         "戸閉装置", "操作盤", "制御盤", "乗場釦", "インジケータ", "防犯カメラ", "インターホン", "換気扇",
         "天井", "床", "ピット", "機械室", "昇降路", "トラベーター", "エスカレーター", "地震感知器",
         "火報盤", "監視盤", "群管理", "停電灯", "ブレーキ"])]
    target = _card("KH-L-001", "横保護線のケーブル条件と施工図の正本", ["横保護線", "施工図"])
    query = ("制御盤の横保護線のケーブル条件が、図面のページによって違って見えます。"
             "どちらが正しいのですか。どこを確認すればいいですか。教えてください。")

    result = module.search_index(_index(target, *fillers), query)

    assert _ids(result)[:1] == ["KH-L-001"]
    scores = {card["knowledgeId"]: score for score, card in module.rank_cards(_index(target, *fillers), query)}
    assert 0.0 <= scores["KH-L-001"] <= 1.0
