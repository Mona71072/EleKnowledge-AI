import assert from 'node:assert/strict';
import test from 'node:test';
import { requestSenpaiSynthesis } from '../src/lib/knowledge-senpai-synthesis.mjs';

const BASE = 'https://api.example.test/dev';
const TOKEN = 'synthetic-token';
const conversationId = '10000000-0000-4000-8000-000000000001';
const turnId = '20000000-0000-4000-8000-000000000001';

function reply(overrides = {}) {
  return {
    senpaiConversationId: conversationId,
    senpaiTurnId: turnId,
    messageId: `senpai-synthesis-${turnId}`,
    content: '## 結論の候補（断定しない）\n候補です',
    inputs: { normal: true, law: false, knowhowCount: 2 },
    timestamp: '2026-10-20T01:00:00Z',
    ...overrides,
  };
}

function ok(body, status = 200) {
  return async () => ({ ok: status < 300, status, json: async () => body });
}

const base = { baseUrl: BASE, getToken: async () => TOKEN, senpaiConversationId: conversationId, senpaiTurnId: turnId };

test('posts only the two identifiers to the synthesis route with a bearer token', async () => {
  let request;
  const result = await requestSenpaiSynthesis({
    ...base,
    fetchImpl: async (url, init) => { request = { url, init }; return { ok: true, status: 200, json: async () => reply() }; },
  });
  assert.equal(request.url, `${BASE}/rag/senpai/synthesis`);
  assert.equal(request.init.method, 'POST');
  assert.equal(request.init.headers.Authorization, `Bearer ${TOKEN}`);
  assert.deepEqual(JSON.parse(request.init.body), { senpaiConversationId: conversationId, senpaiTurnId: turnId });
  assert.equal(result.messageId, `senpai-synthesis-${turnId}`);
  assert.equal(result.content.startsWith('## 結論'), true);
  assert.deepEqual(result.inputs, { normal: true, law: false, knowhowCount: 2 });
});

test('rejects invalid identifiers and endpoints before acquiring a token', async () => {
  let tokenCalls = 0;
  const getToken = async () => { tokenCalls += 1; return TOKEN; };
  for (const patch of [
    { senpaiConversationId: 'nope' }, { senpaiTurnId: undefined }, { senpaiTurnId: turnId.toUpperCase() + 'x' },
    { baseUrl: 'http://api.example.test' }, { baseUrl: '' }, { baseUrl: 'https://u:p@api.example.test' },
  ]) {
    await assert.rejects(
      requestSenpaiSynthesis({ ...base, getToken, fetchImpl: ok(reply()), ...patch }),
      (error) => ['validation', 'config'].includes(error.code),
    );
  }
  assert.equal(tokenCalls, 0);
});

test('maps failures to safe user messages without server detail', async () => {
  const cases = [
    [401, 'auth'], [403, 'unavailable'], [404, 'unavailable'], [409, 'unavailable'],
    [422, 'unavailable'], [429, 'server'], [500, 'server'], [502, 'server'], [504, 'timeout'],
  ];
  for (const [status, code] of cases) {
    await assert.rejects(
      requestSenpaiSynthesis({ ...base, fetchImpl: ok({ message: 'secret traceback' }, status) }),
      (error) => error.code === code && !/secret|traceback/u.test(error.message) && error.message.length > 0,
      `status ${status}`,
    );
  }
  await assert.rejects(
    requestSenpaiSynthesis({ ...base, fetchImpl: async () => { throw new Error('socket secret'); } }),
    (error) => error.code === 'server' && !/secret/u.test(error.message),
  );
});

test('422 tells the user there was nothing to combine', async () => {
  await assert.rejects(
    requestSenpaiSynthesis({ ...base, fetchImpl: ok({}, 422) }),
    (error) => /まとめ/u.test(error.message),
  );
});

test('refuses responses that do not match the requested turn or contract', async () => {
  const bad = [
    reply({ senpaiTurnId: '30000000-0000-4000-8000-000000000001' }),
    reply({ senpaiConversationId: '30000000-0000-4000-8000-000000000001' }),
    reply({ messageId: 'senpai-synthesis-other' }),
    reply({ content: '   ' }),
    reply({ content: 'x'.repeat(32_001) }),
    reply({ inputs: { normal: 'yes', law: false, knowhowCount: 0 } }),
    reply({ inputs: { normal: false, law: false, knowhowCount: 0 } }),
    reply({ inputs: { normal: true, law: true, knowhowCount: -1 } }),
    reply({ timestamp: 'yesterday' }),
    null, 'text',
  ];
  for (const body of bad) {
    await assert.rejects(
      requestSenpaiSynthesis({ ...base, fetchImpl: ok(body) }),
      (error) => error.code === 'invalid_response',
    );
  }
  await assert.rejects(
    requestSenpaiSynthesis({ ...base, fetchImpl: async () => ({ ok: true, status: 200, json: async () => { throw new Error('bad json'); } }) }),
    (error) => error.code === 'invalid_response',
  );
});

test('times out and cancels, including a pending token request', async () => {
  await assert.rejects(
    requestSenpaiSynthesis({ ...base, getToken: () => new Promise(() => {}), timeoutMs: 5, fetchImpl: ok(reply()) }),
    (error) => error.code === 'timeout',
  );
  const controller = new AbortController();
  const pending = requestSenpaiSynthesis({
    ...base, signal: controller.signal,
    fetchImpl: (_url, init) => new Promise((_resolve, reject) => {
      init.signal.addEventListener('abort', () => reject(new Error('aborted')), { once: true });
    }),
  });
  await new Promise((resolve) => setImmediate(resolve));
  controller.abort();
  await assert.rejects(pending, (error) => error.code === 'cancelled');
  const already = new AbortController();
  already.abort();
  await assert.rejects(requestSenpaiSynthesis({ ...base, signal: already.signal, fetchImpl: ok(reply()) }), (error) => error.code === 'cancelled');
});

test('rejects missing token and failing token provider', async () => {
  await assert.rejects(requestSenpaiSynthesis({ ...base, getToken: async () => '', fetchImpl: ok(reply()) }), (error) => error.code === 'auth');
  await assert.rejects(requestSenpaiSynthesis({ ...base, getToken: async () => { throw new Error('x'); }, fetchImpl: ok(reply()) }), (error) => error.code === 'auth');
});

test('bounds an oversized timeout', async () => {
  const started = Date.now();
  const result = await requestSenpaiSynthesis({ ...base, timeoutMs: 10 ** 9, fetchImpl: ok(reply()) });
  assert.ok(result.content);
  assert.ok(Date.now() - started < 1000);
});
