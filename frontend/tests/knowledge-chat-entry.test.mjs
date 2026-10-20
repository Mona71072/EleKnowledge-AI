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
