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

test('uses one stable conversation UUID and a distinct turn UUID pair on every send', async () => {
  const ids = ['10000000-0000-4000-8000-000000000001', '20000000-0000-4000-8000-000000000001', '20000000-0000-4000-8000-000000000002', '30000000-0000-4000-8000-000000000001', '40000000-0000-4000-8000-000000000001'];
  const calls = [];
  const chat = createSenpaiChat({
    createId: () => ids.shift(),
    querySource: async (request) => {
      calls.push(request);
      return answer(request.mode, `${request.mode}-session`, request.query);
    },
  });
  assert.equal(chat.getSnapshot().conversationId, undefined);
  await chat.send('一問目');
  await chat.send('二問目');
  const snapshot = chat.getSnapshot();
  assert.equal(snapshot.conversationId, '10000000-0000-4000-8000-000000000001');
  assert.deepEqual(snapshot.turns.map((turn) => turn.senpaiTurnId), [
    '20000000-0000-4000-8000-000000000001', '20000000-0000-4000-8000-000000000002',
  ]);
  assert.ok(calls.every((call) => call.senpaiConversationId === snapshot.conversationId));
  assert.deepEqual(calls.map((call) => call.senpaiTurnId), [snapshot.turns[0].senpaiTurnId, snapshot.turns[0].senpaiTurnId, snapshot.turns[1].senpaiTurnId, snapshot.turns[1].senpaiTurnId]);
  chat.reset();
  await chat.send('新規相談');
  assert.equal(chat.getSnapshot().conversationId, '30000000-0000-4000-8000-000000000001');
  chat.dispose();
});

test('restores complete history with separate lane sessions and refuses incomplete history', async () => {
  const calls = [];
  const chat = createSenpaiChat({
    createId: () => '30000000-0000-4000-8000-000000000001',
    querySource: async (request) => {
      calls.push(request);
      return answer(request.mode, request.sessionId || `${request.mode}-restored`, request.query);
    },
  });
  const conversationId = '10000000-0000-4000-8000-000000000001';
  chat.restore({
    conversationId,
    complete: true,
    turns: [{
      id: 1,
      senpaiTurnId: '20000000-0000-4000-8000-000000000001',
      query: '保存済みの質問',
      normal: { status: 'success', answer: { ...answer('normal', 'normal-restored', '保存済みの質問'), senpaiConversationId: conversationId, senpaiTurnId: '20000000-0000-4000-8000-000000000001' } },
      law: { status: 'success', answer: { ...answer('law', 'law-restored', '保存済みの質問'), senpaiConversationId: conversationId, senpaiTurnId: '20000000-0000-4000-8000-000000000001' } },
    }],
  });
  assert.equal(chat.getSnapshot().conversationId, conversationId);
  await chat.send('復元後の質問');
  assert.deepEqual(calls.map((call) => call.sessionId), ['normal-restored', 'law-restored']);
  assert.ok(calls.every((call) => call.senpaiConversationId === conversationId));

  chat.restore({ conversationId, complete: false, turns: [] });
  assert.equal(chat.getSnapshot().complete, false);
  await assert.rejects(chat.send('不完全履歴からの送信'), (error) => error.code === 'validation');
  chat.dispose();
});

test('restores a missing lane as paused while the healthy lane continues independently', async () => {
  const calls = [];
  const conversationId = '10000000-0000-4000-8000-000000000001';
  const turnId = '20000000-0000-4000-8000-000000000001';
  const chat = createSenpaiChat({
    createId: () => '30000000-0000-4000-8000-000000000001',
    querySource: async (request) => {
      calls.push(request);
      return answer(request.mode, request.sessionId || `${request.mode}-restored`, request.query);
    },
  });
  chat.restore({
    conversationId, complete: true,
    turns: [
      {
        id: 1, senpaiTurnId: turnId, query: '前の保存済み質問',
        normal: { status: 'success', answer: { ...answer('normal', 'normal-session', '前の保存済み質問'), senpaiConversationId: conversationId, senpaiTurnId: turnId } },
        law: { status: 'success', answer: { ...answer('law', 'law-session', '前の保存済み質問'), senpaiConversationId: conversationId, senpaiTurnId: turnId } },
      },
      {
        id: 2, senpaiTurnId: '20000000-0000-4000-8000-000000000002', query: '最後の保存済み質問',
        normal: { status: 'success', answer: { ...answer('normal', 'normal-session', '最後の保存済み質問'), senpaiConversationId: conversationId, senpaiTurnId: '20000000-0000-4000-8000-000000000002' } },
        law: { status: 'paused', message: '法令KBの回答は保存されていません' },
      },
    ],
  });
  await chat.send('技術KBで続ける質問');
  assert.deepEqual(calls.map(({ mode, sessionId }) => ({ mode, sessionId })), [{ mode: 'normal', sessionId: 'normal-session' }]);
  assert.equal(chat.getSnapshot().turns[2].law.status, 'paused');
  chat.dispose();
});

