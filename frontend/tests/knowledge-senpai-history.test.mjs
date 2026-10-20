import assert from 'node:assert/strict';
import test from 'node:test';
import { getSenpaiConversations, readSenpaiConversation } from '../src/lib/knowledge-senpai-history.mjs';

const BASE = 'https://api.example.test/dev';
const TOKEN = 'synthetic-token';
const conversationId = '10000000-0000-4000-8000-000000000001';
const turnId = '20000000-0000-4000-8000-000000000001';

function response(body, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

function historyFetch(body, onRequest = () => {}) {
  return async (url, init) => {
    onRequest(url, init);
    return response(body);
  };
}

function row(role, mode, overrides = {}) {
  const assistant = role === 'assistant';
  return {
    sessionId: `${mode}-session`, messageId: `${role}-${mode}-message`, userId: 'synthetic-user', role,
    ragMode: mode, content: assistant ? `${mode} の保存済み回答` : '同じ相談の質問',
    timestamp: assistant ? '2026-10-20T01:02:00.000Z' : '2026-10-20T01:00:00.000Z', ttl: 1792458000,
    senpaiConversationId: conversationId, senpaiTurnId: turnId,
    ...(assistant ? { responseType: 'pages', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [] } : {}),
    ...overrides,
  };
}

test('lists only Senpai-context sessions and uses the authenticated shared chat endpoint', async () => {
  let request;
  const result = await getSenpaiConversations({
    baseUrl: BASE, getToken: async () => TOKEN,
    fetchImpl: historyFetch({
      context: 'senpai', complete: true,
      sessions: [{ conversationId, title: '同じ相談の質問', createdAt: '2026-10-20T01:00:00.000Z', lastMessageTime: '2026-10-20T01:02:00.000Z', messageCount: 4, daysUntilDeletion: 60 }],
    }, (url, init) => { request = { url, init }; }),
  });
  assert.equal(request.url, `${BASE}/chat/sessions?context=senpai`);
  assert.equal(request.init.headers.Authorization, `Bearer ${TOKEN}`);
  assert.deepEqual(result.sessions.map((item) => item.conversationId), [conversationId]);
  assert.equal(result.complete, true);
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: async () => TOKEN,
    fetchImpl: historyFetch({ context: 'ordinary', complete: true, sessions: [] }),
  }), (error) => error.code === 'invalid_response');
});

test('bounds token acquisition and reports history timeout without exposing details', async () => {
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: () => new Promise(() => {}), timeoutMs: 5,
    fetchImpl: async () => { throw new Error('must not fetch'); },
  }), (error) => error.code === 'timeout' && /時間内/u.test(error.message));
});

test('cancels pending token acquisition and rejects invalid or untrusted endpoints before auth', async () => {
  const controller = new AbortController();
  const pending = getSenpaiConversations({
    baseUrl: BASE, getToken: () => new Promise(() => {}), signal: controller.signal,
    fetchImpl: async () => { throw new Error('must not fetch'); },
  });
  controller.abort();
  await assert.rejects(pending, (error) => error.code === 'cancelled');

  let calls = 0;
  for (const baseUrl of ['not a URL', 'http://api.example.test', 'https://user:pass@example.test/dev', 'https://example.test/path?token=x']) {
    await assert.rejects(getSenpaiConversations({
      baseUrl, getToken: async () => { calls += 1; return TOKEN; }, fetchImpl: async () => response({}),
    }), (error) => error.code === 'config');
  }
  assert.equal(calls, 0);
});

test('maps auth, authorization, server, network, and malformed HTTP failures to safe errors', async () => {
  let fetchCalls = 0;
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: async () => { throw new Error('private auth details'); },
    fetchImpl: async () => { fetchCalls += 1; return response({}); },
  }), (error) => error.code === 'auth' && !/private auth details/u.test(error.message));
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: async () => '', fetchImpl: async () => { fetchCalls += 1; return response({}); },
  }), (error) => error.code === 'auth');
  assert.equal(fetchCalls, 0);

  for (const [status, code] of [[401, 'auth'], [403, 'unavailable'], [503, 'server'], [400, 'unavailable']]) {
    await assert.rejects(getSenpaiConversations({
      baseUrl: BASE, getToken: async () => TOKEN,
      fetchImpl: async () => response({ detail: 'private server response' }, status),
    }), (error) => error.code === code && !/private server response/u.test(error.message));
  }
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: async () => TOKEN, fetchImpl: async () => { throw new Error('private network detail'); },
  }), (error) => error.code === 'server' && !/private network detail/u.test(error.message));
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: async () => TOKEN, fetchImpl: async () => ({ status: 200 }),
  }), (error) => error.code === 'invalid_response');
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: async () => TOKEN, fetchImpl: async () => ({ ...response({}), json: async () => { throw new Error('private parse detail'); } }),
  }), (error) => error.code === 'invalid_response' && !/private parse detail/u.test(error.message));
});

