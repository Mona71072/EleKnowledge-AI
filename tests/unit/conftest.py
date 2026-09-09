"""tests/unit 共通フィクスチャ。

lambda/rag/rag-function 配下のモジュールを importlib で読み込む処理を一元化する。

- app.py の module スコープは boto3 クライアント・DynamoDB Table を生成するため、
  読み込み結果は名前ごとにキャッシュし、テストセッション全体で1回だけ exec する
- answer_policy.py が retrieval_policy を import するため、exec 中だけ RAG_DIR を
  sys.path に載せ、終了後に必ず戻す（他テストへの path 汚染を防ぐ）
"""
import importlib.util
import os
import sys

import pytest

BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../.."))
RAG_DIR = os.path.join(BASE, "lambda", "rag", "rag-function")

_MODULE_CACHE = {}


def _load_rag_module(name: str, filename: str):
    if name in _MODULE_CACHE:
        return _MODULE_CACHE[name]
    os.environ.setdefault("CHATLOGS_TABLE", "test-chatlogs")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    before = set(sys.modules)
    inserted = RAG_DIR not in sys.path
    if inserted:
        sys.path.insert(0, RAG_DIR)
    try:
        path = os.path.join(RAG_DIR, filename)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        if inserted:
            sys.path.remove(RAG_DIR)
    # exec 中の import で素の名前（retrieval_policy 等）が sys.modules に残ると、
    # 将来別 Lambda の同名モジュールと衝突して実行順依存になるため登録を外す
    # （読み込んだモジュール自身は参照を保持しているので動作に影響しない）
    for key, loaded in list(sys.modules.items()):
        if (
            key != name
            and key not in before
            and str(getattr(loaded, "__file__", "")).startswith(RAG_DIR)
        ):
            del sys.modules[key]
    _MODULE_CACHE[name] = mod
    return mod


@pytest.fixture(scope="session")
def load_rag_module():
    """rag-function 配下のファイルを独立モジュールとして読み込むローダー。"""
    return _load_rag_module


@pytest.fixture(scope="session")
def rag_app():
    """現行実装 app.py。セッション全体で1回だけ読み込んで共有する。"""
    return _load_rag_module("rag_app_under_test", "app.py")
