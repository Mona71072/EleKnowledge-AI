import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

const conversationA = '11111111-1111-4111-8111-111111111111';
const conversationB = '22222222-2222-4222-8222-222222222222';
const empty = { turns: [], running: false };
const deferred = () => { let resolve; let reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const flush = () => new Promise((resolve) => setImmediate(resolve));

function harness(t, api, search = '') {
  const priorWindow = globalThis.window;
  const urls = [];
  globalThis.window = { location: { search }, history: { replaceState: (_state, _title, url) => urls.push(url) } };
  const values = [], effects = [];
  let cursor = 0;
  const react = {
    useState(initial) { const index = cursor++; if (!(index in values)) values[index] = initial; return [values[index], (value) => { values[index] = typeof value === 'function' ? value(values[index]) : value; }]; },
    useRef(initial) { const index = cursor++; if (!(index in values)) values[index] = { current: initial }; return values[index]; },
    useEffect(effect, deps) {
      const index = cursor++, previous = effects[index];
      if (!previous || !deps || deps.some((value, n) => !Object.is(previous.deps?.[n], value))) effects[index] = { effect, deps, pending: true, cleanup: previous?.cleanup };
    },
  };
  const filename = new URL('../src/hooks/useSenpaiHistory.ts', import.meta.url);
  const { outputText } = ts.transpileModule(readFileSync(filename, 'utf8'), { fileName: filename.pathname, compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } });
  const compiledModule = { exports: {} };
  new Function('require', 'module', 'exports', outputText)((name) => {
    if (name === 'react') return react;
    if (name === '@/lib/auth-helpers') return { getIdToken: async () => 'synthetic-token' };
    if (name === '@/lib/knowledge-senpai-history.mjs') return api;
    throw new Error(`Unexpected dependency: ${name}`);
  }, compiledModule, compiledModule.exports);
  const restored = [];
  let cancelled = 0;
  const controllerRef = { current: { cancel: () => { cancelled += 1; }, restore: (saved) => restored.push(saved) } };
  const render = (snapshot = empty) => {
    cursor = 0;
    const result = compiledModule.exports.useSenpaiHistory(snapshot, controllerRef);
    for (const effect of effects) {
      if (!effect?.pending) continue;
      effect.pending = false;
      effect.cleanup?.();
      effect.cleanup = effect.effect();
    }
    return result;
  };
  t.after(() => { effects.forEach((effect) => effect?.cleanup?.()); globalThis.window = priorWindow; });
  return { render, restored, urls, controllerRef, cancelled: () => cancelled };
}

test('switching from one history to another ignores the older completion', async (t) => {
  const a = deferred(), b = deferred();
  const signals = [];
  const view = harness(t, {
    getSenpaiConversations: async () => ({ sessions: [], complete: true }),
    readSenpaiConversation: ({ conversationId, signal }) => { signals.push(signal); return conversationId === conversationA ? a.promise : b.promise; },
  });
  let ui = view.render();
  const first = ui.openConversation(conversationA);
  const second = ui.openConversation(conversationB);
  b.resolve({ conversationId: conversationB, turns: [], complete: true });
  await second;
  a.resolve({ conversationId: conversationA, turns: [], complete: true });
  await first;
  ui = view.render();
  assert.equal(signals[0].aborted, true);
  assert.deepEqual(view.restored.map((saved) => saved.conversationId), [conversationB]);
  assert.equal(ui.opening, false);
  assert.equal(view.urls.at(-1), `/knowledge/chat?conversation=${conversationB}`);
});

test('new consultation cancels a pending history load without restoring it', async (t) => {
  const pending = deferred();
  let signal;
  const view = harness(t, {
    getSenpaiConversations: async () => ({ sessions: [], complete: true }),
    readSenpaiConversation: (request) => { signal = request.signal; return pending.promise; },
  });
  const ui = view.render();
  const reading = ui.openConversation(conversationA);
  ui.resetSelection();
  pending.resolve({ conversationId: conversationA, turns: [], complete: true });
  await reading;
  assert.equal(signal.aborted, true);
  assert.deepEqual(view.restored, []);
  assert.equal(view.urls.at(-1), '/knowledge/chat');
  assert.equal(view.render().opening, false);
});

test('history error is explicit, retry reloads the list, and backend completion remains visible', async (t) => {
  let calls = 0;
  const session = { conversationId: conversationA, title: '保存済みの質問', createdAt: '2026-10-20T00:00:00Z', lastMessageTime: '2026-10-20T00:00:00Z', messageCount: 1, daysUntilDeletion: 59 };
  const view = harness(t, {
    getSenpaiConversations: async () => { if (++calls === 1) throw Object.assign(new Error('履歴サービスに接続できません'), { code: 'server' }); return { sessions: [session], complete: false }; },
    readSenpaiConversation: async () => { throw new Error('unused'); },
  });
  view.render(); await flush();
  let ui = view.render();
  assert.match(ui.error, /接続できません/);
  assert.equal(ui.loading, false);
  ui.refresh(); view.render(); await flush();
  ui = view.render();
  assert.equal(ui.error, '');
  assert.equal(ui.entries[0].title, '保存済みの質問');
  assert.equal(ui.complete, false);
});

test('reload restores the consultation selected in the URL', async (t) => {
  const view = harness(t, {
    getSenpaiConversations: async () => ({ sessions: [], complete: true }),
    readSenpaiConversation: async ({ conversationId }) => ({ conversationId, turns: [], complete: false }),
  }, `?conversation=${conversationA}`);
  view.render(); await flush();
  assert.equal(view.restored[0].conversationId, conversationA);
  assert.equal(view.restored[0].complete, false);
});

test('new question appears before persistence and completion refreshes server history', async (t) => {
  let calls = 0;
  const view = harness(t, {
    getSenpaiConversations: async () => { calls += 1; return { sessions: [], complete: true }; },
    readSenpaiConversation: async () => { throw new Error('unused'); },
  });
  view.render(); await flush();
  const snapshot = { conversationId: conversationA, turns: [{ id: 1, query: '質問した内容', normal: { status: 'loading' }, law: { status: 'loading' } }], running: true };
  const ui = view.render(snapshot);
  assert.equal(ui.entries[0].title, '質問した内容');
  assert.equal(ui.entries[0].pending, true);
  view.render({ ...snapshot, running: false });
  view.render({ ...snapshot, running: false }); await flush();
  assert.equal(calls, 2);
});
