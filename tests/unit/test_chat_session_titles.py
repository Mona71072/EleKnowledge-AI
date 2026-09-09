"""chat-management: セッション一覧のタイトル生成の単体テスト。

一覧タイトルが直近メッセージ（多くは AI 回答）由来だったため、機種未指定時の注意書き
「※機種未指定のため、一般資料…」で履歴一覧が埋まり判別できなくなっていた回帰を防ぐ。
"""
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parents[2]
APP_PATH = REPO / "lambda" / "chat" / "chat-management" / "app.py"

NOTICE = (
    "※機種未指定のため、一般資料・取扱機種スコープ内の候補を含みます。"
    "特定機種の事実としては断定しないでください。"
)


def load_app():
    os.environ.setdefault("CHATLOGS_TABLE", "chatlogs-test")
    os.environ.setdefault("AWS_REGION", "ap-northeast-1")
    os.environ.setdefault("ADMIN_GROUP_NAME", "admin")
    with patch("boto3.resource") as resource:
        table = MagicMock()
        resource.return_value.Table.return_value = table
        spec = importlib.util.spec_from_file_location("chat_mgmt_title_test", str(APP_PATH))
        mod = importlib.util.module_from_spec(spec)
        sys.modules.pop("chat_mgmt_title_test", None)
        spec.loader.exec_module(mod)
        mod.chatlogs_table = table
        return mod, table


def _msg(session_id, role, content, timestamp, ttl=0):
    return {
        "sessionId": session_id,
        "role": role,
        "content": content,
        "timestamp": timestamp,
        "ttl": ttl,
    }


def test_title_uses_first_user_question_not_latest_answer():
    """一覧タイトルは最初のユーザー質問。AI 回答の注意書きで埋めない。"""
    mod, table = load_app()
    # GSI は新しい順（ScanIndexForward=False）で返る
    table.query.return_value = {
        "Items": [
            _msg("s1", "assistant", NOTICE + "\n\n溶接脚長の基準は…", "2026-09-09T08:30:00Z", ttl=200),
            _msg("s1", "user", "溶接の脚長が基準外となる判断基準は？", "2026-09-09T08:29:00Z", ttl=100),
        ]
    }

    sessions = mod.get_sessions_by_user("user-1")

    assert len(sessions) == 1
    assert sessions[0]["title"] == "溶接の脚長が基準外となる判断基準は？"
    assert sessions[0]["messageCount"] == 2
    # createdAt は最古、lastMessageTime は最新、TTL は最後に消えるメッセージ基準
    assert sessions[0]["createdAt"] == "2026-09-09T08:29:00Z"
    assert sessions[0]["lastMessageTime"] == "2026-09-09T08:30:00Z"
    assert sessions[0]["ttl"] == 200


def test_title_falls_back_to_assistant_message_without_notice():
    """ユーザー発言が取得範囲に無ければ AI 回答を使うが、注意書きは落とす。"""
    mod, table = load_app()
    table.query.return_value = {
        "Items": [
            _msg("s2", "assistant", NOTICE + "\n\n# 溶接作業の据付基準（整理）", "2026-09-09T09:00:00Z"),
        ]
    }

    sessions = mod.get_sessions_by_user("user-1")

    assert sessions[0]["title"] == "溶接作業の据付基準（整理）"


def test_title_prefers_oldest_user_message_in_multi_turn_session():
    mod, table = load_app()
    table.query.return_value = {
        "Items": [
            _msg("s3", "user", "2回目の質問", "2026-09-09T10:05:00Z"),
            _msg("s3", "assistant", NOTICE + "\n\n回答2", "2026-09-09T10:04:00Z"),
            _msg("s3", "user", "最初の質問", "2026-09-09T10:00:00Z"),
        ]
    }

    sessions = mod.get_sessions_by_user("user-1")

    assert sessions[0]["title"] == "最初の質問"
    assert sessions[0]["messageCount"] == 3


def test_build_session_title_edge_cases():
    mod, _ = load_app()

    assert mod.build_session_title(None) == "Untitled"
    assert mod.build_session_title("   ") == "Untitled"
    # 注意書きだけで本文が無い場合も一覧を注意書きで埋めない
    assert mod.build_session_title(NOTICE) == "Untitled"
    assert mod.build_session_title("**強調**した質問") == "強調した質問"
    assert len(mod.build_session_title("あ" * 120)) == mod.SESSION_TITLE_MAX_LENGTH


def test_wish_sessions_are_still_excluded():
    mod, table = load_app()
    table.query.return_value = {
        "Items": [
            _msg("wish-1", "user", "こうなってほしい", "2026-09-09T11:00:00Z"),
            _msg("s4", "user", "通常の質問", "2026-09-09T10:00:00Z"),
        ]
    }

    sessions = mod.get_sessions_by_user("user-1")

    assert [s["sessionId"] for s in sessions] == ["s4"]
