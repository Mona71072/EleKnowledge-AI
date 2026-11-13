import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildTimelineRows,
  getSenpaiResearchStatus,
  lawSourceHref,
  mergeResearchSteps,
  normalizeSenpaiResearchResult,
  runSenpaiResearch,
  startSenpaiResearch,
  techSourceHref,
} from '../src/lib/knowledge-senpai-research.mjs';

const BASE = 'https://api.example.test/dev';
const TOKEN = 'synthetic-token';
const jobId = '30000000-0000-4000-8000-000000000001';
const conversationId = '10000000-0000-4000-8000-000000000001';
const turnId = '20000000-0000-4000-8000-000000000001';
const requestId = '40000000-0000-4000-8000-000000000001';

const response = (body, status = 200) => ({ ok: status >= 200 && status < 300, status, json: async () => body });

function step(seq, overrides = {}) {
  return {
    seq, step: 'tech_search', labelJa: '技術資料を検索中', detailJa: '『LINKs ドア 異音』で検索',
    status: 'running', counts: { hits: 8, selected: 4, documents: 3 },
    startedAt: '2026-10-20T01:00:00.000Z', endedAt: null, ...overrides,
  };
}

function result(overrides = {}) {
  return {
    kind: 'answer',
    answerMarkdown: '## 結論の候補\nドアの調整です [T1] [L1] [K1]',
    clarifyQuestions: [],
    sources: {
      tech: [{ ref: 'T1', title: '保守手順書', documentName: 'manual.pdf', pageNumber: 12, sourceUri: 's3://kb-bucket/docs/manual.pdf' }],
      law: [{ ref: 'L1', lawTitle: '建築基準法', provision: '第三十四条', effectiveDate: '2025-04-01', sourceUrl: 'https://laws.e-gov.go.jp/law/325AC0000000201' }],
      knowhow: {
        used: [{ ref: 'K1', knowledgeId: 'KH-1001', cardVersion: 2, title: '調整の勘所', status: 'draft', modelFit: 'other_product', modelFitProducts: ['AXIEZ-LINKs'] }],
        candidates: [{ knowledgeId: 'KH-2002', cardVersion: 1, title: '使わなかったカード' }],
      },
    },
    understanding: { modelType: null, controlMethod: 'VFGLF', part: 'ドア', symptom: '異音', situation: null, intent: 'cause', lawRelevant: true },
    unverifiedRefs: [],
    stopReason: 'sufficient',
    ...overrides,
  };
}

const startOptions = (fetchImpl, overrides = {}) => ({
  baseUrl: BASE, getToken: async () => TOKEN, fetchImpl, question: ' ドアの異音 ', modelType: 'AXIEZ-LINKs',
  senpaiConversationId: conversationId, senpaiTurnId: turnId, clientRequestId: requestId, ...overrides,
});

test('start sends only the contract fields with the bearer token and returns the job', async () => {
  let request;
  const out = await startSenpaiResearch(startOptions(async (url, init) => {
    request = { url, init };
    return response({ jobId, status: 'queued', pollAfterMs: 1500 }, 202);
  }));
  assert.equal(request.url, `${BASE}/rag/senpai/research`);
  assert.equal(request.init.method, 'POST');
  assert.equal(request.init.headers.Authorization, `Bearer ${TOKEN}`);
  assert.deepEqual(JSON.parse(request.init.body), {
    question: 'ドアの異音', modelType: 'AXIEZ-LINKs', senpaiConversationId: conversationId, senpaiTurnId: turnId, clientRequestId: requestId,
  });
  assert.deepEqual(out, { jobId, status: 'queued', pollAfterMs: 1500 });
});

test('start omits modelType when none is chosen and tolerates a missing pollAfterMs', async () => {
  let body;
  const out = await startSenpaiResearch(startOptions(async (_url, init) => {
    body = JSON.parse(init.body);
    return response({ jobId, status: 'queued' }, 202);
  }, { modelType: undefined }));
  assert.equal(Object.hasOwn(body, 'modelType'), false);
  assert.equal(out.pollAfterMs, undefined);
});

