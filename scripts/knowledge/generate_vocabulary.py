#!/usr/bin/env python3
"""適用範囲の語彙ファイルから、コードが使う機種の値を生成する（ノウハウ管理の見直し WP1、方法 A）。

正本は knowledge/registry/applicability-vocabulary.json。生成物は直接編集しない。
語彙ファイルを変えたら、このスクリプトを実行して生成物も一緒にコミットする。

生成物:
- lambda/rag/rag-function/vocabulary_generated.py      Lambda（UI_MODEL_FILTERS・検索の別名・質問中の呼び名・汎用ラベル）
- scripts/knowledge/vocabulary.generated.mjs           索引作成（検索の別名・汎用ラベル）
- frontend/src/data/kb-model-types.generated.mjs       画面（機種一覧・機種キー）

フロント用を .ts ではなく .mjs にしているのは、knowledge-research.mjs などを
`node --test` で直接 import するため（.ts は Node でそのまま読めない）。
kbModelTypes.ts がこれを import して型を付ける。

Usage:
    python scripts/knowledge/generate_vocabulary.py          # 生成物を書き換える
    python scripts/knowledge/generate_vocabulary.py --check  # 生成物が最新かだけ確かめる（差分があれば終了コード 1）
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VOCAB_REL = "knowledge/registry/applicability-vocabulary.json"
REGEN = "python scripts/knowledge/generate_vocabulary.py"
HEADER_LINES = (
    f"生成物。直接編集しない。元: {VOCAB_REL}。",
    f"再生成: {REGEN}",
)
OUTPUT_PY = "lambda/rag/rag-function/vocabulary_generated.py"
OUTPUT_INDEX_MJS = "scripts/knowledge/vocabulary.generated.mjs"
OUTPUT_FRONTEND_MJS = "frontend/src/data/kb-model-types.generated.mjs"


def normalize_label(value: str) -> str:
    """knowhow_retrieval.normalize_model_label と同じ正規化（NFKC・小文字化・前後の空白除去）。"""
    return unicodedata.normalize("NFKC", value).lower().strip()


def _unique(values):
    return list(dict.fromkeys(values))


def _py_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _js_str(value: str) -> str:
    # 既存コードに合わせて単一引用符で書く。エスケープが要る値は語彙に入れない前提で、入っていたら止める。
    if "'" in value or "\\" in value or "\n" in value:
        raise ValueError(f"引用符・バックスラッシュ・改行を含む値は生成できない: {value!r}")
    return f"'{value}'"


def load_model_entries(vocab: dict) -> list[dict]:
    """画面の機種キーを持つ製品系列だけを、語彙ファイルの順で返す。"""
    entries = [e for e in vocab["axes"]["product_lines"] if e.get("ui_filter")]
    keys = [e["ui_filter"]["key"] for e in entries]
    if len(keys) != len(set(keys)):
        raise ValueError(f"ui_filter.key が重複している: {keys}")
    return entries


def build_values(vocab: dict) -> dict:
    entries = load_model_entries(vocab)
    ui_filters = {e["ui_filter"]["key"]: list(e["ui_filter"]["kb_model_types"]) for e in entries}
    aliases = {
        e["ui_filter"]["key"]: _unique(
            normalize_label(v) for v in e["ui_filter"]["kb_model_types"] + e["ui_filter"]["extra_card_aliases"]
        )
        for e in entries
    }
    question_aliases = {e["ui_filter"]["key"]: list(e["question_aliases"]) for e in entries}
    labels = vocab["generic_labels"]
    return {
        "ui_filters": ui_filters,
        "aliases": aliases,
        "question_aliases": question_aliases,
        "generic_elevator": labels["elevator"],
        "generic_escalator": labels["escalator"],
    }


def render_python(values: dict) -> str:
    def tuple_lit(items):
        inner = ", ".join(_py_str(v) for v in items)
        return f"({inner},)" if len(items) == 1 else f"({inner})"

    lines = ['"""' + HEADER_LINES[0], HEADER_LINES[1], "", "rag-function と同じ CodeUri で配る。値の意味は APPLICABILITY-TAXONOMY.md を参照。", '"""', ""]
    lines.append("# 画面の機種キー → 共有 KB の model_type（要素完全一致で listContains に展開する）。")
    lines.append("UI_MODEL_FILTERS = {")
    lines += [f"    {_py_str(k)}: {tuple_lit(v)}," for k, v in values["ui_filters"].items()]
    lines.append("}")
    lines.append("")
    lines.append("# 機種キー → カードの model_scope に書かれた値の別名（NFKC・小文字化済み）。")
    lines.append("MODEL_ALIASES = {")
    lines += [
        f"    {_py_str(k)}: frozenset({{{', '.join(_py_str(a) for a in v)}}}),"
        for k, v in values["aliases"].items()
    ]
    lines.append("}")
    lines.append("")
    lines.append("# 機種キー → 質問中の呼び名（調査ジョブが質問から機種を判定するときに使う）。")
    lines.append("QUESTION_MODEL_ALIASES = {")
    lines += [f"    {_py_str(k)}: {tuple_lit(v)}," for k, v in values["question_aliases"].items()]
    lines.append("}")
    lines.append("")
    lines.append(f"GENERIC_ELEVATOR_LABEL = {_py_str(values['generic_elevator'])}")
    lines.append(f"GENERIC_ESCALATOR_LABEL = {_py_str(values['generic_escalator'])}")
    return "\n".join(lines) + "\n"


def _js_header() -> list[str]:
    return [f"// {line}" for line in HEADER_LINES]


def render_index_mjs(values: dict) -> str:
    lines = _js_header() + [
        "",
        "// 機種キー → カードの model_scope に書かれた値の別名（NFKC・小文字化済み）。build-senpai-index.mjs が使う。",
        "export const MODEL_ALIASES = Object.freeze({",
    ]
    lines += [
        f"  {_js_str(k)}: Object.freeze([{', '.join(_js_str(a) for a in v)}]),"
        for k, v in values["aliases"].items()
    ]
    lines += [
        "});",
        f"export const GENERIC_ELEVATOR_LABEL = {_js_str(values['generic_elevator'])};",
        f"export const GENERIC_ESCALATOR_LABEL = {_js_str(values['generic_escalator'])};",
    ]
    return "\n".join(lines) + "\n"


def render_frontend_mjs(values: dict) -> str:
    lines = _js_header() + [
        "",
        "// 画面の機種一覧。value は API の filters.modelType に渡すキー、targets はサーバーが展開する model_type。",
        "export const KB_MODEL_TYPES = Object.freeze([",
    ]
    for key, targets in values["ui_filters"].items():
        lines.append(
            f"  Object.freeze({{ value: {_js_str(key)}, label: {_js_str(key)}, "
            f"targets: Object.freeze([{', '.join(_js_str(t) for t in targets)}]) }}),"
        )
    lines += [
        "]);",
        "",
        "// 機種キーの一覧（UI_MODEL_FILTERS のキー・検索の MODEL_ALIASES のキーと同じ）。",
        f"export const KB_MODEL_KEYS = Object.freeze([{', '.join(_js_str(k) for k in values['ui_filters'])}]);",
    ]
    return "\n".join(lines) + "\n"


def render_all(vocab: dict) -> dict[str, str]:
    values = build_values(vocab)
    return {
        OUTPUT_PY: render_python(values),
        OUTPUT_INDEX_MJS: render_index_mjs(values),
        OUTPUT_FRONTEND_MJS: render_frontend_mjs(values),
    }


def load_vocab(root: Path = ROOT) -> dict:
    return json.loads((root / VOCAB_REL).read_text(encoding="utf-8"))


def stale_outputs(root: Path = ROOT) -> list[str]:
    """生成し直した内容と、作業ツリーの生成物が違うものを返す（改行は LF に揃えて比べる）。"""
    stale = []
    for rel, text in render_all(load_vocab(root)).items():
        path = root / rel
        current = path.read_text(encoding="utf-8").replace("\r\n", "\n") if path.exists() else None
        if current != text:
            stale.append(rel)
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="生成物が最新かだけ確かめる")
    args = parser.parse_args(argv)
    if args.check:
        stale = stale_outputs()
        for rel in stale:
            print(f"古い生成物: {rel}（{REGEN} を実行する）", file=sys.stderr)
        return 1 if stale else 0
    for rel, text in render_all(load_vocab()).items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print(f"生成: {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
