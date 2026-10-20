import assert from 'node:assert/strict';
import test from 'node:test';
import {
  FIELD_REPORT_REACTIONS,
  FIELD_REPORT_REACTION_LABELS,
  buildFieldReportPayload,
  createFieldReportDraft,
  fieldReportCards,
  listFieldReports,
  submitFieldReport,
  validateFieldReportDraft,
} from '../src/lib/knowledge-senpai-field-report.mjs';

const CONVERSATION_ID = '11111111-1111-4111-8111-111111111111';
const TURN_ID = '22222222-2222-4222-8222-222222222222';
const BASE_URL = 'https://api.example.test/dev';

function card(knowledgeId, cardVersion, title = `${knowledgeId} title`) {
  return {
    knowledgeId, cardVersion, title, sha256: 'a'.repeat(64), status: 'approved', usage: 'navigation_only',
    body: 'カード本文ZZZ-CARD', searchTerms: [], sourceRefs: [], modelScope: {},
  };
}

function turn(overrides = {}) {
  return {
    id: 1,
    senpaiTurnId: TURN_ID,
    modelType: 'NEXCUBE',
    query: '相談本文ZZZ-QUERY',
    normal: {
      status: 'success',
      answer: {
        mode: 'normal', content: '回答本文ZZZ-ANSWER', query: '相談本文ZZZ-QUERY',
        knowhow: { status: 'matched', indexVersion: 'v1', matches: [card('KH-A', 3), card('KH-B', 1)], searchTerms: [] },
      },
    },
    law: { status: 'success', answer: { mode: 'law', content: '法令ZZZ-LAW' } },
    ...overrides,
  };
}

test('vocabulary is the three fixed reactions with Japanese labels', () => {
  assert.deepEqual([...FIELD_REPORT_REACTIONS], ['matched', 'not_matched', 'unsure']);
  assert.equal(FIELD_REPORT_REACTION_LABELS.matched, 'この条件で当てはまった');
  assert.equal(FIELD_REPORT_REACTION_LABELS.not_matched, '当てはまらなかった');
  assert.equal(FIELD_REPORT_REACTION_LABELS.unsure, '分からない');
});

test('draft starts empty except the turn model and never copies the conversation', () => {
  const draft = createFieldReportDraft(turn());
  assert.deepEqual(draft, { finding: '', condition: '', modelType: 'NEXCUBE', reactions: {} });
  assert.deepEqual(createFieldReportDraft(turn({ modelType: undefined })).modelType, '');
});

test('cards come only from the technical answer knowhow matches, de-duplicated', () => {
  const duplicated = turn();
  duplicated.normal.answer.knowhow.matches.push(card('KH-A', 3));
  assert.deepEqual(fieldReportCards(duplicated), [
    { knowledgeId: 'KH-A', cardVersion: 3, title: 'KH-A title' },
    { knowledgeId: 'KH-B', cardVersion: 1, title: 'KH-B title' },
  ]);
  assert.deepEqual(fieldReportCards(turn({ normal: { status: 'error' } })), []);
});

test('payload contains only what the user confirmed and skips unselected cards', () => {
  const draft = {
    finding: '  分かったこと\r\n二行目 ', condition: ' 条件 ', modelType: 'AXIEZ',
    reactions: { 'KH-A': 'not_matched', 'KH-B': '' },
  };
  const payload = buildFieldReportPayload({ conversationId: CONVERSATION_ID, turn: turn(), draft });
  assert.deepEqual(payload, {
    senpaiConversationId: CONVERSATION_ID,
    senpaiTurnId: TURN_ID,
    finding: '分かったこと\n二行目',
    condition: '条件',
    modelType: 'AXIEZ',
    cardReactions: [{ knowledgeId: 'KH-A', cardVersion: 3, reaction: 'not_matched' }],
    confirmed: true,
  });
  const text = JSON.stringify(payload);
  for (const secret of ['ZZZ-QUERY', 'ZZZ-ANSWER', 'ZZZ-LAW', 'ZZZ-CARD']) assert.equal(text.includes(secret), false);
});

test('payload omits empty optional fields and ignores reactions for cards not in the turn', () => {
  const payload = buildFieldReportPayload({
    conversationId: CONVERSATION_ID,
    turn: turn(),
    draft: { finding: 'x', condition: '  ', modelType: '', reactions: { 'KH-OTHER': 'matched' } },
  });
  assert.equal('condition' in payload, false);
  assert.equal('modelType' in payload, false);
  assert.deepEqual(payload.cardReactions, []);
});

test('validation explains missing finding, length, model and identifiers in Japanese', () => {
  assert.deepEqual(validateFieldReportDraft({ finding: ' ', condition: '', modelType: '', reactions: {} }), ['「何が分かったか」を入力してください']);
  assert.match(validateFieldReportDraft({ finding: 'あ'.repeat(501), condition: '', modelType: '', reactions: {} })[0], /500文字/);
  assert.match(validateFieldReportDraft({ finding: 'a', condition: 'あ'.repeat(301), modelType: '', reactions: {} })[0], /300文字/);
  assert.match(validateFieldReportDraft({ finding: 'a', condition: '', modelType: 'X', reactions: {} })[0], /機種/);
  assert.match(validateFieldReportDraft({ finding: 'a', condition: '', modelType: '', reactions: { A: 'bad' } })[0], /反応/);
  assert.deepEqual(validateFieldReportDraft({ finding: 'a', condition: '', modelType: 'NEXCUBE', reactions: { A: 'unsure' } }), []);
  assert.throws(() => buildFieldReportPayload({ conversationId: 'bad', turn: turn(), draft: createFieldReportDraft(turn()) }),
    (error) => error.code === 'validation');
});