test('start validates input before any network or auth call', async () => {
  const never = async () => { throw new Error('must not fetch'); };
  const cases = [
    { question: '   ' }, { question: 'あ'.repeat(2001) }, { question: 5 },
    { modelType: '' }, { modelType: 'x\u0000y' },
    { senpaiConversationId: 'not-a-uuid' }, { senpaiTurnId: 'bad' }, { clientRequestId: 'bad' },
  ];
  for (const override of cases) {
    await assert.rejects(startSenpaiResearch(startOptions(never, override)), (error) => error.code === 'validation', JSON.stringify(override));
  }
  await assert.rejects(startSenpaiResearch(startOptions(never, { baseUrl: 'http://evil.example.test' })), (error) => error.code === 'config');
  await assert.rejects(startSenpaiResearch(startOptions(never, { baseUrl: '' })), (error) => error.code === 'config');
  await assert.rejects(startSenpaiResearch(startOptions(never, { getToken: undefined })), (error) => error.code === 'config');
  await assert.rejects(startSenpaiResearch(startOptions(never, { getToken: async () => '' })), (error) => error.code === 'auth');
  await assert.rejects(startSenpaiResearch(startOptions(never, { getToken: async () => { throw new Error('x'); } })), (error) => error.code === 'auth');
});

test('start maps HTTP failures to safe Japanese messages', async () => {
  const run = (status) => startSenpaiResearch(startOptions(async () => response({ message: 'secret detail' }, status)));
  await assert.rejects(run(401), (error) => error.code === 'auth' && /再ログイン/u.test(error.message));
  await assert.rejects(run(403), (error) => error.code === 'unavailable' && /管理者/u.test(error.message));
  await assert.rejects(run(409), (error) => error.code === 'unavailable' && /実行中/u.test(error.message));
  await assert.rejects(run(429), (error) => error.code === 'server' && /上限|混み合/u.test(error.message) && error.status === 429);
  await assert.rejects(run(504), (error) => error.code === 'timeout');
  await assert.rejects(run(500), (error) => error.code === 'server' && !/secret/u.test(error.message));
  await assert.rejects(run(400), (error) => error.code === 'validation');
  await assert.rejects(run(502), (error) => error.code === 'server' && /調査を開始できませんでした/u.test(error.message));
  await assert.rejects(run(418), (error) => error.code === 'unavailable');
  await assert.rejects(startSenpaiResearch(startOptions(async () => { throw new Error('boom'); })), (error) => error.code === 'server');
  await assert.rejects(startSenpaiResearch(startOptions(async () => undefined)), (error) => error.code === 'invalid_response');
});

test('start rejects malformed accepted responses', async () => {
  const bodies = [null, {}, { jobId: 'nope', status: 'queued' }, { jobId, status: 'running' }, { jobId, status: 'queued', pollAfterMs: 'soon' }];
  for (const body of bodies) {
    await assert.rejects(startSenpaiResearch(startOptions(async () => response(body, 202))), (error) => error.code === 'invalid_response', JSON.stringify(body));
  }
  await assert.rejects(startSenpaiResearch(startOptions(async () => ({ ok: true, status: 202, json: async () => { throw new Error('bad json'); } }))), (error) => error.code === 'invalid_response');
});

test('start honors cancellation and the request timeout', async () => {
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(startSenpaiResearch(startOptions(async () => response({}), { signal: controller.signal })), (error) => error.code === 'cancelled');

  const late = new AbortController();
  const pending = startSenpaiResearch(startOptions(async () => response({}), { getToken: () => new Promise(() => {}), signal: late.signal }));
  late.abort();
  await assert.rejects(pending, (error) => error.code === 'cancelled');

  await assert.rejects(startSenpaiResearch(startOptions(async () => response({}), { getToken: () => new Promise(() => {}), timeoutMs: 5 })), (error) => error.code === 'timeout');
  const aborted = new AbortController();
  await assert.rejects(startSenpaiResearch(startOptions(
    (_url, init) => new Promise((_resolve, reject) => init.signal.addEventListener('abort', () => reject(new Error('aborted')))),
    { timeoutMs: 5, signal: aborted.signal },
  )), (error) => error.code === 'timeout');
});

const statusOptions = (fetchImpl, overrides = {}) => ({
  baseUrl: BASE, getToken: async () => TOKEN, fetchImpl, jobId, afterSeq: 0, ...overrides,
});

