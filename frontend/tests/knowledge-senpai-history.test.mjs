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

test('keeps an unpaired saved lane paused and rejects mismatched or incomplete history', async () => {
  const missingLaw = await readSenpaiConversation({
    baseUrl: BASE, getToken: async () => TOKEN, conversationId,
    fetchImpl: historyFetch({ context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal'), row('assistant', 'normal')] }),
  });
  assert.equal(missingLaw.turns[0].law.status, 'paused');
  assert.match(missingLaw.turns[0].law.message, /保存/);

  for (const payload of [
    { context: 'ordinary', conversationId, complete: true, readOnly: false, messages: [] },
    { context: 'senpai', conversationId: '30000000-0000-4000-8000-000000000001', complete: true, readOnly: false, messages: [] },
    { context: 'senpai', conversationId, complete: false, readOnly: false, messages: [] },
    { context: 'senpai', conversationId, complete: true, readOnly: true, messages: [] },
    { context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal', { senpaiConversationId: '30000000-0000-4000-8000-000000000001' })] },
    { context: 'senpai', conversationId, complete: true, readOnly: false, messages: [row('user', 'normal'), row('user', 'normal')] },
  ]) {
    await assert.rejects(readSenpaiConversation({
      baseUrl: BASE, getToken: async () => TOKEN, conversationId, fetchImpl: historyFetch(payload),
    }), (error) => error.code === 'invalid_response');
  }
});