test('rejects restored histories with duplicate turn UUIDs or colliding mode sessions', () => {
  const conversationId = '10000000-0000-4000-8000-000000000001';
  const firstId = '20000000-0000-4000-8000-000000000001';
  const restoredTurn = (id, senpaiTurnId, normalSession, lawSession, query) => ({
    id, senpaiTurnId, query,
    normal: { status: 'success', answer: { ...answer('normal', normalSession, query), senpaiConversationId: conversationId, senpaiTurnId } },
    law: { status: 'success', answer: { ...answer('law', lawSession, query), senpaiConversationId: conversationId, senpaiTurnId } },
  });
  const chat = createSenpaiChat({ querySource: async () => answer('normal', 'session') });
  assert.throws(() => chat.restore({
    conversationId, complete: true,
    turns: [restoredTurn(1, firstId, 'normal-session', 'law-session', '質問1'), restoredTurn(2, firstId, 'normal-session', 'law-session', '質問2')],
  }), (error) => error.code === 'validation');
  assert.throws(() => chat.restore({
    conversationId, complete: true,
    turns: [restoredTurn(1, firstId, 'shared-session', 'shared-session', '質問1')],
  }), (error) => error.code === 'validation');
  chat.dispose();
});

test('passes an optional model type to both lanes and records it on that turn only', async () => {
  const calls = [];
  const chat = createSenpaiChat({
    querySource: async (request) => {
      calls.push(request);
      return answer(request.mode, request.mode === 'normal' ? 'technical-session' : 'law-session', request.query);
    },
  });

  await chat.send('機種つき', { modelType: ' AXIEZ ' });
  await chat.send('機種なし');
  await chat.send('空指定', { modelType: '   ' });

  assert.deepEqual(calls.map((call) => call.modelType), ['AXIEZ', 'AXIEZ', undefined, undefined, undefined, undefined]);
  assert.equal(Object.hasOwn(calls[2], 'modelType'), false);
  const { turns } = chat.getSnapshot();
  assert.equal(turns[0].modelType, 'AXIEZ');
  assert.equal(Object.hasOwn(turns[1], 'modelType'), false);
  assert.equal(Object.hasOwn(turns[2], 'modelType'), false);
  chat.dispose();
});

test('rejects a non-string model type before creating a turn', async () => {
  let calls = 0;
  const chat = createSenpaiChat({ querySource: async () => { calls += 1; return answer('normal', 's'); } });

  await assert.rejects(chat.send('質問', { modelType: 3 }), (error) => error.code === 'validation');

  assert.equal(calls, 0);
  assert.equal(chat.getSnapshot().turns.length, 0);
  chat.dispose();
});

function restoredTurn(overrides = {}) {
  const conversationId = '10000000-0000-4000-8000-000000000001';
  const senpaiTurnId = '20000000-0000-4000-8000-000000000001';
  return {
    conversationId,
    complete: true,
    turns: [{
      id: 1, senpaiTurnId, query: '保存済みの質問', ...overrides,
      normal: { status: 'success', answer: { ...answer('normal', 'normal-restored', '保存済みの質問'), senpaiConversationId: conversationId, senpaiTurnId } },
      law: { status: 'success', answer: { ...answer('law', 'law-restored', '保存済みの質問'), senpaiConversationId: conversationId, senpaiTurnId } },
    }],
  };
}

test('restore keeps a valid modelType on the turn so the model badge shows', () => {
  const chat = createSenpaiChat({ querySource: async () => answer('normal', 'x') });
  chat.restore(restoredTurn({ modelType: 'NEXCUBE' }));
  assert.equal(chat.getSnapshot().turns[0].modelType, 'NEXCUBE');
  chat.dispose();
});

test('restore drops an invalid modelType and still restores old history without one', () => {
  const chat = createSenpaiChat({ querySource: async () => answer('normal', 'x') });
  for (const bad of ['未知の機種', '', 'AXIEZ\n', 'A'.repeat(65), 5, null, ['AXIEZ']]) {
    chat.restore(restoredTurn({ modelType: bad }));
    assert.equal(chat.getSnapshot().turns.length, 1);
    assert.equal('modelType' in chat.getSnapshot().turns[0], false);
  }
  chat.restore(restoredTurn());
  assert.equal(chat.getSnapshot().turns.length, 1);
  assert.equal('modelType' in chat.getSnapshot().turns[0], false);
  chat.dispose();
});

