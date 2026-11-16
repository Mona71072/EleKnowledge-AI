import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
  KnowhowRewriteError,
  REWRITE_TIMEOUT_MS,
  requestKnowhowRewrite,
  rewriteFailureMessage,
} from '../src/lib/knowhow-rewrite-client.mjs';
import { buildRewriteRequest } from '../src/lib/knowhow-rewrite.mjs';

const contract = JSON.parse(readFileSync(new URL('../../tests/fixtures/knowhow-rewrite/contract.json', import.meta.url), 'utf8'));
const FRONTMATTER = { knowledge_id: 'KH-PIT-TRAP-POSITION-394', card_version: 1, source_refs: [{ ref_type: 'secret_ref' }] };
const BODY = `---\nknowledge_id: KH-PIT-TRAP-POSITION-394\nsource_refs: [secret_ref]\n---\n# 題名\n\n## 統合した回答・ノウハウ\n\n${contract.request.targets[0].body}\n\n## 未確認事項\n\n${contract.request.targets[1].body}\n\n## 使う場面・対象条件\n\n${contract.request.context[0].body}\n`;
const evidence = contract.request.evidence.map((item) => ({ ...item, questionId: 'q1' }));
const { request } = buildRewriteRequest({ frontmatter: FRONTMATTER, body: BODY, evidence });
const baseUrl = 'https://api.example.com/prod/';
const getToken = async () => 'jwt-token';

function respond(status, body) {
  return async () => ({ ok: status >= 200 && status < 300, status, json: async () => body });
}

test('契約のエンドポイントへ要求だけを認証つきで POST し、検証済みの案を返す', async () => {
  const calls = [];
  const fetchImpl = async (url, init) => { calls.push({ url, init }); return respond(200, contract.response)(); };
  const proposal = await requestKnowhowRewrite({ baseUrl, getToken, fetchImpl, request });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, 'https://api.example.com/prod/rag/knowhow/rewrite-proposal');
  assert.equal(calls[0].init.method, 'POST');
  assert.equal(calls[0].init.headers.Authorization, 'Bearer jwt-token');
  assert.equal(calls[0].init.headers['Content-Type'], 'application/json');
  assert.equal(calls[0].init.body, JSON.stringify(request));
  assert.deepEqual(proposal.sections.map((s) => s.status), ['unchanged', 'changed']);
});

test('送信内容にカード全文・frontmatter・題名・内部IDが含まれない', async () => {
  let sent = '';
  await requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: async (_url, init) => { sent = init.body; return respond(200, contract.response)(); } });
  for (const leaked of ['source_refs', 'secret_ref', 'ref_type', '# 題名', 'questionId', '---']) assert.ok(!sent.includes(leaked), leaked);
  assert.deepEqual(Object.keys(JSON.parse(sent)).sort(), ['cardVersion', 'context', 'evidence', 'knowledgeId', 'targets']);
});

const FIXED = {
  401: 'ログイン状態または利用権限を確認してください。',
  403: 'この環境では使えません。',
  409: '元のカード版または対象本文が変わりました。最新のカードで照合し直してから案を作り直してください。',
  429: '混み合っています。少し待ってからやり直してください。',
  502: '案を作れませんでした。やり直してください。',
  504: '案を作れませんでした。やり直してください。',
};

test('HTTP エラーは固定の日本語文言にし、応答本文・例外本文を出さない', async () => {
  for (const [status, message] of Object.entries(FIXED)) {
    await assert.rejects(
      requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: respond(Number(status), { error: 'SECRET-DETAIL KH-X 本文の一部' }) }),
      (error) => error instanceof KnowhowRewriteError && error.message === message && !error.message.includes('SECRET'),
      String(status),
    );
  }
  for (const status of [400, 405, 413, 500, 418]) {
    await assert.rejects(
      requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: respond(status, { error: 'SECRET' }) }),
      (error) => error instanceof KnowhowRewriteError && error.message === rewriteFailureMessage(error) && !error.message.includes('SECRET'),
      String(status),
    );
  }
});

