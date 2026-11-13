"""Structural checks on a proposed body: odd characters, links and HTML, headings, code fences.

The heading and fence rules match findRewriteBodyProblem in frontend/src/lib/knowhow-rewrite-sections.mjs
(same fence regex and closing rule), so a body the server accepts is not rejected by the screen.
"""
import re
import unicodedata

from rewrite_tokens import canonical

_ALLOWED_CONTROLS = frozenset("\n\r\t")
_LINES = re.compile(r"\r\n|\n|\r")
_FENCE = re.compile(r"\s{0,3}(`{3,}|~{3,})(.*)$")
_H2 = re.compile(r" {0,3}##(?:[ \t]|$)")
_SETEXT = re.compile(r" {0,3}(?:-{3,}|={3,})[ \t]*$")
_FRONTMATTER = re.compile(r"-{3,}(?:\s.*)?")
_LINK_OR_HTML = re.compile(
    r"(?:https?://|www\.)[^\s<>()\[\]\"']{0,500}"
    r"|!?\[[^\]\n]{0,300}\]\([^)\n]{0,500}\)?"
    r"|!\["
    r"|\]\("
    r"|<[A-Za-z/!][^<>\n]{0,200}"
    r"|(?:javascript|vbscript|data|file|ftp|mailto)\s{0,3}:[^\s]{0,200}",
    re.IGNORECASE,
)


def has_suspicious_chars(text: str) -> bool:
    """Format characters (zero-width, bidi, BOM), surrogates, and control characters other than newline / tab."""
    for char in text:
        category = unicodedata.category(char)
        if category in ("Cf", "Cs") or (category == "Cc" and char not in _ALLOWED_CONTROLS):
            return True
    return False


def link_or_html_items(text: str) -> set:
    """URLs, Markdown links and images, HTML tags and script-like schemes found in the text (canonical form)."""
    return set(_LINK_OR_HTML.findall(canonical(text)))


def has_new_link_or_html(body: str, original: str) -> bool:
    return not link_or_html_items(body) <= link_or_html_items(original)


def _fence_tracker():
    state = {"open": None}

    def is_fenced(line: str) -> bool:
        match = _FENCE.match(line)
        current = state["open"]
        if current is None:
            if not match or (match.group(1)[0] == "`" and "`" in match.group(2)):
                return False
            state["open"] = (match.group(1)[0], len(match.group(1)))
            return True
        closes = match and match.group(1)[0] == current[0] and len(match.group(1)) >= current[1] and not match.group(2).strip()
        if closes:
            state["open"] = None
        return True

    return is_fenced, state


def structure_problems(body: str) -> list:
    """Codes: heading_in_body (## line, setext line, leading ---) and unclosed_fence."""
    lines = _LINES.split(body)
    first = next((line.strip() for line in lines if line.strip()), "")
    problems = ["heading_in_body"] if _FRONTMATTER.fullmatch(first) else []
    is_fenced, state = _fence_tracker()
    for line in lines:
        if is_fenced(line):
            continue
        if (_H2.match(line) or _SETEXT.match(line)) and "heading_in_body" not in problems:
            problems.append("heading_in_body")
    if state["open"] is not None:
        problems.append("unclosed_fence")
    return problems
