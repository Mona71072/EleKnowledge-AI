import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';
import { createSenpaiChat } from '../src/lib/knowledge-senpai-chat.mjs';
import { KnowledgeResearchError } from '../src/lib/knowledge-research.mjs';
import { readSenpaiConversation } from '../src/lib/knowledge-senpai-history.mjs';
import {
  buildTimelineRows, getSenpaiResearchStatus, mergeResearchSteps, startSenpaiResearch,
} from '../src/lib/knowledge-senpai-research.mjs';

// バックエンドが自分のコードから生成して commit した実際の応答サンプルを、本物のクライアントに通す。
const require = createRequire(import.meta.url);
const DIR = new URL('../../tests/fixtures/knowledge/senpai-research-samples/', import.meta.url);
const sample = (name) => JSON.parse(readFileSync(new URL(name, DIR), 'utf8'));
const asResponse = ({ statusCode, body }) => ({ ok: statusCode >= 200 && statusCode < 300, status: statusCode, json: async () => body });

const BASE = 'https://api.example.test/dev';
const JOB = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const CONVERSATION = '11111111-1111-4111-8111-111111111111';
const TURN = '22222222-2222-4222-8222-222222222222';
const JAPANESE = /[ぁ-んァ-ヶ一-龥]/u;

const client = (fixture) => ({ baseUrl: BASE, getToken: async () => 'token', fetchImpl: async () => asResponse(fixture) });
const status = (name, afterSeq) => getSenpaiResearchStatus({ ...client(sample(name)), jobId: JOB, afterSeq });

function loadTsx(path) {
  const filename = new URL(path, import.meta.url);
  const { outputText } = ts.transpileModule(readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true }, fileName: filename.pathname,
  });
  const compiled = { exports: {} };
  const localRequire = (name) => {
    if (/^\.\/Senpai/u.test(name)) return loadTsx(`../src/components/knowledge/${name.slice(2)}.tsx`);
    if (name === './kb-model-types.generated.mjs') return require('../src/data/kb-model-types.generated.mjs');
    if (name === '@/data/kbModelTypes') return loadTsx('../src/data/kbModelTypes.ts');
    if (name.startsWith('@/lib/')) return require(`../src/lib/${name.slice(6)}`);
    return require(name);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiled, compiled.exports);
  return compiled.exports;
}
const { SenpaiResearchAnswer } = loadTsx('../src/components/knowledge/SenpaiResearchAnswer.tsx');
const render = (research, props = {}) => renderToStaticMarkup(createElement(SenpaiResearchAnswer, {
  research, anchorPrefix: 'senpai-turn-1', developerView: false, ...props,
}));
const unique = (steps) => new Set(steps.map((item) => `${item.step}|${item.startedAt}`)).size;

test('POST 202 sample is accepted', async () => {
  const out = await startSenpaiResearch({
    ...client(sample('post-accepted.json')), question: '質問', senpaiConversationId: CONVERSATION, senpaiTurnId: TURN,
    clientRequestId: '33333333-3333-4333-8333-333333333333',
  });
  assert.deepEqual(out, { jobId: JOB, status: 'queued', pollAfterMs: 1500 });
});

test('running samples parse, fold to one row per (step, startedAt) and merge after a seq', async () => {
  const running = await status('status-running.json', 0);
  assert.equal(running.status, 'running');
  assert.equal(running.pollAfterMs, 1500);
  const rows = buildTimelineRows(running.steps);
  assert.equal(rows.length, unique(running.steps));
  assert.equal(rows.filter((row) => row.step === 'sufficiency').length, 2);
  assert.deepEqual(rows.find((row) => row.step === 'law_search').status, 'skipped');
  const retry = rows.find((row) => row.step === 'retry_search');
  assert.equal(retry.status, 'done');
  assert.equal(retry.detailJa, '『ドア 調整 異音』で再検索');
  assert.equal(rows.at(-1).status, 'running');
  assert.equal(rows.filter((row) => row.status === 'running').length, 1);

  const after = await status('status-running-after-seq.json', 3);
  assert.ok(after.steps.every((item) => item.seq > 3));
  const merged = mergeResearchSteps(running.steps.slice(0, 5), after.steps);
  assert.deepEqual(merged.map((item) => item.seq), [...new Set([...running.steps.slice(0, 5), ...after.steps].map((item) => item.seq))].sort((a, b) => a - b));
});

