"""CloudWatch への構造化ログ。段階名・件数・時間・終了理由・エラー種別だけを出す。

SECURITY: 質問・検索語・本文・回答は出さない。許可するのは数値・真偽値と、
英数字・記号だけの短い識別子のみ（日本語や空白を含む文字列は捨てる）。
"""
import json
import re

_SAFE_TOKEN = re.compile(r'^[A-Za-z0-9_.:-]{1,40}$')


def _safe(value):
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return value
    if isinstance(value, str) and _SAFE_TOKEN.fullmatch(value):
        return value
    return None


def log(stage: str, status: str, error: Exception = None, **fields) -> None:
    record = {'event': 'senpai_research', 'stage': stage, 'status': status}
    if error is not None:
        record['errorClass'] = type(error).__name__
    for key, value in fields.items():
        safe = _safe(value)
        if safe is not None:
            record[key] = safe
    print(json.dumps(record, separators=(',', ':')))
