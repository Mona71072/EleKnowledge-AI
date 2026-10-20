import assert from 'node:assert/strict';
import test from 'node:test';
import { createSenpaiChat } from '../src/lib/knowledge-senpai-chat.mjs';
import { KnowledgeResearchError } from '../src/lib/knowledge-research.mjs';

const UUID_A = '10000000-0000-4000-8000-000000000001';
const jobId = '30000000-0000-4000-8000-000000000001';

function ids() {
  let count = 0;
  return () => `a0000000-0000-4000-8000-${String(++count).padStart(12, '0')}`;
}

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}

const step = (seq, overrides = {}) => ({
  seq, step: 'tech_search', labelJa: '技術資料を検索中', status: 'running',
  startedAt: '2026-10-20T01:00:00.000Z', endedAt: null, ...overrides,
});

function result(overrides = {}) {
  return {
    kind: 'answer', answerMarkdown: '結論です [T1]', clarifyQuestions: [],
    sources: { tech: [{ ref: 'T1', title: '手順書' }], law: [], knowhow: { used: [], candidates: [] } },
    unverifiedRefs: [], ...overrides,
  };
}

function setup(researchSource, options = {}) {
  const snapshots = [];
  let tick = 1_000;
  const chat = createSenpaiChat({
    querySource: async () => { throw new Error('two-lane search must not run in research mode'); },
    researchSource,
    createId: ids(),
    now: () => (tick += 1_000),
    onChange: (snapshot) => snapshots.push(snapshot),
    ...options,
  });
  return { chat, snapshots };
}

test('a research turn starts a job instead of the two lanes and tracks steps to completion', async () => {
  const gate = deferred();
  const requests = [];
  const { chat, snapshots } = setup(async (request) => {
    requests.push(request);
    request.onUpdate({ jobId, status: 'queued', steps: [] });
    request.onUpdate({ jobId, status: 'running', steps: [step(1)] });
    request.onUpdate({ jobId, status: 'running', steps: [step(1), step(2, { step: 'law_search' })] });
    await gate.promise;
    return { jobId, status: 'completed', steps: [step(1), step(2, { step: 'law_search' }), step(3, { step: 'verify', status: 'done' })], result: result(), debug: { budget: { searchesUsed: 2 } } };
  });

  const sending = chat.send('  ドアの異音  ', { modelType: 'AXIEZ-LINKs' });
  await new Promise((resolve) => setImmediate(resolve));
  let turn = chat.getSnapshot().turns[0];
  assert.equal(chat.getSnapshot().running, true);
  assert.equal(turn.query, 'ドアの異音');
  assert.equal(turn.modelType, 'AXIEZ-LINKs');
  assert.equal(turn.research.status, 'running');
  assert.deepEqual(turn.research.steps.map((item) => item.seq), [1, 2]);
  assert.equal(turn.research.jobId, jobId);
  assert.equal(typeof turn.research.startedAt, 'number');
  assert.equal(turn.research.result, undefined);
  assert.equal(turn.normal.status, 'paused');
  assert.equal(turn.law.status, 'paused');

  gate.resolve();
  await sending;
  turn = chat.getSnapshot().turns[0];
  assert.equal(chat.getSnapshot().running, false);
  assert.equal(turn.research.status, 'completed');
  assert.deepEqual(turn.research.steps.map((item) => item.seq), [1, 2, 3]);
  assert.equal(turn.research.result.kind, 'answer');
  assert.equal(turn.research.debug.budget.searchesUsed, 2);
  assert.ok(turn.research.endedAt > turn.research.startedAt);
  assert.throws(() => { turn.research.steps.push(1); }, TypeError);

  const [request] = requests;
  assert.equal(request.question, 'ドアの異音');
  assert.equal(request.modelType, 'AXIEZ-LINKs');
  assert.equal(request.senpaiConversationId, chat.getSnapshot().conversationId);
  assert.equal(request.senpaiTurnId, turn.senpaiTurnId);
  assert.match(request.clientRequestId, /^[0-9a-f-]{36}$/u);
  assert.notEqual(request.clientRequestId, request.senpaiTurnId);
  assert.ok(request.signal instanceof AbortSignal);
  assert.ok(snapshots.length >= 4);
  assert.deepEqual(snapshots.map((snapshot) => snapshot.turns.at(-1)?.research?.status).filter(Boolean).slice(0, 2), ['queued', 'queued']);
});