test('two retry_search runs stay two rows, and a lone running event stays running', () => {
  const event = (seq, startedAt, state) => ({ seq, step: 'retry_search', labelJa: '言い換えて再検索中', status: state, startedAt, endedAt: state === 'running' ? null : startedAt });
  const rows = buildTimelineRows([
    event(1, '2027-01-15T08:00:01Z', 'running'), event(2, '2027-01-15T08:00:01Z', 'done'),
    event(3, '2027-01-15T08:00:05Z', 'running'),
  ]);
  assert.deepEqual(rows.map((row) => row.status), ['done', 'running']);
  assert.equal(buildTimelineRows([event(2, 'a', 'done'), event(1, 'a', 'running')]).length, 1);
});

test('answer sample parses and renders the unified answer with grouped sources', async () => {
  const done = await status('status-answer.json', 0);
  assert.equal(done.status, 'completed');
  assert.equal(done.pollAfterMs, 0);
  assert.equal(done.result.kind, 'answer');
  assert.ok(done.debug.tools.length > 0);
  const rows = buildTimelineRows(done.steps);
  assert.equal(rows.length, 7);
  const page = render({ status: 'completed', steps: done.steps, result: done.result, debug: done.debug }, { selectedModel: 'AXIEZ-LINKs' });
  assert.match(page, /7手順で調査/);
  for (const ref of ['T1', 'L1']) {
    assert.match(page, new RegExp(`href="#senpai-turn-1-ref-${ref}"`));
    assert.match(page, new RegExp(`id="senpai-turn-1-ref-${ref}"`));
  }
  assert.match(page, /href="https:\/\/laws\.e-gov\.go\.jp\//);
  // 技術資料は実在しうるバケット名の s3 URI なので、既存の文書ルートへリンクする。
  assert.match(page, new RegExp(`href="/doc\\?uri=${encodeURIComponent('s3://kb-docs-bucket/docs/TI-1.pdf').replace(/[%.]/g, '\\$&')}#page=3"`));
  assert.doesNotMatch(page, /TI-1\.pdf · 3ページ（安全なリンクを確認できません）/);
  assert.doesNotMatch(page, /ref-T2|ref-K1|ref-K2/);
  // 使わなかった候補・ID・版・長い説明は一般表示に出さない。
  assert.doesNotMatch(page, /候補として渡したが使わなかったノウハウ|ドア全般の点検メモ|探索の手掛かり/);
  assert.doesNotMatch(page, /<h[1-6][^>]*>(結論|根拠と手順)</);
  assert.match(page, /生成した説明は検証を通過していない/);
  assert.doesNotMatch(page, /ref-T9/);
  const dev = render({ status: 'completed', steps: done.steps, result: done.result, debug: done.debug }, { developerView: true });
  assert.match(dev, /照合で外した参照: T9/);
  assert.match(dev, /tech_search/);
  assert.match(dev, /候補として渡したが使わなかったノウハウ[\s\S]*ドア全般の点検メモ/);
  assert.match(dev, /KH-/);
});

test('clarify, not_found and failed samples render their own states', async () => {
  const clarify = await status('status-clarify.json', 0);
  const clarifyPage = render({ status: 'completed', steps: clarify.steps, result: clarify.result }, { query: '質問', onResend() {} });
  assert.match(clarifyPage, /条件の確認が必要です/);
  assert.match(clarifyPage, /機種は何ですか（AXIEZ・NEXCUBE など）/);
  assert.doesNotMatch(clarifyPage, /ノウハウ（未承認・参考）/);
  assert.equal(clarifyPage.match(/機種は何ですか/g).length, 1);
  assert.match(clarifyPage, />AXIEZ</);

  const notFound = await status('status-not-found.json', 0);
  const notFoundPage = render({ status: 'completed', steps: notFound.steps, result: notFound.result });
  assert.match(notFoundPage, /該当する情報を確認できませんでした/);
  assert.doesNotMatch(notFoundPage, /ノウハウ（未承認・参考）/);

  const failed = await status('status-failed-timeout.json', 0);
  assert.equal(failed.status, 'failed');
  assert.equal(failed.error.code, 'Timeout');
  assert.match(failed.error.message, JAPANESE);
  const failedPage = render({ status: 'failed', steps: failed.steps, error: failed.error });
  assert.match(failedPage, /role="alert"/);
  assert.match(failedPage, /<details(?![^>]*\bopen\b)/);
  assert.equal(buildTimelineRows(failed.steps).at(-1).status, 'failed');
});

test('history detail restores the saved answer into the controller and renders it', async () => {
  const saved = await readSenpaiConversation({ ...client(sample('history-detail.json')), conversationId: CONVERSATION });
  assert.equal(saved.turns.length, 1);
  const [turn] = saved.turns;
  assert.equal(turn.senpaiTurnId, TURN);
  assert.equal(turn.modelType, 'AXIEZ-LINKs');
  assert.match(turn.query, /ドアが開閉時に異音/);
  assert.equal(turn.research.status, 'completed');
  assert.deepEqual(turn.research.steps, []);
  assert.equal(turn.research.result.sources.knowhow.used.length, 0);

  const chat = createSenpaiChat({ researchSource: async () => ({}) });
  chat.restore(saved);
  const restored = chat.getSnapshot().turns[0];
  const page = render(restored.research, { selectedModel: restored.modelType });
  assert.doesNotMatch(page, /調べた手順/);
  assert.match(page, /text-\[15px\]/);
  assert.match(page, /生成した説明は検証を通過していない/);
  assert.doesNotMatch(page, /ref-K2/);
  assert.doesNotMatch(page, /ref-T9/);
});

test('every real error response maps to a safe Japanese message with a sensible code', async () => {
  const expected = {
    feature_unavailable: 'unavailable', unauthorized: 'auth', validation_error_post: 'validation',
    validation_error_after_seq: 'validation', job_not_found: 'unavailable', method_not_allowed: 'unavailable',
    job_in_progress: 'unavailable', daily_limit_exceeded: 'server', start_failed: 'server', internal_error: 'server',
  };
  const errors = sample('errors.json');
  assert.equal(errors.length, 10);
  for (const entry of errors) {
    const isPost = entry.request.startsWith('POST');
    const call = isPost
      ? startSenpaiResearch({ ...client(entry), question: '質問', senpaiConversationId: CONVERSATION, senpaiTurnId: TURN, clientRequestId: '33333333-3333-4333-8333-333333333333' })
      : getSenpaiResearchStatus({ ...client(entry), jobId: JOB, afterSeq: 0 });
    await assert.rejects(call, (error) => {
      assert.ok(error instanceof KnowledgeResearchError, entry.name);
      assert.equal(error.code, expected[entry.name], entry.name);
      assert.match(error.message, JAPANESE, entry.name);
      assert.equal(error.message.includes(entry.body.error), false, entry.name);
      return true;
    });
  }
  const byName = Object.fromEntries(errors.map((entry) => [entry.name, entry]));
  const start = (name) => startSenpaiResearch({ ...client(byName[name]), question: '質問', senpaiConversationId: CONVERSATION, senpaiTurnId: TURN, clientRequestId: '33333333-3333-4333-8333-333333333333' });
  await assert.rejects(start('start_failed'), /調査を開始できませんでした/);
  await assert.rejects(start('job_in_progress'), /実行中/);
  await assert.rejects(start('daily_limit_exceeded'), /上限/);
});

test('a synthetic variant of the answer sample with warnings parses, renders them and keeps the rest', async () => {
  const fixture = sample('status-answer.json');
  const warning = '法令の検索に失敗したため確認できていません';
  fixture.body.result = { ...fixture.body.result, warnings: [warning], stopReason: 'budget' };
  const done = await getSenpaiResearchStatus({ ...client(fixture), jobId: JOB, afterSeq: 0 });
  assert.deepEqual(done.result.warnings, [warning]);
  const page = render({ status: 'completed', steps: done.steps, result: done.result });
  assert.match(page, new RegExp(warning, 'u'));
  assert.match(page, /時間の上限に達したため、確認できた範囲でまとめています/);
  fixture.body.result.warnings = 'oops';
  await assert.rejects(getSenpaiResearchStatus({ ...client(fixture), jobId: JOB, afterSeq: 0 }), (error) => error.code === 'invalid_response');
});
