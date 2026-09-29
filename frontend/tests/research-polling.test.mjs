import test from 'node:test';
import assert from 'node:assert/strict';
import {
  POLL_GIVE_UP_MS,
  createJobPoller,
  isPollingExpired,
  nextPollDelayMs,
} from '../src/lib/research-polling.mjs';

const flush = () => new Promise((resolve) => setImmediate(resolve));

/** 時計とタイマーを手動で進める。 */
function createClock() {
  let nowMs = 0;
  let seq = 0;
  const timers = new Map();
  return {
    now: () => nowMs,
    setTimer: (fn, delayMs) => {
      const id = ++seq;
      timers.set(id, { at: nowMs + delayMs, fn });
      return id;
    },
    clearTimer: (id) => timers.delete(id),
    pending: () => timers.size,
    async advance(ms) {
      const end = nowMs + ms;
      for (;;) {
        const next = [...timers.entries()].sort((a, b) => a[1].at - b[1].at)[0];
        if (!next || next[1].at > end) break;
        timers.delete(next[0]);
        nowMs = next[1].at;
        next[1].fn();
        await flush();
      }
      nowMs = end;
    },
  };
}

function setup(fetchJob, extra = {}) {
  const clock = createClock();
  const calls = [];
  const updates = [];
  const events = { giveUp: 0, rateLimited: 0 };
  const poller = createJobPoller({
    fetchJob: (jobId) => {
      calls.push(clock.now());
      return fetchJob(jobId, calls.length);
    },
    onUpdate: (jobId, result) => updates.push(result),
    onGiveUp: () => { events.giveUp += 1; },
    onRateLimited: () => { events.rateLimited += 1; },
    now: clock.now,
    setTimer: clock.setTimer,
    clearTimer: clock.clearTimer,
    ...extra,
  });
  return { clock, calls, updates, events, poller };
}

const running = async () => ({ status: 'running' });

test('確認間隔は経過時間で 2 秒・5 秒・10 秒に切り替わる', () => {
  assert.equal(nextPollDelayMs({ elapsedMs: 0 }), 2000);
  assert.equal(nextPollDelayMs({ elapsedMs: 29999 }), 2000);
  assert.equal(nextPollDelayMs({ elapsedMs: 30000 }), 5000);
  assert.equal(nextPollDelayMs({ elapsedMs: 89999 }), 5000);
  assert.equal(nextPollDelayMs({ elapsedMs: 90000 }), 10000);
});

test('pollAfterMs があれば優先し、1〜30 秒に丸める。数値でなければ無視する', () => {
  assert.equal(nextPollDelayMs({ elapsedMs: 0, pollAfterMs: 3000 }), 3000);
  assert.equal(nextPollDelayMs({ elapsedMs: 0, pollAfterMs: 100 }), 1000);
  assert.equal(nextPollDelayMs({ elapsedMs: 0, pollAfterMs: 60000 }), 30000);
  assert.equal(nextPollDelayMs({ elapsedMs: 0, pollAfterMs: 'abc' }), 2000);
  assert.equal(nextPollDelayMs({ elapsedMs: 0, pollAfterMs: null }), 2000);
});

test('失敗が続くと連続回数ぶん倍にし、上限は 30 秒', () => {
  assert.equal(nextPollDelayMs({ elapsedMs: 0, consecutiveFailures: 1 }), 4000);
  assert.equal(nextPollDelayMs({ elapsedMs: 0, consecutiveFailures: 3 }), 16000);
  assert.equal(nextPollDelayMs({ elapsedMs: 0, consecutiveFailures: 4 }), 30000);
  assert.equal(nextPollDelayMs({ elapsedMs: 0, consecutiveFailures: 2000 }), 30000);
});

test('打ち切りは 6 分（同時実行ロックの有効期限と同じ）', () => {
  assert.equal(POLL_GIVE_UP_MS, 360000);
  assert.equal(isPollingExpired(359999), false);
  assert.equal(isPollingExpired(360000), true);
});

test('3 分の確認は 36 回（従来の 2 秒固定は 90 回）', async () => {
  const { clock, calls, poller } = setup(running);
  poller.start('job-1');
  await clock.advance(180000);
  assert.equal(calls.length, 36);
});

test('完了しなければ 6 分で打ち切り、確認は 53 回で止まる', async () => {
  const { clock, calls, events, poller } = setup(running);
  poller.start('job-1');
  await clock.advance(400000);
  assert.equal(calls.length, 53);
  assert.equal(events.giveUp, 1);
  assert.equal(clock.pending(), 0);
});

test('通信中でも期限で打ち切り、タイマーを残さない', async () => {
  const { clock, events, poller } = setup(() => new Promise(() => {}));
  poller.start('job-1');
  await clock.advance(2000);
  await clock.advance(POLL_GIVE_UP_MS - 2000);
  assert.equal(events.giveUp, 1);
  assert.equal(clock.pending(), 0);
});

