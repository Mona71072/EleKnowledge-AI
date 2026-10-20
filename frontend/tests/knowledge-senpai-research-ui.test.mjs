import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';

const require = createRequire(import.meta.url);

// 実際の TSX を TypeScript でコンパイルし、フレームワーク・認証の境界だけを差し替える。
function loadTsx(path, mocks = {}) {
  const filename = new URL(path, import.meta.url);
  const { outputText } = ts.transpileModule(readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename.pathname,
  });
  const compiledModule = { exports: {} };
  const localRequire = (name) => {
    if (Object.hasOwn(mocks, name)) return mocks[name];
    if (name === 'next/link') return Link;
    if (/^\.\/Senpai[A-Za-z]+$/u.test(name) && name !== './SenpaiFieldReportForm') return loadTsx(`../src/components/knowledge/${name.slice(2)}.tsx`);
    if (name === './SenpaiConversationSidebar') return loadTsx('../src/components/knowledge/SenpaiConversationSidebar.tsx');
    if (name === './SenpaiFieldReportForm') return loadTsx('../src/components/knowledge/SenpaiFieldReportForm.tsx', { '@/lib/auth-helpers': { getIdToken: async () => 'test-token' } });
    if (name === '@/data/kbModelTypes') return loadTsx('../src/data/kbModelTypes.ts');
    if (name === '@/lib/knowledge-senpai-synthesis.mjs') return { requestSenpaiSynthesis: async () => ({}) };
    if (name === '@/lib/knowledge-senpai-field-report.mjs') return require('../src/lib/knowledge-senpai-field-report.mjs');
    if (name.startsWith('@/lib/') && name.endsWith('.mjs')) return require(`../src/lib/${name.slice(6)}`);
    if (name === '@/hooks/useSenpaiHistory') return { useSenpaiHistory: () => ({ entries: [], loading: false, error: '', complete: true, opening: false, openError: '', openConversation: async () => {}, resetSelection() {}, refresh() {} }) };
    return require(name);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const Link = ({ children, href, ...props }) => createElement('a', { href, ...props }, children);
const html = (element) => renderToStaticMarkup(element);
const { SenpaiResearchAnswer } = loadTsx('../src/components/knowledge/SenpaiResearchAnswer.tsx');
const { SenpaiDevPanel } = loadTsx('../src/components/knowledge/SenpaiDevPanel.tsx');

const NOW = Date.now();
const step = (seq, overrides = {}) => ({
  seq, step: 'tech_search', labelJa: '技術資料を検索中', status: 'done',
  startedAt: '2026-10-20T01:00:00.000Z', endedAt: '2026-10-20T01:00:02.000Z', ...overrides,
});

function result(overrides = {}) {
  return {
    kind: 'answer',
    answerMarkdown: '## 結論の候補\nドアの調整です [T1] [L1] [K1]\n\n<img src=x onerror=alert(1)>\n\n[外部](https://evil.example.test/x) [js](javascript:alert(1)) ![画像](https://evil.example.test/p.png)',
    clarifyQuestions: [],
    sources: {
      tech: [{ ref: 'T1', title: '保守手順書', documentName: 'manual.pdf', pageNumber: 12, sourceUri: 's3://kb-bucket/docs/manual.pdf' }],
      law: [{ ref: 'L1', lawTitle: '建築基準法', provision: '第三十四条', effectiveDate: '2025-04-01', sourceUrl: 'https://laws.e-gov.go.jp/law/325AC0000000201' }],
      knowhow: {
        used: [{ ref: 'K1', knowledgeId: 'KH-1001', cardVersion: 2, title: '調整の勘所', status: 'draft', modelFit: 'other_product', modelFitProducts: ['AXIEZ-LINKs'] }],
        candidates: [{ knowledgeId: 'KH-2002', cardVersion: 1, title: '使わなかったカード' }],
      },
    },
    unverifiedRefs: [], ...overrides,
  };
}

const completed = (overrides = {}, resultOverrides = {}) => ({
  status: 'completed', steps: [step(1, { step: 'understand', labelJa: '質問を整理中' }), step(2), step(3, { step: 'law_search', labelJa: '法令を確認中' })],
  startedAt: NOW - 21_000, endedAt: NOW, result: result(resultOverrides), ...overrides,
});

const view = (research, props = {}) => html(createElement(SenpaiResearchAnswer, { research, anchorPrefix: 'senpai-turn-1', developerView: false, ...props }));

test('while running, the live timeline shows labels, details, icons, the current step and elapsed time', () => {
  const page = view({
    status: 'running', startedAt: NOW - 12_000,
    steps: [
      step(1, { step: 'understand', labelJa: '質問を整理中' }),
      step(2, { status: 'running', detailJa: '『LINKs ドア 異音』で検索', endedAt: null }),
    ],
  });
  assert.match(page, /技術資料を検索中…/);
  assert.match(page, /経過 \d+秒/);
  assert.doesNotMatch(page, /約30秒|\/7|>中止</);
  assert.match(page, /質問を整理しました/);
  assert.doesNotMatch(page, /質問を整理中/);
  assert.match(page, /技術資料を検索中/);
  assert.match(page, /『LINKs ドア 異音』で検索/);
  assert.match(page, /aria-label="完了"/);
  assert.match(page, /aria-label="実行中"/);
  assert.equal(page.match(/aria-current="step"/g).length, 1);
  assert.match(page, />詳細</);
  assert.doesNotMatch(page, /<details open/);
  assert.doesNotMatch(page, /結論の候補/);
});

test('a queued job without events says it is starting', () => {
  assert.match(view({ status: 'queued', steps: [], startedAt: NOW }), /調査を開始しています/);
});

test('a skipped step shows its own icon and detail', () => {
  const page = view({ status: 'running', steps: [step(1, { step: 'law_search', labelJa: '法令を確認中', status: 'skipped', detailJa: '法令に関係しない質問' })], startedAt: NOW });
  assert.match(page, /aria-label="省略"/);
  assert.match(page, /法令に関係しない質問/);
});

test('after completion the timeline collapses into 「調べた手順（n）」 and one unified answer is shown', () => {
  const page = view(completed());
  assert.match(page, /<details(?![^>]*\bopen\b)[^>]*>[\s\S]*?21秒・3手順で調査/);
  assert.match(page, /ドアの調整です/);
  assert.doesNotMatch(page, /約30秒/);
  assert.equal(page.match(/aria-label="技術KBからの回答"/g), null);
});

test('reference markers link to the matching source entries', () => {
  const page = view(completed());
  for (const ref of ['T1', 'L1', 'K1']) {
    assert.match(page, new RegExp(`href="#senpai-turn-1-ref-${ref}"`));
    assert.match(page, new RegExp(`id="senpai-turn-1-ref-${ref}"`));
  }
});

test('answer text never produces raw HTML, images or outside links', () => {
  const page = view(completed());
  assert.match(page, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.doesNotMatch(page, /<img/);
  assert.doesNotMatch(page, /href="https:\/\/evil/);
  assert.doesNotMatch(page, /javascript:/);
  assert.match(page, /外部/);
  assert.match(page, /（画像: 画像）/);
});

test('sources are grouped: technical documents, laws, and knowhow (unapproved, reference only)', () => {
  const page = view(completed());
  assert.match(page, /技術資料（1）/);
  assert.equal(page.match(/>開く</g).length, 2);
  assert.match(page, /aria-label="保守手順書：資料を開く"/);
  assert.match(page, /aria-label="建築基準法：e-Govで開く"/);
  assert.match(page, new RegExp(`href="/doc\\?uri=${encodeURIComponent('s3://kb-bucket/docs/manual.pdf').replace(/[%.]/g, '\\$&')}#page=12"`));
  assert.match(page, /保守手順書/);
  assert.match(page, /12ページ/);
  assert.match(page, /法令（1）/);
  assert.match(page, /href="https:\/\/laws\.e-gov\.go\.jp\/law\/325AC0000000201"/);
  assert.match(page, /建築基準法/);
  assert.match(page, /第三十四条・施行日 2025-04-01/);
  assert.match(page, /ノウハウ（未承認・参考）/);
  assert.match(page, /回答で使ったノウハウ/);
  assert.match(page, /調整の勘所/);
  assert.match(page, /未承認（下書き）/);
  assert.match(page, /候補として渡したが使わなかったノウハウ/);
  assert.match(page, /使わなかったカード/);
  assert.doesNotMatch(page, /ノウハウは参照していません/);
});

test('without used knowhow the answer says so and still lists unused candidates', () => {
  const page = view(completed({}, { sources: { tech: [], law: [], knowhow: { used: [], candidates: [{ knowledgeId: 'KH-9', cardVersion: 1, title: '候補だけ' }] } }, answerMarkdown: '本文のみ' }));
  assert.match(page, /ノウハウは参照していません/);
  assert.match(page, /候補だけ/);
  assert.doesNotMatch(page, /技術資料（/);
  assert.doesNotMatch(page, /法令（/);
  const none = view(completed({}, { sources: { tech: [], law: [], knowhow: { used: [], candidates: [] } }, answerMarkdown: '本文のみ' }));
  assert.match(none, /ノウハウは参照していません/);
  assert.doesNotMatch(none, /候補として渡したが使わなかったノウハウ/);
});

test('unsafe source locations are not linked', () => {
  const page = view(completed({}, {
    sources: {
      tech: [{ ref: 'T1', title: '怪しい資料', sourceUri: 'https://evil.example.test/a.pdf' }],
      law: [{ ref: 'L1', lawTitle: '怪しい法令', sourceUrl: 'http://evil.example.test/law' }],
      knowhow: { used: [], candidates: [] },
    },
    answerMarkdown: '本文 [T1] [L1]',
  }));
  assert.doesNotMatch(page, /href="https?:\/\/evil/);
  assert.match(page, /怪しい資料/);
  assert.match(page, /怪しい法令/);
  assert.equal(page.match(/（安全なリンクを確認できません）/g).length, 2);
});

test('the model fit notice shows only for used cards of another product', () => {
  const page = view(completed(), { selectedModel: 'AXIEZ' });
  assert.match(page, /AXIEZ-LINKs（VFGLF・巻上機下部|AXIEZ-LINKs（VFGLF・巻上機上部）の事例です。選択中の AXIEZ（VFGLB・巻上機下部）でも当てはまるかは要確認です。/);
  assert.equal(page.match(/でも当てはまるかは要確認です/g).length, 1);
  assert.doesNotMatch(view(completed()), /でも当てはまるかは要確認です/);
  assert.match(view(completed({}, { understanding: { modelType: 'AXIEZ' } })), /でも当てはまるかは要確認です/);
  const matched = completed({}, {});
  matched.result.sources.knowhow.used[0] = { ...matched.result.sources.knowhow.used[0], modelFit: 'matched' };
  assert.doesNotMatch(view(matched, { selectedModel: 'AXIEZ' }), /でも当てはまるかは要確認です/);
});

test('clarify shows the questions and asks for an answer in the input', () => {
  const page = view(completed({}, { kind: 'clarify', answerMarkdown: '', clarifyQuestions: ['機種は何ですか？', '異音はいつ出ますか？'], sources: { tech: [], law: [], knowhow: { used: [], candidates: [] } } }));
  assert.match(page, /条件の確認が必要です/);
  assert.match(page, /機種は何ですか？/);
  assert.match(page, /異音はいつ出ますか？/);
  assert.match(page, /入力欄/);
});

test('not_found explains that nothing was found', () => {
  const page = view(completed({}, { kind: 'not_found', answerMarkdown: '', sources: { tech: [], law: [], knowhow: { used: [], candidates: [] } } }));
  assert.match(page, /該当する情報を確認できませんでした/);
  assert.doesNotMatch(page, /ノウハウ（未承認・参考）/);
});

test('a budget stop is disclosed', () => {
  assert.match(view(completed({}, { stopReason: 'budget' })), /上限までに確認できた範囲/);
  assert.doesNotMatch(view(completed({}, { stopReason: 'sufficient' })), /上限までに確認できた範囲/);
});

test('failed and cancelled turns keep the steps and show a clear message', () => {
  const failed = view({ status: 'failed', steps: [step(1, { status: 'failed' })], error: { code: 'Timeout', message: '調査が時間内に終わりませんでした。' }, startedAt: NOW - 5000, endedAt: NOW });
  assert.match(failed, /role="alert"[^>]*>調査が時間内に終わりませんでした。/);
  assert.match(failed, /<details(?![^>]*\bopen\b)[^>]*>[\s\S]*?1手順で調査[\s\S]*?詳細/);
  assert.match(failed, /role="alert"/);
  const cancelled = view({ status: 'cancelled', steps: [step(1, { status: 'running', endedAt: null })], startedAt: NOW - 5000, endedAt: NOW });
  assert.match(cancelled, /中止しました（サーバー側の処理は続く場合があります）/);
  assert.match(cancelled, /1手順で調査/);
  const noMessage = view({ status: 'failed', steps: [] });
  assert.match(noMessage, /調査に失敗しました/);
});

test('a restored answer has no step timeline', () => {
  const page = view({ status: 'completed', steps: [], result: result() });
  assert.doesNotMatch(page, /手順で調査/);
  assert.match(page, /ドアの調整です/);
});

test('developer view shows debug, tools table, budget and raw steps; the general view does not', () => {
  const debug = {
    understandingRaw: { intent: 'cause', part: '<b>ドア</b>' },
    queries: { tech: ['LINKs ドア 異音'], law: ['昇降機 戸'], knowhow: 'ドア 異音' },
    tools: [{ seq: 4, tool: 'tech_search', query: 'LINKs ドア 異音', filters: { modelType: 'AXIEZ-LINKs' }, hits: 30, selected: 6, topScores: [0.61, 0.55], ms: 1830 }],
    budget: { searchesUsed: 4, searchesMax: 6, modelCallsUsed: 3, modelCallsMax: 4, elapsedMs: 21500, elapsedMaxMs: 60000 },
  };
  const research = completed({ debug }, { unverifiedRefs: ['T9'] });
  const general = view(research);
  assert.doesNotMatch(general, /開発者表示|understandingRaw|道具の呼び出し/);
  const dev = view(research, { developerView: true });
  assert.match(dev, /開発者表示/);
  assert.match(dev, /understandingRaw/);
  assert.match(dev, /&lt;b&gt;ドア&lt;\/b&gt;/);
  assert.doesNotMatch(dev, /<b>ドア/);
  assert.match(dev, /LINKs ドア 異音/);
  assert.match(dev, /<th[^>]*>上位スコア<\/th>/);
  assert.match(dev, /0\.61, 0\.55/);
  assert.match(dev, />1830</);
  assert.match(dev, /4 \/ 6 回/);
  assert.match(dev, /3 \/ 4 回/);
  assert.match(dev, /21500 \/ 60000 ms/);
  assert.match(dev, /生の段階イベント（3）/);
  assert.match(dev, /照合で外した参照: T9/);
  assert.match(dev, /結論の候補/);
});

test('developer view explains when no debug information exists', () => {
  const dev = html(createElement(SenpaiDevPanel, { steps: [] }));
  assert.match(dev, /デバッグ情報はありません/);
  assert.match(dev, /保存されていません/);
});

// ---- ページ（コントローラ・フラグ・開発者表示の切り替え） ----

function withEnv(name, value, fn) {
  const previous = process.env[name];
  if (value == null) delete process.env[name]; else process.env[name] = value;
  try { return fn(); } finally {
    if (previous === undefined) delete process.env[name]; else process.env[name] = previous;
  }
}

function findAny(root, predicate) {
  return findAnyExpanded(expand(root), predicate);
}

function findAnyExpanded(root, predicate) {
  if (!root || typeof root !== 'object') return null;
  if (Array.isArray(root)) {
    for (const item of root) { const found = findAnyExpanded(item, predicate); if (found) return found; }
    return null;
  }
  if (root.props && predicate(root)) return root;
  const children = root.props?.children;
  for (const child of Array.isArray(children) ? children : [children]) {
    const found = findAnyExpanded(child, predicate);
    if (found) return found;
  }
  return null;
}

function chatPage({ flag = 'true', snapshot, storage = {} }) {
  const React = require('react');
  const slots = [];
  const effects = [];
  let hookIndex = 0;
  let firstRender = true;
  const controllerOptions = [];
  const store = { ...storage };
  globalThis.window = { localStorage: { getItem: (key) => store[key] ?? null, setItem: (key, value) => { store[key] = value; } } };
  const runs = [];
  const cancels = [];
  const Chat = withEnv('NEXT_PUBLIC_ENABLE_SENPAI_RESEARCH', flag, () => loadTsx('../src/components/knowledge/KnowledgeSenpaiChat.tsx', {
    react: {
      ...React,
      useState(initial) {
        const index = hookIndex++;
        if (!(index in slots)) slots[index] = initial;
        return [slots[index], (value) => { slots[index] = typeof value === 'function' ? value(slots[index]) : value; }];
      },
      useRef(initial) {
        const index = hookIndex++;
        if (!(index in slots)) slots[index] = { current: initial };
        return slots[index];
      },
      useEffect(effect) {
        const index = hookIndex++;
        if (firstRender) effects[index] = effect;
      },
    },
    'next/link': Link,
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
    '@/lib/chat-session-link.mjs': { buildChatSessionHref: () => '/chat' },
    '@/lib/knowledge-senpai-chat.mjs': {
      createSenpaiChat: (options) => {
        controllerOptions.push(options);
        return { getSnapshot: () => snapshot, send: async () => {}, cancel() { cancels.push(1); }, reset() {}, dispose() {} };
      },
    },
    '@/lib/knowledge-senpai-research.mjs': { runSenpaiResearch: async (request) => { runs.push(request); return {}; } },
    '@/lib/knowledge-research.mjs': { queryKnowledgeSource: async () => ({}), researchSourceHref: () => null },
  })).KnowledgeSenpaiChat;
  const render = () => {
    hookIndex = 0;
    const element = Chat();
    if (!firstRender) return element;
    // 最初の描画後に副作用（コントローラ作成・保存値の読込）を走らせ、反映された状態で描き直す。
    firstRender = false;
    for (const effect of effects) effect?.();
    hookIndex = 0;
    return Chat();
  };
  return { render, controllerOptions, store, runs, slots, cancels };
}

const base = { conversationId: '10000000-0000-4000-8000-000000000001', running: false };
const laneStub = { status: 'paused', message: 'x' };
const researchTurn = (research, extra = {}) => ({ id: 1, senpaiTurnId: '20000000-0000-4000-8000-000000000001', query: 'ドアの異音', normal: laneStub, law: laneStub, research, ...extra });

test('with the flag on, a research turn shows one unified answer instead of the two lanes', (t) => {
  t.after(() => { delete globalThis.window; });
  const page = chatPage({ snapshot: { ...base, turns: [researchTurn(completed(), { modelType: 'AXIEZ' })] } });
  const out = html(page.render());
  assert.match(out, /結論の候補/);
  assert.match(out, /3手順で調査/);
  assert.match(out, /機種: AXIEZ/);
  assert.doesNotMatch(out, /aria-label="技術KBからの回答"|aria-label="法令KBからの回答"/);
  assert.doesNotMatch(out, /工技先輩のまとめを作る|結果を残す/);
  assert.match(out, /重要な判断は出典で確認してください（ノウハウは未承認）/);
  assert.match(out, />開発者表示</);
  assert.doesNotMatch(out, /aria-label="開発者表示"/);
});

test('with the flag on, the controller runs research through the RAG API with the id token', async (t) => {
  t.after(() => { delete globalThis.window; });
  process.env.NEXT_PUBLIC_RAG_API_URL = 'https://api.example.test/dev';
  const page = chatPage({ snapshot: { ...base, turns: [] } });
  page.render();
  const [options] = page.controllerOptions;
  assert.equal(typeof options.researchSource, 'function');
  const signal = new AbortController().signal;
  await options.researchSource({ question: '質問', senpaiConversationId: 'c', senpaiTurnId: 't', clientRequestId: 'r', signal, onUpdate() {} });
  assert.equal(page.runs[0].baseUrl, 'https://api.example.test/dev');
  assert.equal(page.runs[0].question, '質問');
  assert.equal(page.runs[0].signal, signal);
  assert.equal(await page.runs[0].getToken(), 'test-token');
  delete process.env.NEXT_PUBLIC_RAG_API_URL;
});

test('the developer toggle shows the debug panel and remembers the choice', (t) => {
  t.after(() => { delete globalThis.window; });
  const research = completed({ debug: { queries: { tech: ['検索語A'], law: [] } } });
  const page = chatPage({ snapshot: { ...base, turns: [researchTurn(research)] } });
  assert.doesNotMatch(html(page.render()), /aria-label="開発者表示"/);
  const toggle = findAny(page.render(), (node) => node.type === 'button' && node.props['aria-pressed'] !== undefined);
  assert.equal(toggle.props['aria-pressed'], false);
  toggle.props.onClick();
  assert.equal(page.store['senpai-research-developer-view'], 'true');
  const shown = html(page.render());
  assert.match(shown, /aria-label="開発者表示"/);
  assert.match(shown, /検索語A/);
  findAny(page.render(), (node) => node.type === 'button' && node.props['aria-pressed'] !== undefined).props.onClick();
  assert.equal(page.store['senpai-research-developer-view'], 'false');
  assert.doesNotMatch(html(page.render()), /aria-label="開発者表示"/);
});

test('a saved developer view is restored, and storage failures do not break the page', (t) => {
  t.after(() => { delete globalThis.window; });
  const research = completed({ debug: { queries: { tech: ['検索語B'], law: [] } } });
  const saved = chatPage({ snapshot: { ...base, turns: [researchTurn(research)] }, storage: { 'senpai-research-developer-view': 'true' } });
  saved.render();
  assert.match(html(saved.render()), /検索語B/);

  const broken = chatPage({ snapshot: { ...base, turns: [researchTurn(research)] } });
  globalThis.window = { localStorage: { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } } };
  broken.render();
  findAny(broken.render(), (node) => node.type === 'button' && node.props['aria-pressed'] !== undefined).props.onClick();
  assert.match(html(broken.render()), /aria-label="開発者表示"/);
});

test('with the flag on, input stays enabled after clarify, failure and cancel but not while running', (t) => {
  t.after(() => { delete globalThis.window; });
  const disabledOf = (snapshot) => findAny(chatPage({ snapshot }).render(), (node) => node.type === 'textarea').props.disabled;
  const clarify = completed({}, { kind: 'clarify', clarifyQuestions: ['機種は？'], answerMarkdown: '' });
  assert.equal(disabledOf({ ...base, turns: [researchTurn(clarify)] }), false);
  assert.equal(disabledOf({ ...base, turns: [researchTurn({ status: 'failed', steps: [], error: { code: 'Internal', message: 'x' } })] }), false);
  assert.equal(disabledOf({ ...base, turns: [researchTurn({ status: 'cancelled', steps: [] })] }), false);
  const running = chatPage({ snapshot: { ...base, running: true, turns: [researchTurn({ status: 'running', steps: [step(1, { status: 'running', endedAt: null })], startedAt: NOW })] } });
  assert.equal(findAny(running.render(), (node) => node.type === 'textarea').props.disabled, true);
  assert.match(html(running.render()), /aria-label="中止"/);
  assert.doesNotMatch(html(chatPage({ snapshot: { ...base, turns: [researchTurn(clarify)] } }).render()), /この相談では続けて質問できません/);
});

test('with the flag off nothing changes: no toggle, no research source, two lanes', (t) => {
  t.after(() => { delete globalThis.window; });
  for (const flag of [null, 'false', 'TRUE']) {
    const lane = (mode) => ({ status: 'success', answer: { mode, query: '質問', content: `${mode} 回答`, responseType: 'pages', sessionId: `${mode}-s`, messageId: `${mode}-m`, receivedAt: '2026-10-20T00:00:00Z', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [] } });
    const page = chatPage({ flag, snapshot: { ...base, turns: [{ id: 1, senpaiTurnId: '20000000-0000-4000-8000-000000000001', query: '質問', normal: lane('normal'), law: lane('law') }] } });
    const out = html(page.render());
    assert.equal(page.controllerOptions[0].researchSource, undefined, String(flag));
    assert.doesNotMatch(out, /開発者表示/);
    assert.match(out, /aria-label="技術KBからの回答"/);
    assert.match(out, /aria-label="法令KBからの回答"/);
    assert.match(out, /ローカルファイルは送信されません/);
  }
});

test('with the flag off a restored research turn is still readable but cannot be continued', (t) => {
  t.after(() => { delete globalThis.window; });
  const page = chatPage({ flag: 'false', snapshot: { ...base, turns: [researchTurn({ status: 'completed', steps: [], result: result() })] } });
  const out = html(page.render());
  assert.match(out, /結論の候補/);
  assert.doesNotMatch(out, /開発者表示/);
  assert.match(out, /調査機能が無効の環境では、調査ジョブの相談に続けて質問できません/);
  assert.equal(findAny(page.render(), (node) => node.type === 'textarea').props.disabled, true);
});

// ---- 画面の改善（聞き返し・聞き直し・コールアウト・出典カード・操作ボタン） ----

function expand(node) {
  if (Array.isArray(node)) return node.map(expand);
  if (!node || typeof node !== 'object' || !node.props) return node;
  if (typeof node.type === 'function') {
    try { return expand(node.type(node.props)); } catch { return node; }
  }
  return { ...node, props: { ...node.props, children: expand(node.props.children) } };
}
const textOf = (node) => (Array.isArray(node) ? node.map(textOf).join('') : node && typeof node === 'object' ? textOf(node.props?.children) : typeof node === 'string' || typeof node === 'number' ? String(node) : '');
const buttonByText = (tree, text) => findAny(tree, (node) => node.type === 'button' && textOf(node).trim() === text);
const answerTree = (research, props = {}) => expand(SenpaiResearchAnswer({ research, anchorPrefix: 'senpai-turn-1', developerView: false, ...props }));
const NO_SOURCES = { tech: [], law: [], knowhow: { used: [], candidates: [] } };

test('clarify shows the questions once, even when the markdown repeats them', () => {
  const research = completed({}, {
    kind: 'clarify', sources: NO_SOURCES, clarifyQuestions: ['機種は何ですか', '異音はいつ出ますか'],
    answerMarkdown: '次の点を教えてください。\n\n- 機種は何ですか\n- 異音はいつ出ますか',
  });
  const page = view(research);
  assert.equal(page.match(/機種は何ですか/g).length, 1);
  assert.equal(page.match(/異音はいつ出ますか/g).length, 1);
  assert.match(page, /元の質問に補足して調べ直します/);
  const noQuestions = view(completed({}, { kind: 'clarify', sources: NO_SOURCES, clarifyQuestions: [], answerMarkdown: '本文だけの聞き返し' }));
  assert.match(noQuestions, /本文だけの聞き返し/);
});

test('model chips appear only for a model question and ask again with the original question', () => {
  const calls = [];
  const research = completed({}, { kind: 'clarify', sources: NO_SOURCES, clarifyQuestions: ['機種は何ですか'], answerMarkdown: '' });
  const tree = answerTree(research, { query: '元の質問', onResend: (options) => calls.push(options) });
  const chip = buttonByText(tree, 'AXIEZ-LINKs');
  assert.ok(chip);
  chip.props.onClick();
  assert.deepEqual(calls, [{ query: '元の質問', modelType: 'AXIEZ-LINKs' }]);
  assert.equal(['AXIEZ', 'AXIEZ-LINKs', 'NEXCUBE', 'メルシティ', 'メルワイド', 'エスカレーター'].every((name) => buttonByText(tree, name)), true);

  const other = completed({}, { kind: 'clarify', sources: NO_SOURCES, clarifyQuestions: ['異音はいつ出ますか'], answerMarkdown: '' });
  assert.equal(buttonByText(answerTree(other, { query: 'q', onResend() {} }), 'AXIEZ'), null);
  assert.equal(buttonByText(answerTree(research, {}), 'AXIEZ'), null);
});

test('the knowhow box is hidden for clarify and not_found unless a card was used', () => {
  const candidatesOnly = { tech: [], law: [], knowhow: { used: [], candidates: [{ knowledgeId: 'KH-1', cardVersion: 1, title: '候補' }] } };
  for (const kind of ['clarify', 'not_found']) {
    assert.doesNotMatch(view(completed({}, { kind, answerMarkdown: '', sources: candidatesOnly })), /ノウハウ（未承認・参考）/, kind);
  }
  const used = { tech: [], law: [], knowhow: { used: [{ ref: 'K1', knowledgeId: 'KH-1', cardVersion: 1, title: '使った', status: 'draft' }], candidates: [] } };
  assert.match(view(completed({}, { kind: 'clarify', answerMarkdown: '', clarifyQuestions: ['q'], sources: used })), /ノウハウ（未承認・参考）/);
  assert.match(view(completed({}, { kind: 'answer', answerMarkdown: '本文', sources: NO_SOURCES })), /ノウハウは参照していません/);
});

test('the answer leads with the conclusion and gathers the notes in one subtle block', () => {
  const page = view(completed({}, {
    answerMarkdown: '## 結論の候補\n調整です [T1]\n\n## 技術資料から\n手順です\n\n## 食い違い・不足\n- 階数が不明\n\n## 次に確認すること\n- 音のタイミング',
  }));
  assert.match(page, /aria-label="結論の候補"[^>]*><div class="[^"]*font-medium/);
  assert.doesNotMatch(page, /<h5[^>]*>結論の候補<\/h5>/);
  assert.match(page, /<h5 class="mb-1 text-sm font-semibold text-gray-900">技術資料から<\/h5>/);
  assert.equal(page.match(/<aside/g).length, 1);
  assert.match(page, /<aside aria-label="補足" class="[^"]*bg-gray-50[\s\S]*食い違い・不足[\s\S]*次に確認すること[\s\S]*<\/aside>/);
  assert.doesNotMatch(page, /☐|border-indigo|bg-amber/);
  assert.match(page, /階数が不明/);

  const plain = view(completed({}, { answerMarkdown: '見出しのない回答です [T1]' }));
  assert.match(plain, /見出しのない回答です/);
  assert.doesNotMatch(plain, /<aside/);
});

test('inline refs are coloured chips with the source title, and unverified refs stay plain text', () => {
  const page = view(completed({}, { answerMarkdown: '本文 [T1] [L1] [K1] [T9]', unverifiedRefs: ['T9'] }));
  assert.match(page, /<a href="#senpai-turn-1-ref-T1" title="保守手順書" class="[^"]*bg-blue-50[^"]*">技1<\/a>/);
  assert.match(page, /<a href="#senpai-turn-1-ref-L1" title="建築基準法 第三十四条" class="[^"]*bg-emerald-50[^"]*">法1<\/a>/);
  assert.match(page, /<a href="#senpai-turn-1-ref-K1" title="調整の勘所" class="[^"]*bg-violet-50[^"]*">ノ1<\/a>/);
  assert.match(page, /\[T9\]/);
  assert.doesNotMatch(page, /ref-T9/);
});

test('source rows carry a tinted number pill and keep the knowhow cards split', () => {
  const page = view(completed());
  assert.match(page, /id="senpai-turn-1-ref-T1"[^>]*>[\s\S]*?bg-blue-50[^>]*>技1</);
  assert.match(page, /id="senpai-turn-1-ref-L1"[^>]*>[\s\S]*?bg-emerald-50[^>]*>法1</);
  assert.match(page, /id="senpai-turn-1-ref-K1"[^>]*>[\s\S]*?bg-violet-50[^>]*>ノ1</);
  assert.match(page, /<h4[^>]*>出典<\/h4>/);
  assert.match(page, /ノウハウ 2件（未承認・参考）/);
});

test('a model mismatch banner offers to ask again with the understood model', () => {
  const calls = [];
  const research = completed({}, { understanding: { modelType: 'NEXCUBE' } });
  const tree = answerTree(research, { selectedModel: 'AXIEZ', query: '質問', onResend: (options) => calls.push(options) });
  const page = view(research, { selectedModel: 'AXIEZ', query: '質問', onResend() {} });
  assert.match(page, /質問では NEXCUBE と読めますが、選択中の機種は AXIEZ です。/);
  buttonByText(tree, 'NEXCUBEで聞き直す').props.onClick();
  assert.deepEqual(calls, [{ query: '質問', modelType: 'NEXCUBE' }]);
  assert.doesNotMatch(view(research, { selectedModel: 'NEXCUBE' }), /と読めますが/);
  assert.doesNotMatch(view(research), /と読めますが/);
  assert.match(view(research, { selectedModel: 'AXIEZ' }), /と読めますが/);
  assert.doesNotMatch(view(research, { selectedModel: 'AXIEZ' }), />NEXCUBEで聞き直す</);
});

test('the running view shows elapsed time and clamped, readable details, with no inline cancel', () => {
  const research = {
    status: 'running', startedAt: NOW - 3000,
    steps: [step(1, { status: 'running', endedAt: null, detailJa: 'あ'.repeat(120) }), step(2, { step: 'knowhow', labelJa: 'ノウハウを確認中', status: 'done' })],
  };
  const page = view(research);
  assert.match(page, /経過 \d+秒/);
  assert.doesNotMatch(page, /約30秒|\/7|>中止</);
  assert.match(page, /line-clamp-1[^"]*text-gray-500/);
  assert.match(page, new RegExp(`title="${'あ'.repeat(120)}"`));
  assert.match(page, /text-gray-700">[^<]*<span role="img"|text-gray-700"><span role="img" aria-label="完了"/);
});

test('a step detail that only repeats the label is not shown', () => {
  const page = view({ status: 'failed', startedAt: NOW - 3000, endedAt: NOW, steps: [
    step(1, { step: 'synthesize', labelJa: '回答をまとめています', status: 'failed', detailJa: '回答をまとめています' }),
    step(2, { step: 'tech_search', labelJa: '技術資料を検索中', status: 'done', detailJa: '『LINKs ドア』で検索' }),
  ] });
  assert.doesNotMatch(page, /title="回答をまとめています"/);
  assert.match(page, /title="『LINKs ドア』で検索"/);
});

test('failed and cancelled turns offer 「もう一度試す」 with the same question and model', () => {
  const calls = [];
  for (const research of [
    { status: 'failed', steps: [], error: { code: 'Timeout', message: '時間切れ' } },
    { status: 'cancelled', steps: [] },
  ]) {
    const tree = answerTree(research, { query: '同じ質問', selectedModel: 'AXIEZ', onResend: (options) => calls.push(options) });
    buttonByText(tree, 'もう一度試す').props.onClick();
    assert.doesNotMatch(view(research), /もう一度試す/);
  }
  assert.deepEqual(calls, [{ query: '同じ質問', modelType: 'AXIEZ' }, { query: '同じ質問', modelType: 'AXIEZ' }]);
  const without = answerTree({ status: 'failed', steps: [] }, { query: 'q', onResend: (options) => calls.push(options) });
  buttonByText(without, 'もう一度試す').props.onClick();
  assert.deepEqual(calls.at(-1), { query: 'q' });
});

test('a finished answer has a copy button; other kinds do not', () => {
  assert.match(view(completed()), /aria-label="回答をコピー"/);
  assert.doesNotMatch(view(completed({}, { kind: 'not_found', answerMarkdown: '', sources: NO_SOURCES })), /回答をコピー/);
});

// ---- ページ ----

function turnViews(page) {
  const views = [];
  const view = page.render();
  // コンテナは SenpaiChatView を返す。1段だけ展開すると、相談ごとの部品に渡す props が見える。
  (function walk(node) {
    if (Array.isArray(node)) return node.forEach(walk);
    if (!node || typeof node !== 'object') return;
    if (node.props && 'developerView' in node.props && 'turn' in node.props) views.push(node.props);
    walk(node.props?.children);
  }(view.type(view.props)));
  return views;
}

test('the page passes resend only to the latest research turn, and cancel is the composer stop button', (t) => {
  t.after(() => { delete globalThis.window; });
  const first = researchTurn(completed());
  const second = { ...researchTurn(completed()), id: 2, senpaiTurnId: '20000000-0000-4000-8000-000000000002' };
  const views = turnViews(chatPage({ snapshot: { ...base, turns: [first, second] } }));
  assert.equal(views.length, 2);
  assert.equal(views[0].onResend, undefined);
  assert.equal(typeof views[1].onResend, 'function');
  assert.equal(views[1].onCancel, undefined);

  const page = chatPage({ snapshot: { ...base, running: true, turns: [researchTurn({ status: 'running', steps: [], startedAt: NOW })] } });
  const running = turnViews(page);
  assert.equal(running[0].onResend, undefined);
  assert.equal(running[0].onCancel, undefined);
  const stop = findAny(page.render(), (node) => node.type === 'button' && node.props['aria-label'] === '中止');
  assert.ok(stop);
  stop.props.onClick();
  assert.equal(page.cancels.length, 1);
  assert.equal(html(page.render()).match(/aria-label="中止"/g).length, 1);
});

test('a supplement is shown in the bubble with a quiet note instead of the composed question', (t) => {
  t.after(() => { delete globalThis.window; });
  const turn = researchTurn(completed(), { query: '元\n補足: AXIEZです', supplement: 'AXIEZです', supplementOf: '元' });
  const out = html(chatPage({ snapshot: { ...base, turns: [turn] } }).render());
  assert.match(out, /AXIEZです/);
  assert.match(out, /元の質問に補足して検索/);
  assert.doesNotMatch(out, /補足: AXIEZです/);
});

test('field reports are offered on a finished research answer only, and only with their flag', (t) => {
  t.after(() => { delete globalThis.window; });
  const render = (turn, reportFlag = 'true') => withEnv('NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS', reportFlag, () => html(chatPage({ snapshot: { ...base, turns: [turn] } }).render()));
  assert.match(render(researchTurn(completed())), /aria-label="結果を残す"/);
  assert.doesNotMatch(render(researchTurn(completed()), 'false'), /結果を残す/);
  assert.doesNotMatch(render(researchTurn(completed({}, { kind: 'clarify', clarifyQuestions: ['q'], answerMarkdown: '' }))), /結果を残す/);
  assert.doesNotMatch(render(researchTurn({ status: 'failed', steps: [] })), /結果を残す/);
});

test('the empty state describes the research job and offers three example questions that fill the input', (t) => {
  t.after(() => { delete globalThis.window; });
  const page = chatPage({ snapshot: { ...base, turns: [] } });
  const out = html(page.render());
  assert.match(out, /質問の例/);
  assert.doesNotMatch(out, /技術KB・法令KBへ個別に送ります|法令KBにも個別に問い合わせます/);
  assert.match(out, /何を調べますか？/);
  assert.match(out, /機種: 指定なし/);
  const examples = [];
  (function walk(node) {
    if (Array.isArray(node)) return node.forEach(walk);
    if (!node || typeof node !== 'object') return;
    if (node.type === 'button' && typeof node.props.onClick === 'function' && /を|は/.test(textOf(node)) && textOf(node).length > 20) examples.push(node);
    walk(node.props?.children);
  }(expand(page.render())));
  assert.equal(examples.length, 3);
  examples[1].props.onClick();
  assert.equal(findAny(page.render(), (node) => node.type === 'textarea').props.value, textOf(examples[1]));
  const off = html(chatPage({ flag: 'false', snapshot: { ...base, turns: [] } }).render());
  assert.doesNotMatch(off, /質問の例/);
});

// ---- 仕上げ: 引用と句読点、押せる範囲、操作列の位置 ----

test('a run of ref pills and the punctuation right after it never wrap apart', () => {
  const page = view(completed({}, { answerMarkdown: '調整してください [T1] [L1]。次の文です[K1]、続き\n\n- 項目です[T1]）' }));
  assert.match(page, /調整してください<span class="whitespace-nowrap"><a [^>]*>技1<\/a><a [^>]*>法1<\/a>。<\/span>次の文です/);
  assert.match(page, /<span class="whitespace-nowrap"><a [^>]*>ノ1<\/a>、<\/span>続き/);
  assert.match(page, /<li>項目です<span class="whitespace-nowrap"><a [^>]*>技1<\/a>）<\/span><\/li>/);
  assert.doesNotMatch(page, /ください <span/);
  // 引用のない文や、番号の後ろに句読点がない文は、そのまま。
  const plain = view(completed({}, { answerMarkdown: '句読点のない文[T1] 続く文' }));
  assert.match(plain, /句読点のない文<span class="whitespace-nowrap"><a [^>]*>技1<\/a><\/span> 続く文/);
});

test('small links and buttons keep their look but get a larger invisible hit area', () => {
  const page = view(completed());
  assert.match(page, /<a href="#senpai-turn-1-ref-T1"[^>]*class="[^"]*relative[^"]*before:-inset-y-2/);
  assert.match(page, /aria-label="保守手順書：資料を開く"[^>]*class="[^"]*before:-inset-y-2\.5/);
  const failed = view({ status: 'failed', steps: [] }, { query: 'q', onResend() {} });
  assert.match(failed, /class="[^"]*before:-inset-y-2\.5[^"]*">もう一度試す</);
  const running = view({ status: 'running', startedAt: NOW, steps: [] });
  assert.match(running, /<summary class="flex min-h-8/);
});

test('the action bar comes last, after the sources and the knowhow', () => {
  const page = view(completed(), { query: '質問', onResend() {} });
  const bar = page.indexOf('aria-label="回答の操作"');
  assert.ok(bar > page.indexOf('aria-label="出典"'));
  assert.ok(bar > page.indexOf('ノウハウ 2件'));
  assert.ok(bar > page.indexOf('候補として渡したが使わなかったノウハウ'));
  assert.match(page.slice(bar), /aria-label="回答をコピー"[\s\S]*aria-label="もう一度調べる" title="もう一度調べる"/);
  assert.equal(page.slice(bar).includes('出典'), false);
  assert.doesNotMatch(view({ status: 'failed', steps: [] }, { query: 'q', onResend() {} }), /もう一度調べる/);
});

// ---- 2回目の見直し ----

test('menu dismissal closes on outside press and Escape, not on a press inside the menu', () => {
  const { attachMenuDismissal } = require('../src/lib/knowledge-senpai-menu.mjs');
  const listeners = {};
  const target = {
    addEventListener: (type, fn) => { listeners[type] = fn; },
    removeEventListener: (type) => { delete listeners[type]; },
  };
  let closed = 0;
  const detach = attachMenuDismissal(target, () => { closed += 1; });
  listeners.pointerdown({ target: { closest: (selector) => (selector === '[data-senpai-menu]' ? {} : null) } });
  assert.equal(closed, 0);
  listeners.pointerdown({ target: { closest: () => null } });
  listeners.pointerdown({ target: null });
  listeners.keydown({ key: 'Escape' });
  listeners.keydown({ key: 'a' });
  assert.equal(closed, 3);
  detach();
  assert.deepEqual(Object.keys(listeners), []);
});

test('the header menu reports its open state and closes after an item is chosen', () => {
  const { SenpaiChatHeader } = loadTsx('../src/components/knowledge/SenpaiChatHeader.tsx', { 'next/link': Link });
  const changes = [];
  let toggled = 0;
  const props = { sidebarOpen: false, onOpenSidebar() {}, onNewChat() {}, newChatDisabled: false, showDeveloperToggle: true, developerView: false, onToggleDeveloperView: () => { toggled += 1; }, menuOpen: true, onMenuOpenChange: (open) => changes.push(open) };
  const tree = expand(SenpaiChatHeader(props));
  const details = findAny(tree, (node) => node.type === 'details');
  assert.equal(details.props.open, true);
  assert.ok('data-senpai-menu' in details.props);
  details.props.onToggle({ currentTarget: { open: false } });
  assert.deepEqual(changes, [false]);
  findAny(tree, (node) => node.type === 'button' && node.props['aria-pressed'] !== undefined).props.onClick();
  assert.equal(toggled, 1);
  assert.deepEqual(changes, [false, false]);
  findAny(tree, (node) => node.props['aria-label'] === 'ホームへ戻る').props.onClick();
  findAny(tree, (node) => node.props['aria-label'] === 'ノウハウの確認・編集').props.onClick();
  assert.equal(changes.length, 4);
  assert.match(html(createElement(SenpaiChatHeader, { ...props, menuOpen: false })), /<details data-senpai-menu=""/);
  assert.doesNotMatch(html(createElement(SenpaiChatHeader, { ...props, showDeveloperToggle: false })), /開発者表示/);
});

test('after a clarify result the composer asks for a supplement', (t) => {
  t.after(() => { delete globalThis.window; });
  const placeholder = (turns) => findAny(chatPage({ snapshot: { ...base, turns } }).render(), (node) => node.type === 'textarea').props.placeholder;
  const clarify = completed({}, { kind: 'clarify', clarifyQuestions: ['機種は？'], answerMarkdown: '' });
  assert.equal(placeholder([researchTurn(clarify)]), '補足を入力（例: AXIEZ、走行中に発生）');
  assert.equal(placeholder([researchTurn(completed())]), '質問を入力');
  assert.equal(placeholder([]), '質問を入力');
});

test('legacy lanes render their text as safe markdown', () => {
  const { LaneReply } = loadTsx('../src/components/knowledge/SenpaiLegacyLanes.tsx', { 'next/link': Link });
  const answer = {
    mode: 'normal', query: 'q', content: '## 手順\n- 一つ目\n- 二つ目 [T1]\n\n<img src=x onerror=alert(1)>', responseType: 'pages',
    sessionId: 's', messageId: 'm', receivedAt: '2026-10-20T00:00:00Z', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [],
  };
  const out = html(createElement(LaneReply, { lane: { status: 'success', answer }, mode: 'normal' }));
  assert.match(out, /<h5[^>]*>手順<\/h5>/);
  assert.match(out, /<li>一つ目<\/li>/);
  assert.match(out, /\[T1\]/);
  assert.match(out, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.doesNotMatch(out, /<img/);
});

test('field report reactions are a compact segmented control with radio semantics', () => {
  const React = require('react');
  let calls = 0;
  const { SenpaiFieldReportForm } = loadTsx('../src/components/knowledge/SenpaiFieldReportForm.tsx', {
    react: { ...React, useState(initial) { calls += 1; return [calls === 1 ? true : typeof initial === 'function' ? initial() : initial, () => {}]; } },
    '@/lib/auth-helpers': { getIdToken: async () => 'token' },
  });
  const turn = {
    id: 1, senpaiTurnId: '20000000-0000-4000-8000-000000000001', query: 'q', normal: laneStub, law: laneStub,
    research: completed(),
  };
  const out = html(createElement(SenpaiFieldReportForm, { conversationId: '10000000-0000-4000-8000-000000000001', turn, onSent() {} }));
  assert.match(out, /role="radiogroup" aria-label="調整の勘所への反応"/);
  assert.equal(out.match(/role="radiogroup"/g).length, 2);
  assert.equal(out.match(/type="radio"/g).length, 6);
  for (const label of ['当てはまった', '当てはまらなかった', '分からない']) assert.equal(out.match(new RegExp(`>${label}</label>`, 'g')).length, 2);
  assert.match(out, /min-h-8/);
  assert.match(out, /name="field-report-1-KH-1001"/);
  assert.doesNotMatch(out, /この条件で当てはまった/);
});

test('the research disclaimer is one short line, and the legacy one keeps the local-file sentence', (t) => {
  t.after(() => { delete globalThis.window; });
  const research = html(chatPage({ snapshot: { ...base, turns: [] } }).render());
  assert.match(research, /重要な判断は出典で確認してください（ノウハウは未承認）/);
  assert.ok('重要な判断は出典で確認してください（ノウハウは未承認）'.length <= 30);
  const legacy = html(chatPage({ flag: 'false', snapshot: { ...base, turns: [] } }).render());
  assert.match(legacy, /ローカルファイルは送信されません。重要な判断は出典で確認してください/);
});
