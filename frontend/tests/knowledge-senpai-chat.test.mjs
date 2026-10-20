import assert from 'node:assert/strict';
import test from 'node:test';
import { createSenpaiChat } from '../src/lib/knowledge-senpai-chat.mjs';

function answer(mode, sessionId, query = '質問') {
  return {
    mode,
    sessionId,
    messageId: `${mode}-message`,
    query,
    content: `${mode} answer`,
    responseType: 'pages',
    receivedAt: '2026-10-20T00:00:00.000Z',
    sourceDocuments: [],
    pageCandidates: [],
    clarifyQuestions: [],
  };
}

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}

test('keeps a separate technical and law session through multiple chat turns', async () => {
  const calls = [];
  const chat = createSenpaiChat({
    querySource: async (request) => {
      calls.push(request);
      return answer(request.mode, request.mode === 'normal' ? 'technical-session' : 'law-session', request.query);
    },
  });

  await chat.send('最初の質問');
  const firstSnapshot = chat.getSnapshot();
  await chat.send('関連する追加質問');

  assert.deepEqual(calls.map(({ mode, query, sessionId }) => ({ mode, query, sessionId })), [
    { mode: 'normal', query: '最初の質問', sessionId: undefined },
    { mode: 'law', query: '最初の質問', sessionId: undefined },
    { mode: 'normal', query: '関連する追加質問', sessionId: 'technical-session' },
    { mode: 'law', query: '関連する追加質問', sessionId: 'law-session' },
  ]);
  const snapshot = chat.getSnapshot();
  assert.equal(snapshot.turns.length, 2);
  assert.equal(snapshot.turns[1].normal.answer.query, '関連する追加質問');
  assert.equal(snapshot.turns[1].law.answer.query, '関連する追加質問');
  assert.equal(firstSnapshot.turns.length, 1);
  assert.equal(Object.isFrozen(snapshot.turns), true);
  assert.equal(Object.isFrozen(snapshot.turns[0]), true);
  chat.dispose();
});

test('requires a query function and does not expose unexpected server error details', async () => {
  assert.throws(() => createSenpaiChat({}), (error) => error.code === 'validation');
  const chat = createSenpaiChat({
    querySource: async (request) => {
      if (request.mode === 'normal') throw new Error('secret server traceback');
      return answer('law', 'law-session', request.query);
    },
  });
  await chat.send('質問');
  const message = chat.getSnapshot().turns[0].normal.message;
  assert.match(message, /検索に失敗しました/);
  assert.doesNotMatch(message, /secret server traceback/);
  chat.dispose();
});

test('does not send blank or overlong questions and blocks a second in-flight submission', async () => {
  const pending = deferred();
  const calls = [];
  const chat = createSenpaiChat({ querySource: (request) => { calls.push(request); return pending.promise; } });

  await assert.rejects(chat.send('  \n '), (error) => error.code === 'validation');
  await assert.rejects(chat.send('x'.repeat(2001)), (error) => error.code === 'validation');
  const first = chat.send('最初の質問');
  await assert.rejects(chat.send('重複質問'), (error) => error.code === 'validation');
  assert.equal(chat.getSnapshot().turns.length, 1);
  assert.deepEqual(calls.map((call) => call.query), ['最初の質問', '最初の質問']);
  pending.resolve(answer(calls[0].mode, `${calls[0].mode}-session`));
  await first;
  chat.dispose();
});

test('retains a successful lane, shows the failed lane, and pauses its ambiguous follow-ups', async () => {
  const calls = [];
  const chat = createSenpaiChat({
    querySource: async (request) => {
      calls.push(request);
      if (request.mode === 'normal' && !request.sessionId) throw new Error('temporary failure');
      return answer(request.mode, request.sessionId || 'law-session', request.query);
    },
  });

  await chat.send('最初の質問');
  await chat.send('追加質問');

  const { turns } = chat.getSnapshot();
  assert.equal(turns[0].normal.status, 'error');
  assert.equal(turns[0].law.status, 'success');
  assert.equal(turns[1].normal.status, 'paused');
  assert.ok(turns[1].normal.message);
  assert.equal(turns[1].law.status, 'success');
  assert.equal(calls.filter((call) => call.mode === 'normal').length, 1);
  assert.equal(calls.filter((call) => call.mode === 'law').length, 2);
  chat.dispose();
});