test('modelType is omitted from the job request when none is chosen', async () => {
  let request;
  const { chat } = setup(async (value) => { request = value; return { jobId, status: 'completed', steps: [], result: result() }; });
  await chat.send('質問');
  assert.equal(Object.hasOwn(request, 'modelType'), false);
});

test('older seqs and a status regression after completion are ignored', async () => {
  const { chat } = setup(async (request) => {
    request.onUpdate({ jobId, status: 'running', steps: [step(2)] });
    request.onUpdate({ jobId, status: 'running', steps: [step(1), step(2, { status: 'done' })] });
    return { jobId, status: 'completed', steps: [step(2), step(3, { status: 'done' })], result: result() };
  });
  await chat.send('質問');
  const research = chat.getSnapshot().turns[0].research;
  assert.deepEqual(research.steps.map((item) => [item.seq, item.status]), [[1, 'running'], [2, 'running'], [3, 'done']]);
  assert.equal(research.status, 'completed');
});

test('a failed job keeps its steps and shows the safe error', async () => {
  const { chat } = setup(async () => ({
    jobId, status: 'failed', steps: [step(1, { status: 'failed' })],
    error: { code: 'BudgetExceeded', message: '調査の上限に達しました' },
  }));
  await chat.send('質問');
  const research = chat.getSnapshot().turns[0].research;
  assert.equal(research.status, 'failed');
  assert.equal(research.error.code, 'BudgetExceeded');
  assert.equal(research.steps.length, 1);
  assert.equal(chat.getSnapshot().running, false);
});

test('client-side failures become a failed research with a safe message', async () => {
  const known = setup(async () => { throw new KnowledgeResearchError('unavailable', 'すでに調査を実行中です'); });
  await known.chat.send('質問');
  assert.equal(known.chat.getSnapshot().turns[0].research.status, 'failed');
  assert.equal(known.chat.getSnapshot().turns[0].research.error.message, 'すでに調査を実行中です');

  const unknown = setup(async () => { throw new Error('secret internals'); });
  await unknown.chat.send('質問');
  const error = unknown.chat.getSnapshot().turns[0].research.error;
  assert.doesNotMatch(error.message, /secret/u);
  assert.match(error.message, /調査に失敗/u);

  const incomplete = setup(async () => ({ jobId, status: 'completed', steps: [] }));
  await incomplete.chat.send('質問');
  assert.equal(incomplete.chat.getSnapshot().turns[0].research.status, 'failed');

  const cancelledByLib = setup(async () => { throw new KnowledgeResearchError('cancelled', '調査の確認を中止しました'); });
  await cancelledByLib.chat.send('質問');
  assert.equal(cancelledByLib.chat.getSnapshot().turns[0].research.status, 'cancelled');
});

test('cancel stops waiting, keeps collected steps and allows the next question', async () => {
  const gate = deferred();
  let signal;
  let calls = 0;
  const { chat } = setup(async (request) => {
    calls += 1;
    if (calls === 2) return { jobId, status: 'completed', steps: [], result: result() };
    signal = request.signal;
    request.onUpdate({ jobId, status: 'running', steps: [step(1)] });
    await gate.promise;
    request.onUpdate({ jobId, status: 'running', steps: [step(2)] });
    return { jobId, status: 'completed', steps: [step(2)], result: result() };
  });
  const sending = chat.send('最初の質問');
  await new Promise((resolve) => setImmediate(resolve));
  await assert.rejects(chat.send('割り込み'), (error) => error.code === 'validation');
  chat.cancel();
  assert.equal(signal.aborted, true);
  let research = chat.getSnapshot().turns[0].research;
  assert.equal(research.status, 'cancelled');
  assert.equal(research.steps.length, 1);
  assert.equal(chat.getSnapshot().running, false);

  gate.resolve();
  await sending;
  research = chat.getSnapshot().turns[0].research;
  assert.equal(research.status, 'cancelled');
  assert.equal(research.result, undefined);
  assert.equal(research.steps.length, 1);

  await chat.send('次の質問');
  assert.equal(chat.getSnapshot().turns.length, 2);
  assert.equal(chat.getSnapshot().turns[1].research.status, 'completed');
  chat.cancel();
});

