"""Pure query interpretation policy for EleKnowledge RAG.

This module intentionally contains no AWS clients or persistence.  Keeping the
query/clarification rules pure makes them independently testable and prevents
app.py from mixing request handling, retrieval, persistence, and domain policy.

During the refactor transition, behavior must remain equivalent to the existing
functions in app.py.  Retrieval strategy changes belong in separate PRs.

注意（移行期間中）: app.py はまだ本モジュールを import しておらず、本番 Lambda は
app.py 側のコピーで動作している。app.py の該当ロジックを変更する場合は、必ず
本モジュールと tests/unit/test_rag_query_policy.py のパリティテストも同時に
更新すること（片側だけの変更は配線 PR で本番挙動を巻き戻す）。
"""
import re
import unicodedata


CLARIFY_MARKER = "該当ページを探すために教えてください"

SYMPTOM_RE = re.compile(
    r"振動|騒音|異音|音が|動かない|動かなく|停止|止まら|止ま[るっ]|できない|"
    r"開かない|閉まらない|異臭|エラー|故障|不具合|異常|警報|アラーム|"
    r"過熱|焦げ|漏電|トリップ|作動しない|動作しない|上がらない|下がらない|"
    r"ガタ|がたつき|煙|臭い|鳴[るりっ]|点滅|点灯しない"
)
PART_RE = re.compile(
    r"かご|ドア|扉|巻上|制御盤|制御|ロープ|ガバナ|バッファ|ピット|"
    r"乗場|カゴ|扉開|戸開|戸閉|操作盤|インバータ|モータ|ブレーキ"
)
SITUATION_RE = re.compile(
    r"走行中|停止中|開閉時|起動時|着床|階間|停電|復旧|点検中|"
    r"運転中|待機|朝|夜|常時|たまに|時々"
)
SPEC_QUESTION_RE = re.compile(
    r"とは[？?]|の意味|の定義|の仕様|る条件|条件は|の動作|動作は"
)

ABBREV_MAP = {
    "現調": "現地調査",
    "火管": "火災管制",
    "火災管制運転": "火災管制運転",
    "震管": "地震管制",
    "救運": "救出運転",
    "自発": "自動運転",
    "専発": "専用運転",
    "保発": "保守運転",
    "戸開": "戸開き",
    "戸閉": "戸閉じ",
    "乗場": "乗場",
    "制御盤": "制御盤",
}


def normalize_query_text(text: str) -> str:
    """Normalize Unicode variants and collapse whitespace."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text).strip()
    return re.sub(r"\s+", " ", normalized)


def expand_query_abbreviations(text: str) -> str:
    """Expand the small, explicit domain abbreviation map."""
    if not text:
        return ""
    expanded = text
    for short, full in ABBREV_MAP.items():
        if short in expanded and full not in expanded:
            expanded = expanded.replace(short, full)
    return expanded


def last_assistant_was_clarify(chat_history: list) -> bool:
    """Return True when the latest assistant turn is the clarification prompt."""
    for msg in reversed(chat_history or []):
        role = msg.get("role")
        if role == "assistant":
            return CLARIFY_MARKER in (msg.get("content") or "")
        if role == "user":
            break
    return False


def previous_user_query_before_clarify(chat_history: list) -> str:
    """Find the user query immediately preceding the clarification turn."""
    history = chat_history or []
    for i in range(len(history) - 1, -1, -1):
        msg = history[i]
        if msg.get("role") != "assistant":
            continue
        if CLARIFY_MARKER not in (msg.get("content") or ""):
            continue
        for j in range(i - 1, -1, -1):
            if history[j].get("role") == "user":
                return (history[j].get("content") or "").strip()
        return ""
    return ""


def compose_search_query(query: str, chat_history: list = None) -> str:
    """Combine a clarification follow-up with the original user symptom query."""
    current = (query or "").strip()
    if not last_assistant_was_clarify(chat_history):
        return current
    previous = previous_user_query_before_clarify(chat_history)
    if not previous:
        return current
    if not current:
        return previous
    if previous in current:
        return current
    return f"{previous}\n{current}"


def query_filters_have_category(filters: dict = None) -> bool:
    filters = filters or {}
    raw = filters.get("category")
    if isinstance(raw, str):
        return bool(raw.strip())
    if isinstance(raw, list):
        return any(bool(value) for value in raw)
    return False


def normalize_mode_and_filters(mode: str, filters: dict = None) -> tuple:
    """Preserve the current deprecated spec-mode compatibility behavior."""
    normalized_filters = dict(filters or {})
    normalized_mode = mode or "normal"
    if normalized_mode == "spec":
        normalized_mode = "normal"
        if not query_filters_have_category(normalized_filters):
            normalized_filters["category"] = ["spec", "tech_info", "std"]
    elif normalized_mode != "normal":
        normalized_mode = "normal"
    return normalized_mode, normalized_filters


def needs_clarify(query: str, filters: dict = None, chat_history: list = None) -> tuple:
    """Apply the existing rule-based clarification gate."""
    filters = filters or {}
    if last_assistant_was_clarify(chat_history):
        return False, []

    text = query or ""
    if not SYMPTOM_RE.search(text):
        return False, []
    if SPEC_QUESTION_RE.search(text):
        return False, []

    has_model = bool(filters.get("modelType"))
    has_part = bool(PART_RE.search(text))
    has_situation = bool(SITUATION_RE.search(text))

    questions = []
    if not has_model:
        questions.append("機種（または工事番号）※分かれば精度が上がります")
    if not has_part:
        questions.append("何が／どの部位ですか？（かご／ドア／巻上機／制御盤など）")
    if not has_situation:
        questions.append("いつ発生しますか？（走行中／停止中／開閉時など）")

    if has_model and (has_part or has_situation):
        return False, []
    if not questions:
        return False, []
    return True, questions


def build_clarify_content(questions: list) -> str:
    lines = [CLARIFY_MARKER, ""]
    for index, question in enumerate(questions, start=1):
        lines.append(f"{index}. {question}")
    lines.append("")
    lines.append("追記いただければ、資料の該当ページを探します。")
    return "\n".join(lines)


def build_not_found_content(filters: dict = None) -> str:
    text = (
        "条件に合う頁が十分に見つかりませんでした。\n"
        "機種・症状・対象部位を具体化して再検索してください。\n"
        "（見当違いの回答で埋めないため、ここでは断定しません）"
    )
    if query_filters_have_category(filters):
        text += "\n資料カテゴリの絞り込みを外すと見つかることがあります。"
    return text