test('cancel preserves a completed lane and pauses the cancelled lane on later turns', async () => {
  const lawPending = deferred();
  const calls = [];
  const chat = createSenpaiChat({
    querySource: (request) => {
      calls.push(request);
      if (request.mode === 'normal') return Promise.resolve(answer('normal', 'technical-session', request.query));
      if (!request.sessionId) return new Promise((resolve, reject) => {
        request.signal.addEventListener('abort', () => reject(Object.assign(new Error('cancelled'), { code: 'cancelled' })), { once: true });
        lawPending.promise.then(resolve, reject);
      });
      return Promise.resolve(answer('law', request.sessionId, request.query));
    },
  });

  const sending = chat.send('最初の質問');
  await new Promise((resolve) => setImmediate(resolve));
  chat.cancel();
  await sending;
  assert.equal(chat.getSnapshot().turns[0].normal.status, 'success');
  assert.equal(chat.getSnapshot().turns[0].law.status, 'cancelled');

  await chat.send('追加質問');
  assert.equal(chat.getSnapshot().turns[1].normal.status, 'success');
  assert.equal(chat.getSnapshot().turns[1].law.status, 'paused');
  assert.equal(calls.filter((call) => call.mode === 'normal').length, 2);
  assert.equal(calls.filter((call) => call.mode === 'law').length, 1);
  lawPending.resolve(answer('law', 'law-session'));
  chat.dispose();
});

test('reset clears sessions and ignores responses from the previous conversation', async () => {
  const oldNormal = deferred();
  const oldLaw = deferred();
  const calls = [];
  const chat = createSenpaiChat({
    querySource: (request) => {
      calls.push(request);
      if (request.query === '古い質問') return request.mode === 'normal' ? oldNormal.promise : oldLaw.promise;
      return Promise.resolve(answer(request.mode, `new-${request.mode}`, request.query));
    },
  });

  const staleSend = chat.send('古い質問');
  chat.reset();
  assert.deepEqual(chat.getSnapshot(), { turns: [], running: false });
  await chat.send('新しい質問');
  oldNormal.resolve(answer('normal', 'old-normal', '古い質問'));
  oldLaw.resolve(answer('law', 'old-law', '古い質問'));
  await staleSend;

  assert.equal(chat.getSnapshot().turns.length, 1);
  assert.equal(chat.getSnapshot().turns[0].query, '新しい質問');
  assert.deepEqual(calls.slice(2).map(({ sessionId }) => sessionId), [undefined, undefined]);
  chat.dispose();
});

test('pauses unsafe replies whose mode is wrong or whose session collides across modes', async () => {
  const wrongMode = createSenpaiChat({
    querySource: async (request) => answer(request.mode === 'normal' ? 'law' : 'law', 'shared-session'),
  });
  await wrongMode.send('質問');
  assert.equal(wrongMode.getSnapshot().turns[0].normal.status, 'paused');
  assert.equal(wrongMode.getSnapshot().turns[0].law.status, 'success');
  wrongMode.dispose();

  const collision = createSenpaiChat({
    querySource: async (request) => answer(request.mode, 'same-session'),
  });
  await collision.send('質問');
  assert.equal(collision.getSnapshot().turns[0].normal.status, 'paused');
  assert.equal(collision.getSnapshot().turns[0].law.status, 'paused');
  assert.ok(collision.getSnapshot().turns[0].normal.message);
  assert.ok(collision.getSnapshot().turns[0].law.message);
  collision.dispose();
});

test('dispose aborts pending work and prevents later change notifications', async () => {
  const pending = deferred();
  const snapshots = [];
  const signals = [];
  const chat = createSenpaiChat({
    onChange: (snapshot) => snapshots.push(snapshot),
    querySource: (request) => { signals.push(request.signal); return pending.promise; },
  });
  const sending = chat.send('質問');
  await new Promise((resolve) => setImmediate(resolve));
  chat.dispose();
  const notificationCount = snapshots.length;
  assert.ok(signals.every((signal) => signal.aborted));
  pending.resolve(answer('normal', 'late-normal'));
  await sending;
  assert.equal(snapshots.length, notificationCount);
});
