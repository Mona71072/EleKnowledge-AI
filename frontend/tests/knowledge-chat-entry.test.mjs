import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';
import { parse } from 'yaml';

const require = createRequire(import.meta.url);

// Compile the real TSX with existing TypeScript; replace only framework/auth boundaries.
function loadTsx(path, mocks) {
  const filename = new URL(path, import.meta.url);
  const source = readFileSync(filename, 'utf8');
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename.pathname,
  });
  const compiledModule = { exports: {} };
  const localRequire = (name) => {
    if (Object.hasOwn(mocks, name)) return mocks[name];
    if (name === './SenpaiConversationSidebar') return loadTsx('../src/components/knowledge/SenpaiConversationSidebar.tsx', {});
    if (name === '@/data/kbModelTypes') return loadTsx('../src/data/kbModelTypes.ts', {});
    if (name === '@/lib/knowledge-senpai-synthesis.mjs') return { requestSenpaiSynthesis: async () => ({}) };
    if (name === '@/lib/knowledge-senpai-field-report.mjs') return require('../src/lib/knowledge-senpai-field-report.mjs');
    if (name === './SenpaiFieldReportForm') return loadTsx('../src/components/knowledge/SenpaiFieldReportForm.tsx', { '@/lib/auth-helpers': { getIdToken: async () => 'test-token' } });
    if (name === '@/hooks/useSenpaiHistory') return { useSenpaiHistory: () => ({ entries: [], loading: false, error: '', complete: true, opening: false, openError: '', openConversation: async () => {}, resetSelection() {}, refresh() {} }) };
    return require(name);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const Link = ({ children, href, ...props }) => createElement('a', { href, ...props }, children);

function findElement(root, predicate) {
  if (!root || typeof root !== 'object') return null;
  if (Array.isArray(root)) {
    for (const item of root) { const found = findElement(item, predicate); if (found) return found; }
    return null;
  }
  if (typeof root.type === 'string' && predicate(root)) return root;
  const children = root.props?.children;
  const list = Array.isArray(children) ? children : [children];
  for (const child of list) {
    const found = findElement(child, predicate);
    if (found) return found;
  }
  return null;
}

function loadInteractiveChat({ initialSnapshot, createController }) {
  const React = require('react');
  const slots = [];
  let hookIndex = 0;
  let effectStarted = false;
  const mockReact = {
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
      hookIndex += 1;
      if (!effectStarted) {
        effectStarted = true;
        effect();
      }
    },
  };
  const Chat = loadTsx('../src/components/knowledge/KnowledgeSenpaiChat.tsx', {
    react: mockReact,
    'next/link': Link,
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
    '@/lib/chat-session-link.mjs': { buildChatSessionHref: (sessionId, mode) => `/chat?session=${encodeURIComponent(sessionId)}${mode === 'law' ? '&mode=law' : ''}` },
    '@/lib/knowledge-senpai-chat.mjs': { createSenpaiChat: ({ onChange }) => createController(initialSnapshot, onChange) },
    '@/lib/knowledge-research.mjs': {
      queryKnowledgeSource: async () => ({}),
      researchSourceHref: (source, mode) => mode === 'law' ? source.lawCitation?.sourceUrl : '/doc?uri=encoded',
    },
  }).KnowledgeSenpaiChat;
  return () => {
    hookIndex = 0;
    return Chat();
  };
}

function lane(status, extra = {}) {
  return { status, ...extra };
}

const entry = () => loadTsx('../src/components/knowledge/KnowledgeChatEntry.tsx', {
  'next/link': Link,
  '@/components/ui/Card': { Card: ({ children, className }) => createElement('div', { className }, children) },
}).KnowledgeChatEntry;

test('Amplify dev deployment enables the real Senpai entry for admins only', () => {
  const buildSpec = parse(readFileSync(new URL('../../amplify.yml', import.meta.url), 'utf8'));
  const variables = buildSpec.env.variables;
  assert.match(variables.NEXT_PUBLIC_RAG_API_URL, /\/dev$/);
  const enabled = variables.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH === 'true';
  const Entry = entry();
  assert.match(renderToStaticMarkup(createElement(Entry, { isAdmin: true, enabled })), /href="\/knowledge\/chat"/);
  assert.equal(renderToStaticMarkup(createElement(Entry, { isAdmin: false, enabled })), '');
});

