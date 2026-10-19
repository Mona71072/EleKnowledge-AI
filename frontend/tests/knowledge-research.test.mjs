import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildResearchNote,
  queryKnowledgeSource,
  researchSourceHref,
} from '../src/lib/knowledge-research.mjs';

const BASE = 'https://api.example.test/dev';
const TOKEN = 'test-id-token';

function response(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  };
}

function normalPayload(overrides = {}) {
  return {
    sessionId: 'session_normal_1',
    userMessageId: 'user_1',
    aiMessageId: 'assistant_1',
    responseType: 'pages',
    content: '対象条件を確認してください。',
    clarifyQuestions: [],
    pageCandidates: [
      {
        documentName: '施工要領.pdf',
        sourceUri: 's3://technical-kb/docs/install.pdf',
        pageNumber: 12,
        relevance: 0.86,
        snippet: '固定状態を確認する。',
      },
    ],
    sourceDocuments: [
      {
        documentName: '施工要領.pdf',
        sourceUri: 's3://technical-kb/docs/install.pdf',
        category: 'C資料',
        pageNumber: 12,
      },
    ],
    ...overrides,
  };
}

function lawPayload(overrides = {}) {
  const citation = {
    lawId: '347M50002000032',
    lawTitle: '労働安全衛生規則',
    lawNumber: '昭和四十七年労働省令第三十二号',
    effectiveDate: '2025-04-01',
    provisionType: 'main',
    provisionReference: '第518条',
    sourceUrl: 'https://laws.e-gov.go.jp/law/347M50002000032',
  };
  return normalPayload({
    sessionId: 'session_law_1',
    sourceDocuments: [{ documentName: '労働安全衛生規則', sourceUri: citation.sourceUrl, lawCitation: citation }],
    pageCandidates: [],
    ...overrides,
  });
}

function fetchOk(payload, onRequest = () => {}) {
  return async (url, init) => {
    onRequest(url, init);
    return response(payload);
  };
}

test('posts only the explicit query, mode, and empty filters with the Cognito ID token', async () => {
  let request;
  const answer = await queryKnowledgeSource({
    baseUrl: BASE,
    getToken: async () => TOKEN,
    fetchImpl: fetchOk(normalPayload(), (url, init) => { request = { url, init }; }),
    mode: 'normal',
    query: '非常停止後の固定状態を確認したい',
  });

  assert.equal(request.url, `${BASE}/rag/query`);
  assert.equal(request.init.method, 'POST');
  assert.equal(request.init.headers.Authorization, `Bearer ${TOKEN}`);
  assert.deepEqual(JSON.parse(request.init.body), {
    query: '非常停止後の固定状態を確認したい',
    mode: 'normal',
    filters: {},
  });
  assert.equal(answer.mode, 'normal');
  assert.equal(answer.query, '非常停止後の固定状態を確認したい');
  assert.equal(answer.content, '対象条件を確認してください。');
  assert.equal(answer.responseType, 'pages');
  assert.equal(answer.sessionId, 'session_normal_1');
  assert.equal(answer.messageId, 'assistant_1');
  assert.equal(answer.sourceDocuments[0].sourceUri, 's3://technical-kb/docs/install.pdf');
});

test('law mode is isolated in the request and normalizes the assistant message ID fallback', async () => {
  let body;
  const answer = await queryKnowledgeSource({
    baseUrl: BASE,
    getToken: async () => TOKEN,
    fetchImpl: fetchOk(lawPayload({ aiMessageId: undefined, messageId: 'assistant_law_2' }), (_url, init) => { body = JSON.parse(init.body); }),
    mode: 'law',
    query: '作業床の端部に必要な措置',
  });

  assert.deepEqual(body, { query: '作業床の端部に必要な措置', mode: 'law', filters: {} });
  assert.equal(answer.mode, 'law');
  assert.equal(answer.sessionId, 'session_law_1');
  assert.equal(answer.messageId, 'assistant_law_2');
  assert.equal(answer.sourceDocuments[0].lawCitation.effectiveDate, '2025-04-01');
});

test('validates blank, oversized, unsupported-mode, and malformed endpoint inputs before network access', async () => {
  let calls = 0;
  const common = { baseUrl: BASE, getToken: async () => TOKEN, fetchImpl: async () => { calls += 1; return response(normalPayload()); } };
  for (const options of [
    { mode: 'normal', query: '  \n  ' },
    { mode: 'normal', query: 'x'.repeat(2001) },
    { mode: 'spec', query: 'question' },
    { mode: 'normal', query: 'question', baseUrl: 'http://api.example.test' },
    { mode: 'normal', query: 'question', baseUrl: 'https://user:secret@api.example.test' },
    { mode: 'normal', query: 'question', baseUrl: 'https://api.example.test/path?token=secret' },
  ]) {
    await assert.rejects(queryKnowledgeSource({ ...common, ...options }), (error) => error.code === 'validation' || error.code === 'config');
  }
  assert.equal(calls, 0);
});

test('allows explicit loopback HTTP endpoints for local development only', async () => {
  await queryKnowledgeSource({
    baseUrl: 'http://127.0.0.1:3198/dev',
    getToken: async () => TOKEN,
    fetchImpl: fetchOk(normalPayload()),
    mode: 'normal',
    query: 'local test',
  });
});