test('reset and dispose abort the job and drop late results', async () => {
  const gate = deferred();
  const signals = [];
  const { chat } = setup(async (request) => {
    signals.push(request.signal);
    await gate.promise;
    request.onUpdate({ jobId, status: 'running', steps: [step(1)] });
    return { jobId, status: 'completed', steps: [step(1)], result: result() };
  });
  const sending = chat.send('質問');
  await new Promise((resolve) => setImmediate(resolve));
  chat.reset();
  assert.equal(signals[0].aborted, true);
  assert.deepEqual(chat.getSnapshot().turns, []);
  gate.resolve();
  await sending;
  assert.deepEqual(chat.getSnapshot().turns, []);
  assert.equal(chat.getSnapshot().running, false);

  const gate2 = deferred();
  const second = setup(async (request) => { signals.push(request.signal); await gate2.promise; return { jobId, status: 'completed', steps: [], result: result() }; });
  const pending = second.chat.send('質問');
  await new Promise((resolve) => setImmediate(resolve));
  const before = second.snapshots.length;
  second.chat.dispose();
  assert.equal(signals.at(-1).aborted, true);
  gate2.resolve();
  await pending;
  assert.equal(second.snapshots.length, before);
});

test('restore keeps a saved research answer without steps and lets research continue', async () => {
  const savedTurn = '20000000-0000-4000-8000-000000000001';
  let request;
  const { chat } = setup(async (value) => { request = value; return { jobId, status: 'completed', steps: [], result: result({ answerMarkdown: '続き [T1]' }) }; });
  chat.restore({
    conversationId: UUID_A, complete: true,
    turns: [{
      id: 1, senpaiTurnId: savedTurn, query: '保存された質問', modelType: 'AXIEZ',
      research: { status: 'completed', steps: [{ ignored: true }], result: result() },
      normal: { status: 'paused', message: 'x' }, law: { status: 'paused', message: 'y' },
    }],
  });
  const turn = chat.getSnapshot().turns[0];
  assert.equal(turn.research.status, 'completed');
  assert.deepEqual(turn.research.steps, []);
  assert.equal(turn.research.result.answerMarkdown, '結論です [T1]');
  assert.equal(turn.modelType, 'AXIEZ');

  await chat.send('続きの質問');
  assert.equal(request.senpaiConversationId, UUID_A);
  assert.equal(chat.getSnapshot().turns.length, 2);
  assert.equal(chat.getSnapshot().turns[1].id, 2);
});

test('restore validates saved research and still restores two-lane turns', () => {
  const savedTurn = '20000000-0000-4000-8000-000000000001';
  const { chat } = setup(async () => ({}));
  const base = { conversationId: UUID_A, complete: true };
  const research = (value) => ({ id: 1, senpaiTurnId: savedTurn, query: 'q', research: value });
  for (const value of [{ status: 'running', steps: [], result: result() }, { status: 'completed', steps: [], result: { kind: 'guess' } }, { status: 'completed', steps: [] }, 'nope']) {
    assert.throws(() => chat.restore({ ...base, turns: [research(value)] }), (error) => error.code === 'validation', JSON.stringify(value));
  }

  const answer = (mode) => ({
    mode, query: '二レーンの質問', content: 'a', responseType: 'pages', sessionId: `${mode}-session`, messageId: `${mode}-m`,
    receivedAt: '2026-10-20T00:00:00.000Z', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [],
    senpaiConversationId: UUID_A, senpaiTurnId: savedTurn,
  });
  chat.restore({
    ...base,
    turns: [
      { id: 1, senpaiTurnId: savedTurn, query: '二レーンの質問', normal: { status: 'success', answer: answer('normal') }, law: { status: 'success', answer: answer('law') } },
      { id: 2, senpaiTurnId: '20000000-0000-4000-8000-000000000002', query: '調査の質問', research: { status: 'completed', result: result() } },
    ],
  });
  const turns = chat.getSnapshot().turns;
  assert.equal(turns[0].normal.status, 'success');
  assert.equal(turns[0].research, undefined);
  assert.equal(turns[1].research.status, 'completed');
});

test('synthesis is not available for research turns', async () => {
  const { chat } = setup(async () => ({ jobId, status: 'completed', steps: [], result: result() }), { synthesisSource: async () => ({}) });
  await chat.send('質問');
  await assert.rejects(chat.synthesize(1), (error) => error.code === 'validation');
});

test('without a research source the controller keeps using the two lanes', async () => {
  const modes = [];
  const chat = createSenpaiChat({
    querySource: async (request) => {
      modes.push(request.mode);
      return {
        mode: request.mode, sessionId: `${request.mode}-s`, messageId: `${request.mode}-m`, query: request.query, content: 'x',
        responseType: 'pages', receivedAt: '2026-10-20T00:00:00.000Z', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [],
      };
    },
    createId: ids(),
  });
  await chat.send('質問');
  assert.deepEqual(modes.sort(), ['law', 'normal']);
  assert.equal(chat.getSnapshot().turns[0].research, undefined);
});

