import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';

const require = createRequire(import.meta.url);
const Link = ({ children, href, ...props }) => createElement('a', { href, ...props }, children);
const html = (element) => renderToStaticMarkup(element);

function loadTsx(path) {
  const filename = new URL(path, import.meta.url);
  const { outputText } = ts.transpileModule(readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename.pathname,
  });
  const compiledModule = { exports: {} };
  const localRequire = (name) => {
    if (name === 'next/link') return Link;
    if (/^\.\/Senpai[A-Za-z]+$/u.test(name)) return loadTsx(`../src/components/knowledge/${name.slice(2)}.tsx`);
    if (name === '@/data/kbModelTypes') return loadTsx('../src/data/kbModelTypes.ts');
    if (name === '@/lib/auth-helpers') return { getIdToken: async () => 'test-token' };
    if (name.startsWith('@/lib/') && name.endsWith('.mjs')) return require(`../src/lib/${name.slice(6)}`);
    return require(name);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const HOOK_SHIM = {
  useRef: (initial) => ({ current: initial }),
  useState: (initial) => [typeof initial === 'function' ? initial() : initial, () => {}],
  useEffect() {}, useLayoutEffect() {}, useCallback: (fn) => fn, useMemo: (fn) => fn(), useId: () => 'test-id',
};
function withHookShim(run) {
  const internals = require('react').__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;
  const previous = internals.H;
  internals.H = HOOK_SHIM;
  try { return run(); } finally { internals.H = previous; }
}
function expand(node) {
  if (Array.isArray(node)) return node.map(expand);
  if (!node || typeof node !== 'object' || !node.props) return node;
  const component = typeof node.type === 'function' ? node.type
    : node.type?.$$typeof === Symbol.for('react.memo') && typeof node.type.type === 'function' ? node.type.type : null;
  if (component) {
    try { return expand(withHookShim(() => component(node.props))); } catch { return node; }
  }
  return { ...node, props: { ...node.props, children: expand(node.props.children) } };
}
const textOf = (node) => (Array.isArray(node) ? node.map(textOf).join('') : node && typeof node === 'object' ? textOf(node.props?.children) : typeof node === 'string' || typeof node === 'number' ? String(node) : '');
function findAll(root, predicate, found = []) {
  if (Array.isArray(root)) { root.forEach((item) => findAll(item, predicate, found)); return found; }
  if (!root || typeof root !== 'object') return found;
  if (root.props && predicate(root)) found.push(root);
  findAll(root.props?.children, predicate, found);
  return found;
}

const { SenpaiChatView, reportable } = loadTsx('../src/components/knowledge/SenpaiChatView.tsx');
const { SenpaiChatTurn } = loadTsx('../src/components/knowledge/SenpaiChatTurn.tsx');
const { SenpaiMarkdown } = loadTsx('../src/components/knowledge/SenpaiMarkdown.tsx');
const { SenpaiConversationSidebar } = loadTsx('../src/components/knowledge/SenpaiConversationSidebar.tsx');

const CONVERSATION = '10000000-0000-4000-8000-000000000001';
const TURN = '20000000-0000-4000-8000-000000000001';
const paused = { status: 'paused', message: 'x' };
const NO_SOURCES = { tech: [], law: [], knowhow: { used: [], candidates: [] } };
const clarifyResult = { kind: 'clarify', answerMarkdown: '', clarifyQuestions: ['機種は何ですか'], sources: NO_SOURCES, unverifiedRefs: [] };
const turn = (research, extra = {}) => ({ id: 1, senpaiTurnId: TURN, query: 'ドアの異音', normal: paused, law: paused, research, ...extra });
const baseProps = (snapshot, overrides = {}) => ({
  snapshot, history: { entries: [], loading: false, error: '', complete: true, opening: false, openError: '', onRetry() {} },
  question: '', onQuestionChange() {}, modelType: '', onModelChange() {}, sendError: '', sidebarOpen: false,
  onOpenSidebar() {}, onCloseSidebar() {}, onSubmit() {}, onCancel() {}, onNewChat() {}, onSelectConversation() {},
  onSynthesize() {}, onResend() {}, flags: { research: true, fieldReports: true, synthesis: false },
  developerView: false, onToggleDeveloperView() {}, reports: {}, onReportSent() {}, ...overrides,
});
const render = (props) => html(createElement(SenpaiChatView, props));

test('item 1: the transcript is not a live region; one short sr-only status carries start and result', () => {
  const running = { conversationId: CONVERSATION, running: true, turns: [turn({ status: 'running', startedAt: Date.now(), steps: [] })] };
  const out = render(baseProps(running, { announcement: '調査中です' }));
  assert.equal(out.match(/aria-live/g).length, 1);
  assert.match(out, /<p role="status" aria-live="polite" class="sr-only">調査中です<\/p>/);
  assert.doesNotMatch(out, /aria-relevant/);
  assert.doesNotMatch(out, /role="status" aria-label="調査の経過"/);
  assert.match(out, /<span aria-hidden="true" class="text-xs text-gray-500">経過 /);
});

test('item 2: a turn waiting for the previous server job says so', () => {
  const waiting = { conversationId: CONVERSATION, running: true, turns: [turn({ status: 'queued', waiting: true, startedAt: Date.now(), steps: [] })] };
  assert.match(render(baseProps(waiting)), /前の調査の終了を待っています…/);
  const normal = { ...waiting, turns: [turn({ status: 'queued', startedAt: Date.now(), steps: [] })] };
  assert.doesNotMatch(render(baseProps(normal)), /前の調査の終了を待っています/);
});

test('item 5: a clarify reply shows the remaining characters, caps the input and warns before truncation', () => {
  const snapshot = (query) => ({ conversationId: CONVERSATION, running: false, turns: [turn({ status: 'completed', steps: [], result: clarifyResult }, { query })] });
  const short = render(baseProps(snapshot('ドアの異音'), { question: 'AXIEZ' }));
  assert.doesNotMatch(short, /補足はあと/, 'plenty of room: no hint at all');
  assert.match(short, /maxLength="1990"/);
  assert.doesNotMatch(short, /省略されます/);
  const near = render(baseProps(snapshot('ドアの異音'), { question: 'い'.repeat(1900) }));
  assert.match(near, /<p role="status" aria-live="polite"[^>]*>補足はあと90文字まで入力できます<\/p>/);
  const edge = (typed) => render(baseProps(snapshot('ドアの異音'), { question: 'い'.repeat(typed) }));
  assert.match(edge(1790), /補足はあと200文字/);
  assert.doesNotMatch(edge(1789), /補足はあと/);
  assert.match(edge(1990), /補足はあと0文字/);
  const long = render(baseProps(snapshot('あ'.repeat(1990)), { question: 'い'.repeat(100) }));
  assert.match(long, /maxLength="995"/);
  assert.doesNotMatch(long, /補足はあと/);
  assert.match(long, /role="note"[^>]*>元の質問が長いため、検索では元の質問の後半が省略されます。/);
  const fresh = render(baseProps({ conversationId: CONVERSATION, running: false, turns: [] }));
  assert.match(fresh, /maxLength="2000"/);
  assert.doesNotMatch(fresh, /補足はあと/);
});

test('item 6: a finished turn keeps its 結果を残す form while another question is running', () => {
  const done = turn({ status: 'completed', steps: [], result: { ...clarifyResult, kind: 'answer', answerMarkdown: '結論 [T1]' } });
  assert.equal(reportable(done, true), true);
  assert.equal(reportable(done, false), false);
  assert.equal(reportable({ ...done, senpaiTurnId: undefined }, true), false);
  assert.equal(reportable(turn({ status: 'running', steps: [] }), true), false, 'the running turn itself is not reportable until it has an answer');
});

test('item 8: the open history drawer is a modal dialog and the page behind it is inert', () => {
  const props = { entries: [], selectedId: undefined, loading: false, error: '', complete: true, onNew() {}, onSelect() {}, onClose() {}, onRetry() {} };
  const open = html(createElement(SenpaiConversationSidebar, { ...props, open: true }));
  assert.match(open, /<aside[^>]*role="dialog"[^>]*aria-modal="true"/);
  const closed = html(createElement(SenpaiConversationSidebar, { ...props, open: false }));
  assert.doesNotMatch(closed, /role="dialog"|aria-modal/);
  const idle = { conversationId: undefined, running: false, turns: [] };
  assert.match(render(baseProps(idle, { sidebarOpen: true })), /<main inert=""/);
  assert.doesNotMatch(render(baseProps(idle, { sidebarOpen: false })), /<main[^>]*inert/);
});

test('item 15: only refs that exist become links; text that merely looks like a ref stays plain', () => {
  const markdown = '本文 [T1] と [T9] と [偽](#senpai-turn-1-ref-T9) と [別の相談](#senpai-turn-2-ref-T1)';
  const out = html(createElement(SenpaiMarkdown, { markdown, knownRefs: new Set(['T1']), anchorPrefix: 'senpai-turn-1', refTitles: { T1: '手順書' } }));
  assert.equal(out.match(/<a /g).length, 1);
  assert.match(out, /<a href="#senpai-turn-1-ref-T1" title="手順書"/);
  assert.match(out, /\[T9\]/);
  assert.match(out, /<span>偽<\/span>/);
  assert.match(out, /<span>別の相談<\/span>/);
});

test('item 10: retrying or re-asking a supplemented turn hands back the supplement with the composed question', () => {
  const sent = [];
  const supplemented = turn({ status: 'failed', steps: [], error: { code: 'Timeout', message: '失敗' } }, { query: 'ドアの異音\n補足: AXIEZ', supplement: 'AXIEZ', supplementOf: 'ドアの異音' });
  const tree = expand(createElement(SenpaiChatTurn, {
    turn: supplemented, running: false, conversationId: CONVERSATION, onReportSent() {}, developerView: false, canReport: false,
    synthesisEnabled: false, onSynthesize() {}, onResend: (options) => sent.push(options),
  }));
  const retry = findAll(tree, (node) => node.type === 'button' && textOf(node).trim() === 'もう一度試す')[0];
  retry.props.onClick();
  assert.deepEqual(sent, [{ query: 'ドアの異音\n補足: AXIEZ', supplement: 'AXIEZ', supplementOf: 'ドアの異音' }]);
  assert.match(html(createElement(SenpaiChatTurn, { turn: supplemented, running: false, onReportSent() {}, developerView: false, canReport: false, synthesisEnabled: false, onSynthesize() {} })), /元の質問に補足して検索/);
});

test('items 9, 13 and 20: no informative gray-400 text, reduced-motion aware animation, 40px hit areas', () => {
  const dir = new URL('../src/components/knowledge/', import.meta.url);
  for (const file of readdirSync(dir).filter((name) => /^(Senpai|KnowledgeSenpai).*\.tsx$/u.test(name))) {
    const source = readFileSync(new URL(file, dir), 'utf8');
    assert.doesNotMatch(source, /(?<![:\w-])text-gray-400/u, `${file} uses low-contrast text-gray-400`);
    for (const match of source.matchAll(/animate-pulse(?! motion-reduce:animate-none)/gu)) assert.fail(`${file} animates without motion-reduce at ${match.index}`);
    assert.doesNotMatch(source, /\bh-8 w-8\b/u, `${file} has a 32px icon button`);
  }
});

test('disclosure summaries start with a small decorative chevron and no bullet marker', () => {
  const { SenpaiStepTimeline } = loadTsx('../src/components/knowledge/SenpaiStepTimeline.tsx');
  const step = { seq: 1, step: 'understand', labelJa: '質問を整理中', status: 'done', startedAt: '2026-10-20T01:00:00.000Z', endedAt: '2026-10-20T01:00:02.000Z' };
  const meta = html(createElement(SenpaiStepTimeline, { research: { status: 'completed', steps: [step], startedAt: 0, endedAt: 14000 } }));
  assert.match(meta, /<details class="group[^"]*"><summary class="[^"]*min-h-10[^"]*list-none[^"]*"><svg[^>]*width="12"[^>]*aria-hidden="true"[^>]*class="[^"]*group-open:rotate-90 motion-reduce:transition-none"/);
  assert.match(meta, /<\/svg><span[^>]*>14秒・1手順で調査<\/span>/);
  assert.doesNotMatch(meta, /[▸▾•]/);
  const { SenpaiResearchAnswer } = loadTsx('../src/components/knowledge/SenpaiResearchAnswer.tsx');
  const answer = html(createElement(SenpaiResearchAnswer, {
    anchorPrefix: 'senpai-turn-1', developerView: false,
    research: { status: 'completed', steps: [], result: { kind: 'answer', answerMarkdown: '## 結論\n結論です [T1]\n\n## 根拠と手順\n- 根拠 [T1]', clarifyQuestions: [], unverifiedRefs: [], sources: { tech: [{ ref: 'T1', title: '手順書' }], law: [], knowhow: { used: [], candidates: [] } } } },
  }));
  assert.match(answer, /<summary class="[^"]*min-h-10[^"]*list-none[^"]*"><svg[^>]*aria-hidden="true"[^>]*group-open:rotate-90/);
  assert.doesNotMatch(answer, /[▸▾•]/);
});
