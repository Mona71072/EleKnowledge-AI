import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';

const require = createRequire(import.meta.url);

function loadComponent(name) {
  const file = new URL(`../src/components/knowledge/${name}.tsx`, import.meta.url);
  const { outputText } = ts.transpileModule(readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: file.pathname,
  });
  const compiledModule = { exports: {} };
  const localRequire = (id) => {
    if (id === '@/components/ui/Button') return { Button: ({ variant: _variant, size: _size, ...props }) => createElement('button', props) };
    if (id.startsWith('@/lib/')) return require(`../src/lib/${id.slice(6)}`);
    if (id === 'next/link') return function Link({ children, ...props }) { return createElement('a', props, children); };
    if (id.startsWith('./')) return loadComponent(id.slice(2));
    return require(id);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const answer = { mode: 'normal', responseType: 'pages', content: '固定状態を記録する。', receivedAt: '2026-11-14T11:00:00Z', sourceDocuments: [{ documentName: 'SUE-3-17.pdf', pageNumber: 4, sourceUri: 's3://technical-kb/SUE-3-17.pdf' }], pageCandidates: [] };
const noop = () => {};

test('コメントの追記案は既定で未確認。「確認して追記する」「追記しない」の両方が未選択で、AI回答の注記を出す', () => {
  const { CommentCandidate } = loadComponent('KnowledgeCommentCandidate');
  const html = renderToStaticMarkup(createElement(CommentCandidate, { answer, decision: undefined, onDecide: noop, onEdit: noop }));
  assert.match(html, /AI が KB を検索した結果です。出典を確認してから追記してください。/);
  assert.match(html, /確認して追記する/);
  assert.match(html, /追記しない/);
  assert.match(html, /未確認/);
  assert.equal(html.match(/aria-pressed="false"/g).length, 2);
  assert.doesNotMatch(html, /aria-pressed="true"/);
  assert.match(html, /管理者が出典を確認/);
  assert.doesNotMatch(html, /原資料未確認|AI追記案/);
});

test('選んだ確認結果を押下表示と文言で示す', () => {
  const { CommentCandidate } = loadComponent('KnowledgeCommentCandidate');
  const confirmed = renderToStaticMarkup(createElement(CommentCandidate, { answer, decision: 'confirm', onDecide: noop, onEdit: noop }));
  assert.equal(confirmed.match(/aria-pressed="true"/g).length, 1);
  assert.match(confirmed, /確認済み: 追記する/);
  const skipped = renderToStaticMarkup(createElement(CommentCandidate, { answer, decision: 'skip', onDecide: noop, onEdit: noop }));
  assert.match(skipped, /確認済み: 追記しない/);
});