test('期限直前に送った確認が期限後に返った場合は更新しない', async () => {
  let release;
  const { clock, calls, updates, events, poller } = setup((jobId, n) => {
    if (n < 53) return running();
    return new Promise((resolve) => {
      release = () => resolve({ status: 'running' });
    });
  });
  poller.start('job-1');
  await clock.advance(POLL_GIVE_UP_MS - 10000);
  assert.equal(calls.length, 53);
  const updatesBeforeDelayedResponse = updates.length;
  await clock.advance(10000);
  release();
  await flush();
  assert.equal(updates.length, updatesBeforeDelayedResponse);
  assert.equal(events.giveUp, 1);
  assert.equal(clock.pending(), 0);
});

test('terminal 応答で停止した後は期限タイマーが発火しない', async () => {
  const { clock, events, poller } = setup(async () => ({ status: 'completed' }));
  poller.start('job-1');
  await clock.advance(2000);
  assert.equal(clock.pending(), 0);
  await clock.advance(POLL_GIVE_UP_MS);
  assert.equal(events.giveUp, 0);
  assert.equal(clock.pending(), 0);
});

test('completed / failed を受け取ったら更新を通知して止まる', async () => {
  for (const finalStatus of ['completed', 'failed']) {
    const { clock, calls, updates, poller } = setup(async (jobId, n) => ({ status: n < 3 ? 'running' : finalStatus }));
    poller.start('job-1');
    await clock.advance(60000);
    assert.equal(calls.length, 3);
    assert.deepEqual(updates.map((u) => u.status), ['running', 'running', finalStatus]);
    assert.equal(clock.pending(), 0);
  }
});

test('同じ jobId を二重に start しても確認は 1 本だけ', async () => {
  const { clock, calls, poller } = setup(running);
  assert.equal(poller.start('job-1'), true);
  assert.equal(poller.start('job-1'), false);
  assert.equal(clock.pending(), 2);
  await clock.advance(2000);
  assert.equal(calls.length, 1);
});

test('非表示の間は確認せず、表示に戻ったらすぐ 1 回確認して再開する', async () => {
  const { clock, calls, poller } = setup(running);
  poller.start('job-1');
  poller.setVisible(false);
  assert.equal(clock.pending(), 1);
  await clock.advance(100000);
  assert.equal(calls.length, 0);

  poller.setVisible(true);
  assert.deepEqual(calls, [100000]);
  await flush();
  assert.equal(clock.pending(), 2);
  await clock.advance(10000);
  assert.deepEqual(calls, [100000, 110000]);
});

test('確認中に非表示になったら、その応答のあとは次の確認を予約しない', async () => {
  let release;
  const { clock, calls, poller } = setup(() => new Promise((resolve) => { release = () => resolve({ status: 'running' }); }));
  poller.start('job-1');
  await clock.advance(2000);
  poller.setVisible(false);
  release();
  await flush();
  assert.equal(calls.length, 1);
  assert.equal(clock.pending(), 1);

  poller.setVisible(true);
  assert.equal(calls.length, 2);
});

test('429 は通知して間隔を倍にし、成功すると元に戻る', async () => {
  const { clock, calls, events, poller } = setup(async (jobId, n) => {
    if (n === 1) throw Object.assign(new Error('Too Many Requests'), { status: 429 });
    return { status: 'running' };
  });
  poller.start('job-1');
  await clock.advance(20000);
  assert.equal(events.rateLimited, 1);
  // 2 秒後に失敗 → 4 秒後（6 秒）に成功 → 2 秒間隔に戻る
  assert.deepEqual(calls.slice(0, 4), [2000, 6000, 8000, 10000]);
});

test('通信エラーも間隔を倍にする（429 の通知はしない）', async () => {
  const { clock, calls, events, poller } = setup(async (jobId, n) => {
    if (n <= 2) throw new Error('network');
    return { status: 'running' };
  });
  poller.start('job-1');
  await clock.advance(30000);
  assert.equal(events.rateLimited, 0);
  assert.deepEqual(calls.slice(0, 4), [2000, 6000, 14000, 16000]);
});

test('サーバーの pollAfterMs を次の確認に使う', async () => {
  const { clock, calls, poller } = setup(async (jobId, n) => (n === 1 ? { status: 'queued', pollAfterMs: 5000 } : { status: 'running' }));
  poller.start('job-1');
  await clock.advance(20000);
  assert.deepEqual(calls.slice(0, 3), [2000, 7000, 9000]);
});

test('確認中に stop したら、応答が返っても通知せず次も予約しない', async () => {
  let release;
  const { clock, calls, updates, poller } = setup(() => new Promise((resolve) => { release = () => resolve({ status: 'running' }); }));
  poller.start('job-1');
  await clock.advance(2000);
  poller.stop('job-1');
  release();
  await flush();
  assert.equal(calls.length, 1);
  assert.equal(updates.length, 0);
  assert.equal(clock.pending(), 0);
});
