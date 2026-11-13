import assert from 'node:assert/strict';
import test from 'node:test';
import { CHECK_CONCURRENCY, createCheckRunner, summarizeCheckRun } from '../src/lib/knowhow-check-runner.mjs';

/** 外から解決・拒否できる偽の非同期処理。 */
function deferredExecutor() {
  const calls = new Map();
  let active = 0;
  let peak = 0;
  const execute = (task, signal) => new Promise((resolve, reject) => {
    active += 1;
    peak = Math.max(peak, active);
    const settle = (finish) => (value) => { active -= 1; finish(value); };
    calls.set(task.id, { resolve: settle(resolve), reject: settle(reject), signal, count: (calls.get(task.id)?.count ?? 0) + 1 });
  });
  return { execute, calls, peak: () => peak, active: () => active };
}
const tick = () => new Promise((resolve) => setImmediate(resolve));
const tasksOf = (...ids) => ids.map((id) => ({ id }));
const statuses = (runner) => Object.fromEntries(runner.snapshot().tasks.map((task) => [task.id, task.status]));

test('同時実行数の既定は2', () => {
  assert.equal(CHECK_CONCURRENCY, 2);
});

test('同時実行数は1以上の整数だけを受け付ける', () => {
  for (const concurrency of [0, -1, 1.5, Number.NaN, Number.POSITIVE_INFINITY, 3]) {
    assert.throws(
      () => createCheckRunner({ tasks: tasksOf('a'), execute: async () => 'A', concurrency }),
      /同時実行数/u,
    );
  }
  assert.doesNotThrow(() => createCheckRunner({ tasks: tasksOf('a'), execute: async () => 'A', concurrency: 1 }));
});

test('同時に走るのは2件までで、終わった分だけ次が始まる', async () => {
  const fake = deferredExecutor();
  const runner = createCheckRunner({ tasks: tasksOf('a', 'b', 'c', 'd', 'e'), execute: fake.execute });
  runner.start();
  await tick();
  assert.deepEqual(statuses(runner), { a: 'running', b: 'running', c: 'pending', d: 'pending', e: 'pending' });
  fake.calls.get('a').resolve('A');
  await tick();
  assert.deepEqual(statuses(runner), { a: 'done', b: 'running', c: 'running', d: 'pending', e: 'pending' });
  for (const id of ['b', 'c']) fake.calls.get(id).resolve(id);
  await tick();
  for (const id of ['d', 'e']) fake.calls.get(id).resolve(id);
  await tick();
  assert.equal(fake.peak(), 2);
  assert.equal(runner.snapshot().running, false);
  assert.equal(runner.snapshot().tasks[0].result, 'A');
  assert.deepEqual(summarizeCheckRun(runner.snapshot()), { total: 5, done: 5, failed: 0, cancelled: 0, finished: 5 });
});

test('1件が失敗しても残りは進み、失敗の内容は呼び出し側の説明だけを持つ', async () => {
  const fake = deferredExecutor();
  const runner = createCheckRunner({
    tasks: tasksOf('a', 'b', 'c'),
    execute: fake.execute,
    describeFailure: (error, task) => `${task.id} は失敗（${error.code}）`,
  });
  runner.start();
  await tick();
  fake.calls.get('a').reject(Object.assign(new Error('秘密の本文'), { code: 'server' }));
  await tick();
  fake.calls.get('b').resolve('B');
  await tick();
  fake.calls.get('c').resolve('C');
  await tick();
  const snapshot = runner.snapshot();
  assert.deepEqual(statuses(runner), { a: 'failed', b: 'done', c: 'done' });
  assert.equal(snapshot.tasks[0].failure, 'a は失敗（server）');
  assert.doesNotMatch(JSON.stringify(snapshot), /秘密の本文/u);
  assert.equal(snapshot.running, false);
});

test('中止すると実行中・未実行は中止になり、あとから届いた結果は反映されない', async () => {
  const fake = deferredExecutor();
  const updates = [];
  const runner = createCheckRunner({ tasks: tasksOf('a', 'b', 'c'), execute: fake.execute, onUpdate: (snapshot) => updates.push(snapshot) });
  runner.start();
  await tick();
  fake.calls.get('a').resolve('A');
  await tick();
  runner.cancel();
  assert.deepEqual(statuses(runner), { a: 'done', b: 'cancelled', c: 'cancelled' });
  assert.equal(fake.calls.get('b').signal.aborted, true);
  assert.equal(runner.snapshot().running, false);
  const countAfterCancel = updates.length;
  fake.calls.get('b').resolve('遅れて届いた応答');
  fake.calls.get('c').reject(new Error('遅れて届いた失敗'));
  await tick();
  assert.deepEqual(statuses(runner), { a: 'done', b: 'cancelled', c: 'cancelled' });
  assert.equal(updates.length, countAfterCancel, '中止後は通知しない');
  assert.equal(runner.snapshot().tasks[1].result, undefined);
});