test('results preserve explicit insufficiency and failed judgment stop reasons', () => {
  for (const stopReason of ['insufficient', 'judgment_failed', 'partial']) {
    const normalized = normalizeSenpaiResearchResult(result({ stopReason }));
    assert.equal(normalized.stopReason, stopReason);
  }
  assert.throws(() => normalizeSenpaiResearchResult(result({ stopReason: 'unknown' })));
});

test('status requests the job with afterSeq and returns validated steps', async () => {
  let request;
  const out = await getSenpaiResearchStatus(statusOptions(async (url, init) => {
    request = { url, init };
    return response({ jobId, status: 'running', steps: [step(1), step(2, { step: 'law_search', labelJa: '法令を確認中', status: 'done', endedAt: '2026-10-20T01:00:03.000Z' })], pollAfterMs: 2500, extra: 'ignored' });
  }, { afterSeq: 0 }));
  assert.equal(request.url, `${BASE}/rag/senpai/research/${jobId}?afterSeq=0`);
  assert.equal(request.init.method, 'GET');
  assert.equal(request.init.headers.Authorization, `Bearer ${TOKEN}`);
  assert.equal(out.status, 'running');
  assert.equal(out.pollAfterMs, 2500);
  assert.equal(out.steps.length, 2);
  assert.equal(out.steps[1].endedAt, '2026-10-20T01:00:03.000Z');
  assert.equal(Object.hasOwn(out, 'extra'), false);
  assert.equal(Object.hasOwn(out, 'result'), false);
});

test('status tolerates absent optional step fields and omits afterSeq when not given', async () => {
  let url;
  const out = await getSenpaiResearchStatus(statusOptions(async (requested) => {
    url = requested;
    return response({ jobId, status: 'queued', steps: [{ seq: 1, step: 'understand', labelJa: '質問を整理中', status: 'running', startedAt: '2026-10-20T01:00:00Z' }] });
  }, { afterSeq: undefined }));
  assert.equal(url, `${BASE}/rag/senpai/research/${jobId}`);
  assert.equal(out.steps[0].detailJa, undefined);
  assert.equal(out.steps[0].counts, undefined);
  assert.equal(out.steps[0].endedAt, null);
  assert.equal(out.pollAfterMs, undefined);
});

test('status rejects bad ids and bad afterSeq before fetching', async () => {
  const never = async () => { throw new Error('must not fetch'); };
  await assert.rejects(getSenpaiResearchStatus(statusOptions(never, { jobId: 'x' })), (error) => error.code === 'validation');
  for (const afterSeq of [-1, 1.5, '2', Number.NaN]) {
    await assert.rejects(getSenpaiResearchStatus(statusOptions(never, { afterSeq })), (error) => error.code === 'validation', String(afterSeq));
  }
});

test('status rejects unknown enum values and malformed bodies', async () => {
  const bad = [
    null,
    { jobId: 'other', status: 'running', steps: [] },
    { jobId, status: 'cancelled', steps: [] },
    { jobId, status: 'running' },
    { jobId, status: 'running', steps: [step(1, { step: 'mystery' })] },
    { jobId, status: 'running', steps: [step(1, { status: 'paused' })] },
    { jobId, status: 'running', steps: [step(0)] },
    { jobId, status: 'running', steps: [step(1, { labelJa: '' })] },
    { jobId, status: 'running', steps: [step(1, { startedAt: 'yesterday' })] },
    { jobId, status: 'running', steps: [step(1, { counts: 'many' })] },
    { jobId, status: 'running', steps: [step(1, { counts: { hits: -1 } })] },
    { jobId, status: 'running', steps: [step(1, { endedAt: 'late' })] },
    { jobId, status: 'running', steps: [], pollAfterMs: 'soon' },
    { jobId, status: 'completed', steps: [] },
    { jobId, status: 'completed', steps: [], result: result({ kind: 'guess' }) },
    { jobId, status: 'failed', steps: [] },
    { jobId, status: 'failed', steps: [], error: { code: 'Weird', message: 'x' } },
    { jobId, status: 'running', steps: Array.from({ length: 201 }, (_v, i) => step(i + 1)) },
  ];
  for (const body of bad) {
    await assert.rejects(getSenpaiResearchStatus(statusOptions(async () => response(body))), (error) => error.code === 'invalid_response', JSON.stringify(body)?.slice(0, 80));
  }
  await assert.rejects(getSenpaiResearchStatus(statusOptions(async () => ({ ok: true, status: 200, json: async () => { throw new Error('bad'); } }))), (error) => error.code === 'invalid_response');
});

