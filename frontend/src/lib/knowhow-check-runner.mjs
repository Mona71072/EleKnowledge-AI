// 一括照合の実行制御（キュー・同時実行数・中止・再試行）。画面にも通信にも依存しない。
import { createLatestGuard } from './latest-request.mjs';

/** 同時に実行する照合の最大数。 */
export const CHECK_CONCURRENCY = 2;

const RETRYABLE = new Set(['failed', 'cancelled']);

function freezeSnapshot(tasks, running) {
  return Object.freeze({ tasks: Object.freeze(tasks.map((task) => Object.freeze({ ...task }))), running });
}

/**
 * 照合タスクを、同時実行数を守って順に実行する。
 * - 1件の失敗では止めない（`isFatal` が true を返す失敗だけ、残りを始めずに中止扱いにする）
 * - `cancel()` のあとに届いた結果は捨てる（`createLatestGuard`）
 * - `dispose()` のあとは通知も反映もしない（画面を離れたあと用）
 * @param {{
 *   tasks: ReadonlyArray<{ id: string }>,
 *   execute: (task: { id: string }, signal: AbortSignal) => Promise<unknown>,
 *   concurrency?: number,
 *   onUpdate?: (snapshot: { tasks: ReadonlyArray<object>, running: boolean }) => void,
 *   describeFailure?: (error: unknown, task: { id: string }) => string,
 *   isFatal?: (error: unknown) => boolean,
 * }} options
 */
export function createCheckRunner({ tasks, execute, concurrency = CHECK_CONCURRENCY, onUpdate, describeFailure, isFatal }) {
  if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > CHECK_CONCURRENCY) {
    throw new TypeError(`同時実行数は1〜${CHECK_CONCURRENCY}の整数で指定してください。`);
  }
  if (new Set(tasks.map((task) => task.id)).size !== tasks.length) throw new TypeError('照合タスクの ID が重複しています。');
  const guard = createLatestGuard();
  let entries = tasks.map((task) => ({ ...task, status: 'pending' }));
  let token = null;
  let controller = null;
  let disposed = false;

  const activeCount = () => entries.filter((entry) => entry.status === 'running').length;
  const isRunning = () => token !== null && entries.some((entry) => entry.status === 'pending' || entry.status === 'running');
  const snapshot = () => freezeSnapshot(entries, isRunning());
  const notify = () => { if (!disposed) onUpdate?.(snapshot()); };
  const patch = (id, change) => {
    entries = entries.map((entry) => (entry.id === id ? change(entry) : entry));
  };

  const settle = (runToken, id, change) => {
    if (disposed || !guard.isLatest(runToken)) return;
    patch(id, change);
    pump();
    notify();
  };

  const fail = (runToken, id, error) => {
    if (disposed || !guard.isLatest(runToken)) return;
    const task = entries.find((entry) => entry.id === id);
    const failure = describeFailure ? describeFailure(error, task) : '照合に失敗しました。';
    const failed = ({ result: _result, ...entry }) => ({ ...entry, status: 'failed', failure });
    if (!isFatal?.(error)) {
      settle(runToken, id, failed);
      return;
    }
    // 続けても全部失敗する種類（認証切れなど）: 残りは始めず、実行中も止めて中止扱いにする。
    patch(id, failed);
    stopActive();
    notify();
  };

  function stopActive() {
    guard.invalidate();
    controller?.abort();
    token = null;
    entries = entries.map((entry) => (
      entry.status === 'pending' || entry.status === 'running' ? { ...entry, status: 'cancelled' } : entry
    ));
  }

  const launch = (entry) => {
    const runToken = token;
    const { signal } = controller;
    patch(entry.id, ({ failure: _failure, result: _result, ...rest }) => ({ ...rest, status: 'running' }));
    Promise.resolve()
      .then(() => execute(entry, signal))
      .then(
        (result) => settle(runToken, entry.id, (current) => ({ ...current, status: 'done', result })),
        (error) => fail(runToken, entry.id, error),
      );
  };

  function pump() {
    if (token === null) return;
    while (activeCount() < concurrency) {
      const next = entries.find((entry) => entry.status === 'pending');
      if (!next) break;
      launch(next);
    }
    if (!isRunning()) token = null;
  }

  const activate = () => {
    if (token !== null) return;
    token = guard.begin();
    controller = new AbortController();
  };

  return {
    /** 未実行のタスクを始める。 */
    start() {
      if (disposed || !entries.some((entry) => entry.status === 'pending')) return;
      activate();
      pump();
      notify();
    },
    /** 実行中・未実行を中止する。あとから届く結果は反映しない。 */
    cancel() {
      if (disposed || token === null) return;
      stopActive();
      notify();
    },
    /** 失敗・中止した1件をもう一度実行する。 */
    retry(id) {
      const target = entries.find((entry) => entry.id === id);
      if (disposed || !target || !RETRYABLE.has(target.status)) return;
      patch(id, ({ failure: _failure, ...entry }) => ({ ...entry, status: 'pending' }));
      activate();
      pump();
      notify();
    },
    /** 画面を離れるときに呼ぶ。以後は通知も反映もしない。 */
    dispose() {
      disposed = true;
      guard.invalidate();
      controller?.abort();
      token = null;
    },
    snapshot,
  };
}

/**
 * 進捗の件数をまとめる。
 * @param {{ tasks: ReadonlyArray<{ status: string }> }} snapshot
 */
export function summarizeCheckRun(snapshot) {
  const count = (status) => snapshot.tasks.filter((task) => task.status === status).length;
  const done = count('done');
  const failed = count('failed');
  const cancelled = count('cancelled');
  return { total: snapshot.tasks.length, done, failed, cancelled, finished: done + failed + cancelled };
}
