import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';

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
  const localRequire = (name) => Object.hasOwn(mocks, name) ? mocks[name] : require(name);
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const Link = ({ children, href, ...props }) => createElement('a', { href, ...props }, children);

function findElement(root, predicate) {
  if (!root || typeof root !== 'object') return null;
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
  assert.match(html, /href="\/"/);
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
      status: 'matched', indexVersion: 'a'.repeat(64), searchTerms: ['設置条件'],
      matches: [{
        knowledgeId: 'KH-<img src=x>', cardVersion: 3, sha256: 'b'.repeat(64), title: '仮設材の固定',
        status: 'draft', usage: 'navigation_only', body: '<img src=x onerror=alert(1)>本文',
        searchTerms: ['仮設材'], sourceRefs: [{ type: 'Lists', id: 'L-1', title: '不具合一覧' }],
        modelScope: { models: ['M1'], excludes: ['M1R'] },
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
  assert.match(html, /KH-&lt;img src=x&gt;/);
  assert.match(html, /仮設材の固定/);
  assert.match(html, /未承認/);
  assert.match(html, /参照用のみ/);
  assert.match(html, /除外/);
  assert.match(html, /不具合一覧/);
  assert.match(html, /<details/);
  assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;本文/);
  assert.doesNotMatch(html, /<img\b|href="javascript:/);
  assert.match(html, /承認済み資料ではありません/);
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
  assert.match(html, /関連部分をAIへの参考情報として利用/);
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

test('chat explains separate history retention and that its combined transcript is local to this page', () => {
  const initialSnapshot = { turns: [], running: false };
  const render = loadInteractiveChat({
    initialSnapshot,
    createController: (snapshot) => ({ getSnapshot: () => snapshot, send: async () => {}, cancel() {}, reset() {}, dispose() {} }),
  });
  render();
  const html = renderToStaticMarkup(render());

  assert.match(html, /60日/);
  assert.match(html, /再読み込み/);
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
