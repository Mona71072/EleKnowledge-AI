import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { mkdtemp, rm } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import ts from 'typescript';
import * as client from '../src/lib/common-knowledge.mjs';

const require = createRequire(import.meta.url);
const ROOT = fileURLToPath(new URL('../../', import.meta.url));

async function until(condition) {
  const end = Date.now() + 20000;
  while (!condition()) {
    if (Date.now() > end) throw new Error('Synthetic UI action did not complete');
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
}

// Execute the actual TSX handlers with React state boundaries under test control.
// HTTP, API validation and the SQLite ledger/working/canonical persistence are real.
function mount() {
  const state = [];
  let index = 0;
  const filename = new URL('../src/components/knowledge/common-knowledge-inbox.tsx', import.meta.url);
  const { outputText } = ts.transpileModule(readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
  });
  const compiled = { exports: {} };
  new Function('require', 'module', 'exports', outputText)((name) => {
    if (name === 'react') return { useState(initial) {
      const slot = index++;
      if (!(slot in state)) state[slot] = typeof initial === 'function' ? initial() : initial;
      return [state[slot], (value) => { state[slot] = value; }];
    } };
    if (name === '@/lib/auth-helpers') return { getIdToken: async () => { throw new Error('No real authentication in I1'); } };
    if (name === '@/lib/common-knowledge.mjs') return client;
    return require(name);
  }, compiled, compiled.exports);
  function tree() { index = 0; return compiled.exports.CommonKnowledgeInbox(); }
  function nodes(node) {
    if (Array.isArray(node)) return node.flatMap((value) => nodes(value));
    if (!node || typeof node !== 'object') return [];
    return [node, ...nodes(node.props?.children)];
  }
  function text(node) {
    if (Array.isArray(node)) return node.map(text).join('');
    if (node && typeof node === 'object') return text(node.props?.children);
    return node == null || typeof node === 'boolean' ? '' : String(node);
  }
  const label = (name) => nodes(tree()).find((node) => node.type === 'label' && text(node).trim().startsWith(name));
  return {
    select(name, value) { nodes(label(name)).find((node) => node.type === 'select').props.onChange({ target: { value } }); },
    input(name, value) { nodes(label(name)).find((node) => ['input', 'textarea'].includes(node.type)).props.onChange({ target: { value, checked: value } }); },
    async click(name) {
      const button = nodes(tree()).find((node) => node.type === 'button' && text(node).includes(name));
      assert.ok(button, `Missing button: ${name}`);
      assert.ok(!button.props.disabled, `Disabled button: ${name}`);
      button.props.onClick();
      await until(() => !text(tree()).includes('保存先へ確認中…'));
    },
    text() { return text(tree()); },
  };
}

test('actual UI handlers complete all three synthetic entry lifecycles over loopback HTTP', { timeout: 120000 }, async () => {
  const data = await mkdtemp(path.join(tmpdir(), 'common-knowledge-ui-'));
  const oldEnv = { ...process.env };
  const oldWindow = globalThis.window;
  let child;
  try {
    process.env.NODE_ENV = 'development';
    process.env.NEXT_PUBLIC_COMMON_KNOWLEDGE_SYNTHETIC = 'true';
    process.env.NEXT_PUBLIC_COMMON_KNOWLEDGE_API_URL = 'http://127.0.0.1:8765';
    globalThis.window = { location: { hostname: 'localhost' } };
    const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
    child = spawn(python, ['-X', 'utf8', path.join(ROOT, 'scripts/knowledge/run-common-knowledge-local.py'),
      '--enable-synthetic', '--data-dir', data], { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
    let output = '';
    child.stdout.on('data', (value) => { output += value; });
    child.stderr.on('data', (value) => { output += value; });
    child.on('error', (error) => { output += error.message; });
    await until(() => output.includes('persistent local ledger ready.') || child.exitCode !== null);
    assert.equal(child.exitCode, null, output);
    const ui = mount();
    for (const [index, type] of ['field_report', 'unknown_term', 'correction'].entries()) {
      ui.select('合成の操作者', 'contributor');
      ui.select('候補の種類', type);
      const cardId = type === 'correction' ? 'KH-SYN-UI-0' : `KH-SYN-UI-${index}`;
      if (type === 'correction') {
        ui.input('訂正対象の単元ID', cardId);
        ui.input('訂正対象の承認版', '1');
      }
      ui.input('共有する最小文脈', `架空機種Aの合成${type}。原資料ではない。`);
      ui.input('この文面', true);
      await ui.click('明示して投函');
      assert.match(ui.text(), /投函を保存しました/);
      ui.select('合成の操作者', 'editor');
      await ui.click('最新状態を再取得');
      await ui.click('編集を引き受ける');
      if (type !== 'correction') ui.input('単元ID', cardId);
      await ui.click('作業版を保存');
      assert.match(ui.text(), /作業版の保存が完了/);
      await ui.click('この版の技術確認を依頼');
      assert.match(ui.text(), /特定版を技術確認待ち/);
      ui.select('合成の操作者', 'reviewer');
      await ui.click('この版を技術承認');
      assert.match(ui.text(), /技術承認と正本反映が完了/);
      ui.select('合成の操作者', 'publisher');
      ui.input('確認した公開世代', type === 'correction' ? '2' : '0');
      await ui.click('承認版を公開');
      assert.match(ui.text(), /特定版を公開しました/);
      ui.select('合成の操作者', 'reader');
      await ui.click('公開版を毎回確認して読む');
      assert.match(ui.text(), /架空機種A・改訂1の説明/);
      const read = await client.requestKnowledge({ baseUrl: 'http://127.0.0.1:8765',
        token: 'synthetic-agent', actor: 'agent', path: `/published/${cardId}` });
      assert.ok(ui.text().includes(read.rawSha256));
      ui.select('合成の操作者', 'publisher');
      await ui.click('公開を停止');
      assert.match(ui.text(), /公開を停止しました/);
      ui.select('合成の操作者', 'agent');
      await ui.click('公開版を毎回確認して読む');
      assert.match(ui.text(), /NotPublished/);
      assert.ok(!ui.text().includes(read.rawSha256));
    }
  } finally {
    if (child && child.exitCode === null) {
      child.kill();
      await new Promise((resolve) => child.once('exit', resolve));
    }
    process.env = oldEnv;
    globalThis.window = oldWindow;
    assert.equal(path.dirname(path.resolve(data)), path.resolve(tmpdir()));
    await rm(data, { recursive: true, force: true });
  }
});
