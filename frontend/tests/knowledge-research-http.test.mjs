import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import test from 'node:test';
import { queryKnowledgeSource } from '../src/lib/knowledge-research.mjs';

async function localApi(t, handler) {
  const originalEnvironment = process.env.NODE_ENV;
  process.env.NODE_ENV = 'test';
  t.after(() => {
    if (originalEnvironment === undefined) delete process.env.NODE_ENV;
    else process.env.NODE_ENV = originalEnvironment;
  });
  const server = createServer(handler);
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise((resolve) => {
    server.closeAllConnections();
    server.close(resolve);
  }));
  return `http://127.0.0.1:${server.address().port}`;
}

function payload(mode) {
  return {
    sessionId: `synthetic-${mode}`,
    aiMessageId: `synthetic-${mode}-answer`,
    content: '合成された接続試験の応答。実務上の助言ではありません。',
    responseType: 'pages',
    sourceDocuments: [],
    pageCandidates: [],
    clarifyQuestions: [],
  };
}

test('real HTTP sends independent mode requests and only the explicit question', async (t) => {
  const requests = [];
  const baseUrl = await localApi(t, async (req, res) => {
    let raw = '';
    for await (const chunk of req) raw += chunk;
    const body = JSON.parse(raw);
    requests.push({ method: req.method, path: req.url, auth: req.headers.authorization, body });
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(payload(body.mode)));
  });
  const answers = await Promise.all(['normal', 'law'].map((mode) => queryKnowledgeSource({
    baseUrl, mode, query: '合成された比較質問', getToken: async () => 'synthetic-token',
  })));
  assert.deepEqual(answers.map((answer) => answer.sessionId), ['synthetic-normal', 'synthetic-law']);
  assert.equal(requests.length, 2);
  for (const request of requests) {
    assert.equal(request.method, 'POST');
    assert.equal(request.path, '/rag/query');
    assert.equal(request.auth, 'Bearer synthetic-token');
    assert.deepEqual(Object.keys(request.body).sort(), ['filters', 'mode', 'query']);
    assert.equal(request.body.query, '合成された比較質問');
    assert.deepEqual(request.body.filters, {});
  }
});

test('a real HTTP law-gate failure leaves the technical result available', async (t) => {
  const baseUrl = await localApi(t, async (req, res) => {
    let raw = '';
    for await (const chunk of req) raw += chunk;
    const { mode } = JSON.parse(raw);
    res.writeHead(mode === 'law' ? 403 : 200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(mode === 'law' ? { error: 'FeatureUnavailable' } : payload(mode)));
  });
  const [technical, law] = await Promise.allSettled(['normal', 'law'].map((mode) => queryKnowledgeSource({
    baseUrl, mode, query: '合成された片側停止の質問', getToken: async () => 'synthetic-token',
  })));
  assert.equal(technical.status, 'fulfilled');
  assert.equal(technical.value.mode, 'normal');
  assert.equal(law.status, 'rejected');
  assert.equal(law.reason.code, 'unavailable');
});

test('aborting a real pending HTTP request ends the caller without waiting for the server', async (t) => {
  let started;
  const requestStarted = new Promise((resolve) => { started = resolve; });
  const baseUrl = await localApi(t, (_req, _res) => started());
  const controller = new AbortController();
  const pending = queryKnowledgeSource({
    baseUrl, mode: 'law', query: '合成された中止試験',
    getToken: async () => 'synthetic-token', signal: controller.signal,
  });
  await requestStarted;
  controller.abort();
  await assert.rejects(pending, (error) => error.code === 'cancelled');
});
