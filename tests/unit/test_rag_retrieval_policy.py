"""Parity tests for the extracted retrieval policy module.

移行期間限定のテスト: app.py が retrieval_policy を import するよう配線された
時点で new == legacy は恒真（自明に成立）になるため、配線 PR で本ファイルを
モジュール単体の振る舞いテストへ書き換える（または削除する）こと。
"""
import pytest


@pytest.fixture(scope="module")
def modules(rag_app, load_rag_module):
    return rag_app, load_rag_module("rag_retrieval_new", "retrieval_policy.py")


def test_policy_constants_match_existing_behavior(modules):
    legacy, new = modules
    assert new.PAGE_NUMBER_META_KEYS == legacy.PAGE_NUMBER_META_KEYS


def _text_result(uri: str, score: float, text: str, chunk_id: str = ""):
    metadata = {"x-amz-bedrock-kb-source-uri": uri}
    if chunk_id:
        metadata["x-amz-bedrock-kb-chunk-id"] = chunk_id
    return {
        "score": score,
        "metadata": metadata,
        "content": {"text": text},
    }


def test_chunk_helpers_match_existing_behavior(modules):
    legacy, new = modules
    text = {"content": {"text": "abc"}}
    image = {"content": {"type": "IMAGE", "byteContent": "data:image/png;base64,XYZ"}}

    assert new.chunk_text(text) == legacy.chunk_text(text)
    assert new.chunk_text(image) == legacy.chunk_text(image)
    assert new.chunk_image_b64(image) == legacy.chunk_image_b64(image)


def test_merge_results_matches_existing_behavior(modules):
    legacy, new = modules
    first = _text_result("s3://b/a.pdf", 0.4, "same", "1")
    better = _text_result("s3://b/a.pdf", 0.9, "same", "1")
    other = _text_result("s3://b/b.pdf", 0.7, "other", "2")

    assert new.merge_retrieval_results([first, other], [better]) == legacy.merge_retrieval_results(
        [first, other], [better]
    )


def test_page_number_matches_existing_behavior(modules):
    legacy, new = modules
    cases = [
        {"x-amz-bedrock-kb-document-page-number": "3"},
        {"x-amz-bedrock-kb-page-number": 4.0},
        {"x-amz-bedrock-kb-document-page-number": "bad"},
        {},
    ]
    for metadata in cases:
        assert new.extract_page_number(metadata) == legacy.extract_page_number(metadata)


@pytest.mark.parametrize("mode", ["normal", "spec"])
def test_selection_matches_existing_behavior(modules, mode):
    legacy, new = modules
    results = [
        _text_result("s3://b/a.pdf", 0.91, "a1", "1"),
        _text_result("s3://b/a.pdf", 0.89, "a2", "2"),
        _text_result("s3://b/a.pdf", 0.87, "a3", "3"),
        _text_result("s3://b/b.pdf", 0.50, "b1", "4"),
        _text_result("s3://b/c.pdf", 0.29, "c1", "5"),
    ]

    assert new.select_retrieval_results(results, mode) == legacy.select_retrieval_results(
        results, mode
    )


@pytest.mark.parametrize(
    "results,mode",
    [
        ([], "normal"),
        ([_text_result("s3://b/a.pdf", 0.1, "a")], "normal"),
        ([_text_result("s3://b/a.pdf", 0.55, "a")], "normal"),
        ([_text_result("s3://b/a.pdf", 0.25, "a")], "spec"),
    ],
)
def test_weak_gate_matches_existing_behavior(modules, results, mode):
    legacy, new = modules
    assert new.is_weak_retrieval(results, mode) == legacy.is_weak_retrieval(results, mode)


@pytest.mark.parametrize("mode", ["normal", "spec"])
@pytest.mark.parametrize(
    "score",
    [0.199, 0.2, 0.201, 0.219, 0.22, 0.221, 0.299, 0.3, 0.301],
)
def test_threshold_boundaries_match_existing_behavior(modules, mode, score):
    # 閾値（spec 0.2 / weak-gate 0.22 / normal 0.3）の境界前後を総当たりで固定し、
    # 片側コピーだけ閾値が調整された場合に固定入力サンプルをすり抜けるのを防ぐ
    legacy, new = modules
    results = [_text_result("s3://b/a.pdf", score, "t", "1")]
    assert new.select_retrieval_results(results, mode) == legacy.select_retrieval_results(
        results, mode
    )
    assert new.is_weak_retrieval(results, mode) == legacy.is_weak_retrieval(results, mode)


def test_rank_key_is_optional_and_only_changes_order(modules):
    legacy, new = modules
    results = [
        {**_text_result("s3://b/a.pdf", 0.9, "a"), "rerankScore": 0.1},
        {**_text_result("s3://b/b.pdf", 0.8, "b"), "rerankScore": 0.9},
        _text_result("s3://b/c.pdf", 0.7, "c"),
    ]

    assert new.select_retrieval_results(results) == legacy.select_retrieval_results(results)
    selected = new.select_retrieval_results(results, rank_key="rerankScore")
    assert [item["content"]["text"] for item in selected] == ["b", "a", "c"]
    assert [item["score"] for item in selected] == [0.8, 0.9, 0.7]