test('status returns the result, a safe error message and debug when present', async () => {
  const done = await getSenpaiResearchStatus(statusOptions(async () => response({
    jobId, status: 'completed', steps: [], result: result(),
    debug: {
      understandingRaw: { intent: 'cause' }, queries: { tech: ['a'], law: ['b'], knowhow: 'c' },
      tools: [{ seq: 4, tool: 'tech_search', query: 'q', filters: { modelType: 'AXIEZ' }, hits: 30, selected: 6, topScores: [0.6, 0.5], ms: 1830 }],
      budget: { searchesUsed: 4, searchesMax: 6, modelCallsUsed: 3, modelCallsMax: 4, elapsedMs: 21500, elapsedMaxMs: 60000 },
    },
  })));
  assert.equal(done.result.kind, 'answer');
  assert.equal(done.debug.tools[0].ms, 1830);
  assert.equal(done.debug.budget.searchesMax, 6);

  const failed = await getSenpaiResearchStatus(statusOptions(async () => response({
    jobId, status: 'failed', steps: [], error: { code: 'Timeout', message: 'server detail' },
  })));
  assert.equal(failed.error.code, 'Timeout');
  assert.match(failed.error.message, /時間/u);
  assert.doesNotMatch(failed.error.message, /server detail/u);

  const malformedDebug = await getSenpaiResearchStatus(statusOptions(async () => response({
    jobId, status: 'completed', steps: [], result: result(), debug: { tools: 'oops' },
  })));
  assert.equal(malformedDebug.debug, undefined);
});

test('status maps HTTP failures; 404 is not retryable and 429 keeps its status', async () => {
  const run = (status) => getSenpaiResearchStatus(statusOptions(async () => response({}, status)));
  await assert.rejects(run(401), (error) => error.code === 'auth');
  await assert.rejects(run(403), (error) => error.code === 'unavailable');
  await assert.rejects(run(404), (error) => error.code === 'unavailable' && /見つかりません/u.test(error.message));
  await assert.rejects(run(429), (error) => error.code === 'server' && error.status === 429);
  await assert.rejects(run(502), (error) => error.code === 'server');
  await assert.rejects(run(504), (error) => error.code === 'timeout');
  await assert.rejects(run(418), (error) => error.code === 'unavailable');
});

test('stage usage and marginal evidence survive normalization without private text', async () => {
  const measurement = { stage: 'sufficiency', modelCalls: 1, ms: 45,
    usage: { inputTokens: 50, outputTokens: 10 }, usageMissing: true, completed: true,
    body: 'private body', query: 'private query' };
  const debug = { stages: [measurement], progress: [{ round: 1, action: 'retry_search',
    searches: 1, newCandidateItems: 2, newExposedEvidence: 0, evidenceValidity: 'unassessed', outcome: 'progress' }],
  stopDetail: 'no_exposed_progress', lastJudgment: 'insufficient', budget: { inputBytesMax: 120000 } };
  const normalized = await getSenpaiResearchStatus(statusOptions(async () => response({
    jobId, status: 'completed', steps: [], result: result(), debug,
  })));
  assert.equal(normalized.debug.stages[0].usage.inputTokens, 50);
  assert.equal(normalized.debug.stages[0].usageMissing, true);
  assert.equal(normalized.debug.progress[0].newExposedEvidence, 0);
  assert.equal(normalized.debug.stopDetail, 'no_exposed_progress');
  assert.equal(normalized.debug.lastJudgment, 'insufficient');
  assert.equal(normalized.debug.budget.inputBytesMax, 120000);
  assert.doesNotMatch(JSON.stringify(normalized.debug), /private/u);
  for (const broken of [{ ...debug, stages: [{ ms: -1 }] }, { ...debug, stopDetail: 'arbitrary text' }]) {
    const out = await getSenpaiResearchStatus(statusOptions(async () => response({
      jobId, status: 'completed', steps: [], result: result(), debug: broken,
    })));
    assert.equal(out.result.kind, 'answer');
    assert.equal(out.debug, undefined);
  }
});

