import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';

const require = createRequire(import.meta.url);

function loadPanel() {
  const filename = new URL('../src/components/knowledge/KnowledgeSourceReviewPanel.tsx', import.meta.url);
  const source = readFileSync(filename, 'utf8');
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: filename.pathname,
  });
  const compiledModule = { exports: {} };
  const localRequire = (name) => {
    if (name === '@/lib/knowledge-source-review.mjs') return {
      getReviewSources: () => [
        { kind: 'lists', id: '123', label: 'Lists §123' },
        { kind: 'onenote', id: 'page-1', label: 'OneNote 現場メモ' },
        { kind: 'technical', id: 'manual', label: '技術KB（手動確認）' },
        { kind: 'onenote', id: 'manual', label: '別のOneNoteページ' },
        { kind: 'lists', id: 'manual', label: '別のLists項目' },
      ],
      resolveReviewSource: (source, enteredId) => source?.id === 'manual' && source.kind !== 'technical'
        ? (enteredId?.trim() ? { ...source, id: enteredId.trim() } : null)
        : source,
      readReviewSourceSnapshot: () => ({ text: '抜粋です。', capturedOn: '2026-11-01' }),
      MAX_SOURCE_SNAPSHOT_BYTES: 256 * 1024,
    };
    return require(name);
  };
  new Function('require', 'module', 'exports', outputText)(localRequire, compiledModule, compiledModule.exports);
  return compiledModule.exports.KnowledgeSourceReviewPanel;
}

test('source review panel offers linked sources, human outcomes, and prior records', () => {
  const Panel = loadPanel();
  const html = renderToStaticMarkup(createElement(Panel, {
    metadata: {},
    revision: 4,
    records: [{
      source: { kind: 'lists', id: '123', label: 'Lists §123' }, method: 'snapshot', capturedOn: '2026-11-01',
      locator: 'lists.md', outcome: 'conditions_differ', note: '適用条件に差があります。', recordedAt: '2026-11-13T00:00:00.000Z', revision: 3,
    }],
    onRecord() {},
  }));

  assert.match(html, /Lists §123/);
  assert.match(html, /OneNote 現場メモ/);
  assert.match(html, /技術KB（手動確認）/);
  assert.match(html, /ローカルのMarkdownを選ぶ/);
  assert.match(html, /ファイルがない場合はMarkdownを貼り付け/);
  assert.match(html, /照合結果を選択してください/);
  assert.match(html, /ファイル名、ページ名、または項目ID/);
  assert.match(html, /内容に食い違いがある/);
  assert.match(html, /適用条件が異なる/);
  assert.match(html, /適用条件に差があります。/);
  assert.match(html, /現在の作業版: 4/);
  assert.doesNotMatch(html, /承認済み/);
});
