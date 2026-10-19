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
  assert.match(html, /工技先輩/);
  assert.match(html, /開発中/);
  assert.match(html, /管理者/);
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
  let workbenchRenders = 0;
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
      '@/components/knowledge/KnowledgeWorkbench': {
        KnowledgeWorkbench: ({ research }) => {
          workbenchRenders += 1;
          assert.equal(research, true);
          return createElement('form', { 'aria-label': 'KB質問' });
        },
      },
    }).default;
    return { html: renderToStaticMarkup(createElement(Layout, null, createElement(Page))), workbenchRenders };
  } finally {
    if (previous === undefined) delete process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH;
    else process.env.NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH = previous;
  }
}

test('direct user-side route mounts the shared research workspace for admins', () => {
  const { html, workbenchRenders } = renderRoute('ok', 'true');
  assert.equal(workbenchRenders, 1);
  assert.match(html, /aria-label="KB質問"/);
  assert.match(html, /href="\/"/);
  assert.doesNotMatch(html, /href="\/admin/);
});

test('direct route denies nonadmins before mounting the question/editor UI', () => {
  const { html, workbenchRenders } = renderRoute('denied', 'true');
  assert.equal(workbenchRenders, 0);
  assert.match(html, /管理者権限が必要です/);
  assert.doesNotMatch(html, /<form/);
});

test('membership pending, including login redirect, never mounts the workspace', () => {
  const { html, workbenchRenders } = renderRoute('loading', 'true');
  assert.equal(workbenchRenders, 0);
  assert.match(html, /読み込み中/);
  assert.doesNotMatch(html, /<form/);
});

test('disabled route explains availability without mounting the workspace', () => {
  for (const enabled of ['false', '', 'TRUE']) {
    const { html, workbenchRenders } = renderRoute('ok', enabled);
    assert.equal(workbenchRenders, 0);
    assert.match(html, /無効/);
    assert.match(html, /href="\/"/);
    assert.doesNotMatch(html, /<form/);
  }
});
