"""質問の文言から、画面の機種キーを 1 つだけ決定的に読み取る（AI を使わない）。

2026-11-12 itai 決定: 先輩チャットで機種が未選択のとき、質問に 1 機種の呼び名だけがあれば、
画面で選んだのと同じ絞り込みにする。2 機種以上なら絞らない。呼び名の正本は語彙ファイルの
question_aliases（vocabulary_generated.QUESTION_MODEL_ALIASES）。

誤検知を避ける規則:
- 長い呼び名を先に当てる（「アクシーズリンクス」「AXIEZ-LINKs」の中の「アクシーズ」「AXIEZ」で AXIEZ にしない）。
- 前後が同じ種類の文字なら当てない（英数字の呼び名は英数字に、カタカナの呼び名はカタカナに挟まれていたら
  単語の一部とみなす。例:「リンクスイッチ」の「リンクス」、「hyperlinks」の「links」は当てない）。
"""
import importlib.util
import os
import re
import sys
import unicodedata

try:
    import vocabulary_generated as _vocabulary
except ModuleNotFoundError as exc:
    if exc.name != 'vocabulary_generated':
        raise
    _spec = importlib.util.spec_from_file_location(
        'question_model_vocabulary', os.path.join(os.path.dirname(__file__), 'vocabulary_generated.py'))
    _vocabulary = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _vocabulary
    _spec.loader.exec_module(_vocabulary)

MAX_QUESTION_CHARS = 12000
_LATIN = re.compile(r'[0-9a-z]')
_KATAKANA = re.compile(r'[゠-ヿ]')


def _normalize(value: str) -> str:
    return unicodedata.normalize('NFKC', value).casefold()


def _same_class(alias_char: str, neighbour: str) -> bool:
    for pattern in (_LATIN, _KATAKANA):
        if pattern.fullmatch(alias_char) and pattern.fullmatch(neighbour):
            return True
    return False


_ALIASES = sorted(
    ((_normalize(alias), model) for model, aliases in _vocabulary.QUESTION_MODEL_ALIASES.items()
     for alias in aliases if alias.strip()),
    key=lambda item: -len(item[0]))


def mentioned_models(question) -> list:
    """質問に出てくる機種キーを、出てきた順に重複なく返す。"""
    if not isinstance(question, str) or not question:
        return []
    text = _normalize(question[:MAX_QUESTION_CHARS])
    taken = [False] * len(text)
    found = []
    for alias, model in _ALIASES:
        start = text.find(alias)
        while start != -1:
            end = start + len(alias)
            before = text[start - 1] if start > 0 else ''
            after = text[end] if end < len(text) else ''
            if (not any(taken[start:end])
                    and not (before and _same_class(alias[0], before))
                    and not (after and _same_class(alias[-1], after))):
                for index in range(start, end):
                    taken[index] = True
                found.append((start, model))
            start = text.find(alias, start + 1)
    ordered = []
    for _, model in sorted(found):
        if model not in ordered:
            ordered.append(model)
    return ordered


def model_from_question(question):
    """1 機種だけが出てくるときにその機種キー、それ以外（0 または 2 以上）は None。"""
    models = mentioned_models(question)
    return models[0] if len(models) == 1 else None


def notice(model: str) -> str:
    return f'※質問の文言から機種を {model} と判断して絞り込みました（画面の「機種」で変更できます）。'