test('honors an already-aborted signal and aborts a pending history fetch', async () => {
  const alreadyAborted = new AbortController();
  alreadyAborted.abort();
  await assert.rejects(getSenpaiConversations({
    baseUrl: BASE, getToken: async () => TOKEN, signal: alreadyAborted.signal,
  }), (error) => error.code === 'cancelled');

  const controller = new AbortController();
  const pending = getSenpaiConversations({
    baseUrl: BASE, getToken: async () => TOKEN, signal: controller.signal,
    fetchImpl: async (_url, { signal }) => new Promise((_resolve, reject) => {
      signal.addEventListener('abort', () => reject(new Error('cancelled')), { once: true });
    }),
  });
  controller.abort();
  await assert.rejects(pending, (error) => error.code === 'cancelled');
});

test('pairs saved lane messages by turn UUID and question and keeps server knowhow card data', async () => {
  const knowhow = {
    status: 'matched', indexVersion: 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    matches: [{ knowledgeId: 'KH-1234', cardVersion: 7, sha256: 'b'.repeat(64), title: '保存当時のカード', status: 'draft', usage: 'navigation_only', body: '保存版本文', searchTerms: ['対象'], sourceRefs: [{ ref_type: 'lists_item', list_item_id: 'list-1' }], modelScope: { product_lines: ['A'] } }],
    searchTerms: ['対象'],
  };
  const result = await readSenpaiConversation({
    baseUrl: BASE, getToken: async () => TOKEN, conversationId,
    fetchImpl: historyFetch({
      context: 'senpai', conversationId, complete: true, readOnly: false,
      messages: [row('user', 'normal'), row('assistant', 'normal', { knowhow }), row('user', 'law'), row('assistant', 'law')],
    }, (url) => assert.equal(url, `${BASE}/chat/sessions/${conversationId}/messages?context=senpai`)),
  });
  assert.equal(result.conversationId, conversationId);
  assert.equal(result.complete, true);
  assert.equal(result.turns.length, 1);
  assert.equal(result.turns[0].senpaiTurnId, turnId);
  assert.equal(result.turns[0].query, '同じ相談の質問');
  assert.equal(result.turns[0].normal.answer.knowhow.matches[0].cardVersion, 7);
  assert.equal(result.turns[0].law.answer.mode, 'law');
  assert.equal(result.turns[0].normal.answer.sessionId, 'normal-session');
  assert.equal(result.turns[0].law.answer.sessionId, 'law-session');
});

test('defaults only absent stored response arrays for pages, not_found, and clarify', async () => {
  const responseTypes = ['pages', 'not_found', 'clarify'];
  const ids = responseTypes.map((_, index) => `20000000-0000-4000-8000-00000000000${index + 1}`);
  const messages = responseTypes.flatMap((responseType, index) => {
    const savedUser = row('user', 'normal', {
      senpaiTurnId: ids[index], messageId: `user-${index}`, content: `質問 ${index}`,
    });
    const savedAssistant = row('assistant', 'normal', {
      senpaiTurnId: ids[index], messageId: `assistant-${index}`, content: `回答 ${index}`, responseType,
    });
    delete savedAssistant.sourceDocuments;
    delete savedAssistant.pageCandidates;
    delete savedAssistant.clarifyQuestions;
    return [savedUser, savedAssistant];
  });
  const result = await readSenpaiConversation({
    baseUrl: BASE, getToken: async () => TOKEN, conversationId,
    fetchImpl: historyFetch({ context: 'senpai', conversationId, complete: true, readOnly: false, messages }),
  });
  assert.deepEqual(result.turns.map((turn) => turn.normal.answer.responseType), responseTypes);
  for (const turn of result.turns) {
    assert.deepEqual(turn.normal.answer.sourceDocuments, []);
    assert.deepEqual(turn.normal.answer.pageCandidates, []);
    assert.deepEqual(turn.normal.answer.clarifyQuestions, []);
  }
});

