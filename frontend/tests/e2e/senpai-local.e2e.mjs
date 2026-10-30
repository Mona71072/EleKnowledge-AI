import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { chromium } from 'playwright';

const HOST = '127.0.0.1';
const OWNER = 'synthetic-user';
const conversations = new Map();
const requests = [];
let web;
let browser;
let api;

function json(response, status, value) {
  response.writeHead(status, {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Authorization,Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Content-Type': 'application/json',
  });
  response.end(JSON.stringify(value));
}

function collectBody(request) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    request.on('data', (chunk) => chunks.push(chunk));
    request.on('end', () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}')); }
      catch (error) { reject(error); }
    });
    request.on('error', reject);
  });
}

function answerFor(body) {
  const empty = body.query.includes('根拠なし');
  const sourceDocuments = body.mode === 'normal' && !empty ? [{
    title: '合成資料: AXIEZ 点検要領',
    documentName: 'synthetic-axiez-inspection.pdf',
    pageNumber: 4,
    sourceUri: 's3://synthetic-documents/synthetic-axiez-inspection.pdf',
    modelType: 'AXIEZ',
    snippet: '合成評価用の出典です。実資料ではありません。',
  }] : [];
  return {
    content: empty ? '' : `合成応答 (${body.mode}): ${body.query}`,
    responseType: empty ? 'not_found' : 'pages',
    sessionId: body.sessionId || `synthetic-${body.mode}-session`,
    messageId: `synthetic-${body.mode}-${body.senpaiTurnId}`,
    clarifyQuestions: [],
    sourceDocuments,
    pageCandidates: [],
    ...(body.includeKnowhow ? {
      knowhow: { status: 'not_found', indexVersion: `sha256:${'0'.repeat(64)}`, matches: [], searchTerms: [] },
    } : {}),
  };
}

function historyRow({ conversationId, turnId, mode, role, content, timestamp, sessionId }) {
  return {
    userId: OWNER,
    sessionId,
    messageId: `${mode}-${role}-${turnId}`,
    role,
    content,
    ragMode: mode,
    senpaiConversationId: conversationId,
    senpaiTurnId: turnId,
    timestamp,
    ttl: Math.floor(Date.now() / 1000) + 60 * 24 * 60 * 60,
  };
}

function createApiServer() {
  return createServer(async (request, response) => {
    if (request.method === 'OPTIONS') return json(response, 200, {});
    if (request.headers.authorization !== 'Bearer dev-token') return json(response, 401, { error: 'Unauthorized' });
    const url = new URL(request.url || '/', `http://${HOST}`);
    if (request.method === 'GET' && url.pathname === '/chat/sessions') {
      const sessions = [...conversations.entries()].map(([conversationId, value]) => ({
        conversationId,
        title: [...value.turns.values()][0]?.[0]?.content || '合成質問',
        createdAt: value.createdAt,
        lastMessageTime: new Date().toISOString(),
        messageCount: value.turns.size,
        daysUntilDeletion: 60,
      }));
      return json(response, 200, { context: 'senpai', complete: true, sessions });
    }
    const detail = url.pathname.match(/^\/chat\/sessions\/([0-9a-f-]+)\/messages$/iu);
    if (request.method === 'GET' && detail) {
      const conversationId = detail[1];
      const conversation = conversations.get(conversationId);
      if (!conversation) return json(response, 404, { error: 'Not found' });
      return json(response, 200, {
        context: 'senpai', conversationId, complete: true, readOnly: false,
        messages: [...conversation.turns.values()].flat(),
      });
    }
    if (request.method === 'POST' && url.pathname === '/rag/query') {
      const body = await collectBody(request);
      requests.push(body);
      await new Promise((resolve) => setTimeout(resolve, 300));
      if (body.query.includes('検索失敗')) return json(response, 503, { error: 'synthetic failure' });
      const turnId = body.senpaiTurnId;
      const conversationId = body.senpaiConversationId;
      const answer = answerFor(body);
      if (!conversationId || !turnId) return json(response, 400, { error: 'Missing synthetic conversation identity' });
      const conversation = conversations.get(conversationId) || { turns: new Map(), createdAt: new Date().toISOString() };
      const turnRows = conversation.turns.get(turnId) || [];
      const now = new Date().toISOString();
      turnRows.push(
        historyRow({ conversationId, turnId, mode: body.mode, role: 'user', content: body.query, timestamp: now, sessionId: answer.sessionId }),
        historyRow({ conversationId, turnId, mode: body.mode, role: 'assistant', content: answer.content, timestamp: new Date(Date.now() + 1).toISOString(), sessionId: answer.sessionId }),
      );
      conversation.turns.set(turnId, turnRows);
      conversations.set(conversationId, conversation);
      return json(response, 200, {
        ...answer,
        ...(body.senpaiConversationId ? { senpaiConversationId: body.senpaiConversationId } : {}),
        ...(body.senpaiTurnId ? { senpaiTurnId: body.senpaiTurnId } : {}),
      });
    }
    return json(response, 404, { error: 'Not found' });
  });
}

async function availablePort() {
  const server = createServer();
  server.listen(0, HOST);
  await once(server, 'listening');
  const { port } = server.address();
  await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  return port;
}

