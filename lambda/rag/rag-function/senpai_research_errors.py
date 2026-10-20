"""調査ジョブの失敗の種類。利用者に返す code と日本語メッセージを持つ（内部情報は載せない）。"""

CODES = ('Timeout', 'BudgetExceeded', 'Internal', 'QuestionUnavailable')


class ResearchFailure(Exception):
    """ジョブを failed で終わらせる失敗。debug は管理者向けの診断（本文を含まない）。"""

    def __init__(self, code: str, message: str, debug: dict = None):
        super().__init__(code)
        self.code = code
        self.message = message
        self.debug = debug or {}


class TimeBudgetExceeded(Exception):
    """残り時間が足りず、モデル・検索を呼べない（呼ぶと Lambda の Timeout を超えるため）。"""


class KnowhowUnavailable(Exception):
    """ノウハウの索引を読めない（調査は続行し、ノウハウなしで答える）。"""