test('normalizeSenpaiResearchResult checks every source group strictly', () => {
  const ok = normalizeSenpaiResearchResult(result());
  assert.equal(ok.sources.knowhow.used[0].modelFit, 'other_product');
  assert.deepEqual(ok.sources.knowhow.used[0].modelFitProducts, ['AXIEZ-LINKs']);
  assert.equal(ok.understanding.intent, 'cause');
  assert.equal(ok.stopReason, 'sufficient');

  const minimal = normalizeSenpaiResearchResult({ kind: 'not_found', sources: { tech: [], law: [], knowhow: { used: [], candidates: [] } } });
  assert.equal(minimal.answerMarkdown, '');
  assert.deepEqual(minimal.clarifyQuestions, []);
  assert.deepEqual(minimal.unverifiedRefs, []);
  assert.equal(minimal.understanding, undefined);

  const broken = [
    null, 'text', result({ answerMarkdown: '' }), result({ answerMarkdown: 5 }), result({ answerMarkdown: 'あ'.repeat(64001) }),
    result({ sources: null }),
    result({ sources: { tech: [{ ref: 'X1', title: 't' }], law: [], knowhow: { used: [], candidates: [] } } }),
    result({ sources: { tech: [{ ref: 'T1' }], law: [], knowhow: { used: [], candidates: [] } } }),
    result({ sources: { tech: [{ ref: 'T1', title: 't', pageNumber: 0 }], law: [], knowhow: { used: [], candidates: [] } } }),
    result({ sources: { tech: [], law: [{ ref: 'L1' }], knowhow: { used: [], candidates: [] } } }),
    result({ sources: { tech: [], law: [], knowhow: { used: [{ ref: 'K1', knowledgeId: 'KH-1', cardVersion: 1, title: 't', status: 'archived' }], candidates: [] } } }),
    result({ sources: { tech: [], law: [], knowhow: { used: [{ ref: 'K1', knowledgeId: 'KH-1', cardVersion: 1, title: 't', status: 'draft', modelFit: 'sort_of' }], candidates: [] } } }),
    result({ sources: { tech: [], law: [], knowhow: { used: [], candidates: [{ knowledgeId: 'KH-1', cardVersion: 0, title: 't' }] } } }),
    result({ sources: { tech: [], law: [], knowhow: { used: 'none', candidates: [] } } }),
    result({ understanding: { intent: 'whatever' } }),
    result({ understanding: { lawRelevant: 'yes' } }),
    result({ stopReason: 'gave_up' }),
    result({ unverifiedRefs: [1] }),
    result({ clarifyQuestions: [1] }),
  ];
  for (const value of broken) {
    assert.throws(() => normalizeSenpaiResearchResult(value), (error) => error.code === 'invalid_response', JSON.stringify(value)?.slice(0, 90));
  }
});

test('source hrefs reuse the document route and only allow e-Gov law links', () => {
  const tech = techSourceHref({ sourceUri: 's3://kb-bucket/docs/manual.pdf', pageNumber: 12 });
  assert.equal(tech, `/doc?uri=${encodeURIComponent('s3://kb-bucket/docs/manual.pdf')}#page=12`);
  assert.equal(techSourceHref({ sourceUri: 'https://evil.example.test/x' }), undefined);
  assert.equal(techSourceHref({}), undefined);
  assert.equal(lawSourceHref({ sourceUrl: 'https://laws.e-gov.go.jp/law/325AC0000000201' }), 'https://laws.e-gov.go.jp/law/325AC0000000201');
  assert.equal(lawSourceHref({ sourceUrl: 'https://laws.e-gov.go.jp/law/325AC0000000201/20250401_000AC0000000001#Mp-At_34' }), 'https://laws.e-gov.go.jp/law/325AC0000000201/20250401_000AC0000000001#Mp-At_34');
  assert.equal(lawSourceHref({ sourceUrl: 'https://laws.e-gov.go.jp/第三十五条' }), `https://laws.e-gov.go.jp/${encodeURI('第三十五条')}`);
  for (const sourceUrl of ['http://laws.e-gov.go.jp/law/325AC0000000201', 'https://evil.example.test/law/325AC0000000201', 'https://laws.e-gov.go.jp.evil.test/law/1', 'https://user:pw@laws.e-gov.go.jp/law/325AC0000000201', 'https://laws.e-gov.go.jp:8443/law/1', 'javascript:alert(1)', 'not a url', undefined]) {
    assert.equal(lawSourceHref({ sourceUrl }), undefined, String(sourceUrl));
  }
});