test('keeps an unpaired saved lane paused and rejects mismatched or incomplete history', async () => {
  const missingLaw = await readSenpaiConversation({
    baseUrl: BASE, getToken: async () => TOKEN, conversationId,
    fetchImpl: historyFetch({ context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal'), row('assistant', 'normal')] }),
  });
  assert.equal(missingLaw.turns[0].law.status, 'paused');
  assert.match(missingLaw.turns[0].law.message, /保存/);
  assert.equal(missingLaw.complete, true);

  for (const payload of [
    { context: 'ordinary', conversationId, complete: true, readOnly: false, messages: [] },
    { context: 'senpai', conversationId: '30000000-0000-4000-8000-000000000001', complete: true, readOnly: false, messages: [] },
    { context: 'senpai', conversationId, complete: true, readOnly: true, messages: [] },
    { context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal', { senpaiConversationId: '30000000-0000-4000-8000-000000000001' })] },
    { context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal'), row('user', 'normal')] },
    { context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal'), row('user', 'law', { userId: 'another-user', messageId: 'user-law-message' })] },
    { context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal'), row('assistant', 'normal', { sourceDocuments: null })] },
  ]) {
    await assert.rejects(readSenpaiConversation({
      baseUrl: BASE, getToken: async () => TOKEN, conversationId, fetchImpl: historyFetch(payload),
    }), (error) => error.code === 'invalid_response');
  }
});

async function readWithNormalAssistant(overrides) {
  return readSenpaiConversation({
    baseUrl: BASE, getToken: async () => TOKEN, conversationId,
    fetchImpl: historyFetch({
      context: 'senpai', conversationId, complete: true, readOnly: false,
      messages: [row('user', 'normal'), row('assistant', 'normal', overrides), row('user', 'law'), row('assistant', 'law', { modelType: 'AXIEZ' })],
    }),
  });
}

test('carries a known saved model filter from the normal lane onto the restored turn', async () => {
  const result = await readWithNormalAssistant({ modelType: 'メルシティ' });
  assert.equal(result.turns[0].modelType, 'メルシティ');
});

test('drops a missing, unknown, or malformed saved model filter without failing the restore', async () => {
  for (const bad of [undefined, '未知の機種', '', 'AXIEZ\n', 'A'.repeat(65), 7, ['AXIEZ'], null]) {
    const result = await readWithNormalAssistant(bad === undefined ? {} : { modelType: bad });
    assert.equal(result.turns.length, 1);
    assert.equal('modelType' in result.turns[0], false, `unexpected modelType for ${JSON.stringify(bad)}`);
  }
});

test('ignores a model filter that only appears on the law lane', async () => {
  const result = await readWithNormalAssistant({});
  assert.equal('modelType' in result.turns[0], false);
});

function synthesisRow(overrides = {}) {
  return {
    sessionId: `senpai-synthesis-${turnId}`, messageId: `senpai-synthesis-${turnId}`, userId: 'synthetic-user',
    role: 'assistant', ragMode: 'senpai_synthesis', content: '保存されたまとめ本文',
    timestamp: '2026-10-20T01:05:00.000Z', ttl: 1792458000,
    senpaiConversationId: conversationId, senpaiTurnId: turnId,
    synthesisInputs: { normal: true, law: true, knowhowCount: 1 },
    ...overrides,
  };
}

async function readWith(messages) {
  return readSenpaiConversation({
    baseUrl: BASE, getToken: async () => TOKEN, conversationId,
    fetchImpl: historyFetch({ context: 'senpai', conversationId, complete: true, readOnly: false, messages }),
  });
}

const laneRows = () => [row('user', 'normal'), row('assistant', 'normal'), row('user', 'law'), row('assistant', 'law')];

test('attaches a saved synthesis row to its turn without turning it into a lane', async () => {
  const result = await readWith([...laneRows(), synthesisRow()]);
  assert.equal(result.turns.length, 1);
  assert.deepEqual(result.turns[0].synthesis, {
    status: 'success', content: '保存されたまとめ本文', messageId: `senpai-synthesis-${turnId}`,
    inputs: { normal: true, law: true, knowhowCount: 1 },
  });
  assert.equal(result.turns[0].normal.status, 'success');
  assert.equal(result.turns[0].law.status, 'success');
});

test('older histories without a synthesis row have no synthesis field', async () => {
  const result = await readWith(laneRows());
  assert.equal('synthesis' in result.turns[0], false);
});

test('omits malformed synthesis inputs but keeps the saved text', async () => {
  const result = await readWith([...laneRows(), synthesisRow({ synthesisInputs: { normal: 'x' } })]);
  assert.equal(result.turns[0].synthesis.content, '保存されたまとめ本文');
  assert.equal('inputs' in result.turns[0].synthesis, false);
});

test('rejects synthesis rows that do not belong to the turn or are malformed', async () => {
  const bad = [
    synthesisRow({ messageId: 'senpai-synthesis-other' }),
    synthesisRow({ role: 'user' }),
    synthesisRow({ content: '  ' }),
    synthesisRow({ content: 'x'.repeat(32_001) }),
    synthesisRow({ timestamp: 'later' }),
    synthesisRow({ userId: 'someone-else' }),
  ];
  for (const synthesis of bad) {
    await assert.rejects(readWith([...laneRows(), synthesis]), (error) => error.code === 'invalid_response');
  }
  await assert.rejects(readWith([...laneRows(), synthesisRow(), synthesisRow({ messageId: `senpai-synthesis-${turnId}` })]), (error) => error.code === 'invalid_response');
});

test('a synthesis row cannot create a turn on its own', async () => {
  await assert.rejects(readWith([synthesisRow()]), (error) => error.code === 'invalid_response');
});
