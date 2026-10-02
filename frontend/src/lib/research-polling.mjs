/**
 * じっくりモードの進捗確認（設計 docs/design-2026-09-24-rag-two-modes.md §4.11「進捗の確認間隔」）。
 * 画面・API には触れない。fetchJob・時計・タイマーは呼び出し側から渡す。
 */

/** 送信からの経過時間ごとの確認間隔。3 分で 36 回。 */
export const POLL_SCHEDULE = [
  { untilMs: 30000, delayMs: 2000 },
  { untilMs: 90000, delayMs: 5000 },
  { untilMs: Infinity, delayMs: 10000 },
];
export const POLL_MIN_MS = 1000;
export const POLL_MAX_MS = 30000;
/** 起動待ち 120 秒＋実行 180 秒＋余裕。同時実行ロックの有効期限（360 秒）と同じ。 */
export const POLL_GIVE_UP_MS = 360000;

const TERMINAL_STATUSES = new Set(['completed', 'failed']);

/**
 * 次の確認までの待ち時間（ミリ秒）。サーバーの pollAfterMs があれば 1〜30 秒に丸めて優先し、
 * 直前まで失敗（429・通信エラー）が続いていれば連続回数ぶん倍にする（上限 30 秒）。
 *
 * @param {{ elapsedMs: number, pollAfterMs?: number | null, consecutiveFailures?: number }} params
 * @returns {number}
 */
export function nextPollDelayMs({ elapsedMs, pollAfterMs, consecutiveFailures = 0 }) {
  const base = Number.isFinite(pollAfterMs)
    ? Math.min(Math.max(pollAfterMs, POLL_MIN_MS), POLL_MAX_MS)
    : POLL_SCHEDULE.find((step) => elapsedMs < step.untilMs).delayMs;
  return Math.min(base * 2 ** consecutiveFailures, POLL_MAX_MS);
}

/** 確認を打ち切る時間を過ぎたか。 */
export function isPollingExpired(elapsedMs) {
  return elapsedMs >= POLL_GIVE_UP_MS;
}

/**
 * ジョブごとに確認のタイマーを 1 本だけ持つ。タブが非表示の間は止め、表示に戻ったら即 1 回確認する。
 *
 * @param {{
 *   fetchJob: (jobId: string) => Promise<{ status: string, pollAfterMs?: number }>,
 *   onUpdate?: (jobId: string, result: object) => void,
 *   onGiveUp?: (jobId: string) => void,
 *   onRateLimited?: (jobId: string) => void,
 *   now?: () => number,
 *   setTimer?: (fn: () => void, delayMs: number) => unknown,
 *   clearTimer?: (timer: unknown) => void,
 * }} deps 通信エラーは `status` を持つ Error として投げる（429 なら onRateLimited を呼ぶ）
 */
export function createJobPoller({
  fetchJob,
  onUpdate,
  onGiveUp,
  onRateLimited,
  now = Date.now,
  setTimer = setTimeout,
  clearTimer = clearTimeout,
}) {
  const jobs = new Map();

  function giveUp(jobId, job) {
    if (jobs.get(jobId) !== job) return;
    stop(jobId);
    onGiveUp?.(jobId);
  }

  function schedule(jobId, job) {
    const delayMs = nextPollDelayMs({
      elapsedMs: now() - job.startedAt,
      pollAfterMs: job.pollAfterMs,
      consecutiveFailures: job.failures,
    });
    job.timer = setTimer(() => tick(jobId), delayMs);
  }

  async function tick(jobId) {
    const job = jobs.get(jobId);
    if (!job || job.inFlight) return;
    job.timer = null;
    if (isPollingExpired(now() - job.startedAt)) {
      giveUp(jobId, job);
      return;
    }

    job.inFlight = true;
    let result;
    let rateLimited = false;
    try {
      result = await fetchJob(jobId);
      job.failures = 0;
      job.pollAfterMs = result?.pollAfterMs;
    } catch (error) {
      job.failures += 1;
      job.pollAfterMs = undefined;
      rateLimited = error?.status === 429;
    } finally {
      job.inFlight = false;
    }

    // 待っている間に stop されていたら何もしない（同じ jobId の再 start とも区別する）
    if (jobs.get(jobId) !== job) return;
    if (isPollingExpired(now() - job.startedAt)) {
      giveUp(jobId, job);
      return;
    }
    if (rateLimited) onRateLimited?.(jobId);
    if (result) {
      onUpdate?.(jobId, result);
      if (TERMINAL_STATUSES.has(result.status)) {
        stop(jobId);
        return;
      }
    }
    if (!job.paused) schedule(jobId, job);
  }

  /** 同じ jobId が確認中なら何もせず false を返す。 */
  function start(jobId, { visible = true } = {}) {
    if (jobs.has(jobId)) return false;
    const startedAt = now();
    const job = {
      startedAt,
      failures: 0,
      pollAfterMs: undefined,
      timer: null,
      expirationTimer: null,
      inFlight: false,
      paused: !visible,
    };
    jobs.set(jobId, job);
    job.expirationTimer = setTimer(() => giveUp(jobId, job), Math.max(0, POLL_GIVE_UP_MS - (now() - startedAt)));
    if (!job.paused) schedule(jobId, job);
    return true;
  }

  function stop(jobId) {
    const job = jobs.get(jobId);
    if (!job) return;
    if (job.timer !== null) clearTimer(job.timer);
    if (job.expirationTimer !== null) clearTimer(job.expirationTimer);
    jobs.delete(jobId);
  }

  function stopAll() {
    for (const jobId of [...jobs.keys()]) stop(jobId);
  }

  /** タブの表示・非表示（document.visibilityState）に合わせて呼ぶ。 */
  function setVisible(visible) {
    for (const [jobId, job] of jobs) {
      if (!visible) {
        job.paused = true;
        if (job.timer !== null) {
          clearTimer(job.timer);
          job.timer = null;
        }
      } else if (job.paused) {
        job.paused = false;
        if (!job.inFlight) tick(jobId);
      }
    }
  }

  return { start, stop, stopAll, setVisible };
}
