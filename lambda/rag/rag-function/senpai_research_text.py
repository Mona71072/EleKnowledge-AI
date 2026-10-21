"""調査ジョブの文字列まわりの共通部品（JSON 抽出・正規化・プロンプト用エスケープ）。"""
import html
import json
import unicodedata

STRING_FIELD_MAX_CHARS = 200


def normalize_for_match(value: str) -> str:
    """全角・半角・大小の違いを同じ語として比べるための正規化。"""
    return unicodedata.normalize('NFKC', str(value or '')).casefold().strip()


def extract_json_object(text: str):
    """モデルの出力から JSON オブジェクト1つを取り出す。見つからなければ None。"""
    if not isinstance(text, str):
        return None
    candidate = text.strip()
    for attempt in (candidate, _between_braces(candidate)):
        if not attempt:
            continue
        try:
            parsed = json.loads(attempt)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _between_braces(text: str) -> str:
    start, end = text.find('{'), text.rfind('}')
    return text[start:end + 1] if 0 <= start < end else ''


def clean_string(value, limit: int = STRING_FIELD_MAX_CHARS):
    """空でない文字列を limit 文字まで。文字列以外・空は None。"""
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped[:limit] if stripped else None


def escape_text(value: str) -> str:
    """非信頼データをタグ内に置くためのエスケープ（タグの閉じ・開きを作らせない）。"""
    return html.escape(str(value or ''), quote=False)


def escape_json(value) -> str:
    """JSON 文字列化したうえで <>& を \\u エスケープする（RAG のノウハウ受け渡しと同じ）。"""
    return (
        json.dumps(value, ensure_ascii=False, separators=(',', ':'))
        .replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    )
