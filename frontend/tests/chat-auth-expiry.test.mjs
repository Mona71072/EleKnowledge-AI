import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
import axios from 'axios';
import { createJobPoller } from '../src/lib/research-polling.mjs';

const source = readFileSync(new URL('../src/app/chat/page.tsx', import.meta.url), 'utf8');
const ast = ts.createSourceFile('page.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

function findVariable(name) {
  let found;
  function visit(node) {
    if (ts.isVariableDeclaration(node) && node.name.getText(ast) === name) found = node.initializer.getText(ast);
    ts.forEachChild(node, visit);
  }
  visit(ast);
  assert.ok(found, `${name} must exist in the chat page`);
  return found;
}

function compile(expression, context) {
  const { outputText } = ts.transpileModule(`const actual = ${expression};`, {
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.None },
  });
  return vm.runInNewContext(`(() => { ${outputText}\nreturn actual; })()`, context);
}

function setup() {
  const events = { redirects: [], errors: [], stopped: 0, requests: 0 };
  const context = {
    Error, axios, crypto: { randomUUID: () => 'synthetic-request' },
    console: { error() {} },
    router: { replace: (path) => events.redirects.push(path) },
    loginRedirectedRef: { current: false },
    researchPollerRef: { current: { stopAll: () => { events.stopped += 1; } } },
    pendingResearchRequestRef: { current: null },
    setError: (error) => events.errors.push(error),
    setLoading() {}, setIsLoadingSessions() {}, setResearchJob() {}, setResearchRateLimited() {},
    setMessages() {}, setInput() {}, textareaRef: { current: null },
    ragMode: 'normal', answerMode: 'research', researchModeAvailable: true,
    RESEARCH_MODE_SETTING: 'beta', loading: false, researchIsRunning: false,
    userId: 'synthetic-user', readOnlySession: false, input: 'synthetic question',
    currentSession: null, isLawMode: false, selectedCategories: [], selectedModel: '',
    CHAT_API_URL: 'https://chat.invalid', RESEARCH_API_URL: 'https://research.invalid', API_URL: 'https://rag.invalid',
    fetchAuthSession: async () => ({ tokens: { idToken: { toString: () => 'synthetic-token' } } }),
  };
  context.handleAuthenticationError = compile(findVariable('handleAuthenticationError'), context);
  context.getAuthToken = compile(findVariable('getAuthToken'), context);
  return { context, events };
}

test('401 stops polling and redirects once; other failures do not redirect', () => {
  const { context, events } = setup();
  for (const status of [403, 429, 500, undefined]) {
    assert.equal(context.handleAuthenticationError({ isAxiosError: true, response: { status } }), false);
  }
  assert.equal(events.redirects.length, 0);
  const error = Object.assign(new Error('Authentication required'), { status: 401 });
  assert.equal(context.handleAuthenticationError(error), true);
  assert.equal(context.handleAuthenticationError({ isAxiosError: true, response: { status: 401 } }), true);
  assert.deepEqual(events.redirects, ['/login?next=%2Fchat']);
  assert.match(events.errors[0], /もう一度ログイン/u);
  assert.equal(events.stopped, 2);
});

test('missing or expired tokens are 401, while network errors keep their identity', async () => {
  const { context } = setup();
  assert.equal(await context.getAuthToken(), 'synthetic-token');
  for (const session of [{}, { tokens: {} }]) {
    context.fetchAuthSession = async () => session;
    await assert.rejects(context.getAuthToken(), (error) => error.status === 401);
  }
  for (const name of ['NotAuthorizedException', 'UserUnAuthenticatedException']) {
    context.fetchAuthSession = async () => { throw Object.assign(new Error('expired'), { name }); };
    await assert.rejects(context.getAuthToken(), (error) => error.status === 401);
  }
  const networkError = new Error('Network Error');
  context.fetchAuthSession = async () => { throw networkError; };
  await assert.rejects(context.getAuthToken(), (error) => error === networkError);
});

for (const name of ['handleSendMessage', 'fetchSessions', 'fetchSessionMessages', 'resumeResearchJob', 'refreshQuota']) {
  test(`${name}: API 401 or missing tokens redirect without retrying the request`, async () => {
    for (const answerMode of name === 'handleSendMessage' ? ['normal', 'research'] : ['research']) {
    for (const missingToken of [false, true]) {
      const { context, events } = setup();
      context.answerMode = answerMode;
      const unauthorized = Object.assign(new axios.AxiosError('Unauthorized'), { response: { status: 401 } });
      context.axios = {
        isAxiosError: axios.isAxiosError,
        get: async () => { events.requests += 1; throw unauthorized; },
        post: async () => { events.requests += 1; throw unauthorized; },
      };
      if (missingToken) context.fetchAuthSession = async () => ({});
      await compile(findVariable(name), context)('synthetic-session');
      assert.deepEqual(events.redirects, ['/login?next=%2Fchat']);
      assert.equal(events.requests, missingToken ? 0 : 1);
    }
    }
  });
}

test('progress 401 stops the real poller without rescheduling or reporting give-up', async () => {
  const { context, events } = setup();
  let pollerOptions;
  context.createJobPoller = (options) => { pollerOptions = options; return { stopAll() {} }; };
  context.document = { addEventListener() {}, removeEventListener() {} };
  const effects = [];
  function visit(node) {
    if (ts.isCallExpression(node) && node.expression.getText(ast) === 'useEffect') effects.push(node.arguments[0].getText(ast));
    ts.forEachChild(node, visit);
  }
  visit(ast);
  compile(effects.find((effect) => effect.includes('createJobPoller')), context)();
  context.axios = {
    isAxiosError: axios.isAxiosError,
    get: async () => { throw Object.assign(new axios.AxiosError('Unauthorized'), { response: { status: 401 } }); },
  };
  const timers = new Map();
  let timerId = 0;
  const poller = createJobPoller({
    ...pollerOptions,
    setTimer: (fn) => { timers.set(++timerId, fn); return timerId; },
    clearTimer: (id) => timers.delete(id),
    onGiveUp: () => assert.fail('401 must not become a polling timeout'),
  });
  context.researchPollerRef.current = poller;
  poller.start('synthetic-job');
  const [tickId, tick] = [...timers.entries()][1];
  timers.delete(tickId);
  await tick();
  assert.equal(timers.size, 0);
  assert.deepEqual(events.redirects, ['/login?next=%2Fchat']);
});