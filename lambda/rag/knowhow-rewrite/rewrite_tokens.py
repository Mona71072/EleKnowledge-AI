"""Value tokens (document numbers, rule numbers, quantities) used to back a rewritten body with evidence.

Based on frontend/src/lib/knowhow-card-check-text.mjs, but stricter: a number followed by anything that
looks like a unit counts as a quantity, whatever the unit is. All matching happens on a canonical form
(NFKC, no format characters, digit-group commas removed, ASCII minus) and on a second form without Markdown
emphasis marks, so `**600** cm` is checked as `600 cm`. Whitespace and case are ignored when comparing.

Every regex runs on segments of at most MAX_SEGMENT_CHARS and has no nested unbounded quantifier over the
same characters, so the time grows linearly with the input length.
"""
import re
import unicodedata

MAX_SEGMENT_CHARS = 2_000

_DOCUMENT = r"(?<![A-Za-z0-9-])(?!KH-)[A-Z]{1,4}(?:-[A-Z0-9]+(?:\.[0-9A-Z]+)*|・[0-9]+(?:\.[0-9]+)*)+"
_RULE = r"告示\s?(?:第\s?)?[0-9]+(?:\s?号)?|JIS\s?[A-Z]?\s?[0-9]{3,5}|(?:第\s?)?(?<![0-9])[0-9]+\s?条"
_JP_UNIT = (
    "ミリ|センチ|メートル|キロ|グラム|リットル|ボルト|アンペア|ワット|ヘルツ|ルクス|秒|分|度|回|個|本|階|台|枚|倍|割"
    "|人|名|件|箇所|か所|ヶ所|カ所|段|極"
)
_UNIT = rf"(?:[A-Za-z]{{1,4}}(?![A-Za-z])|°C|[°%μΩ]|{_JP_UNIT})"
_SEP = r"[ \t]{0,2}"
_NUMBER = r"[0-9]+(?:\.[0-9]+)?"
_QUANTITY = rf"(?:(?<![0-9A-Za-z])[-+]|±)?(?<![0-9]){_NUMBER}{_SEP}{_UNIT}"
_KANJI = rf"[〇零一二三四五六七八九十百千万]{{1,10}}{_SEP}{_UNIT}"
_VALUE = re.compile(rf"(?P<doc>{_DOCUMENT})|(?P<rule>{_RULE})|(?P<quantity>{_QUANTITY})|(?P<kanji>{_KANJI})")
_BARE_NUMBER = re.compile(r"(?<![0-9A-Za-z.])[0-9]+(?:\.[0-9]+)?(?![0-9A-Za-z])")
_LIST_MARKER = re.compile(r"^\s{0,3}[0-9]{1,3}[.)）]\s")
_GROUP_COMMA = re.compile(r"(?<=[0-9]),(?=[0-9])")
_MINUS_LIKE = str.maketrans({c: "-" for c in "−‒–—―﹣"})
_EMPHASIS = re.compile(r"[*_`]|~~")
_SPACES = re.compile(r"\s+")
_DIGIT = re.compile(r"[0-9]")
_ENOUGH = ("十", "分")  # 「十分に」は数量ではない


def canonical(text: str) -> str:
    """NFKC, no format characters (zero-width etc.), ASCII minus, digit-group commas removed."""
    text = unicodedata.normalize("NFKC", text or "")
    text = "".join(c for c in text if unicodedata.category(c) != "Cf").translate(_MINUS_LIKE)
    return _GROUP_COMMA.sub("", text)


def variants(text: str) -> list:
    """The canonical form and the same text without Markdown emphasis marks (checked both ways)."""
    base = canonical(text)
    plain = _EMPHASIS.sub("", base)
    return [base] if plain == base else [base, plain]


def token_key(token: str) -> str:
    return _SPACES.sub("", token).lower()


def _prepared(text: str) -> str:
    """Line-start list numbers removed, lines joined by a space (so a number and its unit on two lines meet)."""
    return " ".join(_LIST_MARKER.sub("", line) for line in re.split(r"\r\n|\n|\r", text))


def _segments(text: str):
    prepared = _prepared(text)
    for start in range(0, max(len(prepared), 1), MAX_SEGMENT_CHARS):
        yield prepared[start:start + MAX_SEGMENT_CHARS]


def _is_value(match: re.Match) -> bool:
    if match.group("doc") is not None:
        return bool(_DIGIT.search(match.group("doc")))
    if match.group("kanji") is not None:
        text = match.group("kanji").replace(" ", "")
        return text[0] != _ENOUGH[0] or text[1:] != _ENOUGH[1]
    return True


def _value_spans(segment: str) -> list:
    return [(m.start(), m.end()) for m in _VALUE.finditer(segment) if _is_value(m)]


def value_tokens(text: str) -> list:
    """Values in order of appearance (all forms), one entry per distinct key."""
    found = {}
    for form in variants(text):
        for segment in _segments(form):
            for start, end in _value_spans(segment):
                token = segment[start:end].strip()
                found.setdefault(token_key(token), token)
    return list(found.values())


def _is_number(token: str) -> bool:
    return "." in token or len(token) >= 2


def all_numbers(text: str) -> set:
    return {
        match.group(0)
        for form in variants(text) for segment in _segments(form)
        for match in _BARE_NUMBER.finditer(segment) if _is_number(match.group(0))
    }


def bare_numbers(text: str) -> list:
    """Numbers (2+ digits or decimal) that are not part of a value token, in order of appearance."""
    found = {}
    for form in variants(text):
        for segment in _segments(form):
            blanked = list(segment)
            for start, end in _value_spans(segment):
                blanked[start:end] = " " * (end - start)
            for match in _BARE_NUMBER.finditer("".join(blanked)):
                if _is_number(match.group(0)):
                    found.setdefault(match.group(0), None)
    return list(found)


class Support:
    """What the request itself backs: value keys and numbers found in the allowed texts."""

    def __init__(self, texts: list) -> None:
        self.keys = {token_key(token) for text in texts for token in value_tokens(text)}
        self.numbers = set().union(*(all_numbers(text) for text in texts)) if texts else set()

    def unsupported_values(self, body: str) -> list:
        return [token for token in value_tokens(body) if token_key(token) not in self.keys]

    def unverified_numbers(self, body: str) -> list:
        return [number for number in bare_numbers(body) if number not in self.numbers]