test('401 は auth、403 は unavailable、429 は throttled、502/504 は failed として区別できる', async () => {
  const codeOf = async (status) => requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: respond(status, {}) }).catch((error) => error.code);
  assert.equal(await codeOf(401), 'auth');
  assert.equal(await codeOf(403), 'unavailable');
  assert.equal(await codeOf(409), 'conflict');
  assert.equal(await codeOf(429), 'throttled');
  assert.equal(await codeOf(502), 'failed');
  assert.equal(await codeOf(504), 'failed');
});

test('通信失敗・不正な JSON・形式違いの応答は、例外本文を出さずに失敗にする', async () => {
  await assert.rejects(
    requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: async () => { throw new Error('SECRET connect refused'); } }),
    (error) => error.code === 'network' && !error.message.includes('SECRET'),
  );
  await assert.rejects(
    requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: async () => ({ ok: true, status: 200, json: async () => { throw new Error('SECRET'); } }) }),
    (error) => error.code === 'invalid_response' && !error.message.includes('SECRET'),
  );
  await assert.rejects(
    requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: respond(200, { knowledgeId: 'KH-OTHER', cardVersion: 1, sections: [] }) }),
    (error) => error.code === 'invalid_response',
  );
});

test('接続先・トークンの不備は送信せずに失敗にする', async () => {
  let called = false;
  const fetchImpl = async () => { called = true; return respond(200, contract.response)(); };
  await assert.rejects(requestKnowhowRewrite({ baseUrl: '', getToken, request, fetchImpl }), (error) => error.code === 'config');
  await assert.rejects(requestKnowhowRewrite({ baseUrl: 'http://api.example.com', getToken, request, fetchImpl }), (error) => error.code === 'config');
  await assert.rejects(requestKnowhowRewrite({ baseUrl, getToken: async () => '', request, fetchImpl }), (error) => error.code === 'auth');
  await assert.rejects(requestKnowhowRewrite({ baseUrl, getToken: async () => { throw new Error('x'); }, request, fetchImpl }), (error) => error.code === 'auth');
  await assert.rejects(requestKnowhowRewrite({ baseUrl, getToken, request: null, fetchImpl }), (error) => error.code === 'config');
  assert.equal(called, false);
});

const hangingFetch = (_url, init) => new Promise((_resolve, reject) => {
  init.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')), { once: true });
});

test('中止できる。送る前に中止済みなら通信しない', async () => {
  const controller = new AbortController();
  const pending = requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: hangingFetch, signal: controller.signal });
  setTimeout(() => controller.abort(), 10);
  await assert.rejects(pending, (error) => error.code === 'cancelled' && error.message === '案の作成を中止しました。');
  const done = new AbortController();
  done.abort();
  let called = false;
  await assert.rejects(
    requestKnowhowRewrite({ baseUrl, getToken, request, signal: done.signal, fetchImpl: async () => { called = true; } }),
    (error) => error.code === 'cancelled',
  );
  assert.equal(called, false);
});

test('タイムアウトは既定35秒で、時間内に終わらなければ中断して timeout にする', async () => {
  assert.equal(REWRITE_TIMEOUT_MS, 35_000);
  await assert.rejects(
    requestKnowhowRewrite({ baseUrl, getToken, request, fetchImpl: hangingFetch, timeoutMs: 20 }),
    (error) => error.code === 'timeout' && error.message === '案の作成が時間内に完了しませんでした。やり直してください。',
  );
});

test('通信失敗のメッセージ関数は、想定外の例外にも固定文言を返す', () => {
  assert.equal(rewriteFailureMessage(new Error('SECRET')), '案を作れませんでした。やり直してください。');
  assert.equal(rewriteFailureMessage(null), '案を作れませんでした。やり直してください。');
});
