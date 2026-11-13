"""「まとめ」「結果を残す」の該当ターン検索の窓が、先輩履歴の表示範囲以上であることを固定する。"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _const(path: str, name: str) -> int:
    text = (REPO / path).read_text(encoding="utf-8")
    return int(re.search(rf"^{name}\s*=\s*(\d+)", text, re.M).group(1))


def test_turn_search_window_covers_senpai_history_view():
    page_size = _const("lambda/chat/chat-management/app.py", "SENPAI_HISTORY_PAGE_SIZE")
    max_pages = _const("lambda/chat/chat-management/app.py", "SENPAI_HISTORY_MAX_PAGES")
    for path in (
        "lambda/rag/senpai-synthesis/synthesis_store.py",
        "lambda/rag/senpai-field-report/field_report_store.py",
    ):
        assert _const(path, "HISTORY_PAGE_SIZE") >= page_size
        assert _const(path, "HISTORY_MAX_PAGES") >= max_pages
