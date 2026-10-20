"""調査ジョブの予算（検索回数・モデル呼び出し回数・経過時間）。ワーカー内の複数スレッドから使う。"""
import threading
import time


class Budget:
    def __init__(self, limits, clock=time.monotonic):
        self._limits = limits
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
