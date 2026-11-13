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

const question = { id: 'basis-1', kind: 'basis', text: '点検資料を確認できますか？', selected: true, targets: ['normal'], sourceSection: '手順', sourceText: '合成の確認箇所' };
const noop = () => {};

test('質問候補を表示し、実行前に検索先とAPI呼び出し回数を確認できる', () => {
  const { KnowhowCheckQuestions } = loadComponent('KnowhowCheckQuestions');
  const html = renderToStaticMarkup(createElement(KnowhowCheckQuestions, { questions: [question], onChange: noop, onStart: noop }));
  assert.match(html, /質問 1/);
  assert.match(html, /点検資料を確認できますか/);
  assert.match(html, /技術KB 1回・法令KB 0回/);
  assert.match(html, /合成の確認箇所/);
});

const baseProps = { decisions: {}, onDecide: noop, onRetry: noop, onCancel: noop };
const doneTask = (answer, id = question.id) => ({ id: `${id}-normal`, questionId: id, query: question.text, mode: 'normal', status: 'done', result: answer });
const found = { mode: 'normal', responseType: 'pages', content: 'ピット点検タラップの基準です。', receivedAt: '2026-11-14T11:00:00Z', sourceDocuments: [{ documentName: 'SUE-3-17.pdf', pageNumber: 4, sourceUri: 's3://technical-kb/SUE-3-17.pdf' }], pageCandidates: [] };
const notFound = { mode: 'normal', responseType: 'not_found', receivedAt: '2026-11-14T11:00:00Z', sourceDocuments: [], pageCandidates: [] };

test('照合結果の進捗と失敗を表示し、選んだ応答が揃うまで確認の操作を出さない', () => {
  const { KnowhowCheckResults } = loadComponent('KnowhowCheckResults');
  const task = { id: 'basis-1-normal', questionId: question.id, mode: 'normal', query: question.text };
  const html = renderToStaticMarkup(createElement(KnowhowCheckResults, {
    ...baseProps,
    questions: [{ ...question, targets: ['normal', 'law'] }],
    snapshot: { running: true, tasks: [
      { ...task, status: 'failed', failure: '照合に失敗しました。' },
      { ...task, id: 'basis-1-law', mode: 'law', status: 'running' },
    ] },
  }));
  assert.ok(html.includes('1 / 2 件'));
  assert.match(html, /再試行/);
  assert.match(html, /中止/);
  assert.doesNotMatch(html, /確認して追記する/);
  assert.doesNotMatch(html, /件中/);
});

test('既定は未確認で、確認して追記する・追記しないの両方が未選択。AI回答の注記と件数を出す', () => {
  const { KnowhowCheckResults } = loadComponent('KnowhowCheckResults');
  const html = renderToStaticMarkup(createElement(KnowhowCheckResults, {
    ...baseProps, questions: [question], snapshot: { running: false, tasks: [doneTask(found)] },
  }));
  assert.match(html, /AI が KB を検索した結果です。出典を確認してから追記してください。/);
  assert.match(html, /1件中 0件を追記・0件を追記しない・1件が未確認/);
  assert.match(html, /未確認のものはカードに入りません/);
  assert.match(html, /確認して追記する/);
  assert.match(html, /追記しない/);
  assert.equal(html.match(/aria-pressed="false"/g).length, 2);
  assert.doesNotMatch(html, /aria-pressed="true"/);
  assert.match(html, /出典を確認して追記/);
  assert.doesNotMatch(html, /追記案を採用する/);
});

test('出典が無い結果は「KB に該当資料なし」の確認記録として入ることを区別して表示する', () => {
  const { KnowhowCheckResults } = loadComponent('KnowhowCheckResults');
  const html = renderToStaticMarkup(createElement(KnowhowCheckResults, {
    ...baseProps, questions: [question], snapshot: { running: false, tasks: [doneTask(notFound)] },
  }));
  assert.match(html, /出典がありません。確認すると「KB に該当資料なし（2026-11-14）」の記録として入ります/);
  assert.match(html, /技術KBに該当資料なし/);
});

test('聞き返しや出典なしの回答は「KB に該当資料なし」と書かず、正確な記録として入ることを表示する', () => {
  const { KnowhowCheckResults } = loadComponent('KnowhowCheckResults');
  const clarify = { ...notFound, responseType: 'clarify' };
  const html = renderToStaticMarkup(createElement(KnowhowCheckResults, {
    ...baseProps, questions: [question], snapshot: { running: false, tasks: [doneTask(clarify)] },
  }));
  assert.doesNotMatch(html, /KB に該当資料なし/);
  assert.match(html, /根拠になる出典が見つかりませんでした（聞き返し・出典なしの回答を含む）/);
  assert.match(html, /根拠になる出典が見つからなかった（聞き返し・出典なしの回答を含む）（2026-11-14）/);
});

test('確認状態ごとに押下表示と件数が変わる', () => {
  const { KnowhowCheckResults } = loadComponent('KnowhowCheckResults');
  const second = { ...question, id: 'basis-2', text: '別の質問' };
  const html = renderToStaticMarkup(createElement(KnowhowCheckResults, {
    ...baseProps,
    decisions: { 'basis-1': 'confirm', 'basis-2': 'skip' },
    questions: [question, second],
    snapshot: { running: false, tasks: [doneTask(found), doneTask(found, 'basis-2')] },
  }));
  assert.match(html, /2件中 1件を追記・1件を追記しない・0件が未確認/);
  assert.equal(html.match(/aria-pressed="true"/g).length, 2);
  assert.match(html, /確認済み: 追記する/);
  assert.match(html, /確認済み: 追記しない/);
});