function synthesisResult(request, overrides = {}) {
  return {
    senpaiConversationId: request.senpaiConversationId,
    senpaiTurnId: request.senpaiTurnId,
    messageId: `senpai-synthesis-${request.senpaiTurnId}`,
    content: 'まとめ本文',
    inputs: { normal: true, law: true, knowhowCount: 0 },
    timestamp: '2026-10-20T01:00:00Z',
    ...overrides,
  };
}

function chatWithSynthesis(synthesisSource, query = async (request) => answer(request.mode, `${request.mode}-session`, request.query)) {
  return createSenpaiChat({ querySource: query, synthesisSource });
}

test('synthesize moves the turn synthesis lane from loading to success using only identifiers', async () => {
  const pending = deferred();
  const calls = [];
  const chat = chatWithSynthesis((request) => { calls.push(request); return pending.promise; });
  await chat.send('質問');
  const { conversationId, turns } = chat.getSnapshot();
  assert.equal(turns[0].synthesis, undefined);

  const running = chat.synthesize(turns[0].id);
  assert.equal(chat.getSnapshot().turns[0].synthesis.status, 'loading');
  pending.resolve(synthesisResult({ senpaiConversationId: conversationId, senpaiTurnId: turns[0].senpaiTurnId }));
  await running;

  assert.deepEqual(Object.keys(calls[0]).sort(), ['senpaiConversationId', 'senpaiTurnId', 'signal']);
  assert.equal(calls[0].senpaiConversationId, conversationId);
  assert.equal(calls[0].senpaiTurnId, turns[0].senpaiTurnId);
  const synthesis = chat.getSnapshot().turns[0].synthesis;
  assert.equal(synthesis.status, 'success');
  assert.equal(synthesis.content, 'まとめ本文');
  assert.equal(synthesis.messageId, `senpai-synthesis-${turns[0].senpaiTurnId}`);
  assert.equal(Object.isFrozen(chat.getSnapshot().turns[0].synthesis), true);
  chat.dispose();
});

test('synthesize is refused while running, while a lane loads, with no successful lane, or for unknown turns', async () => {
  const pending = deferred();
  let sourceCalls = 0;
  const failing = chatWithSynthesis(() => { sourceCalls += 1; return Promise.resolve(); }, async () => { throw new Error('down'); });
  await failing.send('質問');
  await assert.rejects(failing.synthesize(failing.getSnapshot().turns[0].id), (error) => error.code === 'validation');
  await assert.rejects(failing.synthesize(999), (error) => error.code === 'validation');

  const slow = chatWithSynthesis(() => { sourceCalls += 1; return Promise.resolve(); }, () => pending.promise);
  const sending = slow.send('質問');
  await assert.rejects(slow.synthesize(slow.getSnapshot().turns[0].id), (error) => error.code === 'validation');
  pending.reject(new Error('x'));
  await sending;

  const noSource = createSenpaiChat({ querySource: async (request) => answer(request.mode, `${request.mode}-s`, request.query) });
  await noSource.send('質問');
  await assert.rejects(noSource.synthesize(noSource.getSnapshot().turns[0].id), (error) => error.code === 'validation');
  assert.equal(sourceCalls, 0);
  for (const chat of [failing, slow, noSource]) chat.dispose();
});

test('synthesize works with one successful lane and does not repeat after success', async () => {
  let calls = 0;
  const chat = chatWithSynthesis(async (request) => { calls += 1; return synthesisResult(request, { inputs: { normal: true, law: false, knowhowCount: 1 } }); }, async (request) => {
    if (request.mode === 'law') throw new Error('law down');
    return answer('normal', 'normal-session', request.query);
  });
  await chat.send('質問');
  const id = chat.getSnapshot().turns[0].id;
  await chat.synthesize(id);
  await chat.synthesize(id);
  assert.equal(calls, 1);
  assert.deepEqual(chat.getSnapshot().turns[0].synthesis.inputs, { normal: true, law: false, knowhowCount: 1 });
  chat.dispose();
});

