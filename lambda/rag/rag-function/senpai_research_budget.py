"""調査ジョブの予算（検索回数・モデル呼び出し回数・経過時間）。ワーカー内の複数スレッドから使う。"""
import threading
import time


MIN_CALL_MS = 3000      # これより短い待ち時間では呼ばない（ほぼ確実に間に合わない）
FINAL_MARGIN_MS = 2000  # まとめの後に照合・保存のため残す時間
DEFAULT_CALL_CAP_S = 40
SEARCH_MIN_REMAINING_MS = 15000  # 検索を始めるのに必要な残り（検索 + まとめが入る余地）


class Budget:
    """経過時間は 2 段で見る。

    - 柔らかい上限（job_ms）: 追加の検索・判断を始めてよいか。まとめ用の時間（synth_reserve_ms）を残す。
    - 硬い上限（hard_limit_ms）: 検索・モデル呼び出しの待ち時間の天井。既定は job_ms + synth_reserve_ms で、
      Lambda の残り時間から安全マージンを引いた値を渡すと、それを超えない。
    """

    def __init__(self, limits, clock=time.monotonic, hard_limit_ms=None, call_cap_s=DEFAULT_CALL_CAP_S):
        self._limits = limits
        self._hard_limit_ms = (
            limits.job_ms + limits.synth_reserve_ms if hard_limit_ms is None
            else min(hard_limit_ms, limits.job_ms + limits.synth_reserve_ms)
        )
        self._call_cap_s = call_cap_s
        self._clock = clock
        self._started = clock()
        self._lock = threading.Lock()
        self._searches = 0
        self._model_calls = 0

    def try_search(self) -> bool:
        with self._lock:
            if self._searches >= self._limits.max_searches:
                return False
            self._searches += 1
            return True

    def try_model_call(self, reserve: int = 0) -> bool:
        """reserve 回分（まとめ用など）を残せるときだけ消費する。"""
        with self._lock:
            if self._model_calls + reserve >= self._limits.max_model_calls:
                return False
            self._model_calls += 1
            return True

    def searches_left(self) -> int:
        with self._lock:
            return self._limits.max_searches - self._searches

    def elapsed_ms(self) -> int:
        return int((self._clock() - self._started) * 1000)

    def remaining_ms(self) -> int:
        """硬い上限までの残り時間。"""
        return self._hard_limit_ms - self.elapsed_ms()

    def call_timeout_s(self, *, final: bool):
        """1 回の呼び出しに許す読み取り待ち（秒）。足りなければ None（呼ばない）。

        final=False はまとめ用の時間を残す。final=True（まとめ）は照合の余白だけ残す。
        """
        reserve = FINAL_MARGIN_MS if final else self._limits.synth_reserve_ms
        available_ms = self.remaining_ms() - reserve
        if available_ms < MIN_CALL_MS:
            return None
        return min(self._call_cap_s, available_ms / 1000)

    def search_allowed(self) -> bool:
        return self.remaining_ms() >= SEARCH_MIN_REMAINING_MS

    def time_allows_more(self) -> bool:
        """まとめ用の時間を残して、まだ追加の作業をしてよいか。"""
        return self.elapsed_ms() + self._limits.synth_reserve_ms < self._limits.job_ms

    def snapshot(self) -> dict:
        with self._lock:
            return {
                'searchesUsed': self._searches,
                'searchesMax': self._limits.max_searches,
                'modelCallsUsed': self._model_calls,
                'modelCallsMax': self._limits.max_model_calls,
                'elapsedMs': self.elapsed_ms(),
                'elapsedMaxMs': self._limits.job_ms,
            }
