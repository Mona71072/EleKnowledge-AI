import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';

const require = createRequire(import.meta.url);

function loadTsx(path) {
  const filename = new URL(path, import.meta.url);
  const source = require('node:fs').readFileSync(filename, 'utf8');
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename.pathname,
  });
  const compiledModule = { exports: {} };
  const localRequire = (name) => {
    if (name === '../../lib/line-diff.mjs') return require('../src/lib/line-diff.mjs');
    if (name === '../../lib/knowledge-diff-sections.mjs') return require('../src/lib/knowledge-diff-sections.mjs');
    return require(name);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports;
}

const { KnowledgeLineDiff } = loadTsx('../src/components/knowledge/KnowledgeLineDiff.tsx');
const render = (before, after) => renderToStaticMarkup(createElement(KnowledgeLineDiff, { before, after }));

test('差分は変更行と前後3行を表示し、離れた共通行を折りたたむ', () => {
  const before = ['先頭', '前1', '前2', '前3', '古い値', '後1', '後2', '後3', '中間', '後半旧', '終端'].join('\n');
  const after = before.replace('古い値', '新しい値').replace('後半旧', '後半新');
  const html = render(before, after);

  assert.match(html, /追加2行/);
  assert.match(html, /削除2行/);
  assert.match(html, /前1/);
  assert.match(html, /後3/);
  assert.match(html, /ほか \d+ 行/);
  assert.match(html, /−/);
  assert.match(html, /\+/);
});

test('差分に変更前後の行番号列と、追加・削除・文脈の読み上げ名を表示する', () => {
  const html = render('一行目\n古い値\n三行目', '一行目\n新しい値\n三行目');

  assert.match(html, /変更前/);
  assert.match(html, /変更後/);
  assert.match(html, /aria-label="変更なし、変更前1行目、変更後1行目"/);
  assert.match(html, /aria-label="削除、変更前2行目"/);
  assert.match(html, /aria-label="追加、変更後2行目"/);
  assert.match(html, />1<\/span>/);
  assert.match(html, />2<\/span>/);
});

test('変更が無いときは案内を表示する', () => {
  assert.match(render('同じ\n文章', '同じ\n文章'), /変更はありません/);
});

test('差分表が大きすぎる場合は変更前と変更後を全文表示する', () => {
  const before = Array.from({ length: 2100 }, (_, index) => `前${index}`).join('\n');
  const after = Array.from({ length: 2100 }, (_, index) => `後${index}`).join('\n');
  const html = render(before, after);

  assert.match(html, /差分が大きいため全文を表示しています/);
  assert.match(html, /変更前/);
  assert.match(html, /変更後/);
  assert.match(html, /前2099/);
  assert.match(html, /後2099/);
});

test('差分と全文表示は [before, after] に依存させてメモ化し、再描画で作り直さない', () => {
  const react = require('react');
  const memoCalls = [];
  const diffCalls = [];
  const filename = new URL('../src/components/knowledge/KnowledgeLineDiff.tsx', import.meta.url);
  const { outputText } = ts.transpileModule(require('node:fs').readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename.pathname,
  });
  const lineDiff = require('../src/lib/line-diff.mjs');
  const localRequire = (name) => {
    if (name === 'react') return { ...react, useMemo: (factory, deps) => { memoCalls.push(deps); return factory(); } };
    if (name === '../../lib/line-diff.mjs') return { ...lineDiff, diffLines: (...args) => { diffCalls.push(args); return lineDiff.diffLines(...args); } };
    if (name === '../../lib/knowledge-diff-sections.mjs') return require('../src/lib/knowledge-diff-sections.mjs');
    return require(name);
  };
  const compiledModule = { exports: {} };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  const { KnowledgeLineDiff: Memoized } = compiledModule.exports;

  renderToStaticMarkup(createElement(Memoized, { before: '古い\n同じ', after: '新しい\n同じ' }));
  assert.ok(memoCalls.length >= 1, 'diff is computed inside useMemo');
  assert.ok(memoCalls.every((deps) => Array.isArray(deps) && deps.includes('古い\n同じ') && deps.includes('新しい\n同じ')),
    'every memo depends on before and after');
  assert.equal(diffCalls.length, 1);

  const big = (prefix) => Array.from({ length: 2100 }, (_, index) => `${prefix}${index}`).join('\n');
  memoCalls.length = 0;
  renderToStaticMarkup(createElement(Memoized, { before: big('前'), after: big('後') }));
  assert.ok(memoCalls.length >= 1, 'the full-text view is memoized too');
});

test('行内の強調は既定ではオフで、出力が変わらない。有効にすると変わった部分だけを濃い背景で示す', () => {
  const before = '前\n距離は 800 mm 以内です\n後';
  const after = '前\n距離は 600 mm 以内です\n後';
  const plain = renderToStaticMarkup(createElement(KnowledgeLineDiff, { before, after }));
  const off = renderToStaticMarkup(createElement(KnowledgeLineDiff, { before, after, inlineHighlight: false }));
  assert.equal(off, plain);
  assert.doesNotMatch(plain, /<mark/);
  const on = renderToStaticMarkup(createElement(KnowledgeLineDiff, { before, after, inlineHighlight: true }));
  assert.match(on, /<mark[^>]*bg-red-300[^>]*>800<\/mark>/);
  assert.match(on, /<mark[^>]*bg-green-300[^>]*>600<\/mark>/);
  assert.match(on, /mm 以内です/);
  assert.doesNotMatch(on.replace(/<mark[^>]*>[^<]*<\/mark>/g, '').replace(/<[^>]*>/g, ''), /800|600/);
});

test('原文との差分に変更節へのコメント導線を置き、削除節と重複節はリンクにしない', () => {
  const html = renderToStaticMarkup(createElement(KnowledgeLineDiff, {
    before: '## A\nold\n\n## B\ntext',
    after: '## A\nnew\n\n## C\ntext\n\n## C\nsecond',
    onSectionSelect: () => {},
  }));

  assert.match(html, /data-testid="changed-section-shortcuts"/);
  assert.match(html, /data-section-label="A" data-section-status="changed"/);
  assert.match(html, /「A」にコメント/);
  assert.match(html, /data-section-label="B" data-section-status="removed"/);
  assert.match(html, /「B」は削除/);
  assert.match(html, /data-section-label="C" data-section-status="ambiguous"/);
  assert.doesNotMatch(html, /「C」にコメント/);
});