test('synthesis errors are shown safely and can be retried; mismatching results are rejected', async () => {
  let attempt = 0;
  const chat = chatWithSynthesis(async (request) => {
    attempt += 1;
    if (attempt === 1) throw new Error('secret stack');
    if (attempt === 2) return synthesisResult(request, { senpaiTurnId: '30000000-0000-4000-8000-000000000001' });
    if (attempt === 3) throw Object.assign(new Error('x'), { code: 'timeout', message: '時間内に完了しませんでした', name: 'KnowledgeResearchError' });
    return synthesisResult(request);
  });
  await chat.send('質問');
  const id = chat.getSnapshot().turns[0].id;
  await chat.synthesize(id);
  let state = chat.getSnapshot().turns[0].synthesis;
  assert.equal(state.status, 'error');
  assert.doesNotMatch(state.message, /secret/u);
  await chat.synthesize(id);
  assert.equal(chat.getSnapshot().turns[0].synthesis.status, 'error');
  await chat.synthesize(id);
  assert.equal(chat.getSnapshot().turns[0].synthesis.status, 'error');
  await chat.synthesize(id);
  state = chat.getSnapshot().turns[0].synthesis;
  assert.equal(state.status, 'success');
  chat.dispose();
});

test('a reset or restore discards an in-flight synthesis result', async () => {
  const pending = deferred();
  let aborted = false;
  const chat = chatWithSynthesis((request) => {
    request.signal.addEventListener('abort', () => { aborted = true; });
    return pending.promise;
  });
  await chat.send('質問');
  const turn = chat.getSnapshot().turns[0];
  const request = { senpaiConversationId: chat.getSnapshot().conversationId, senpaiTurnId: turn.senpaiTurnId };
  const running = chat.synthesize(turn.id);
  chat.reset();
  pending.resolve(synthesisResult(request));
  await running;
  assert.equal(aborted, true);
  assert.deepEqual(chat.getSnapshot().turns, []);
  chat.dispose();
});

test('restore keeps a saved synthesis, ignores malformed ones, and accepts older histories', async () => {
  const conversationId = '10000000-0000-4000-8000-000000000001';
  const mk = (suffix, synthesis) => {
    const turnId = `20000000-0000-4000-8000-00000000000${suffix}`;
    return {
      id: Number(suffix), senpaiTurnId: turnId, query: `質問${suffix}`,
      normal: { status: 'success', answer: { ...answer('normal', 'normal-restored', `質問${suffix}`), senpaiConversationId: conversationId, senpaiTurnId: turnId } },
      law: { status: 'success', answer: { ...answer('law', 'law-restored', `質問${suffix}`), senpaiConversationId: conversationId, senpaiTurnId: turnId } },
      ...(synthesis ? { synthesis } : {}),
    };
  };
  const chat = chatWithSynthesis(async (request) => synthesisResult(request));
  chat.restore({
    conversationId, complete: true,
    turns: [
      mk('1', { status: 'success', content: '保存されたまとめ', messageId: 'senpai-synthesis-x', inputs: { normal: true, law: true, knowhowCount: 2 } }),
      mk('2', { status: 'success', content: '   ', messageId: 'senpai-synthesis-y' }),
      mk('3', { status: 'error', message: 'x' }),
      mk('4'),
    ],
  });
  const turns = chat.getSnapshot().turns;
  assert.deepEqual({ ...turns[0].synthesis }, {
    status: 'success', content: '保存されたまとめ', messageId: 'senpai-synthesis-x',
    inputs: { normal: true, law: true, knowhowCount: 2 },
  });
  assert.equal(turns[1].synthesis, undefined);
  assert.equal(turns[2].synthesis, undefined);
  assert.equal(turns[3].synthesis, undefined);
  await chat.synthesize(turns[3].id);
  assert.equal(chat.getSnapshot().turns[3].synthesis.status, 'success');
  chat.dispose();
});

test('cancelling a later search does not discard an in-flight synthesis of an earlier turn', async () => {
  const pendingSynthesis = deferred();
  let queries = 0;
  const chat = chatWithSynthesis(() => pendingSynthesis.promise, (request) => {
    queries += 1;
    if (queries <= 2) return Promise.resolve(answer(request.mode, `${request.mode}-session`, request.query));
    return new Promise((_resolve, reject) => {
      request.signal.addEventListener('abort', () => reject(Object.assign(new Error('aborted'), { code: 'cancelled' })), { once: true });
    });
  });
  await chat.send('最初');
  const first = chat.getSnapshot().turns[0];
  const running = chat.synthesize(first.id);
  const sending = chat.send('次の質問');
  chat.cancel();
  await sending;
  pendingSynthesis.resolve(synthesisResult({ senpaiConversationId: chat.getSnapshot().conversationId, senpaiTurnId: first.senpaiTurnId }));
  await running;
  assert.equal(chat.getSnapshot().turns[0].synthesis.status, 'success');
  chat.dispose();
});
