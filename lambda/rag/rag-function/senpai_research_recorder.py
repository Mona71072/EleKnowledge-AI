"""段階イベント（steps[]）の記録。実行の前後にコードが追記する。モデルの文章からは作らない。

追記専用で seq は 1 から連続する。保存に失敗したイベントは番号を消費しない
（番号が飛ぶと以降の追記がすべて拒否されるため）。
"""
import threading
from datetime import datetime, timezone

DETAIL_MAX_CHARS = 120

STEP_LABELS = {
    'understand': '質問を整理中',
    'knowhow': 'ノウハウを確認中',
    'tech_search': '技術資料を検索中',
    'law_search': '法令を確認中',
    'sufficiency': '足りない点を確認中',
    'retry_search': '言い換えて再検索中',
    'doc_page': '資料のページを確認中',
    'clarify': '確認が必要な点を整理中',
    'synthesize': '回答をまとめています',
    'verify': '根拠を照合中',
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _bounded(detail):
    return detail[:DETAIL_MAX_CHARS] if isinstance(detail, str) and detail else None


class StepRecorder:
    def __init__(self, append, now_iso=utc_now_iso):
        """append(event) -> bool。False または例外のイベントは記録されなかったものとして扱う。"""
        self._append = append
        self._now_iso = now_iso
        self._lock = threading.Lock()
        self._next_seq = 1

    def _emit(self, event: dict):
        """連番を付けて追記する。記録できたときだけ seq を返す。"""
        with self._lock:
            numbered = {**event, 'seq': self._next_seq}
            try:
                stored = self._append(numbered)
            except Exception:  # noqa: BLE001 - 進捗の保存失敗で調査を止めない
                stored = False
            if not stored:
                return None
            self._next_seq += 1
            return numbered['seq']

    def _event(self, step: str, status: str, started_at: str, ended_at, detail, counts) -> dict:
        event = {'step': step, 'labelJa': STEP_LABELS[step], 'status': status,
                 'startedAt': started_at, 'endedAt': ended_at}
        if _bounded(detail):
            event['detailJa'] = _bounded(detail)
        if counts is not None:
            event['counts'] = counts
        return event

    def begin(self, step: str, detail=None) -> dict:
        started_at = self._now_iso()
        seq = self._emit(self._event(step, 'running', started_at, None, detail, None))
        return {'step': step, 'startedAt': started_at, 'detail': detail, 'seq': seq}

    def end(self, handle: dict, status: str = 'done', detail=None, counts=None) -> None:
        self._emit(self._event(
            handle['step'], status, handle['startedAt'], self._now_iso(),
            detail if detail is not None else handle.get('detail'), counts,
        ))

    def skip(self, step: str, detail=None) -> None:
        now = self._now_iso()
        self._emit(self._event(step, 'skipped', now, now, detail, None))
