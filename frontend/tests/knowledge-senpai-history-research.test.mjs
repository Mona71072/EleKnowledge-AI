import assert from 'node:assert/strict';
import test from 'node:test';
import { readSenpaiConversation } from '../src/lib/knowledge-senpai-history.mjs';
import { createSenpaiChat } from '../src/lib/knowledge-senpai-chat.mjs';

const BASE = 'https://api.example.test/dev';
const conversationId = '10000000-0000-4000-8000-000000000001';
const researchTurn = '20000000-0000-4000-8000-0000000000aa';
const laneTurn = '20000000-0000-4000-8000-0000000000bb';

const response = (body) => ({ ok: true, status: 200, json: async () => body });
const read = (messages) => readSenpaiConversation({
  baseUrl: BASE, getToken: async () => 'token', conversationId,
  fetchImpl: async () => response({ context: 'senpai', conversationId, complete: true, readOnly: false, messages }),
});

function result(overrides = {}) {
  return {
    kind: 'answer', answerMarkdown: '保存された統一回答 [T1] [K1]', clarifyQuestions: [],
    sources: {
      tech: [{ ref: 'T1', title: '手順書', pageNumber: 3, sourceUri: 's3://kb-bucket/a.pdf' }], law: [],
      knowhow: { used: [{ ref: 'K1', knowledgeId: 'KH-1', cardVersion: 1, title: '勘所', status: 'draft' }], candidates: [] },
    },
    unverifiedRefs: [], stopReason: 'sufficient', ...overrides,
  };
}

function row(role, overrides = {}) {
  const assistant = role === 'assistant';
  return {
    sessionId: 'research-session', messageId: `${role}-research-${researchTurn.slice(-2)}`, userId: 'synthetic-user', role,
    ragMode: 'senpai_research', content: assistant ? '保存された統一回答 [T1] [K1]' : 'ドアの異音について',
    timestamp: assistant ? '2026-10-20T01:02:00.000Z' : '2026-10-20T01:00:00.000Z', ttl: 1792458000,
    senpaiConversationId: conversationId, senpaiTurnId: researchTurn,
    ...(assistant ? { responseType: 'pages', researchResult: result() } : {}),
    ...overrides,
  };
}

test('a saved research answer restores as a completed research turn without steps', async () => {
  const saved = await read([row('user'), row('assistant', { modelType: 'AXIEZ-LINKs' })]);
  assert.equal(saved.turns.length, 1);
  const turn = saved.turns[0];
  assert.equal(turn.query, 'ドアの異音について');
  assert.equal(turn.modelType, 'AXIEZ-LINKs');
  assert.equal(turn.research.status, 'completed');
  assert.deepEqual(turn.research.steps, []);
  assert.equal(turn.research.result.answerMarkdown, '保存された統一回答 [T1] [K1]');
  assert.equal(turn.research.result.sources.knowhow.used[0].ref, 'K1');
  assert.equal(turn.normal.status, 'paused');
  assert.equal(turn.law.status, 'paused');
});

test('a research row without a user row or without researchResult is rejected', async () => {
  await assert.rejects(read([row('assistant')]), (error) => error.code === 'invalid_response');
  const bare = row('assistant');
  delete bare.researchResult;
  await assert.rejects(read([row('user'), bare]), (error) => error.code === 'invalid_response');
});

test('a research question with no saved answer is not shown as a turn', async () => {
  const saved = await read([row('user')]);
  assert.deepEqual(saved.turns, []);
});

test('malformed saved research and mixed row types are rejected', async () => {
  await assert.rejects(read([row('user'), row('assistant', { researchResult: result({ kind: 'guess' }) })]), (error) => error.code === 'invalid_response');
  await assert.rejects(read([row('user'), row('assistant', { researchResult: result({ sources: 'x' }) })]), (error) => error.code === 'invalid_response');
  await assert.rejects(read([row('user'), row('assistant'), row('assistant', { messageId: 'dup' })]), (error) => error.code === 'invalid_response');
  await assert.rejects(read([row('user'), row('assistant'), row('user', { ragMode: 'normal', messageId: 'mixed', sessionId: 'normal-s' })]), (error) => error.code === 'invalid_response');
  await assert.rejects(read([row('user', { ragMode: 'unknown_mode' })]), (error) => error.code === 'invalid_response');
});

test('research and two-lane turns can share one conversation and restore into the controller', async () => {
  const lane = (role, mode) => ({
    sessionId: `${mode}-session`, messageId: `${role}-${mode}`, userId: 'synthetic-user', role, ragMode: mode,
    content: role === 'user' ? '二レーンの質問' : `${mode} 回答`,
    timestamp: role === 'user' ? '2026-10-19T01:00:00.000Z' : '2026-10-19T01:01:00.000Z', ttl: 1792458000,
    senpaiConversationId: conversationId, senpaiTurnId: laneTurn,
    ...(role === 'assistant' ? { responseType: 'pages', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [] } : {}),
  });
  const saved = await read([row('user'), row('assistant'), lane('user', 'normal'), lane('assistant', 'normal'), lane('user', 'law'), lane('assistant', 'law')]);
  assert.deepEqual(saved.turns.map((turn) => Boolean(turn.research)), [false, true]);
  assert.equal(saved.turns[0].query, '二レーンの質問');

  const chat = createSenpaiChat({ researchSource: async () => ({}), querySource: async () => ({}) });
  chat.restore(saved);
  const turns = chat.getSnapshot().turns;
  assert.equal(turns[0].normal.status, 'success');
  assert.equal(turns[1].research.result.answerMarkdown, '保存された統一回答 [T1] [K1]');
});
