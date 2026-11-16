import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { chromium } from 'playwright';

const HOST = '127.0.0.1';
const OWNER = 'synthetic-user';
const conversations = new Map();
const requests = [];
const retryRequests = new Set();
const commentLawRetryRequests = new Set();
const rewriteRequests = [];
const fieldSummaryRequests = [];
const rewriteProblems = [];
const screenshotDirectory = process.env.KNOWHOW_SCREENSHOT_DIR;
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
  const commentReview = body.query.includes('点検対象の停止条件と復旧条件');
  const empty = body.query.includes('根拠なし')
    && !(body.mode === 'normal' && body.query.includes('一時失敗'));
  const sourceDocuments = !empty && (body.mode === 'normal' || commentReview) ? [{
    title: body.mode === 'law' ? '合成資料: 点検安全基準' : '合成資料: AXIEZ 点検要領',
    documentName: body.mode === 'law' ? 'synthetic-inspection-law.pdf' : 'synthetic-axiez-inspection.pdf',
    pageNumber: 4,
    ...(body.mode === 'law' && commentReview ? {
      lawCitation: {
        lawId: '347M50002000032',
        lawTitle: '合成点検安全基準',
        lawNumber: '合成評価用令第三十二号',
        effectiveDate: '2025-04-01',
        provisionType: 'main',
        provisionReference: '第4条',
        sourceUrl: 'https://laws.e-gov.go.jp/law/347M50002000032',
      },
    } : {
      sourceUri: 's3://synthetic-documents/synthetic-axiez-inspection.pdf',
      ...(body.mode === 'normal' ? { modelType: 'AXIEZ' } : {}),
    }),
    snippet: '合成評価用の出典です。実資料ではありません。',
  }] : [];
  return {
    content: empty ? '' : commentReview
      ? body.mode === 'law'
        ? '合成法令追記案: 適用対象と必要な安全措置を確認し、記録を保存する。'
        : '合成追記案: 点検前に対象機器の停止状態を確認し、復旧後に異常がないことを記録する。'
      : `合成応答 (${body.mode}): ${body.query}`,
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

const REWRITE_MAIN = '統合した回答・ノウハウ';
const REWRITE_ADDED_LINE = '- 合成の根拠に基づく書き換え: 点検資料の要件を確認済み。';
const SECTION_COMMENT = '点検対象の停止条件と復旧条件を、根拠資料に沿って明記したい。';
const FIELD_EXCERPT = '合成条件で確認端子を目視した記録です。\r\n観測時の状況も記録した。';
const FIELD_OUTSIDE_SELECTION = '原文の選択外を検出する合成文字列';
const FIELD_SUMMARY = '合成条件で確認端子の表示を目視した事例がある。';

/** 書き換え案のモック。送られた内容が契約どおりで、未確認の根拠やカード全文を含まないことをここで確認する。 */
function rewriteResponseFor(body) {
  const text = JSON.stringify(body);
  const evidence = Array.isArray(body.evidence) ? body.evidence : [];
  if (Object.keys(body).sort().join(',') !== 'cardVersion,context,evidence,knowledgeId,targets') rewriteProblems.push('keys');
  if (evidence.length !== 1 || evidence[0].lane !== 'technical') rewriteProblems.push('evidence は出典つきの技術KB 1件だけ');
  if (!evidence[0]?.answer?.includes('合成応答 (normal)')) rewriteProblems.push('answer');
  for (const leaked of ['source_refs', 'lists_item', 'onenote_id', '合成試験用の安全な点検手順', 'synthetic-local-card.md', 'questionId']) {
    if (text.includes(leaked)) rewriteProblems.push(`含めてはいけない: ${leaked}`);
  }
  if (!body.targets.some((target) => target.heading === REWRITE_MAIN)) rewriteProblems.push('targets');
  if (rewriteProblems.length) return null;
  return {
    knowledgeId: body.knowledgeId,
    cardVersion: body.cardVersion,
    sections: body.targets.map((target) => target.heading === REWRITE_MAIN
      ? { heading: target.heading, status: 'changed', body: `${target.body}\n${REWRITE_ADDED_LINE}`, reason: '確認済みの根拠 1 で点検資料の記載を確認できたため。', evidence: [1], warnings: [] }
      : { heading: target.heading, status: 'unchanged' }),
    conflicts: [{ heading: null, summary: '合成の食い違い: カードの記述と根拠の記述が異なります。', evidence: [1] }],
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
      if (body.query.includes('一時失敗') && body.mode === 'normal' && !retryRequests.has(body.query)) {
        retryRequests.add(body.query);
        return json(response, 503, { error: 'synthetic transient failure' });
      }
      if (body.mode === 'law' && body.query.includes(SECTION_COMMENT) && !commentLawRetryRequests.has(body.query)) {
        commentLawRetryRequests.add(body.query);
        return json(response, 503, { error: 'synthetic comment law failure' });
      }
      if (!body.senpaiConversationId || !body.senpaiTurnId) return json(response, 200, answerFor(body));
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
    if (request.method === 'POST' && url.pathname === '/rag/knowhow/rewrite-proposal') {
      const body = await collectBody(request);
      if (body.evidence?.[0]?.lane === 'field') {
        fieldSummaryRequests.push(body);
        return json(response, 200, {
          knowledgeId: body.knowledgeId, cardVersion: body.cardVersion,
          sections: [{ heading: REWRITE_MAIN, status: 'changed', body: FIELD_SUMMARY, reason: '指定された箇所に記載があるため。', evidence: [1] }],
          conflicts: [],
        });
      }
      rewriteRequests.push(body);
      await new Promise((resolve) => setTimeout(resolve, 300));
      const result = rewriteResponseFor(body);
      return result ? json(response, 200, result) : json(response, 400, { error: 'ValidationError' });
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

async function testFieldMaterialWorkflow(page) {
  await page.clock.setFixedTime('2026-11-17T12:00:00+09:00');
  const field = page.getByRole('region', { name: '現場資料の取り込み' });
  const original = Buffer.from(`\uFEFF合成の現場資料\r\n${FIELD_EXCERPT}\r\n${FIELD_OUTSIDE_SELECTION}\r\n`, 'utf8');
  const file = field.getByLabel('現場資料ファイルを選ぶ');
  await file.setInputFiles({ name: 'synthetic-field-notes.txt', mimeType: 'text/plain', buffer: original });
  const preview = field.getByLabel('選んだ資料のプレビュー');
  await preview.evaluate((element, value) => {
    const start = element.value.indexOf(value);
    if (start < 0) throw new Error('The synthetic excerpt does not appear in the source preview');
    element.setSelectionRange(start, start + value.length);
  }, FIELD_EXCERPT.replaceAll('\r\n', '\n'));
  await field.getByRole('button', { name: '選択範囲を抜粋にする' }).click();
  await field.getByText('出典情報を入力', { exact: true }).click();
  await field.getByLabel('資料名', { exact: true }).fill('合成現場資料');
  await field.getByLabel('版', { exact: true }).fill('合成第2版');
  await field.getByLabel('ページ・項目などの場所').fill('確認事項の節');
  await field.getByLabel('確認済みの参照URL（任意）').fill('https://example.invalid/field-notes');
  const originalDownload = page.waitForEvent('download');
  await field.getByRole('button', { name: '原本をダウンロード' }).click();
  const { readFile } = await import('node:fs/promises');
  assert.deepEqual(await readFile(await (await originalDownload).path()), original, 'the original is locally recoverable byte for byte');
  const generate = field.getByRole('button', { name: '要約案を作る', exact: true });
  assert.equal(await generate.isDisabled(), true, 'selected excerpt is not sent without consent');
  assert.equal(fieldSummaryRequests.length, 0);
  await field.getByLabel('確認テーマ', { exact: true }).fill('目視の事例を整理する');
  await field.getByLabel('選んだ抜粋・確認テーマ・資料名・確認日（本日）をAIへ送ってよいことを確認した').check();
  await generate.click();
  await field.getByRole('button', { name: '要約欄へ反映' }).click();
  assert.equal(fieldSummaryRequests.length, 1);
  const request = fieldSummaryRequests[0];
  assert.deepEqual(request.targets, [{ heading: REWRITE_MAIN, body: '' }]);
  assert.deepEqual(request.context, []);
  assert.equal(request.knowledgeId, 'KH-FIELD-MATERIAL');
  assert.equal(request.evidence[0].question, '目視の事例を整理する');
  assert.equal(request.evidence[0].checkedOn, '2026-11-17');
  assert.equal(request.evidence[0].lane, 'field');
  assert.equal(request.evidence[0].answer, FIELD_EXCERPT);
  assert.deepEqual(request.evidence[0].sources, [{ title: '合成現場資料' }]);
  for (const privateValue of [FIELD_OUTSIDE_SELECTION, 'synthetic-field-notes.txt', 'example.invalid', '根拠なしの合成質問', '現場資料の合成テストカード']) {
    assert.equal(JSON.stringify(request).includes(privateValue), false);
  }
  const apply = field.getByRole('button', { name: '作業中のMarkdownに反映' });
  assert.equal(await apply.isDisabled(), true, 'human review and preview gate application');
  await field.getByLabel('要約案と資料の抜粋を確認した').check();
  await field.getByRole('button', { name: '変更案をプレビュー' }).click();
  await apply.click();
  const recordDownload = page.waitForEvent('download');
  await page.getByRole('button', { name: 'JSON作業記録を保存' }).click();
  const recordText = await readFile(await (await recordDownload).path(), 'utf8');
  const saved = JSON.parse(recordText);
  assert.match(saved.proposal.markdown, /## 現場資料に基づくノウハウ/u);
  assert.match(saved.proposal.markdown, new RegExp(FIELD_SUMMARY, 'u'));
  assert.match(saved.proposal.markdown, /local-sha256:[a-f0-9]{64}/u);
  assert.match(saved.proposal.markdown, /origin: field_report/u);
  assert.match(saved.proposal.markdown, /確認事項の節/u);
  assert.equal(saved.proposal.publishable, false);
  for (const originalText of [FIELD_EXCERPT.split('\r\n')[0], FIELD_OUTSIDE_SELECTION]) {
    assert.equal(saved.proposal.markdown.includes(originalText), false);
  }
  await page.getByLabel('JSON作業記録を開く').setInputFiles({
    name: 'synthetic-field-record.json', mimeType: 'application/json', buffer: Buffer.from(recordText),
  });
  await page.getByRole('status').filter({ hasText: 'JSON作業記録を開きました。' }).waitFor();
  assert.match(await page.getByLabel('Markdown本文を編集').inputValue(), new RegExp(FIELD_SUMMARY, 'u'));
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
      NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE: 'true',
      NEXT_PUBLIC_ENABLE_KNOWHOW_FIELD_MATERIAL: 'true',
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
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, timezoneId: 'Asia/Tokyo' });
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
  await page.getByRole('link', { name: '不足を確認する' }).click();
  await page.getByText('先輩チャットで情報が見つからなかった相談から開きました。', { exact: false }).waitFor();
  assert.equal(new URL(page.url()).search, '', 'the chat query is not passed in the URL');
  const newTitle = page.getByLabel('カードのタイトル');
  assert.equal(await newTitle.inputValue(), '', 'the question is not copied to the draft');
  await newTitle.fill('現場資料の合成テストカード');
  await page.getByRole('button', { name: '下書きを作成' }).click();
  await page.getByLabel('Markdown本文を編集').waitFor();
  await testFieldMaterialWorkflow(page);

  await page.goto(`${baseUrl}/knowledge/chat`);
  await question.fill('検索失敗を再現する合成質問');
  await page.getByRole('button', { name: '質問を送信' }).click();
  await page.getByRole('alert').first().waitFor();
  await page.getByRole('heading', { name: '先輩チャット' }).waitFor();
  assert.equal(requests.filter((item) => item.query.includes('検索失敗')).length, 2);
  assert.equal(await page.getByRole('link', { name: '不足を確認する' }).count(), 0, 'service failures do not create knowledge gaps');

  await page.goto(`${baseUrl}/admin/knowledge/research`);
  await page.getByRole('heading', { name: '工技先輩（開発中）' }).waitFor();
  const syntheticCard = `---
knowledge_id: KH-SYNTHETIC-001
card_version: 1
title: 合成試験用の安全な点検手順
source_refs:
  - ref_type: lists_item
    list_item_id: "71"
  - ref_type: onenote_page
    onenote_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa:42"
---
# 合成試験用の安全な点検手順

## 統合した回答・ノウハウ
- 合成条件で動作を確認する。

## 未確認事項
- （該当なし）

## KB確認に基づく追記
（該当なし）

## 正式資料・元情報
（該当なし）
`;
  const markdownPicker = page.getByLabel('Markdownファイルを選択');
  await markdownPicker.setInputFiles({
    name: 'synthetic-local-card.md',
    mimeType: 'text/markdown',
    buffer: Buffer.from(syntheticCard, 'utf8'),
  });
  const cardBody = page.getByLabel('Markdown本文を編集');
  const commentRegion = page.getByRole('region', { name: 'コメントから追記案を作る' });
  const optionalCardSearch = page.locator('#optional-card-search');
  const optionalManualResearch = page.locator('#optional-manual-research');
  const optionalOneNote = page.locator('#optional-onenote');
  const optionalMetadata = page.locator('#optional-metadata');
  await page.getByRole('heading', { name: '工技先輩（開発中）' }).waitFor();
  assert.equal(await optionalCardSearch.evaluate((details) => details.open), false, 'card-wide KB search is closed by default');
  assert.equal(await optionalManualResearch.evaluate((details) => details.open), false, 'manual KB search is closed by default');
  assert.equal(await optionalOneNote.evaluate((details) => details.open), false, 'OneNote and original-card information are closed by default');
  assert.equal(await optionalMetadata.evaluate((details) => details.open), false, 'original-card metadata is closed by default');
  assert.equal(await page.getByRole('heading', { name: 'カードを一括照合' }).count(), 0, 'secondary card-search controls are not shown initially');
  assert.equal(await cardBody.isVisible(), true, 'the primary Markdown editor is available immediately');
  assert.equal(await commentRegion.isVisible(), true, 'the primary comment workflow is available immediately');
  await optionalCardSearch.locator('summary').click();
  await page.getByRole('heading', { name: 'カードを一括照合' }).waitFor();

  await page.getByLabel('照合する参照先').selectOption('lists:71');
  await page.getByLabel('照合するMarkdownファイルを選ぶ').setInputFiles({
    name: 'lists-snapshot.md',
    mimeType: 'text/markdown',
    buffer: Buffer.from('---\nsnapshot_type: lists_csv_import\nsource_system: Microsoft Lists\nsource_list_name: 首都工・不具合情報共有リスト\nsnapshot_date: 2026-11-12\n---\n## Lists item ID 71: 点検ルール\n項目71の確認済み条件。\n## Lists item ID 72: 隣接項目\n項目72の隣接資料の内容。JSONには残さない抜粋です。\n', 'utf8'),
  });
  const loadedExcerpt = page.getByRole('region', { name: '読み込んだ資料の抜粋' });
  await loadedExcerpt.getByText(/項目71の確認済み条件/).waitFor();
  assert.equal(await loadedExcerpt.getByText(/項目72|隣接資料の内容/).count(), 0, 'snapshot review shows only the linked Lists item');
  await page.getByLabel('ファイル名、ページ名、または項目ID').fill('Lists item 71 / 点検ルール');
  await page.getByLabel('カードとの照合結果').selectOption('supports');
  await page.getByRole('textbox', { name: '確認メモ', exact: true }).fill('項目71の確認済み条件をカードと照合した。');
  await page.getByRole('button', { name: '照合記録を追加' }).click();
  await page.getByText('Lists §71 · カードの内容を支持する', { exact: true }).waitFor();
  await page.getByText('スナップショット · Lists item 71 / 点検ルール · 資料日 2026-11-12', { exact: true }).waitFor();

  const updatedCardBody = `${await cardBody.inputValue()}\n- Lists item 71 を照合し、確認した適用条件を追加する。`;
  await cardBody.fill(updatedCardBody);
  assert.match(await cardBody.inputValue(), /Lists item 71 を照合し、確認した適用条件を追加する。/u);
  const commentField = commentRegion.getByLabel('足りない内容のコメント');
  const commentDraft = '任意ツールを開閉しても、このコメント下書きを保つ。';
  await commentField.fill(commentDraft);
  await optionalManualResearch.locator('summary').click();
  await optionalManualResearch.getByLabel('技術KBと法令KBへの質問').waitFor();
  assert.equal(await cardBody.inputValue(), updatedCardBody, 'opening manual search preserves the editor contents');
  assert.equal(await commentField.inputValue(), commentDraft, 'opening manual search preserves the comment draft');
  await optionalOneNote.locator('summary').click();
  await optionalOneNote.getByRole('region', { name: 'OneNote追記案と確認' }).waitFor();
  assert.equal(await cardBody.inputValue(), updatedCardBody, 'opening OneNote tools preserves the editor contents');
  assert.equal(await commentField.inputValue(), commentDraft, 'opening OneNote tools preserves the comment draft');
  await optionalOneNote.locator('summary').click();
  await optionalManualResearch.locator('summary').click();
  await commentField.fill('');
  if (process.env.CAPTURE_KNOWHOW_SCREENSHOTS === '1' && screenshotDirectory) {
    await mkdir(screenshotDirectory, { recursive: true });
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.locator('#review-card-sources').screenshot({
      path: join(screenshotDirectory, 'card-source-review.png'),
      style: 'header.sticky, nextjs-portal { visibility: hidden; }',
    });
  }

  const generatedQuestion = page.getByRole('textbox', { name: '質問 1' });
  await generatedQuestion.fill('一時失敗の根拠なし 合成質問');
  await page.getByRole('group', { name: /質問 1/ }).getByLabel('法令KB').check();
  if (process.env.CAPTURE_KNOWHOW_SCREENSHOTS === '1') {
    await page.setViewportSize({ width: 1100, height: 820 });
    if (screenshotDirectory) await mkdir(screenshotDirectory, { recursive: true });
    await page.getByRole('region', { name: 'カードを一括照合' })
      .screenshot({ path: screenshotDirectory ? join(screenshotDirectory, 'card-check-questions.png') : undefined });
  } else {
    assert.equal(await page.locator('body').evaluate((element) => element.scrollWidth > window.innerWidth), false, 'card-check page does not overflow on mobile');
  }
  const checkButton = page.getByRole('button', { name: '照合する', exact: true });
  await checkButton.click();
  if (process.env.CAPTURE_KNOWHOW_SCREENSHOTS === '1' && screenshotDirectory) {
    await page.getByRole('region', { name: 'カードを一括照合' })
      .screenshot({ path: join(screenshotDirectory, 'card-check-running.png') });
  }
  await page.getByRole('button', { name: '中止' }).waitFor();
  await page.getByRole('button', { name: '再試行' }).waitFor();
  const firstBatch = requests.filter((item) => item.query === '一時失敗の根拠なし 合成質問');
  assert.deepEqual(new Set(firstBatch.map((item) => item.mode)), new Set(['normal', 'law']));
  for (const item of firstBatch) {
    assert.deepEqual(Object.keys(item).sort(), ['filters', 'mode', 'query']);
    assert.deepEqual(item.filters, {});
    assert.equal(JSON.stringify(item).includes('synthetic-local-card.md'), false);
    assert.equal(JSON.stringify(item).includes('KH-SYNTHETIC-001'), false);
    assert.equal(JSON.stringify(item).includes('合成試験用の安全な点検手順'), false);
  }

  await page.getByRole('button', { name: '再試行' }).click();
  await page.getByText('合成資料: AXIEZ 点検要領', { exact: true }).waitFor();
  await page.getByText(
    'このKBでは該当情報を確認できませんでした。もう一方のKBで代用せず、結果を分けて扱ってください。',
    { exact: true },
  ).waitFor();
  if (process.env.CAPTURE_KNOWHOW_SCREENSHOTS === '1' && screenshotDirectory) {
    await page.getByText('追記される内容を読む', { exact: true }).click();
    await page.getByRole('region', { name: 'カードを一括照合' })
      .screenshot({ path: join(screenshotDirectory, 'card-check-proposals.png') });
  }
  assert.equal(requests.filter((item) => item.query === '一時失敗の根拠なし 合成質問' && item.mode === 'normal').length, 2);
  assert.equal(requests.filter((item) => item.query === '一時失敗の根拠なし 合成質問' && item.mode === 'law').length, 1);

  const proposalChoice = page.getByRole('button', { name: '確認して追記する' });
  await proposalChoice.click();
  const rewritePanel = page.getByRole('region', { name: 'AI による本文の書き換え案' });
  await rewritePanel.getByText(/確認済みの根拠 1 件、書き換え対象 2 節/u).waitFor();
  await rewritePanel.getByRole('button', { name: 'AI に本文の書き換え案を作らせる' }).click();
  await rewritePanel.getByText('変更理由: 確認済みの根拠 1 で点検資料の記載を確認できたため。').waitFor();
  assert.equal(rewriteRequests.length, 1, 'the rewrite proposal is requested once');
  assert.deepEqual(rewriteProblems, [], `the rewrite request broke the contract: ${rewriteProblems.join(' | ')}`);
  const sectionChoices = rewritePanel.getByRole('article', { name: `${REWRITE_MAIN}の書き換え案` }).getByRole('button');
  assert.equal(await sectionChoices.count(), 2, 'the rewrite section has confirm and reject choices');
  assert.deepEqual(
    await sectionChoices.evaluateAll((buttons) => buttons.map((button) => button.getAttribute('aria-pressed'))),
    ['false', 'false'],
    'the rewrite section is unconfirmed by default',
  );
  await rewritePanel.getByText('1節中 0節を反映・0節を反映しない・1節が未確認').waitFor();
  const rewriteDecision = rewritePanel.getByRole('button', { name: '確認して反映する' });
  await rewriteDecision.click();
  await rewritePanel.getByText(/本文の主張を変えました。Git に入れるときは card_version を上げ/).waitFor();

  await page.getByRole('button', { name: '差分を確認' }).click();
  const rewritePreview = page.getByRole('region', { name: '採用する追記案の差分' });
  await rewritePreview.waitFor();
  await rewriteDecision.click();
  assert.equal(await rewritePreview.count(), 0, 'unconfirming the rewrite clears the preview built from the old decision');
  assert.equal(await page.getByRole('button', { name: '本文に反映' }).count(), 0, 'stale rewrite preview cannot be applied');

  await rewriteDecision.click();
  await page.getByRole('button', { name: '差分を確認' }).click();
  await rewritePreview.waitFor();
  await page.getByRole('heading', { name: '読み込んだ原文との差分' }).waitFor();
  if (process.env.CAPTURE_KNOWHOW_SCREENSHOTS === '1' && screenshotDirectory) {
    await page.getByRole('region', { name: 'カードを一括照合' })
      .screenshot({ path: join(screenshotDirectory, 'card-check-diff.png') });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.locator('body').evaluate((element) => element.scrollWidth > window.innerWidth), false, 'proposal preview does not overflow on mobile');
  await page.getByRole('button', { name: '本文に反映' }).click();
  await page.getByRole('heading', { name: '照合する質問を確認' }).waitFor();
  assert.equal(await page.getByRole('button', { name: '確認して追記する' }).count(), 0, 'adoption clears the confirmed proposals of the previous body');
  await page.getByRole('tab', { name: '差分' }).click();
  await page.getByRole('heading', { name: '合成試験用の安全な点検手順' }).waitFor();
  assert.match(await page.locator('main').innerText(), /KB照合/);
  assert.match(await page.locator('main').innerText(), /合成の根拠に基づく書き換え/, 'the rewritten section reaches the edited body together with the addition');
  assert.match(await page.locator('main').innerText(), /正式資料・元情報/);
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: '修正したMarkdownを保存' }).click();
  const download = await downloadPromise;
  const downloadedPath = await download.path();
  const downloadedMarkdown = await (await import('node:fs/promises')).readFile(downloadedPath, 'utf8');
  assert.match(downloadedMarkdown, /knowledge_id: KH-SYNTHETIC-001/);
  assert.match(downloadedMarkdown, /^status: draft$/m, 'export remains a draft proposal');
  assert.match(downloadedMarkdown, /合成試験用の安全な点検手順/);
  assert.match(downloadedMarkdown, /Lists item 71 を照合し、確認した適用条件を追加する。/u, 'the evidence-informed card edit is included in the draft');
  assert.match(downloadedMarkdown, /KB照合/);
  assert.match(downloadedMarkdown, /## 統合した回答・ノウハウ\n- 合成条件で動作を確認する。\n- 合成の根拠に基づく書き換え: 点検資料の要件を確認済み。/u, 'the confirmed section rewrite is in the draft');
  assert.doesNotMatch(downloadedMarkdown, /合成の食い違い/u, 'a conflict nobody added stays out of the card');
  assert.match(downloadedMarkdown, /## KB確認に基づく追記\n\n### KB照合（確認日 \d{4}-\d{2}-\d{2}）/u, 'the placeholder section is replaced by the confirmed addition');
  assert.doesNotMatch(downloadedMarkdown, /## KB確認に基づく追記\n（該当なし）/u, 'the no-information placeholder is gone');
  assert.match(downloadedMarkdown, /- 確認: 管理者が出典を確認（\d{4}-\d{2}-\d{2}）/u, 'the confirmation line is recorded');
  assert.doesNotMatch(downloadedMarkdown, /KB照合メモ（原資料未確認）/u, 'no unverified memo section is created');
  assert.match(downloadedMarkdown, /## 未確認事項\n- （該当なし）/u, 'unrelated empty sections remain available for human review');
  assert.match(downloadedMarkdown, /## 正式資料・元情報\n（該当なし）/u, 'reference section remains in the exported draft');

  const reviewExportPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'JSON作業記録を保存' }).click();
  const reviewExport = await reviewExportPromise;
  const reviewExportPath = await reviewExport.path();
  const reviewPacketText = await (await import('node:fs/promises')).readFile(reviewExportPath, 'utf8');
  const reviewPacket = JSON.parse(reviewPacketText);
  assert.equal(reviewPacket.sourceReviews[0].source.id, '71');
  assert.equal(reviewPacket.sourceReviews[0].source.kind, 'lists');
  assert.equal(reviewPacket.sourceReviews[0].revision, 0, 'the recorded source review remains tied to the pre-edit card revision');
  assert.equal(reviewPacket.sourceReviews[0].locator, 'Lists item 71 / 点検ルール');
  assert.equal(reviewPacketText.includes('項目72の隣接資料の内容'), false, 'neighboring source item is not exported');
  assert.equal(reviewPacketText.includes('項目71の確認済み条件。'), false, 'raw source excerpt is not exported');
  assert.match(reviewPacket.proposal.markdown, /Lists item 71 を照合し、確認した適用条件を追加する。/u);

  const targetSection = commentRegion.getByLabel('追記する節');
  const targetOption = await targetSection.locator('option').evaluateAll((options) => {
    const match = options.find((option) => option.textContent?.includes('統合した回答・ノウハウ'));
    return match?.value;
  });
  assert.ok(targetOption, 'the existing H2 section is available as a comment target');
  await page.getByRole('button', { name: `「${REWRITE_MAIN}」にコメント` }).click();
  await page.waitForFunction(() => document.activeElement?.getAttribute('data-testid') === 'review-comment-input');
  assert.equal(await targetSection.inputValue(), targetOption, 'the diff shortcut preselects the changed H2');
  const targetedComment = commentRegion.getByLabel('足りない内容のコメント');
  await targetedComment.fill(SECTION_COMMENT);
  await commentRegion.getByRole('button', { name: 'コメントを追加' }).click();
  await commentRegion.getByText(SECTION_COMMENT, { exact: true }).waitFor();

  const searchText = commentRegion.getByText('AIに送る検索文').locator('xpath=..').locator('p.whitespace-pre-wrap');
  const approvedQuery = await searchText.innerText();
  assert.match(approvedQuery, /合成試験用の安全な点検手順/u);
  assert.match(approvedQuery, /統合した回答・ノウハウ/u);
  assert.ok(approvedQuery.includes(SECTION_COMMENT));
  assert.equal(approvedQuery.includes('Lists item 71 を照合し、確認した適用条件を追加する。'), false, 'the whole card body is not sent');
  assert.equal(approvedQuery.includes('合成条件で動作を確認する。'), false, 'unrelated card content is excluded from the query');

  const beforeCommentRequests = requests.length;
  await commentRegion.getByRole('button', { name: 'AIで技術KB・法令KBを再確認' }).click();
  const techLane = commentRegion.getByRole('region', { name: '技術KBの検索結果' });
  const lawLane = commentRegion.getByRole('region', { name: '法令KBの検索結果' });
  const techGroup = commentRegion.getByRole('group', { name: '技術KBの照会と追記案' });
  const lawGroup = commentRegion.getByRole('group', { name: '法令KBの照会と追記案' });
  await techLane.getByText('合成資料: AXIEZ 点検要領', { exact: true }).waitFor();
  const lawRetry = lawGroup.getByRole('button', { name: '法令KBだけ再確認' });
  await lawRetry.waitFor();
  const techDraft = techGroup.getByLabel('技術KBの追記案');
  const initialTechDraft = await techDraft.inputValue();
  assert.match(initialTechDraft, /合成追記案/u);
  const editedTechDraft = `${initialTechDraft}\n作業記録を担当者が確認する。`;
  await techDraft.fill(editedTechDraft);
  assert.equal(await commentRegion.getByRole('region', { name: '追記前後の差分' }).count(), 0, 'nothing is added before the administrator confirms');
  assert.equal(await commentRegion.getByRole('button', { name: '確認した追記を対象の節に反映' }).count(), 0, 'no apply button before any confirmation');
  await techGroup.getByRole('button', { name: '確認して追記する' }).click();
  assert.equal(requests.length - beforeCommentRequests, 2, 'initial section recheck uses two KB requests');
  await lawRetry.click();
  await lawLane.getByText('合成点検安全基準', { exact: true }).waitFor();
  assert.equal(await techDraft.inputValue(), editedTechDraft, 'a law-only retry preserves the edited technical draft');
  const commentDiff = commentRegion.getByRole('region', { name: '追記前後の差分' });
  assert.match(await commentDiff.innerText(), /作業記録を担当者が確認する。/u, 'the confirmed technical choice still contributes to the preview');
  assert.match(await lawGroup.getByLabel('法令KBの追記案').inputValue(), /合成法令追記案/u);
  assert.match(await techLane.innerText(), /合成資料: AXIEZ 点検要領/u, 'the tech candidate is shown with its source');
  assert.match(await lawLane.innerText(), /合成点検安全基準/u, 'the law candidate is shown with its source');

  const commentRequests = requests.slice(beforeCommentRequests);
  assert.deepEqual(commentRequests.map((item) => item.mode).sort(), ['law', 'law', 'normal'], 'retry requests only the failed lane');
  for (const item of commentRequests) {
    assert.deepEqual(Object.keys(item).sort(), ['filters', 'mode', 'query']);
    assert.equal(item.query, approvedQuery);
    assert.deepEqual(item.filters, {});
    assert.equal(JSON.stringify(item).includes('KH-SYNTHETIC-001'), false);
    assert.equal(JSON.stringify(item).includes('Lists item 71 を照合し、確認した適用条件を追加する。'), false);
  }

  await lawGroup.getByRole('button', { name: '確認して追記する' }).click();
  await commentDiff.waitFor();
  assert.match(await commentDiff.innerText(), /合成条件で動作を確認する。/u, 'the before side of the section diff is visible');
  assert.match(await commentDiff.innerText(), /合成追記案: 点検前に対象機器の停止状態/u, 'the after side contains the tech candidate');
  assert.match(await commentDiff.innerText(), /合成法令追記案: 適用対象と必要な安全措置/u, 'the after side contains the law candidate');
  if (process.env.CAPTURE_KNOWHOW_SCREENSHOTS === '1' && screenshotDirectory) {
    await mkdir(screenshotDirectory, { recursive: true });
    await commentRegion.screenshot({ path: join(screenshotDirectory, 'card-comment-diff.png') });
  }
  await commentRegion.getByRole('button', { name: '確認した追記を対象の節に反映' }).click();
  await page.getByRole('tab', { name: '編集' }).click();
  const changedBody = await page.getByLabel('Markdown本文を編集').inputValue();
  const sectionStart = changedBody.indexOf('## 統合した回答・ノウハウ');
  const sectionEnd = changedBody.indexOf('\n## ', sectionStart + 1);
  const changedSection = changedBody.slice(sectionStart, sectionEnd < 0 ? undefined : sectionEnd);
  assert.match(changedSection, /合成追記案: 点検前に対象機器の停止状態を確認し、復旧後に異常がないことを記録する。/u, 'the tech candidate is inserted into the selected H2');
  assert.match(changedSection, /合成法令追記案: 適用対象と必要な安全措置を確認し、記録を保存する。/u, 'the law candidate is inserted into the selected H2');
  assert.match(changedSection, /確認: 管理者が出典を確認（\d{4}-\d{2}-\d{2}）/u, 'the inserted answer carries the administrator confirmation line');
  assert.doesNotMatch(changedSection, /原資料未確認|AI追記案/u, 'the inserted answer is not labelled as unverified AI text');
  assert.equal(await commentRegion.getByRole('region', { name: '技術KBの検索結果' }).count(), 0, 'applying an answer clears the result tied to the old body revision');
  await page.getByRole('tab', { name: 'プレビュー' }).click();
  await page.locator('a[href^="/doc?uri="]').first().waitFor();
  await page.getByRole('tab', { name: '差分' }).click();
  assert.match(await page.locator('main').innerText(), /管理者が出典を確認/u);
  assert.match(await page.locator('main').innerText(), /点検前に対象機器の停止状態を確認し/u);

  const finalMarkdownPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: '修正したMarkdownを保存' }).click();
  const finalMarkdownDownload = await finalMarkdownPromise;
  const finalMarkdown = await (await import('node:fs/promises')).readFile(await finalMarkdownDownload.path(), 'utf8');
  assert.match(finalMarkdown, /## 統合した回答・ノウハウ[\s\S]*点検前に対象機器の停止状態を確認[\s\S]*確認: 管理者が出典を確認/u);

  const finalJsonPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'JSON作業記録を保存' }).click();
  const finalJsonDownload = await finalJsonPromise;
  const finalReviewPacket = JSON.parse(await (await import('node:fs/promises')).readFile(await finalJsonDownload.path(), 'utf8'));
  assert.equal(finalReviewPacket.reviewComments.length, 1);
  assert.equal(finalReviewPacket.reviewComments[0].text, SECTION_COMMENT);
  assert.equal(JSON.stringify(finalReviewPacket.reviewComments).includes('合成追記案'), false, 'JSON preserves the human comment, not AI answers');

  await page.getByLabel('JSON作業記録を開く').setInputFiles({
    name: finalJsonDownload.suggestedFilename(),
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(finalReviewPacket)),
  });
  await page.getByRole('status').filter({ hasText: 'JSON作業記録を開きました。' }).waitFor();
  await page.getByRole('tab', { name: '編集' }).click();
  assert.equal(await cardBody.inputValue(), changedBody, 'opening the saved JSON restores exactly the edited body');
  await commentRegion.getByText(SECTION_COMMENT, { exact: true }).waitFor();

  assert.equal(await page.locator('body').evaluate((element) => element.scrollWidth > window.innerWidth), false, 'mobile page does not overflow horizontally');
  await page.setViewportSize({ width: 1280, height: 800 });
  assert.equal(await page.locator('body').evaluate((element) => element.scrollWidth > window.innerWidth), false, 'desktop page does not overflow horizontally');
  assert.deepEqual(pageErrors, [], `browser runtime errors: ${pageErrors.join(' | ')}`);
  console.log('PASS: synthetic Senpai and field-material workflows, excerpt-only suggestion, cited draft restore, lane retry, and mobile/desktop viewport.');
} finally {
  await browser?.close();
  await stop(web);
  if (api?.listening) await new Promise((resolve) => api.close(resolve));
}