test('admin sees a user-side chat entry when the development flag is enabled', () => {
  const html = renderToStaticMarkup(createElement(entry(), { isAdmin: true, enabled: true }));
  assert.match(html, /href="\/knowledge\/chat"/);
  assert.match(html, /先輩チャット/);
  assert.match(html, /開発中/);
  assert.match(html, /管理者/);
  assert.match(html, /技術KBや法令KBについて会話形式で質問/);
  assert.doesNotMatch(html, /Markdownを選ぶ|編集案へ取り込/);
});

test('nonadmins and unresolved membership see no chat entry or placeholder', () => {
  for (const isAdmin of [false, undefined]) {
    assert.equal(renderToStaticMarkup(createElement(entry(), { isAdmin, enabled: true })), '');
  }
});

test('disabled or unspecified flag hides the entry even from admins', () => {
  for (const enabled of [false, undefined]) {
    assert.equal(renderToStaticMarkup(createElement(entry(), { isAdmin: true, enabled })), '');
  }
});

function renderRoute(gate, enabled) {
  const previous = process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH;
  process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH = enabled;
  let chatRenders = 0;
  try {
    const { AdminOnlyGuard } = loadTsx('../src/components/auth/AdminOnlyGuard.tsx', {
      'next/link': Link,
      '@/components/ui/Loading': { Loading: ({ text }) => createElement('p', null, text) },
      '@/hooks/useAdminGate': { useAdminGate: () => gate },
    });
    const Layout = loadTsx('../src/app/knowledge/chat/layout.tsx', {
      '@/components/auth/AdminOnlyGuard': { AdminOnlyGuard },
    }).default;
    const Page = loadTsx('../src/app/knowledge/chat/page.tsx', {
      'next/link': Link,
      '@/components/knowledge/KnowledgeSenpaiChat': {
        KnowledgeSenpaiChat: () => {
          chatRenders += 1;
          return createElement('section', { 'aria-label': '先輩チャット' }, createElement('form', { 'aria-label': '先輩への質問' }));
        },
      },
    }).default;
    return { html: renderToStaticMarkup(createElement(Layout, null, createElement(Page))), chatRenders };
  } finally {
    if (previous === undefined) delete process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH;
    else process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH = previous;
  }
}