async function waitForWeb(url) {
  const deadline = Date.now() + 90_000;
  while (Date.now() < deadline) {
    if (web.exitCode !== null) throw new Error(`Next.js exited early (${web.exitCode})`);
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch { /* Wait for Next.js startup. */ }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error('Next.js did not become ready within 90 seconds');
}

async function stop(child) {
  if (!child || child.exitCode !== null) return;
  child.kill('SIGTERM');
  await Promise.race([once(child, 'exit'), new Promise((resolve) => setTimeout(resolve, 5_000))]);
  if (child.exitCode === null) child.kill('SIGKILL');
}

try {
  const apiPort = await availablePort();
  api = createApiServer();
  api.listen(apiPort, HOST);
  await once(api, 'listening');

  const webPort = await availablePort();
  web = spawn('npm', ['run', 'dev', '--', '--hostname', HOST, '--port', String(webPort)], {
    cwd: new URL('../..', import.meta.url),
    env: {
      ...process.env,
      NEXT_TELEMETRY_DISABLED: '1',
      NEXT_PUBLIC_SKIP_AUTH: 'true',
      NEXT_PUBLIC_DEV_ADMIN: 'true',
      NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH: 'true',
      NEXT_PUBLIC_ENABLE_SENPAI_RESEARCH: 'false',
      NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS: 'false',
      NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS: 'false',
      NEXT_PUBLIC_RAG_API_URL: `http://${HOST}:${apiPort}`,
      NEXT_PUBLIC_CHAT_API_URL: `http://${HOST}:${apiPort}`,
    },
    stdio: 'inherit',
  });
  const baseUrl = `http://${HOST}:${webPort}`;
  await waitForWeb(`${baseUrl}/knowledge/chat`);

  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const pageErrors = [];
  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
    console.error('Browser page error:', error);
  });
  page.on('console', (message) => { if (message.type() === 'error') console.error('Browser console:', message.text()); });
  await page.goto(`${baseUrl}/knowledge/chat`);
  try {
    await page.getByRole('heading', { name: '先輩チャット' }).waitFor({ timeout: 10_000 });
  } catch (error) {
    console.error('Initial page text:', (await page.locator('body').innerText()).slice(0, 1200));
    throw error;
  }

  const question = page.getByRole('textbox', { name: '質問を入力' });
  await question.fill('合成質問: AXIEZ の点検資料を確認');
  await page.getByRole('button', { name: '質問を送信' }).click();
  await page.getByRole('button', { name: '中止' }).waitFor();
  assert.equal(await question.isDisabled(), true, 'composer is disabled during the in-flight request');
  try {
    await page.getByRole('region', { name: '技術KBからの回答' }).getByText('合成応答 (normal): 合成質問: AXIEZ の点検資料を確認').waitFor({ timeout: 10_000 });
  } catch (error) {
    console.error('After first request:', (await page.locator('body').innerText()).slice(-1800));
    console.error('Synthetic API requests:', JSON.stringify(requests));
    throw error;
  }
  await page.getByRole('link', { name: '合成資料: AXIEZ 点検要領 · 4ページ' }).waitFor();
  assert.equal(requests.length, 2, 'one request per search lane');
  assert.deepEqual(new Set(requests.map((item) => item.mode)), new Set(['normal', 'law']));
  assert.equal(new Set(requests.map((item) => item.senpaiTurnId)).size, 1);

  await page.getByRole('button', { name: '履歴を開く' }).click();
  await page.getByRole('button', { name: /合成質問: AXIEZ の点検資料を確認/ }).click();
  await page.getByRole('region', { name: '技術KBからの回答' }).getByText('合成応答 (normal): 合成質問: AXIEZ の点検資料を確認').waitFor();
  const savedConversationId = new URL(page.url()).searchParams.get('conversation');
  assert.ok(savedConversationId && /^[0-9a-f-]{36}$/iu.test(savedConversationId));
  assert.ok(requests.every((item) => item.senpaiConversationId === savedConversationId));

  await page.getByRole('button', { name: '新しい相談を始める' }).click();
  await question.fill('根拠なしの合成質問');
  await page.getByRole('button', { name: '質問を送信' }).click();
  await page.getByRole('region', { name: '技術KBからの回答' }).getByText('このKBでは該当情報を確認できませんでした。').waitFor();
  const emptyResultAlerts = await page.getByRole('alert').allInnerTexts();
  assert.ok(emptyResultAlerts.every((text) => !text.includes('検索結果の形式') && !text.includes('検索サービス')), `empty result should not become a search error: ${emptyResultAlerts.join(' | ')}`);

  await page.getByRole('button', { name: '新しい相談を始める' }).click();
  await question.fill('検索失敗を再現する合成質問');
  await page.getByRole('button', { name: '質問を送信' }).click();
  await page.getByRole('alert').first().waitFor();
  await page.getByRole('heading', { name: '先輩チャット' }).waitFor();
  assert.equal(requests.filter((item) => item.query.includes('検索失敗')).length, 2);

  assert.equal(await page.locator('body').evaluate((element) => element.scrollWidth > window.innerWidth), false, 'mobile page does not overflow horizontally');
  await page.setViewportSize({ width: 1280, height: 800 });
  assert.equal(await page.locator('body').evaluate((element) => element.scrollWidth > window.innerWidth), false, 'desktop page does not overflow horizontally');
  assert.deepEqual(pageErrors, [], `browser runtime errors: ${pageErrors.join(' | ')}`);
  console.log('PASS: synthetic browser flow, two-lane API, citation display, history restore, no-evidence state, search-failure state, mobile/desktop viewport.');
} finally {
  await browser?.close();
  await stop(web);
  if (api?.listening) await new Promise((resolve) => api.close(resolve));
}