function response(status, body) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

const savedReport = {
  reportId: `field-report-${TURN_ID}`, senpaiConversationId: CONVERSATION_ID, senpaiTurnId: TURN_ID,
  createdAt: '2026-10-20T01:00:00Z', finding: 'x', reviewState: 'unconfirmed',
  cardReactions: [{ knowledgeId: 'KH-A', cardVersion: 3, reaction: 'not_matched' }],
};

test('submit posts the payload with a bearer token and normalizes the saved report', async () => {
  const calls = [];
  const payload = buildFieldReportPayload({ conversationId: CONVERSATION_ID, turn: turn(), draft: { ...createFieldReportDraft(turn()), finding: 'x' } });
  const result = await submitFieldReport({
    baseUrl: `${BASE_URL}/`, getToken: async () => 'token', payload,
    fetchImpl: async (url, init) => { calls.push({ url, init }); return response(200, { ...savedReport, userId: 'leak' }); },
  });
  assert.equal(calls[0].url, `${BASE_URL}/rag/senpai/field-reports`);
  assert.equal(calls[0].init.method, 'POST');
  assert.equal(calls[0].init.headers.Authorization, 'Bearer token');
  assert.deepEqual(JSON.parse(calls[0].init.body), payload);
  assert.equal(result.reviewState, 'unconfirmed');
  assert.equal('userId' in result, false);
});

test('submit maps server statuses to safe Japanese messages', async () => {
  const payload = buildFieldReportPayload({ conversationId: CONVERSATION_ID, turn: turn(), draft: { ...createFieldReportDraft(turn()), finding: 'x' } });
  const cases = [[400, /入力内容/], [401, /再ログイン/], [403, /利用できません/], [404, /保存期間/], [409, /保存できませんでした/], [500, /時間をおいて/]];
  for (const [status, message] of cases) {
    await assert.rejects(
      submitFieldReport({ baseUrl: BASE_URL, getToken: async () => 'token', payload, fetchImpl: async () => response(status, { message: 'secret traceback' }) }),
      (error) => message.test(error.message) && !error.message.includes('secret'),
    );
  }
  await assert.rejects(
    submitFieldReport({ baseUrl: BASE_URL, getToken: async () => 'token', payload, fetchImpl: async () => response(200, { reportId: 'x' }) }),
    (error) => error.code === 'invalid_response',
  );
  await assert.rejects(
    submitFieldReport({ baseUrl: 'http://evil.example', getToken: async () => 'token', payload, fetchImpl: async () => response(200, savedReport) }),
    (error) => error.code === 'config',
  );
  await assert.rejects(
    submitFieldReport({ baseUrl: BASE_URL, getToken: async () => '', payload, fetchImpl: async () => response(200, savedReport) }),
    (error) => error.code === 'auth',
  );
});

test('submit can be cancelled and times out', async () => {
  const payload = buildFieldReportPayload({ conversationId: CONVERSATION_ID, turn: turn(), draft: { ...createFieldReportDraft(turn()), finding: 'x' } });
  const never = (_url, init) => new Promise((_resolve, reject) => init.signal.addEventListener('abort', () => reject(new Error('aborted'))));
  const controller = new AbortController();
  const pending = submitFieldReport({ baseUrl: BASE_URL, getToken: async () => 'token', payload, fetchImpl: never, signal: controller.signal });
  controller.abort();
  await assert.rejects(pending, (error) => error.code === 'cancelled');
  await assert.rejects(
    submitFieldReport({ baseUrl: BASE_URL, getToken: async () => 'token', payload, fetchImpl: never, timeoutMs: 5 }),
    (error) => error.code === 'timeout',
  );
});

test('list reads only reports of the requested conversation keyed by turn', async () => {
  let requested;
  const reports = await listFieldReports({
    baseUrl: BASE_URL, getToken: async () => 'token', conversationId: CONVERSATION_ID,
    fetchImpl: async (url) => {
      requested = url;
      return response(200, { reports: [savedReport, { ...savedReport, senpaiConversationId: 'other', senpaiTurnId: 'x' }, { bad: true }] });
    },
  });
  assert.equal(requested, `${BASE_URL}/rag/senpai/field-reports?senpaiConversationId=${CONVERSATION_ID}`);
  assert.deepEqual(Object.keys(reports), [TURN_ID]);
  await assert.rejects(
    listFieldReports({ baseUrl: BASE_URL, getToken: async () => 'token', conversationId: 'bad', fetchImpl: async () => response(200, { reports: [] }) }),
    (error) => error.code === 'validation',
  );
});