test('maps missing token, HTTP failures, network failures, and malformed response to safe Japanese errors', async () => {
  const cases = [
    [() => queryKnowledgeSource({ baseUrl: BASE, getToken: async () => '', fetchImpl: fetchOk(normalPayload()), mode: 'normal', query: 'question' }), 'auth'],
    [() => queryKnowledgeSource({ baseUrl: BASE, getToken: async () => TOKEN, fetchImpl: async () => response({ message: 'secret server traceback' }, 403), mode: 'law', query: 'question' }), 'unavailable'],
    [() => queryKnowledgeSource({ baseUrl: BASE, getToken: async () => TOKEN, fetchImpl: async () => { throw new Error('secret network detail'); }, mode: 'normal', query: 'question' }), 'server'],
    [() => queryKnowledgeSource({ baseUrl: BASE, getToken: async () => TOKEN, fetchImpl: fetchOk({ ...normalPayload(), content: 9 }), mode: 'normal', query: 'question' }), 'invalid_response'],
  ];

  for (const [run, code] of cases) {
    await assert.rejects(run(), (error) => {
      assert.equal(error.code, code);
      assert.match(error.message, /[ぁ-んァ-ヶ一-龠]/u);
      assert.doesNotMatch(error.message, /secret|traceback|network detail/i);
      return true;
    });
  }
});

test('bounds token acquisition and fetch with one timeout and cleans up a caller abort', async () => {
  await assert.rejects(
    queryKnowledgeSource({
      baseUrl: BASE,
      getToken: () => new Promise(() => {}),
      fetchImpl: fetchOk(normalPayload()),
      mode: 'normal',
      query: 'question',
      timeoutMs: 10,
    }),
    (error) => error.code === 'timeout',
  );

  const controller = new AbortController();
  const pending = queryKnowledgeSource({
    baseUrl: BASE,
    getToken: async () => TOKEN,
    fetchImpl: (_url, init) => new Promise((_resolve, reject) => init.signal.addEventListener('abort', () => reject(new Error('aborted')))),
    mode: 'normal',
    query: 'question',
    signal: controller.signal,
  });
  controller.abort();
  await assert.rejects(pending, (error) => error.code === 'cancelled');
});

test('maps S3 and legacy signed S3 sources to authenticated document relay and rejects unsafe links', () => {
  assert.equal(
    researchSourceHref({ sourceUri: 's3://technical-kb/docs/install manual.pdf', pageNumber: 12 }, 'normal'),
    `/doc?uri=${encodeURIComponent('s3://technical-kb/docs/install manual.pdf')}#page=12`,
  );
  assert.equal(
    researchSourceHref({ sourceUri: 'https://technical-kb.s3.ap-northeast-1.amazonaws.com/docs/install.pdf?X-Amz-Signature=secret' }, 'normal'),
    `/doc?uri=${encodeURIComponent('s3://technical-kb/docs/install.pdf')}`,
  );
  assert.equal(researchSourceHref({ sourceUri: 'javascript:alert(1)' }, 'normal'), undefined);
  assert.equal(researchSourceHref({ sourceUri: 'https://attacker.example.test/doc.pdf' }, 'normal'), undefined);
});

test('only accepts verified e-Gov law citations and keeps API-provided legal dates and references', () => {
  const valid = lawPayload().sourceDocuments[0];
  assert.equal(researchSourceHref(valid, 'law'), valid.lawCitation.sourceUrl);
  assert.equal(researchSourceHref({ ...valid, lawCitation: { ...valid.lawCitation, sourceUrl: 'https://evil.example.test/law/347M50002000032' } }, 'law'), undefined);
  assert.equal(researchSourceHref({ sourceUri: valid.lawCitation.sourceUrl }, 'law'), undefined);
});

test('strips signed source URLs from normalized results and keeps a deterministic labeled research note', async () => {
  const signed = 'https://technical-kb.s3.ap-northeast-1.amazonaws.com/docs/a.pdf?X-Amz-Signature=must-not-leak';
  const answer = await queryKnowledgeSource({
    baseUrl: BASE,
    getToken: async () => TOKEN,
    fetchImpl: fetchOk(normalPayload({ sourceDocuments: [{ documentName: 'a.pdf', sourceUri: signed }] })),
    mode: 'normal',
    query: '確認条件は何か',
  });
  assert.equal(answer.sourceDocuments[0].sourceUri, 's3://technical-kb/docs/a.pdf');
  assert.doesNotMatch(JSON.stringify(answer), /X-Amz-Signature|must-not-leak/);

  const note = buildResearchNote(answer);
  assert.match(note, /AI候補/);
  assert.match(note, /未確認/);
  assert.match(note, /確認条件は何か/);
  assert.match(note, /a\.pdf/);
  assert.match(note, /s3:\/\/technical-kb\/docs\/a\.pdf/);
  assert.equal(buildResearchNote(answer), note);
});

test('does not create an adoptable note for clarify and not_found results', () => {
  for (const responseType of ['clarify', 'not_found']) {
    assert.throws(
      () => buildResearchNote({ mode: 'normal', query: 'question', responseType, content: 'no evidence', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [] }),
      (error) => error.code === 'validation',
    );
  }
});