test('direct user-side route mounts a conversational chat for admins', () => {
  const { html, chatRenders } = renderRoute('ok', 'true');
  assert.equal(chatRenders, 1);
  assert.match(html, /aria-label="先輩チャット"/);
  assert.match(html, /aria-label="先輩への質問"/);
  assert.doesNotMatch(html, /href="\/admin|Markdownを選ぶ/);
});

test('direct route denies nonadmins before mounting the question/editor UI', () => {
  const { html, chatRenders } = renderRoute('denied', 'true');
  assert.equal(chatRenders, 0);
  assert.match(html, /管理者権限が必要です/);
  assert.doesNotMatch(html, /<form/);
});

test('membership pending, including login redirect, never mounts the workspace', () => {
  const { html, chatRenders } = renderRoute('loading', 'true');
  assert.equal(chatRenders, 0);
  assert.match(html, /読み込み中/);
  assert.doesNotMatch(html, /<form/);
});

test('disabled route explains availability without mounting the workspace', () => {
  for (const enabled of ['false', '', 'TRUE']) {
    const { html, chatRenders } = renderRoute('ok', enabled);
    assert.equal(chatRenders, 0);
    assert.match(html, /無効/);
    assert.match(html, /href="\/"/);
    assert.doesNotMatch(html, /<form/);
  }
});

test('chat page starts as an empty conversation with a message composer and reset action', () => {
  const Chat = loadTsx('../src/components/knowledge/KnowledgeSenpaiChat.tsx', {
    'next/link': Link,
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
    '@/lib/chat-session-link.mjs': { buildChatSessionHref: (sessionId, mode) => `/chat?session=${encodeURIComponent(sessionId)}${mode === 'law' ? '&mode=law' : ''}` },
    '@/lib/knowledge-senpai-chat.mjs': {
      createSenpaiChat: () => ({ getSnapshot: () => ({ turns: [], running: false }), send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
    },
    '@/lib/knowledge-research.mjs': { queryKnowledgeSource: async () => ({}), researchSourceHref: () => null },
  }).KnowledgeSenpaiChat;
  const html = renderToStaticMarkup(createElement(Chat));

  assert.match(html, /aria-label="先輩チャット"/);
  assert.match(html, /aria-label="質問を入力"/);
  assert.match(html, /質問を送信/);
  assert.match(html, /新しい相談/);
  assert.match(html, /href="\/"/);
  assert.match(html, /技術KB/);
  assert.match(html, /法令KB/);
  assert.doesNotMatch(html, /Markdownファイルを選択|照合まとめ/);
});

test('Senpai chat opts normal searches into the server Markdown index and leaves law searches unchanged', async () => {
  const React = require('react');
  let querySource;
  const Chat = loadTsx('../src/components/knowledge/KnowledgeSenpaiChat.tsx', {
    react: {
      ...React,
      useEffect(effect) { effect(); },
      useState(initial) { return [initial, () => {}]; },
      useRef(initial) { return { current: initial }; },
    },
    'next/link': Link,
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
    '@/lib/chat-session-link.mjs': { buildChatSessionHref: () => '/chat' },
    '@/lib/knowledge-senpai-chat.mjs': {
      createSenpaiChat: (options) => {
        querySource = options.querySource;
        return { getSnapshot: () => ({ turns: [], running: false }), send: async () => {}, cancel() {}, reset() {}, dispose() {} };
      },
    },
    '@/lib/knowledge-research.mjs': { queryKnowledgeSource: async (options) => options, researchSourceHref: () => null },
  }).KnowledgeSenpaiChat;
  Chat();
  const normal = await querySource({ mode: 'normal', query: '質問', signal: new AbortController().signal });
  const law = await querySource({ mode: 'law', query: '質問', signal: new AbortController().signal });

  assert.equal(normal.includeKnowhow, true);
  assert.equal(law.includeKnowhow, undefined);
});

test('renders returned Markdown as escaped collapsed text with status, identity, scope, and source references', () => {
  const answer = {
    mode: 'normal', query: '設置条件', content: '技術KB回答', responseType: 'pages', sessionId: 'session-tech',
    messageId: 'm1', receivedAt: '2026-10-20T00:00:00Z', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [],
    knowhow: {
      status: 'matched', indexVersion: `sha256:${'a'.repeat(64)}`, searchTerms: ['設置条件'],
      matches: [{
        knowledgeId: 'KH-1001', cardVersion: 3, sha256: 'b'.repeat(64), title: '仮設材の固定',
        status: 'draft', usage: 'navigation_only', body: '<img src=x onerror=alert(1)>本文',
        searchTerms: ['仮設材'], sourceRefs: [{ ref_type: 'lists_item', list_item_id: 'L-1', source_id: 'SRC-1' }],
        modelScope: { model_abbreviations: ['M1'], excludes: ['M1R'] },
      }],
    },
  };
  const initialSnapshot = { running: false, turns: [{ id: 1, query: '設置条件', normal: lane('success', { answer }), law: lane('paused') }] };
  const render = loadInteractiveChat({
    initialSnapshot,
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.match(html, /参照したノウハウMarkdown/);
  assert.match(html, /KH-1001/);
  assert.match(html, /仮設材の固定/);
  assert.match(html, /未承認/);
  assert.match(html, /参照用のみ/);
  assert.match(html, /除外/);
  assert.match(html, /SRC-1/);
  assert.match(html, /<details/);
  assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;本文/);
  assert.doesNotMatch(html, /<img\b|href="javascript:/);
  assert.match(html, /技術的な根拠や承認を示しません/);
});

test('explains that Markdown retrieval is server-authorized and does not upload a local vault or edit files', () => {
  const Chat = loadTsx('../src/components/knowledge/KnowledgeSenpaiChat.tsx', {
    'next/link': Link,
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
    '@/lib/chat-session-link.mjs': { buildChatSessionHref: () => '/chat' },
    '@/lib/knowledge-senpai-chat.mjs': {
      createSenpaiChat: () => ({ getSnapshot: () => ({ turns: [], running: false }), send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
    },
    '@/lib/knowledge-research.mjs': { queryKnowledgeSource: async () => ({}), researchSourceHref: () => null },
  }).KnowledgeSenpaiChat;
  const html = renderToStaticMarkup(createElement(Chat));

  assert.match(html, /サーバーで検索が許可されたノウハウMarkdown/);
  assert.match(html, /参考に技術KBを調べ/);
  assert.match(html, /ローカルファイルは送信されません/);
  assert.match(html, /Markdownの編集やOneNoteへの追記は行いません/);
});

test('pending first reply does not say both searches failed or ask to start over', () => {
  const initialSnapshot = {
    running: true,
    turns: [{ id: 1, query: '最初の質問', normal: lane('loading'), law: lane('loading') }],
  };
  const render = loadInteractiveChat({
    initialSnapshot,
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.match(html, /技術KBを検索しています/);
  assert.match(html, /法令KBを検索しています/);
  assert.doesNotMatch(html, /両方の検索が失敗または中止/);
});

test('late completion from an old相談 does not erase a newer draft', async () => {
  const initialSnapshot = { turns: [], running: false };
  let finishSend;
  const render = loadInteractiveChat({
    initialSnapshot,
    createController: (snapshot, onChange) => ({
      getSnapshot: () => snapshot,
      send: (query) => {
        onChange({ turns: [{ id: 1, query, normal: lane('loading'), law: lane('loading') }], running: true });
        return new Promise((resolve) => { finishSend = resolve; });
      },
      cancel() {},
      reset() { onChange({ turns: [], running: false }); },
      dispose() {},
    }),
  });

  const root = render();
  const input = findElement(root, (element) => element.type === 'textarea' && element.props['aria-label'] === '質問を入力');
  input.props.onChange({ target: { value: '古い相談の質問' } });
  let view = render();
  const form = findElement(view, (element) => element.type === 'form' && element.props.onSubmit);
  const sending = form.props.onSubmit({ preventDefault() {} });
  view = render();
  const reset = findElement(view, (element) => element.type === 'button' && element.props.children === '新しい相談');
  reset.props.onClick();
  view = render();
  const newInput = findElement(view, (element) => element.type === 'textarea' && element.props['aria-label'] === '質問を入力');
  newInput.props.onChange({ target: { value: '新しい相談の下書き' } });
  finishSend();
  await sending;
  view = render();

  assert.equal(findElement(view, (element) => element.type === 'textarea' && element.props['aria-label'] === '質問を入力').props.value, '新しい相談の下書き');
});

test('optional model select defaults to unspecified and offers the six UI model keys', () => {
  const render = loadInteractiveChat({
    initialSnapshot: { turns: [], running: false },
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.match(html, /機種（任意）/);
  assert.match(html, /<option value="" selected="">指定しない<\/option>|<option value="">指定しない<\/option>/);
  for (const key of ['AXIEZ', 'AXIEZ-LINKs', 'NEXCUBE', 'メルシティ', 'メルワイド', 'エスカレーター']) {
    assert.match(html, new RegExp(`<option value="${key}"`));
  }
});

test('chosen model is sent only when non-empty and is kept across turns', async () => {
  const sent = [];
  const render = loadInteractiveChat({
    initialSnapshot: { turns: [], running: false },
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async (...args) => { sent.push(args); }, cancel() {}, reset() {}, dispose() {} }),
  });
  const submitWith = async (question) => {
    findElement(render(), (el) => el.type === 'textarea').props.onChange({ target: { value: question } });
    await findElement(render(), (el) => el.type === 'form').props.onSubmit({ preventDefault() {} });
  };
  render();
  await submitWith('指定なし');
  findElement(render(), (el) => el.type === 'select').props.onChange({ target: { value: 'NEXCUBE' } });
  await submitWith('NEXCUBE一回目');
  await submitWith('NEXCUBE二回目');

  assert.deepEqual(sent, [['指定なし'], ['NEXCUBE一回目', { modelType: 'NEXCUBE' }], ['NEXCUBE二回目', { modelType: 'NEXCUBE' }]]);
});

test('Senpai chat forwards the model type to the research query', async () => {
  const React = require('react');
  let querySource;
  const Chat = loadTsx('../src/components/knowledge/KnowledgeSenpaiChat.tsx', {
    react: { ...React, useEffect(effect) { effect(); }, useState(initial) { return [initial, () => {}]; }, useRef(initial) { return { current: initial }; } },
    'next/link': Link,
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
    '@/lib/chat-session-link.mjs': { buildChatSessionHref: () => '/chat' },
    '@/lib/knowledge-senpai-chat.mjs': {
      createSenpaiChat: (options) => {
        querySource = options.querySource;
        return { getSnapshot: () => ({ turns: [], running: false }), send: async () => {}, cancel() {}, reset() {}, dispose() {} };
      },
    },
    '@/lib/knowledge-research.mjs': { queryKnowledgeSource: async (options) => options, researchSourceHref: () => null },
  }).KnowledgeSenpaiChat;
  Chat();
  const withModel = await querySource({ mode: 'normal', query: '質問', modelType: 'AXIEZ', signal: new AbortController().signal });
  const without = await querySource({ mode: 'normal', query: '質問', signal: new AbortController().signal });

  assert.equal(withModel.modelType, 'AXIEZ');
  assert.equal(Object.hasOwn(without, 'modelType'), false);
});

test('a turn shows the model it was filtered by only when one was chosen', () => {
  const render = loadInteractiveChat({
    initialSnapshot: {
      running: false,
      turns: [
        { id: 1, query: '指定あり', modelType: 'AXIEZ', normal: lane('loading'), law: lane('loading') },
        { id: 2, query: '指定なし', normal: lane('loading'), law: lane('loading') },
      ],
    },
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.equal((html.match(/機種: /g) || []).length, 1);
  assert.match(html, /機種: AXIEZ/);
});

test('safe lane errors are shown and a healthy lane answer remains visible', () => {
  const initialSnapshot = {
    running: false,
    turns: [{ id: 1, query: '故障時の確認手順', normal: lane('success', { answer: { mode: 'normal', query: '故障時の確認手順', content: '技術側で確認できた回答', responseType: 'pages', sessionId: 'session-tech', messageId: 'm1', receivedAt: '2026-10-20T00:00:00Z', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [] } }), law: lane('error', { message: '法令KBを利用できません。接続設定・APIの有効化・権限を確認してください。' }) }],
  };
  const render = loadInteractiveChat({
    initialSnapshot,
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.match(html, /技術側で確認できた回答/);
  assert.match(html, /法令KBを利用できません。接続設定・APIの有効化・権限を確認してください。/);
});

test('Senpai chat has a left conversation history and keeps saved consultations after reload', () => {
  const initialSnapshot = { turns: [], running: false };
  const render = loadInteractiveChat({
    initialSnapshot,
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.match(html, /60日/);
  assert.match(html, /再読み込み/);
  assert.match(html, /aria-label="相談履歴"/);
  assert.match(html, /履歴を開く/);
  assert.doesNotMatch(html, /まとめ表示は保存されない|再読み込みすると表示が消えます/);
});

test('law source displays the returned law number, provision reference, and effective date', () => {
  const lawSource = {
    lawCitation: {
      lawId: 'SYNTHLAW0001', lawTitle: 'サンプル法', lawNumber: '令和八年法律第一号',
      provisionType: 'Article', provisionReference: '第十二条', effectiveDate: '2026-04-01',
      sourceUrl: 'https://elaws.e-gov.go.jp/document?lawid=SYNTHLAW0001',
    },
  };
  const initialSnapshot = {
    running: false,
    turns: [{ id: 1, query: '根拠法令は？', normal: lane('paused'), law: lane('success', { answer: { mode: 'law', query: '根拠法令は？', content: '法令回答', responseType: 'pages', sessionId: 'session-law', messageId: 'm2', receivedAt: '2026-10-20T00:00:00Z', sourceDocuments: [lawSource], pageCandidates: [], clarifyQuestions: [] } }) }],
  };
  const render = loadInteractiveChat({
    initialSnapshot,
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.match(html, /令和八年法律第一号/);
  assert.match(html, /第十二条/);
  assert.match(html, /2026-04-01/);
});

test('history sidebar selects the requested consultation, escapes titles, and distinguishes errors from empty history', () => {
  const { SenpaiConversationSidebar } = loadTsx('../src/components/knowledge/SenpaiConversationSidebar.tsx', {});
  const selected = [];
  const props = {
    open: true, entries: [{ conversationId: '11111111-1111-4111-8111-111111111111', title: '<img src=x>質問', createdAt: '2026-10-20T00:00:00Z', lastMessageTime: '2026-10-20T00:00:00Z', messageCount: 2, daysUntilDeletion: 59 }],
    selectedId: '11111111-1111-4111-8111-111111111111', loading: false, error: '', complete: true,
    onNew() {}, onSelect: (id) => selected.push(id), onClose() {}, onRetry() {},
  };
  const tree = SenpaiConversationSidebar(props);
  const current = findElement(tree, (element) => element.type === 'button' && element.props['aria-current'] === 'page');
  current.props.onClick();
  assert.deepEqual(selected, [props.selectedId]);
  const html = renderToStaticMarkup(tree);
  assert.match(html, /&lt;img src=x&gt;質問/);
  assert.doesNotMatch(html, /<img\b/);
  assert.match(html.replace(/<!--.*?-->/gu, ''), /2件の質問/);
  assert.match(html, /履歴メニューを閉じる/);
  const failed = renderToStaticMarkup(createElement(SenpaiConversationSidebar, { ...props, entries: [], error: '履歴の取得失敗' }));
  assert.match(failed, /履歴の取得失敗/);
  assert.match(failed, /履歴を再取得/);
  assert.doesNotMatch(failed, /履歴はまだありません/);
});


function findAnyElement(root, predicate) {
  if (!root || typeof root !== 'object') return null;
  if (Array.isArray(root)) {
    for (const item of root) { const found = findAnyElement(item, predicate); if (found) return found; }
    return null;
  }
  if (root.props && predicate(root)) return root;
  const children = root.props?.children;
  for (const child of Array.isArray(children) ? children : [children]) {
    const found = findAnyElement(child, predicate);
    if (found) return found;
  }
  return null;
}

const TURN_UUID = '20000000-0000-4000-8000-000000000001';
const baseAnswer = (mode) => ({
  mode, query: '質問', content: `${mode}回答`, responseType: 'pages', sessionId: `${mode}-s`, messageId: `${mode}-m`,
  receivedAt: '2026-10-20T00:00:00Z', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [],
});

function synthesisChat(turnOverrides = {}, { running = false, synthesisFlag = 'true' } = {}) {
  const calls = [];
  const turn = {
    id: 1, senpaiTurnId: TURN_UUID, query: '質問',
    normal: lane('success', { answer: baseAnswer('normal') }),
    law: lane('success', { answer: baseAnswer('law') }),
    ...turnOverrides,
  };
  const snapshot = { conversationId: '10000000-0000-4000-8000-000000000001', running, turns: [turn] };
  const render = withSynthesisFlag(synthesisFlag, () => loadInteractiveChat({
    initialSnapshot: snapshot,
    createController: (initial) => ({
      getSnapshot: () => initial, send: async () => {}, cancel() {}, reset() {}, dispose() {},
      synthesize: async (id) => { calls.push(id); },
    }),
  }));
  render();
  return { render, calls };
}

function withSynthesisFlag(value, fn) {
  const previous = process.env.NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS;
  if (value == null) delete process.env.NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS;
  else process.env.NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS = value;
  try { return fn(); } finally {
    if (previous === undefined) delete process.env.NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS;
    else process.env.NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS = previous;
  }
}

test('the synthesis button is hidden unless the development flag is on, but a saved synthesis still shows', () => {
  for (const synthesisFlag of [null, 'false']) {
    assert.doesNotMatch(html(synthesisChat({}, { synthesisFlag }).render), /工技先輩のまとめを作る/);
    const saved = html(synthesisChat({ synthesis: { status: 'success', content: '保存済みのまとめ', messageId: `senpai-synthesis-${TURN_UUID}` } }, { synthesisFlag }).render);
    assert.match(saved, /保存済みのまとめ/);
  }
});

const html = (render) => renderToStaticMarkup(render());

test('offers a manual synthesis button only when both lanes settled and one succeeded', () => {
  assert.match(html(synthesisChat().render), /工技先輩のまとめを作る/);
  assert.match(html(synthesisChat({ law: lane('error', { message: 'x' }) }).render), /工技先輩のまとめを作る/);
  assert.doesNotMatch(html(synthesisChat({}, { running: true }).render), /工技先輩のまとめを作る/);
  assert.doesNotMatch(html(synthesisChat({ law: lane('loading') }).render), /工技先輩のまとめを作る/);
  assert.doesNotMatch(html(synthesisChat({ normal: lane('error'), law: lane('cancelled') }).render), /工技先輩のまとめを作る/);
  assert.doesNotMatch(html(synthesisChat({ senpaiTurnId: undefined }).render), /工技先輩のまとめを作る/);
});

test('the synthesis button asks the controller to synthesize that turn', () => {
  const { render, calls } = synthesisChat();
  const element = findAnyElement(render(), (node) => typeof node.props.onSynthesize === 'function');
  assert.ok(element);
  element.props.onSynthesize(1);
  assert.deepEqual(calls, [1]);
});

test('renders loading, error with retry, and a saved synthesis above the lane columns', () => {
  const loading = html(synthesisChat({ synthesis: { status: 'loading' } }).render);
  assert.match(loading, /まとめを作成しています/);
  assert.doesNotMatch(loading, /工技先輩のまとめを作る/);

  const failed = html(synthesisChat({ synthesis: { status: 'error', message: '時間内に完了しませんでした' } }).render);
  assert.match(failed, /時間内に完了しませんでした/);
  assert.match(failed, /工技先輩のまとめを作る/);

  const done = html(synthesisChat({ synthesis: {
    status: 'success', content: '<b>候補</b>です\n改行', messageId: `senpai-synthesis-${TURN_UUID}`,
    inputs: { normal: true, law: false, knowhowCount: 2 },
  } }).render);
  assert.match(done, /工技先輩のまとめ（試作・開発中）/);
  assert.match(done, /下の2つの回答を組み合わせただけ/);
  assert.match(done, /出典で確認/);
  assert.match(done, /&lt;b&gt;候補&lt;\/b&gt;です/);
  assert.doesNotMatch(done, /<b>候補/);
  assert.doesNotMatch(done, /工技先輩のまとめを作る/);
  assert.match(done, /法令KBの回答は使っていません/);
  assert.ok(done.indexOf('工技先輩のまとめ（試作・開発中）') < done.indexOf('技術KBからの回答'));
});

test('wires the synthesis source to the RAG API with the id token', async () => {
  const React = require('react');
  let synthesisSource;
  const requests = [];
  const Chat = loadTsx('../src/components/knowledge/KnowledgeSenpaiChat.tsx', {
    react: { ...React, useEffect(effect) { effect(); }, useState(initial) { return [initial, () => {}]; }, useRef(initial) { return { current: initial }; } },
    'next/link': Link,
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
    '@/lib/chat-session-link.mjs': { buildChatSessionHref: () => '/chat' },
    '@/lib/knowledge-senpai-chat.mjs': {
      createSenpaiChat: (options) => {
        synthesisSource = options.synthesisSource;
        return { getSnapshot: () => ({ turns: [], running: false }), send: async () => {}, cancel() {}, reset() {}, dispose() {} };
      },
    },
    '@/lib/knowledge-senpai-synthesis.mjs': { requestSenpaiSynthesis: async (options) => { requests.push(options); return {}; } },
    '@/lib/knowledge-research.mjs': { queryKnowledgeSource: async () => ({}), researchSourceHref: () => null },
  }).KnowledgeSenpaiChat;
  Chat();
  const signal = new AbortController().signal;
  await synthesisSource({ senpaiConversationId: 'c', senpaiTurnId: 't', signal });
  assert.equal(requests[0].senpaiConversationId, 'c');
  assert.equal(requests[0].senpaiTurnId, 't');
  assert.equal(requests[0].signal, signal);
  assert.equal(await requests[0].getToken(), 'test-token');
});

test('labels the new scope-verification keys and never renders an undefined label', () => {
  const answer = {
    ...baseAnswer('normal'),
    knowhow: {
      status: 'matched', indexVersion: `sha256:${'a'.repeat(64)}`, searchTerms: [],
      matches: [{
        knowledgeId: 'KH-1', cardVersion: 1, sha256: 'b'.repeat(64), title: 'カード', status: 'draft',
        usage: 'navigation_only', body: '本文', searchTerms: [],
        sourceRefs: [{ ref_type: 'x', brand_new_ref: 'R1' }],
        modelScope: {
          scope_status: 'verified', scope_verified_by: '山田', scope_verified_at: '2026-10-19', future_scope_key: ['A', 'B'],
        },
      }],
    },
  };
  const verified = html(synthesisChat({ normal: lane('success', { answer }) }).render);
  assert.match(verified, /適用範囲の確認/);
  assert.match(verified, /担当者確認済み/);
  assert.match(verified, /確認者/);
  assert.match(verified, /確認日/);
  assert.match(verified, /future_scope_key/);
  assert.match(verified, /brand_new_ref/);
  assert.doesNotMatch(verified, /undefined/);

  const unverified = structuredClone(answer);
  unverified.knowhow.matches[0].modelScope = { scope_status: 'pending' };
  assert.match(html(synthesisChat({ normal: lane('success', { answer: unverified }) }).render), /未確認/);
});

function withFieldReportsFlag(value, fn) {
  const previous = process.env.NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS;
  if (value === undefined) delete process.env.NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS;
  else process.env.NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS = value;
  try { return fn(); } finally {
    if (previous === undefined) delete process.env.NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS;
    else process.env.NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS = previous;
  }
}

test('「結果を残す」 is hidden unless the development flag is on', () => {
  for (const flag of [undefined, 'false']) {
    withFieldReportsFlag(flag, () => assert.doesNotMatch(html(synthesisChat().render), /結果を残す/));
  }
});

test('「結果を残す」 appears only after a settled turn with at least one answer', () => {
  withFieldReportsFlag('true', () => {
    assert.match(html(synthesisChat().render), /結果を残す/);
    assert.match(html(synthesisChat({ law: lane('error', { message: 'x' }) }).render), /結果を残す/);
    assert.doesNotMatch(html(synthesisChat({}, { running: true }).render), /結果を残す/);
    assert.doesNotMatch(html(synthesisChat({ law: lane('loading') }).render), /結果を残す/);
    assert.doesNotMatch(html(synthesisChat({ normal: lane('error'), law: lane('cancelled') }).render), /結果を残す/);
    assert.doesNotMatch(html(synthesisChat({ senpaiTurnId: undefined }).render), /結果を残す/);
  });
});

test('the field report form starts closed, copies nothing, and shows a sent report as unconfirmed', () => {
  const { SenpaiFieldReportForm } = loadTsx('../src/components/knowledge/SenpaiFieldReportForm.tsx', {
    '@/lib/auth-helpers': { getIdToken: async () => 'test-token' },
  });
  const turn = {
    id: 1, senpaiTurnId: TURN_UUID, query: '相談本文ZZZ', modelType: 'NEXCUBE',
    normal: lane('success', { answer: baseAnswer('normal') }), law: lane('success', { answer: baseAnswer('law') }),
  };
  const conversationId = '10000000-0000-4000-8000-000000000001';
  const closed = renderToStaticMarkup(createElement(SenpaiFieldReportForm, { conversationId, turn, onSent() {} }));
  assert.match(closed, /<button[^>]*>結果を残す<\/button>/);
  assert.doesNotMatch(closed, /相談本文ZZZ|textarea/);
  const sent = renderToStaticMarkup(createElement(SenpaiFieldReportForm, {
    conversationId, turn, onSent() {},
    sent: { reportId: 'r', senpaiConversationId: conversationId, senpaiTurnId: TURN_UUID, createdAt: '2026-10-20T00:00:00Z', finding: 'x', reviewState: 'unconfirmed', cardReactions: [] },
  }));
  assert.match(sent, /送信済みです（未確認）/);
  assert.doesNotMatch(sent, /<button/);
  assert.equal(renderToStaticMarkup(createElement(SenpaiFieldReportForm, { turn, onSent() {} })), '');
});