test('失敗した1件を再試行すると成功に変わる', async () => {
  const fake = deferredExecutor();
  const runner = createCheckRunner({ tasks: tasksOf('a', 'b'), execute: fake.execute });
  runner.start();
  await tick();
  fake.calls.get('a').reject(new Error('x'));
  fake.calls.get('b').resolve('B');
  await tick();
  assert.deepEqual(statuses(runner), { a: 'failed', b: 'done' });
  runner.retry('a');
  await tick();
  assert.deepEqual(statuses(runner), { a: 'running', b: 'done' });
  assert.equal(runner.snapshot().running, true);
  fake.calls.get('a').resolve('A2');
  await tick();
  assert.deepEqual(statuses(runner), { a: 'done', b: 'done' });
  assert.equal(runner.snapshot().tasks[0].result, 'A2');
  assert.equal(runner.snapshot().tasks[0].failure, undefined);
  assert.equal(fake.calls.get('a').count, 2);
  assert.equal(fake.calls.get('b').count, 1, '成功した分は再実行しない');
});

test('再試行できるのは失敗・中止だけで、実行中の再試行でも同時実行は2を超えない', async () => {
  const fake = deferredExecutor();
  const runner = createCheckRunner({ tasks: tasksOf('a', 'b', 'c', 'd'), execute: fake.execute });
  runner.start();
  await tick();
  fake.calls.get('a').reject(new Error('x'));
  await tick();
  runner.retry('a');
  runner.retry('b');
  runner.retry('存在しない');
  await tick();
  assert.equal(fake.active(), 2);
  for (const id of ['b', 'c']) fake.calls.get(id).resolve(id);
  await tick();
  for (const id of ['d', 'a']) fake.calls.get(id).resolve(id);
  await tick();
  assert.equal(fake.peak(), 2);
  assert.deepEqual(statuses(runner), { a: 'done', b: 'done', c: 'done', d: 'done' });
});

test('中止したあとの再試行は新しい実行として反映される', async () => {
  const fake = deferredExecutor();
  const runner = createCheckRunner({ tasks: tasksOf('a'), execute: fake.execute });
  runner.start();
  await tick();
  const first = fake.calls.get('a');
  runner.cancel();
  runner.retry('a');
  await tick();
  first.resolve('古い応答');
  await tick();
  assert.deepEqual(statuses(runner), { a: 'running' });
  fake.calls.get('a').resolve('新しい応答');
  await tick();
  assert.equal(runner.snapshot().tasks[0].result, '新しい応答');
});

test('続けても無駄な失敗（認証切れ）では、残りを始めずに中止扱いにする', async () => {
  const fake = deferredExecutor();
  const runner = createCheckRunner({
    tasks: tasksOf('a', 'b', 'c', 'd'),
    execute: fake.execute,
    isFatal: (error) => error.code === 'auth',
  });
  runner.start();
  await tick();
  fake.calls.get('a').reject(Object.assign(new Error('x'), { code: 'auth' }));
  await tick();
  assert.deepEqual(statuses(runner), { a: 'failed', b: 'cancelled', c: 'cancelled', d: 'cancelled' });
  assert.equal(fake.calls.has('c'), false);
  assert.equal(runner.snapshot().running, false);
});

test('破棄したあとは通知も反映もしない（画面を離れたあとに state を更新しない）', async () => {
  const fake = deferredExecutor();
  const updates = [];
  const runner = createCheckRunner({ tasks: tasksOf('a', 'b'), execute: fake.execute, onUpdate: (snapshot) => updates.push(snapshot) });
  runner.start();
  await tick();
  const count = updates.length;
  runner.dispose();
  fake.calls.get('a').resolve('A');
  await tick();
  runner.retry('a');
  runner.start();
  await tick();
  assert.equal(updates.length, count);
  assert.equal(fake.calls.get('a').signal.aborted, true);
});

test('通知される状態は毎回新しいオブジェクトで、前の状態を書き換えない', async () => {
  const fake = deferredExecutor();
  const updates = [];
  const runner = createCheckRunner({ tasks: tasksOf('a'), execute: fake.execute, onUpdate: (snapshot) => updates.push(snapshot) });
  runner.start();
  await tick();
  fake.calls.get('a').resolve('A');
  await tick();
  assert.equal(updates[0].tasks[0].status, 'running');
  assert.equal(updates.at(-1).tasks[0].status, 'done');
  assert.notEqual(updates[0], updates.at(-1));
  assert.ok(Object.isFrozen(updates[0]) && Object.isFrozen(updates[0].tasks));
});

test('同期的に例外を投げる処理も失敗として扱い、タスクが無ければ何もしない', async () => {
  const runner = createCheckRunner({ tasks: tasksOf('a'), execute: () => { throw new Error('sync'); } });
  runner.start();
  await tick();
  assert.deepEqual(statuses(runner), { a: 'failed' });
  const empty = createCheckRunner({ tasks: [], execute: async () => 1 });
  empty.start();
  assert.equal(empty.snapshot().running, false);
  assert.throws(() => createCheckRunner({ tasks: tasksOf('a', 'a'), execute: async () => 1 }), /重複/u);
});