test('mergeResearchSteps is append-only, idempotent and ignores older or duplicate seqs', () => {
  const first = Object.freeze([step(1), step(2)]);
  const merged = mergeResearchSteps(first, [step(2, { status: 'done' }), step(3), step(1)]);
  assert.deepEqual(merged.map((item) => item.seq), [1, 2, 3]);
  assert.equal(merged[1].status, 'running');
  assert.equal(first.length, 2);
  assert.deepEqual(mergeResearchSteps(merged, merged), merged);
  assert.deepEqual(mergeResearchSteps(merged, []), merged);
  assert.deepEqual(mergeResearchSteps([], [step(5), step(4)]).map((item) => item.seq), [4, 5]);
  assert.deepEqual(mergeResearchSteps(undefined, undefined), []);
});

test('buildTimelineRows folds a finished event into its running row', () => {
  const rows = buildTimelineRows([
    step(1, { step: 'understand', labelJa: '質問を整理中', detailJa: undefined }),
    step(2, { step: 'understand', labelJa: '質問を整理中', status: 'done', endedAt: '2026-10-20T01:00:02.000Z' }),
    step(3, { step: 'tech_search' }),
    step(4, { step: 'law_search', labelJa: '法令を確認中' }),
    step(5, { step: 'law_search', labelJa: '法令を確認中', status: 'skipped', detailJa: '法令に関係しない質問' }),
    step(6, { step: 'clarify', labelJa: '確認が必要な点を整理中', status: 'failed' }),
  ]);
  assert.deepEqual(rows.map((row) => [row.step, row.status]), [
    ['understand', 'done'], ['tech_search', 'running'], ['law_search', 'skipped'], ['clarify', 'failed'],
  ]);
  assert.equal(rows[2].detailJa, '法令に関係しない質問');
  assert.equal(rows[0].endedAt, '2026-10-20T01:00:02.000Z');
  assert.deepEqual(buildTimelineRows(undefined), []);
});

// ---- polling runner ----

function createClock() {
  let nowMs = 0;
  let seq = 0;
  const timers = new Map();
  return {
    now: () => nowMs,
    setTimer: (fn, delayMs) => { const id = ++seq; timers.set(id, { at: nowMs + delayMs, fn }); return id; },
    clearTimer: (id) => timers.delete(id),
    pending: () => timers.size,
    async advance(ms) {
      const end = nowMs + ms;
      for (;;) {
        const next = [...timers.entries()].sort((a, b) => a[1].at - b[1].at)[0];
        if (!next || next[1].at > end) break;
        timers.delete(next[0]);
        nowMs = next[1].at;
        next[1].fn();
        await new Promise((resolve) => setImmediate(resolve));
      }
      nowMs = end;
    },
  };
}

function scripted(responses) {
  const calls = [];
  const fetchImpl = async (url, init) => {
    calls.push({ url, method: init.method });
    if (init.method === 'POST') return response({ jobId, status: 'queued', pollAfterMs: 1500 }, 202);
    const next = responses.shift();
    if (typeof next === 'function') return next();
    return response(next.body, next.status ?? 200);
  };
  return { fetchImpl, calls };
}

const runOptions = (clock, fetchImpl, overrides = {}) => ({
  ...startOptions(fetchImpl), now: clock.now, setTimer: clock.setTimer, clearTimer: clock.clearTimer, ...overrides,
});

test('runner polls with a growing afterSeq, merges steps and resolves on completion', async () => {
  const clock = createClock();
  const { fetchImpl, calls } = scripted([
    { body: { jobId, status: 'running', steps: [step(1), step(2)], pollAfterMs: 3000 } },
    { body: { jobId, status: 'running', steps: [step(2), step(3)], pollAfterMs: 3000 } },
    { body: { jobId, status: 'completed', steps: [step(4, { status: 'done' })], result: result() } },
  ]);
  const updates = [];
  const done = runSenpaiResearch(runOptions(clock, fetchImpl, { onUpdate: (update) => updates.push(update) }));
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(calls.length, 1);
  await clock.advance(2000);
  await clock.advance(3000);
  await clock.advance(3000);
  const final = await done;
  assert.equal(final.status, 'completed');
  assert.deepEqual(final.steps.map((item) => item.seq), [1, 2, 3, 4]);
  assert.equal(final.result.kind, 'answer');
  assert.deepEqual(calls.filter((call) => call.method === 'GET').map((call) => new URL(call.url).searchParams.get('afterSeq')), ['0', '2', '3']);
  assert.equal(updates[0].status, 'queued');
  assert.equal(updates[0].jobId, jobId);
  assert.equal(updates.at(-1).status, 'completed');
  assert.equal(clock.pending(), 0);
});