import { createFieldReportDraft, buildFieldReportPayload, fieldReportCards } from '../src/lib/knowledge-senpai-field-report.mjs';

const clarifyResult = () => result({ kind: 'clarify', answerMarkdown: '', clarifyQuestions: ['機種は何ですか'] });

test('an answer right after a clarify result is sent together with the original question', async () => {
  const questions = [];
  const { chat } = setup(async (request) => {
    questions.push(request.question);
    return { jobId, status: 'completed', steps: [], result: questions.length === 1 ? clarifyResult() : result() };
  });
  await chat.send('ドアの異音', { modelType: 'AXIEZ' });
  await chat.send('AXIEZです');
  assert.deepEqual(questions, ['ドアの異音', 'ドアの異音\n補足: AXIEZです']);
  const turn = chat.getSnapshot().turns[1];
  assert.equal(turn.query, 'ドアの異音\n補足: AXIEZです');
  assert.equal(turn.supplement, 'AXIEZです');
  assert.equal(turn.supplementOf, 'ドアの異音');
  assert.equal(chat.getSnapshot().turns[0].supplement, undefined);

  await chat.send('次の話題');
  assert.equal(questions[2], '次の話題');
  assert.equal(chat.getSnapshot().turns[2].supplement, undefined);
});

test('a fresh send, a failed turn and a long reply never get composed wrongly', async () => {
  const questions = [];
  let kind = 'clarify';
  const { chat } = setup(async (request) => {
    questions.push(request.question);
    return kind === 'fail' ? { jobId, status: 'failed', steps: [], error: { code: 'Internal', message: 'x' } }
      : { jobId, status: 'completed', steps: [], result: kind === 'clarify' ? clarifyResult() : result() };
  });
  await chat.send('元の質問');
  await chat.send('元の質問', { modelType: 'NEXCUBE', fresh: true });
  assert.equal(questions[1], '元の質問');
  assert.equal(chat.getSnapshot().turns[1].supplement, undefined);
  assert.equal(chat.getSnapshot().turns[1].modelType, 'NEXCUBE');

  kind = 'fail';
  await chat.send('失敗する質問', { fresh: true });
  kind = 'answer';
  await chat.send('もう一度', { fresh: true });
  assert.equal(questions.at(-1), 'もう一度');

  kind = 'clarify';
  const long = setup(async (request) => { questions.push(request.question); return { jobId, status: 'completed', steps: [], result: clarifyResult() }; });
  await long.chat.send('あ'.repeat(1990));
  await long.chat.send('い'.repeat(100));
  assert.equal(Array.from(questions.at(-1)).length, 2000);
});

test('field reports for a research turn use the knowhow cards of the result', () => {
  const research = {
    status: 'completed', steps: [],
    result: result({ sources: { tech: [], law: [], knowhow: {
      used: [{ ref: 'K1', knowledgeId: 'KH-1', cardVersion: 2, title: '使った', status: 'draft' }],
      candidates: [{ knowledgeId: 'KH-2', cardVersion: 1, title: '渡しただけ' }, { knowledgeId: 'KH-1', cardVersion: 2, title: '重複' }],
    } } }),
  };
  const turn = { id: 1, senpaiTurnId: '20000000-0000-4000-8000-000000000001', query: 'q', modelType: 'AXIEZ', research, normal: { status: 'paused' }, law: { status: 'paused' } };
  assert.deepEqual(fieldReportCards(turn), [
    { knowledgeId: 'KH-1', cardVersion: 2, title: '使った' }, { knowledgeId: 'KH-2', cardVersion: 1, title: '渡しただけ' },
  ]);
  const draft = { ...createFieldReportDraft(turn), finding: '分かったこと', reactions: { 'KH-1': 'matched', 'KH-2': '' } };
  assert.equal(draft.modelType, 'AXIEZ');
  const payload = buildFieldReportPayload({ conversationId: UUID_A, turn, draft });
  assert.equal(payload.senpaiTurnId, turn.senpaiTurnId);
  assert.deepEqual(payload.cardReactions, [{ knowledgeId: 'KH-1', cardVersion: 2, reaction: 'matched' }]);
  assert.deepEqual(fieldReportCards({ ...turn, research: { status: 'running', steps: [] } }), []);
});