test('runner resolves a failed job with its error', async () => {
  const clock = createClock();
  const { fetchImpl } = scripted([{ body: { jobId, status: 'failed', steps: [step(1, { status: 'failed' })], error: { code: 'BudgetExceeded', message: 'x' } } }]);
  const done = runSenpaiResearch(runOptions(clock, fetchImpl));
  await new Promise((resolve) => setImmediate(resolve));
  await clock.advance(2000);
  const final = await done;
  assert.equal(final.status, 'failed');
  assert.equal(final.error.code, 'BudgetExceeded');
});

test('runner retries transient errors with backoff and stops on fatal ones', async () => {
  const clock = createClock();
  const { fetchImpl, calls } = scripted([
    { body: {}, status: 500 },
    { body: { jobId, status: 'completed', steps: [], result: result() } },
  ]);
  const done = runSenpaiResearch(runOptions(clock, fetchImpl));
  await new Promise((resolve) => setImmediate(resolve));
  await clock.advance(2000);
  assert.equal(calls.filter((call) => call.method === 'GET').length, 1);
  await clock.advance(3999);
  assert.equal(calls.filter((call) => call.method === 'GET').length, 1);
  await clock.advance(1);
  assert.equal((await done).status, 'completed');

  const fatalClock = createClock();
  const fatal = scripted([{ body: {}, status: 404 }, { body: { jobId, status: 'running', steps: [] } }]);
  const rejected = runSenpaiResearch(runOptions(fatalClock, fatal.fetchImpl));
  rejected.catch(() => {});
  await new Promise((resolve) => setImmediate(resolve));
  await fatalClock.advance(2000);
  await assert.rejects(rejected, (error) => error.code === 'unavailable');
  await fatalClock.advance(60000);
  assert.equal(fatal.calls.filter((call) => call.method === 'GET').length, 1);
  assert.equal(fatalClock.pending(), 0);
});

test('runner stops polling when aborted and reports cancellation', async () => {
  const clock = createClock();
  const { fetchImpl, calls } = scripted([{ body: { jobId, status: 'running', steps: [step(1)] } }, { body: { jobId, status: 'running', steps: [] } }]);
  const controller = new AbortController();
  const updates = [];
  const done = runSenpaiResearch(runOptions(clock, fetchImpl, { signal: controller.signal, onUpdate: (update) => updates.push(update) }));
  done.catch(() => {});
  await new Promise((resolve) => setImmediate(resolve));
  await clock.advance(2000);
  controller.abort();
  await assert.rejects(done, (error) => error.code === 'cancelled');
  await clock.advance(60000);
  assert.equal(calls.filter((call) => call.method === 'GET').length, 1);
  assert.equal(clock.pending(), 0);
  assert.ok(updates.length >= 1);

  const early = new AbortController();
  early.abort();
  await assert.rejects(runSenpaiResearch(runOptions(clock, fetchImpl, { signal: early.signal })), (error) => error.code === 'cancelled');
});

test('runner gives up with a timeout after the polling window', async () => {
  const clock = createClock();
  const { fetchImpl } = scripted(Array.from({ length: 100 }, () => ({ body: { jobId, status: 'running', steps: [] } })));
  const done = runSenpaiResearch(runOptions(clock, fetchImpl));
  done.catch(() => {});
  await new Promise((resolve) => setImmediate(resolve));
  await clock.advance(400000);
  await assert.rejects(done, (error) => error.code === 'timeout' && /時間/u.test(error.message));
  assert.equal(clock.pending(), 0);
});

test('runner waits and retries every 5s while the previous job is still running (409), then gives up with the 409 error', async () => {
  const clock = createClock();
  let posts = 0;
  let waiting = 0;
  const done = runSenpaiResearch(runOptions(clock, async (_url, init) => {
    if (init.method === 'POST') posts += 1;
    return response({}, 409);
  }, { onWaiting: () => { waiting += 1; } }));
  done.catch(() => {});
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(posts, 1);
  assert.equal(waiting, 1);
  await clock.advance(4999);
  assert.equal(posts, 1);
  await clock.advance(1);
  assert.equal(posts, 2);
  await clock.advance(145000);
  await assert.rejects(done, (error) => error.code === 'unavailable' && error.status === 409 && /実行中/u.test(error.message));
  assert.ok(posts >= 30 && posts <= 32, `posts=${posts}`);
  assert.equal(clock.pending(), 0);
});

test('runner starts as soon as the 409 clears and then polls normally', async () => {
  const clock = createClock();
  let posts = 0;
  const { fetchImpl: inner } = scripted([{ body: { jobId, status: 'completed', steps: [], result: result() } }]);
  const done = runSenpaiResearch(runOptions(clock, async (url, init) => {
    if (init.method === 'POST') { posts += 1; if (posts < 3) return response({}, 409); }
    return inner(url, init);
  }));
  await new Promise((resolve) => setImmediate(resolve));
  await clock.advance(10000);
  await clock.advance(2000);
  assert.equal((await done).status, 'completed');
  assert.equal(posts, 3);
});

test('runner stops waiting for the previous job when aborted', async () => {
  const clock = createClock();
  const controller = new AbortController();
  let posts = 0;
  const done = runSenpaiResearch(runOptions(clock, async () => { posts += 1; return response({}, 409); }, { signal: controller.signal }));
  done.catch(() => {});
  await new Promise((resolve) => setImmediate(resolve));
  controller.abort();
  await assert.rejects(done, (error) => error.code === 'cancelled');
  await clock.advance(60000);
  assert.equal(posts, 1);
  assert.equal(clock.pending(), 0);
});

test('runner does not wait on other start failures', async () => {
  const clock = createClock();
  await assert.rejects(runSenpaiResearch(runOptions(clock, async () => response({}, 429))), (error) => error.code === 'server');
  assert.equal(clock.pending(), 0);
});

test('runner pauses polling while the tab is hidden and checks again once it is visible', async () => {
  const clock = createClock();
  const listeners = new Set();
  const doc = {
    visibilityState: 'visible',
    addEventListener: (type, fn) => { if (type === 'visibilitychange') listeners.add(fn); },
    removeEventListener: (type, fn) => { if (type === 'visibilitychange') listeners.delete(fn); },
  };
  const { fetchImpl, calls } = scripted([
    { body: { jobId, status: 'running', steps: [step(1)] } },
    { body: { jobId, status: 'completed', steps: [], result: result() } },
  ]);
  const done = runSenpaiResearch(runOptions(clock, fetchImpl, { visibility: doc }));
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(listeners.size, 1);
  await clock.advance(2000);
  const gets = () => calls.filter((call) => call.method === 'GET').length;
  assert.equal(gets(), 1);
  doc.visibilityState = 'hidden';
  listeners.forEach((fn) => fn());
  await clock.advance(30000);
  assert.equal(gets(), 1);
  doc.visibilityState = 'visible';
  listeners.forEach((fn) => fn());
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal((await done).status, 'completed');
  assert.equal(gets(), 2);
  assert.equal(listeners.size, 0);
});

test('result.warnings is optional, bounded and strictly a list of non-empty strings', () => {
  const base = { kind: 'not_found', sources: { tech: [], law: [], knowhow: { used: [], candidates: [] } } };
  assert.equal('warnings' in normalizeSenpaiResearchResult(base), false);
  assert.deepEqual(normalizeSenpaiResearchResult({ ...base, warnings: [] }).warnings, []);
  assert.deepEqual(normalizeSenpaiResearchResult({ ...base, warnings: ['法令の検索に失敗したため確認できていません'] }).warnings, ['法令の検索に失敗したため確認できていません']);
  for (const bad of [null, 'text', {}, [''], ['  '], [1], ['x'.repeat(201)], Array.from({ length: 11 }, () => '注意')]) {
    assert.throws(() => normalizeSenpaiResearchResult({ ...base, warnings: bad }), (error) => error.code === 'invalid_response', JSON.stringify(bad)?.slice(0, 40));
  }
});
