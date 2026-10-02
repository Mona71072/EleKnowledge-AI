/* eslint-disable */
// EleKnowledge 利用者マニュアル用 画面キャプチャ
// - 公開ページ: 実サイト(develop)をそのまま撮影
// - ログイン後ページ: 実サイトの develop ビルドに対し、ブラウザ内で認証トークンと API 応答を差し替えて撮影
//   （バックエンド・DynamoDB には一切書き込まない）
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = 'https://develop.d9ngenggxas1k.amplifyapp.com';
const CLIENT_ID = 'doa4arfmc7shs8u0mb91u70mq';
const POOL_ID = 'ap-northeast-1_DN17ekXik';
const OUT = path.join(__dirname, 'shots');
fs.mkdirSync(OUT, { recursive: true });

const SAMPLE_NAME = '現場 太郎';
const SAMPLE_EMAIL = 'sample.user@meltec.co.jp';
const SAMPLE_SUB = '11111111-2222-3333-4444-555555555555';
const USERNAME = SAMPLE_SUB;

function b64url(obj) {
  return Buffer.from(JSON.stringify(obj)).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
}
function jwt(payload) {
  return `${b64url({ alg: 'RS256', typ: 'JWT', kid: 'sample' })}.${b64url(payload)}.c2lnbmF0dXJl`;
}
const now = Math.floor(Date.now() / 1000);
const exp = now + 60 * 60 * 24 * 30;
const ID_TOKEN = jwt({
  sub: SAMPLE_SUB, email: SAMPLE_EMAIL, name: SAMPLE_NAME, email_verified: true,
  'cognito:username': USERNAME, aud: CLIENT_ID, token_use: 'id', auth_time: now, iat: now, exp,
  iss: `https://cognito-idp.ap-northeast-1.amazonaws.com/${POOL_ID}`,
});
const ACCESS_TOKEN = jwt({
  sub: SAMPLE_SUB, username: USERNAME, client_id: CLIENT_ID, token_use: 'access', scope: 'aws.cognito.signin.user.admin',
  auth_time: now, iat: now, exp, iss: `https://cognito-idp.ap-northeast-1.amazonaws.com/${POOL_ID}`, jti: 'sample',
});

const seedScript = `
(() => {
  const p = 'CognitoIdentityServiceProvider.${CLIENT_ID}';
  try {
    localStorage.setItem(p + '.LastAuthUser', ${JSON.stringify(USERNAME)});
    localStorage.setItem(p + '.${USERNAME}.idToken', ${JSON.stringify(ID_TOKEN)});
    localStorage.setItem(p + '.${USERNAME}.accessToken', ${JSON.stringify(ACCESS_TOKEN)});
    localStorage.setItem(p + '.${USERNAME}.refreshToken', 'sample-refresh-token');
    localStorage.setItem(p + '.${USERNAME}.clockDrift', '0');
    localStorage.setItem(p + '.${USERNAME}.signInDetails', JSON.stringify({ loginId: ${JSON.stringify(SAMPLE_EMAIL)}, authFlowType: 'USER_SRP_AUTH' }));
    localStorage.setItem('home:guideCollapsed', '0');
  } catch (e) {}
})();
`;

// Amplify は ssr:true 設定のためトークンは Cookie に保存される → Cookie を差し込む
const COOKIE_DOMAIN = 'develop.d9ngenggxas1k.amplifyapp.com';
function authCookies() {
  const p = `CognitoIdentityServiceProvider.${CLIENT_ID}`;
  const mk = (name, value) => ({ name, value, domain: COOKIE_DOMAIN, path: '/', secure: true, sameSite: 'Lax', expires: exp });
  return [
    mk(`${p}.LastAuthUser`, USERNAME),
    mk(`${p}.${USERNAME}.idToken`, ID_TOKEN),
    mk(`${p}.${USERNAME}.accessToken`, ACCESS_TOKEN),
    mk(`${p}.${USERNAME}.refreshToken`, 'sample-refresh-token'),
    mk(`${p}.${USERNAME}.clockDrift`, '0'),
    mk(`${p}.${USERNAME}.signInDetails`, encodeURIComponent(JSON.stringify({ loginId: SAMPLE_EMAIL, authFlowType: 'USER_SRP_AUTH' }))),
  ];
}

// ---------------------------------------------------------------- mock data
const TS = () => new Date().toISOString();
const DOC = (name, cat) => `s3://sample-bucket/docs/documents/${cat}/${name}`;
const Q_MAIN = '現場代理人が着工時に用意する書類は？';
const ANSWER_MAIN =
  '※機種未指定のため、一般資料・取扱機種スコープ内の候補を含みます。特定機種の事実としては断定しないでください。\n\n' +
  '## 着工時に用意する書類\n\n' +
  '### 資料から分かること\n\n' +
  '**現場代理人業務マニュアル（GM-01-05）** によると、着工前に「書類提出状況報告シート」と「元請用 管理チェックシート」を用いて以下をチェックし、職制承認を得ます：\n\n' +
  '- 請負区分（元請・下請）の確認\n- 協力会社へ提出する書類\n- 業務遂行上必要な書類\n- 安全パトロール実施予定日\n\n' +
  '**現場代理人業務マニュアル（GM-01-14）** では、現場に設置する看板・標識として：\n\n' +
  '- 工事看板・標識\n- 建設業の許可票\n- 労災保険関係成立票\n- 確認済証\n\n' +
  '### 注意・不明点\n\n' +
  '- 具体的な書類リストの詳細は「書類提出状況報告シート」の様式に記載されている\n' +
  '- 外装工事等のペンディング事項がある場合、着工後にもフォローが必要';
const SRC_MAIN = [
  ['GM-01-05-D.pdf', 0.56], ['TI-1404.pdf', 0.55], ['GM-01-18-B.pdf', 0.55], ['GM-01-10-B.pdf', 0.54],
  ['GM-01-19-B.pdf', 0.53], ['GM-01-23-B.pdf', 0.53], ['GM-01-22-C.pdf', 0.53], ['GM-01-00-_.pdf', 0.53], ['GM-01-14-B.pdf', 0.52],
].map(([n, r]) => ({
  documentName: n, sourceUri: DOC(n, n.startsWith('TI') ? 'テクニカルインフォメーション' : '現場代理人業務マニュアル'),
  category: n.startsWith('TI') ? 'TI' : '現場代理人業務マニュアル', modelType: '共通', relevance: r, pageNumber: 2,
}));
const PAGES_MAIN = [
  { documentName: 'GM-01-05-D.pdf', category: '現場代理人業務マニュアル', pageNumber: 2, relevance: 0.56, snippet: '5章（書類提出状況報告シートの運用）現場代理人業務マニュアル GM-01-05 5. 書類提出状況報告シートの運用 現場代理人業務において着工前・着工後・引渡しのタイミングで、協力会社へ提出する書類や業務遂行上…' },
  { documentName: 'TI-1404.pdf', category: 'テクニカルインフォメーション', pageNumber: 4, relevance: 0.55, snippet: '補足・着工前だけでなく、着工後確認欄にも完了確認の項目を設けておりますが、これは外装工事等のペンディング事項が本体着工前に完了しない場合があるためです。' },
  { documentName: 'GM-01-18-B.pdf', category: '現場代理人業務マニュアル', pageNumber: 5, relevance: 0.55, snippet: '2023/11/02 - B6.13 章（工程管理）現場代理人業務マニュアル GM-01-18（4）発注（監理盤工事が据付工事会社とは別会社の場合。据付工事会社の場合はＧＸ発注）施工前には見積書を入手し…' },
  { documentName: 'GM-01-10-B.pdf', category: '現場代理人業務マニュアル', pageNumber: 3, relevance: 0.54, snippet: '使用電源 定格速度 吊りロープ システム構成 GOVの運用 頂部固定作業床 工事手配 材料（頂部 作業床以外の材料・部品）一発着工 多段着工 2023/11/02 - B6.5 章（施工計画書）…' },
  { documentName: 'GM-01-14-B.pdf', category: '現場代理人業務マニュアル', pageNumber: 1, relevance: 0.52, snippet: '現場に設置する看板・標識 工事看板・標識 建設業の許可票 労災保険関係成立票 確認済証 施工体制用看板 産業廃棄物保管場所看板 工事写真用黒板' },
].map((c) => ({ ...c, sourceUri: DOC(c.documentName, c.category) }));

const CLARIFY = {
  content: '該当ページを探すために教えてください\n\n1. 機種（または工事番号）※分かれば精度が上がります\n2. 何が／どの部位ですか？（かご／ドア／巻上機／制御盤など）\n3. いつ発生しますか？（走行中／停止中／開閉時など）\n\n追記いただければ、資料の該当ページを探します。',
  responseType: 'clarify',
  clarifyQuestions: ['機種（または工事番号）※分かれば精度が上がります', '何が／どの部位ですか？（かご／ドア／巻上機／制御盤など）', 'いつ発生しますか？（走行中／停止中／開閉時など）'],
  pageCandidates: [], sourceDocuments: [], citations: [],
};
const NOT_FOUND = {
  content: '条件に合う頁が十分に見つかりませんでした。\n機種・症状・対象部位を具体化して再検索してください。\n（見当違いの回答で埋めないため、ここでは断定しません）\n資料カテゴリの絞り込みを外すと見つかることがあります。',
  responseType: 'not_found', clarifyQuestions: [],
  pageCandidates: [{ documentName: 'SUE-2-04.pdf', category: '据付基準', pageNumber: 1, relevance: 0.31, lowConfidence: true, sourceUri: DOC('SUE-2-04.pdf', '据付基準'), snippet: '指示脚長(mm) 最小脚長(mm) 最大脚長(mm) 表1 指示脚長と隅肉サイズの関係 解説 部材角部の溶け落ちを防止するために最大隅肉溶接サイズ（脚長）に注意して施工すること。' }],
  sourceDocuments: [], citations: [],
};

const SESSIONS = [
  { sessionId: 'sess-001', title: '着工時の必要書類', createdAt: TS(), lastMessageTime: TS(), messageCount: 2, daysUntilDeletion: 60 },
  { sessionId: 'sess-002', title: '溶接脚長の基準外判定', createdAt: TS(), lastMessageTime: TS(), messageCount: 2, daysUntilDeletion: 59 },
  { sessionId: 'sess-003', title: '地震感知器の取付位置', createdAt: TS(), lastMessageTime: TS(), messageCount: 4, daysUntilDeletion: 45 },
  { sessionId: 'sess-004', title: '乗場ドアの異音対処', createdAt: TS(), lastMessageTime: TS(), messageCount: 6, daysUntilDeletion: 31 },
];
const state = { sessionsVisible: false, lastQuery: Q_MAIN, lastAnswer: null, ragDelay: 0, feedback: {} };

function ragAnswerFor(query) {
  if (/異音がする/.test(query)) return { ...CLARIFY };
  if (/ブラケット取付寸法/.test(query)) return { ...NOT_FOUND };
  return { content: ANSWER_MAIN, responseType: 'pages', clarifyQuestions: [], pageCandidates: PAGES_MAIN, sourceDocuments: SRC_MAIN, citations: SRC_MAIN.map((d) => d.documentName) };
}

async function installMocks(context) {
  await context.route(/cognito-idp\.[a-z0-9-]+\.amazonaws\.com/, async (route) => {
    const req = route.request();
    const target = req.headers()['x-amz-target'] || '';
    const json = (body, status = 200) => route.fulfill({ status, contentType: 'application/x-amz-json-1.1', body: JSON.stringify(body) });
    if (target.endsWith('.GetUser')) {
      return json({ Username: USERNAME, UserAttributes: [
        { Name: 'sub', Value: SAMPLE_SUB }, { Name: 'email_verified', Value: 'true' },
        { Name: 'name', Value: SAMPLE_NAME }, { Name: 'email', Value: SAMPLE_EMAIL } ] });
    }
    if (target.endsWith('.InitiateAuth')) {
      return json({ __type: 'NotAuthorizedException', message: 'Incorrect username or password.' }, 400);
    }
    if (target.endsWith('.ForgotPassword')) {
      return json({ CodeDeliveryDetails: { AttributeName: 'email', DeliveryMedium: 'EMAIL', Destination: 's***@m***.co.jp' } });
    }
    if (target.endsWith('.ConfirmSignUp')) return json({});
    if (target.endsWith('.GlobalSignOut') || target.endsWith('.RevokeToken')) return json({});
    return json({ __type: 'MockNotImplemented', message: target }, 400);
  });

  await context.route(/execute-api\.ap-northeast-1\.amazonaws\.com|\/announcements(\?|$)/, async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const p = url.pathname;
    const m = req.method();
    const json = (body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
    if (/\/announcements$/.test(p)) return json({ announcements: [], serverTime: TS() });
    if (m === 'GET' && /\/chat\/sessions$/.test(p)) return json({ sessions: state.sessionsVisible ? SESSIONS : [] });
    if (m === 'GET' && /\/chat\/sessions\/[^/]+\/messages$/.test(p)) {
      const a = state.lastAnswer || ragAnswerFor(state.lastQuery);
      return json({ messages: [
        { messageId: 'msg-user-1', role: 'user', content: state.lastQuery, timestamp: state.userTs || TS() },
        { messageId: 'msg-ai-1', role: 'assistant', content: a.content, timestamp: state.aiTs || TS(), responseType: a.responseType,
          clarifyQuestions: a.clarifyQuestions, pageCandidates: a.pageCandidates, sourceDocuments: a.sourceDocuments, citations: a.citations,
          feedback: state.feedback.feedback || null, feedbackReason: state.feedback.reason || null, feedbackComment: state.feedback.comment || null },
      ] });
    }
    if (m === 'DELETE' && /\/chat\/sessions\/[^/]+$/.test(p)) return json({ message: 'deleted' });
    if (m === 'PUT' && /\/chat\/messages\/[^/]+\/feedback$/.test(p)) {
      const b = req.postDataJSON() || {};
      state.feedback = { feedback: b.feedback, reason: b.reason || state.feedback.reason, comment: b.comment || state.feedback.comment };
      return json({ message: 'ok' });
    }
    if (m === 'POST' && /\/chat\/suggestions$/.test(p)) return json({ messageId: 'wish-1' });
    if (m === 'POST' && /\/rag\/query$/.test(p)) {
      const b = req.postDataJSON() || {};
      state.lastQuery = b.query || Q_MAIN;
      const a = ragAnswerFor(state.lastQuery);
      state.lastAnswer = a;
      state.feedback = {};
      state.userTs = TS();
      if (state.ragDelay) await new Promise((r) => setTimeout(r, state.ragDelay));
      state.aiTs = TS();
      state.sessionsVisible = true;
      return json({ sessionId: 'sess-001', messageId: 'msg-user-1', aiMessageId: 'msg-ai-1', timestamp: state.aiTs, ...a, queryFilters: b.filters || {} });
    }
    if (m === 'GET' && /\/rag\/document$/.test(p)) {
      await new Promise((r) => setTimeout(r, 4000));
      return json({ url: 'about:blank', expiresIn: 300 });
    }
    if (m === 'OPTIONS') return route.fulfill({ status: 200, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*' } });
    return json({ message: 'mock: not found ' + p }, 404);
  });
}

// ---------------------------------------------------------------- annotation helpers
async function annotate(page, items, opts = {}) {
  // items: [{ sel, nth, n, label, pad }]  -> draws red frame + numbered badge (absolute, so fullPage works)
  const boxes = [];
  for (const it of items) {
    let box = it.box;
    if (!box) {
      const loc = page.locator(it.sel).nth(it.nth || 0);
      await loc.waitFor({ state: 'visible', timeout: 10000 });
      box = await loc.boundingBox();
    }
    if (!box) throw new Error('no box for ' + it.sel);
    boxes.push({ ...box, n: it.n, pad: it.pad ?? 4, badge: it.badge || 'tl' });
  }
  await page.evaluate(({ boxes, color }) => {
    const root = document.createElement('div');
    root.id = '__annot';
    root.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;z-index:2147483000;pointer-events:none;';
    const sx = window.scrollX, sy = window.scrollY;
    for (const b of boxes) {
      const f = document.createElement('div');
      f.style.cssText = `position:absolute;left:${b.x + sx - b.pad}px;top:${b.y + sy - b.pad}px;width:${b.width + b.pad * 2}px;height:${b.height + b.pad * 2}px;border:3px solid ${color};border-radius:6px;box-sizing:border-box;box-shadow:0 0 0 2px rgba(255,255,255,.9);`;
      root.appendChild(f);
      const badge = document.createElement('div');
      const bx = (b.badge === 'tr' || b.badge === 'br') ? b.x + sx + b.width + b.pad - 14 : b.x + sx - b.pad - 14;
      const by = (b.badge === 'bl' || b.badge === 'br') ? b.y + sy + b.height + b.pad - 14 : b.y + sy - b.pad - 14;
      badge.textContent = String(b.n);
      badge.style.cssText = `position:absolute;left:${bx}px;top:${by}px;width:28px;height:28px;border-radius:50%;background:${color};color:#fff;font:bold 16px/28px Arial,sans-serif;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.4);`;
      root.appendChild(badge);
    }
    document.body.appendChild(root);
  }, { boxes, color: opts.color || '#d62828' });
  return boxes;
}
async function clearAnnot(page) {
  await page.evaluate(() => document.getElementById('__annot')?.remove());
}
async function shot(page, name, o = {}) {
  await page.waitForTimeout(o.wait ?? 300);
  const file = path.join(OUT, name + '.png');
  await page.screenshot({ path: file, fullPage: !!o.fullPage, clip: o.clip, animations: 'disabled' });
  console.log('saved', name);
}
// clip around the union of boxes with margin (viewport coords)
function clipAround(boxes, margin, vw, vh) {
  let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
  for (const b of boxes) { x1 = Math.min(x1, b.x); y1 = Math.min(y1, b.y); x2 = Math.max(x2, b.x + b.width); y2 = Math.max(y2, b.y + b.height); }
  x1 = Math.max(0, x1 - margin); y1 = Math.max(0, y1 - margin);
  x2 = Math.min(vw, x2 + margin); y2 = Math.min(vh, y2 + margin);
  return { x: x1, y: y1, width: x2 - x1, height: y2 - y1 };
}

// ---------------------------------------------------------------- main
module.exports = { chromium, seedScript, authCookies, installMocks, BASE, state, annotate, clearAnnot, shot, clipAround, DOC, Q_MAIN };
if (require.main === module) (async () => {
  const browser = await chromium.launch({ headless: true });
  const VW = 1440, VH = 900;

  // ===== 公開ページ（実サイトそのまま） =====
  if (!process.env.SKIP_PUBLIC) {
    const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1.5, locale: 'ja-JP' });
    await installMocks(ctx); // Cognito 呼び出し(ログイン失敗・パスワードリセット・コード確認)のみ差し替え
    const page = await ctx.newPage();

    // 01 login
    await page.goto(`${BASE}/login`, { waitUntil: 'networkidle' });
    await page.fill('#email', SAMPLE_EMAIL);
    await page.fill('#password', 'Sample#2026pw');
    let boxes = await annotate(page, [
      { sel: '#email', n: 1 }, { sel: '#password', n: 2 },
      { sel: 'button[aria-label="パスワードを表示"]', n: 3, badge: 'tr' },
      { sel: 'button[type="submit"]', n: 4 },
      { sel: 'a[href="/forgot-password"]', n: 5, badge: 'bl' }, { sel: 'a[href="/signup"]', n: 6, badge: 'bl' },
    ]);
    await shot(page, '01-login');
    await shot(page, '01-login-zoom', { clip: clipAround(boxes, 40, VW, VH) });
    await clearAnnot(page);
    // 02 login error (mocked NotAuthorizedException)
    await page.click('button[type="submit"]');
    await page.waitForSelector('text=メールアドレスまたはパスワードが正しくありません', { timeout: 15000 });
    boxes = await annotate(page, [{ sel: 'text=メールアドレスまたはパスワードが正しくありません', n: 1, pad: 8 }]);
    await shot(page, '02-login-error-zoom', { clip: clipAround(boxes, 60, VW, VH) });
    await clearAnnot(page);

    // 03 signup
    await page.goto(`${BASE}/signup`, { waitUntil: 'networkidle' });
    await page.fill('#name', SAMPLE_NAME);
    await page.fill('#email', SAMPLE_EMAIL);
    await page.fill('#password', 'Sample#2026pw');
    await page.locator('#password').blur();
    boxes = await annotate(page, [
      { sel: '#name', n: 1 }, { sel: '#email', n: 2 }, { sel: '#password', n: 3 },
      { box: await (async () => { const a = await page.locator('text=強い').boundingBox(); const b = await page.locator('span:has-text("記号")').last().boundingBox(); return clipAround([{...a, x: b.x - 24, width: a.x + a.width - b.x + 24}, b], 0, VW, VH); })(), n: 4, badge: 'tr' },
      { sel: 'button[type="submit"]', n: 5 }, { sel: 'a[href="/login"]', n: 6, badge: 'bl' },
    ]);
    await shot(page, '03-signup');
    await shot(page, '03-signup-zoom', { clip: clipAround(boxes, 40, VW, VH) });
    await clearAnnot(page);
    // signup validation error example: weak password
    await page.fill('#password', 'abc');
    await page.locator('#password').blur();
    await page.waitForSelector('text=パスワードは8文字以上である必要があります');
    boxes = await annotate(page, [{ sel: 'text=パスワードは8文字以上である必要があります', n: 1, pad: 6 }]);
    await shot(page, '03-signup-error-zoom', { clip: clipAround(boxes, 60, VW, VH) });
    await clearAnnot(page);

    // 04 verify
    await page.goto(`${BASE}/verify?email=${encodeURIComponent(SAMPLE_EMAIL)}`, { waitUntil: 'networkidle' });
    const digits = page.locator('input[aria-label^="確認コード"]');
    for (let i = 0; i < 6; i++) await digits.nth(i).fill(String((i + 1)));
    boxes = await annotate(page, [
      { sel: '#email', n: 1 },
      { box: clipAround([await digits.nth(0).boundingBox(), await digits.nth(5).boundingBox()], 0, VW, VH), n: 2 },
      { sel: 'button[type="submit"]', n: 3 },
      { sel: 'button:has-text("確認コードを再送信")', n: 4, badge: 'bl' },
      { sel: 'a[href="/login"]', n: 5, badge: 'bl' },
    ]);
    await shot(page, '04-verify');
    await shot(page, '04-verify-zoom', { clip: clipAround(boxes, 40, VW, VH) });
    await clearAnnot(page);
    await page.click('button[type="submit"]');
    await page.waitForSelector('text=メールアドレスが確認されました', { timeout: 15000 });
    boxes = await annotate(page, [{ sel: 'text=メールアドレスが確認されました', n: 1, pad: 8 }]);
    await shot(page, '04-verify-done-zoom', { clip: clipAround(boxes, 60, VW, VH), wait: 100 });
    await clearAnnot(page);

    // 05 forgot password
    await page.goto(`${BASE}/forgot-password`, { waitUntil: 'networkidle' });
    await page.fill('input[type="email"]', SAMPLE_EMAIL);
    boxes = await annotate(page, [{ sel: 'input[type="email"]', n: 1 }, { sel: 'button[type="submit"]', n: 2 }]);
    await shot(page, '05-forgot-step1');
    await shot(page, '05-forgot-step1-zoom', { clip: clipAround(boxes, 40, VW, VH) });
    await clearAnnot(page);
    await page.click('button[type="submit"]');
    await page.waitForSelector('text=リセットコードと新しいパスワードを入力してください', { timeout: 15000 });
    await page.fill('input[placeholder="メールで受け取ったコード"]', '123456');
    await page.fill('input[placeholder^="8文字以上"]', 'Sample#2026pw');
    await page.fill('input[placeholder="パスワードを再入力"]', 'Sample#2026pw');
    boxes = await annotate(page, [
      { sel: 'input[placeholder="メールで受け取ったコード"]', n: 1 },
      { sel: 'input[placeholder^="8文字以上"]', n: 2 },
      { sel: 'input[placeholder="パスワードを再入力"]', n: 3 },
      { sel: 'button[type="submit"]', n: 4 },
      { sel: 'button:has-text("メールアドレスを変更する")', n: 5, badge: 'bl' },
    ]);
    await shot(page, '05-forgot-step2');
    await shot(page, '05-forgot-step2-zoom', { clip: clipAround(boxes, 40, VW, VH) });
    await clearAnnot(page);
    await ctx.close();
  }

  // ===== ログイン後ページ（トークンと API 応答をブラウザ内で差し替え） =====
  {
    const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1.5, locale: 'ja-JP' });
    await ctx.addInitScript(seedScript);
    await ctx.addCookies(authCookies());
    await installMocks(ctx);
    const page = await ctx.newPage();
    global.__page = page;
    page.on('pageerror', (e) => console.log('pageerror:', e.message));

    // 06 home
    await page.goto(`${BASE}/`, { waitUntil: 'networkidle' });
    await page.waitForSelector('text=こんにちは', { timeout: 20000 }).catch(() => {});
    await page.waitForSelector('#hero-heading', { timeout: 20000 });
    await page.waitForSelector('text=現在お知らせはありません', { timeout: 20000 });
    let boxes = await annotate(page, [
      { sel: 'input[aria-label="チャットへの質問"]', n: 1 },
      { sel: 'button:has-text("質問する")', n: 2, badge: 'tr' },
      { sel: 'text=質問例:', n: 3, badge: 'bl', pad: 6 },
      { sel: 'a[href="/chat"]', n: 4 },
      { sel: 'button:has-text("ログアウト")', n: 5, badge: 'tr' },
      { sel: '#guide-heading', n: 6, pad: 8 },
      { sel: '#announcements-heading', n: 7, pad: 8 },
    ]);
    await shot(page, '06-home', { fullPage: true });
    await clearAnnot(page);
    boxes = await annotate(page, [
      { sel: 'input[aria-label="チャットへの質問"]', n: 1 },
      { sel: 'button:has-text("質問する")', n: 2, badge: 'tr' },
      { sel: 'text=質問例:', n: 3, badge: 'bl', pad: 6 },
    ]);
    await shot(page, '06-home-hero-zoom', { clip: clipAround(boxes, 40, VW, VH) });
    await clearAnnot(page);
    // header zoom (name / logout)
    boxes = await annotate(page, [{ sel: 'button:has-text("ログアウト")', n: 5, badge: 'tr' }]);
    await shot(page, '06-home-header-zoom', { clip: { x: VW - 520, y: 0, width: 520, height: 70 } });
    await clearAnnot(page);

    // 07 chat empty
    await page.goto(`${BASE}/chat`, { waitUntil: 'networkidle' });
    await page.waitForSelector('text=何をお調べしますか？', { timeout: 20000 });
    await page.waitForSelector('text=セッションはまだありません', { timeout: 20000 });
    boxes = await annotate(page, [
      { sel: 'button:has-text("新規チャット")', n: 1 },
      { sel: 'text=セッションはまだありません', n: 2, pad: 10, badge: 'tr' },
      { sel: 'button:has-text("KE-LG の据付で注意すべきポイントは？")', n: 3 },
      { sel: 'button:has-text("絞り込み")', n: 4 },
      { sel: 'textarea', n: 5 },
      { sel: 'button:has-text("送信")', n: 6, badge: 'tr' },
      { sel: 'button:has-text("こうなってほしい")', n: 7, badge: 'tr' },
      { sel: 'a[href="/"]', n: 8, badge: 'tr' },
    ]);
    await shot(page, '07-chat-empty');
    await clearAnnot(page);

    // 08 filter panel
    await page.click('button:has-text("絞り込み")');
    await page.waitForSelector('text=取扱機種の絞り込み 6 項目のみ表示しています');
    const chipStd = page.locator('button:has-text("据付基準")').first();
    const chipAxiez = page.locator('button', { hasText: /^AXIEZ$/ }).first();
    boxes = await annotate(page, [
      { sel: 'button:has-text("絞り込み")', n: 1 },
      { box: await (async () => { const a = await page.locator('button:has-text("C資料")').boundingBox(); const b = await page.locator('button:has-text("品質管理業務マニュアル")').boundingBox(); return clipAround([a, b], 0, VW, VH); })(), n: 2 },
      { box: await (async () => { const a = await chipAxiez.boundingBox(); const b = await page.locator('button:has-text("エスカレーター")').first().boundingBox(); return clipAround([a, b], 0, VW, VH); })(), n: 3 },
    ]);
    await shot(page, '08-filter-open-zoom', { clip: { x: 230, y: VH - 300, width: VW - 230, height: 300 } });
    await clearAnnot(page);
    await chipStd.click();
    await chipAxiez.click();
    await page.waitForSelector('text=選択中:');
    boxes = await annotate(page, [
      { sel: 'button:has-text("据付基準")', n: 1 }, { box: await chipAxiez.boundingBox(), n: 2, badge: 'bl' },
      { sel: 'text=選択中:', n: 3, pad: 6, badge: 'bl' }, { sel: 'button:has-text("すべての機種に戻す")', n: 4, badge: 'tr' },
    ]);
    await shot(page, '09-filter-selected-zoom', { clip: { x: 230, y: VH - 330, width: VW - 230, height: 330 } });
    await clearAnnot(page);
    await page.click('button:has-text("絞り込み")'); // collapse -> pills
    await page.waitForSelector('button:has-text("すべてクリア")');
    boxes = await annotate(page, [
      { sel: 'button:has-text("絞り込み")', n: 1 },
      { sel: 'button[title="クリックで解除"]', nth: 0, n: 2 }, { sel: 'button[title="クリックで解除"]', nth: 1, n: 3 },
      { sel: 'button:has-text("すべてクリア")', n: 4 },
    ]);
    await shot(page, '10-filter-pills-zoom', { clip: { x: 230, y: VH - 130, width: 900, height: 130 } });
    await clearAnnot(page);
    await page.click('button:has-text("すべてクリア")');

    // 11 send question -> typing indicator
    state.ragDelay = 2500;
    await page.fill('textarea', Q_MAIN);
    boxes = await annotate(page, [{ sel: 'textarea', n: 1 }, { sel: 'button:has-text("送信")', n: 2, badge: 'tr' }]);
    await shot(page, '11-chat-typed-zoom', { clip: { x: 230, y: VH - 110, width: VW - 230, height: 110 } });
    await clearAnnot(page);
    await page.click('button:has-text("送信")');
    await page.waitForSelector('text=考え中...', { timeout: 10000 });
    await shot(page, '12-chat-thinking', { wait: 200 });
    state.ragDelay = 0;
    // wait for typewriter + citations
    await page.waitForSelector('text=参考資料', { timeout: 90000 });
    await page.waitForSelector('text=セッションはまだありません', { state: 'detached', timeout: 20000 });
    await page.waitForTimeout(800);
    // 履歴を開き直して本文を全文表示させる（モック即応答によるタイプライター競合の回避）
    await page.locator('p.font-medium', { hasText: '着工時の必要書類' }).first().click();
    await page.waitForSelector('div.chat-markdown h2:has-text("着工時に用意する書類")', { timeout: 20000 });
    await page.waitForTimeout(500);

    // 13 answer (tall viewport so the whole bubble is visible)
    await page.setViewportSize({ width: VW, height: 1500 });
    await page.waitForTimeout(500);
    const scrollMsgsBottom = async () => {
      await page.evaluate(() => { const c = document.querySelector('div[style*="calc(100vh"]'); if (c) c.scrollTop = c.scrollHeight; });
      await page.waitForTimeout(500);
    };
    const bubbleBox = async () => page.locator('text=EleKnowledge AI').last().locator('xpath=ancestor::div[contains(@class,"rounded-2xl")]').boundingBox();
    const unionBox = (arr) => clipAround(arr, 0, 100000, 100000);
    await page.locator('text=該当頁候補').scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    const barBox = async () => unionBox([
      await page.locator('button[aria-label="回答をコピー"]').boundingBox(),
      await page.locator('button[aria-label="解けなかった"]').boundingBox(),
    ]);
    boxes = await annotate(page, [
      { sel: 'text=該当頁候補', n: 1, pad: 6 },
      { sel: 'div.chat-markdown p:has-text("機種未指定のため")', n: 2, pad: 4 },
      { sel: 'p:has-text("参考資料")', n: 3, pad: 4 },
      { sel: 'button:has-text("件表示")', n: 4, badge: 'bl' },
      { box: await barBox(), n: 5, badge: 'bl', pad: 6 },
    ]);
    await shot(page, '13-chat-answer');
    await clearAnnot(page);
    // page candidates zoom
    boxes = await annotate(page, [{ sel: 'text=該当頁候補', n: 1, pad: 6 }, { sel: 'a:has-text("GM-01-05-D.pdf")', nth: 0, n: 2 }]);
    const cand = await page.locator('div:has(> p:has-text("該当頁候補"))').first().boundingBox();
    await shot(page, '13-candidates-zoom', { clip: clipAround([cand], 20, VW, 1500) });
    await clearAnnot(page);
    // feedback bar zoom
    {
      const bb = await bubbleBox(); const bar = await barBox();
      boxes = await annotate(page, [
        { sel: 'button[aria-label="回答をコピー"]', n: 1, badge: 'bl' },
        { sel: 'button[aria-label="疑問が解けた"]', n: 2 },
        { sel: 'button[aria-label="解けなかった"]', n: 3, badge: 'tr' },
      ]);
      await shot(page, '13-feedback-bar-zoom', { clip: { x: bb.x, y: bar.y - 40, width: bb.width, height: bar.height + 80 } });
      await clearAnnot(page);
    }
    // citations zoom (expanded)
    await page.click('button:has-text("件表示")');
    await page.waitForSelector('button:has-text("折りたたむ")');
    await scrollMsgsBottom();
    {
      const bb = await bubbleBox();
      const top = await page.locator('p:has-text("参考資料")').first().boundingBox();
      const bar = await barBox();
      boxes = await annotate(page, [
        { sel: 'p:has-text("参考資料")', n: 1, pad: 4 },
        { sel: 'a:has-text("GM-01-05-D.pdf")', nth: 1, n: 2 },
        { sel: 'button:has-text("折りたたむ")', n: 3, badge: 'bl' },
      ]);
      await shot(page, '14-citations-zoom', { clip: { x: bb.x, y: top.y - 30, width: bb.width, height: bar.y - top.y + 20 } });
      await clearAnnot(page);
    }
    await page.click('button:has-text("折りたたむ")');

    // 15 feedback bad -> panel
    await page.click('button[aria-label="解けなかった"]');
    await page.waitForSelector('text=詳しく教えてください（任意）');
    await page.waitForTimeout(1200);
    await scrollMsgsBottom();
    {
      const bb = await bubbleBox(); const bar = await barBox();
      const panelOuter = await page.locator('div.rounded-lg.border-red-100').first().boundingBox();
      boxes = await annotate(page, [
        { sel: 'button[aria-label="解けなかった"]', n: 1 },
        { sel: 'button:has-text("資料が違う")', n: 2 },
        { sel: 'textarea[id^="feedback-comment-"]', n: 3 },
        { sel: 'button:has-text("補足を送る")', n: 4, badge: 'tr' },
        { sel: 'button:has-text("閉じる")', nth: 0, n: 5, badge: 'tr' },
      ]);
      await shot(page, '15-feedback-bad-zoom', { clip: { x: bb.x, y: bar.y - 30, width: bb.width, height: panelOuter.y + panelOuter.height - bar.y + 50 } });
      await clearAnnot(page);
    }
    await page.click('button:has-text("資料が違う")');
    await page.waitForSelector('text=理由を記録しました');
    await page.fill('textarea[id^="feedback-comment-"]', '別の機種の資料が出てきた');
    await page.click('button:has-text("補足を送る")');
    await page.waitForSelector('text=補足を記録しました');
    await page.waitForSelector('text=補足: 別の機種の資料が出てきた');
    await scrollMsgsBottom();
    {
      const bb = await bubbleBox(); const bar = await barBox();
      const note = await page.locator('text=補足: 別の機種の資料が出てきた').boundingBox();
      boxes = await annotate(page, [{ sel: 'span:has-text("資料が違う")', n: 1, pad: 4 }, { sel: 'text=補足: 別の機種の資料が出てきた', n: 2, pad: 4, badge: 'bl' }, { sel: 'button:has-text("理由・補足を編集")', n: 3, badge: 'tr' }]);
      await shot(page, '16-feedback-bad-done-zoom', { clip: { x: bb.x, y: bar.y - 30, width: bb.width, height: note.y + note.height - bar.y + 50 } });
      await clearAnnot(page);
    }
    // 17 good
    await page.click('button[aria-label="疑問が解けた"]');
    await page.waitForSelector('span:has-text("記録しました")');
    await page.waitForTimeout(300);
    {
      const bb = await bubbleBox(); const bar = await barBox();
      boxes = await annotate(page, [{ sel: 'button[aria-label="疑問が解けた"]', n: 1 }, { sel: 'span:has-text("記録しました")', n: 2, pad: 4, badge: 'tr' }]);
      await shot(page, '17-feedback-good-zoom', { clip: { x: bb.x, y: bar.y - 40, width: bb.width, height: bar.height + 80 } });
      await clearAnnot(page);
    }

    // 18 sessions sidebar (hover -> delete x)
    await page.setViewportSize({ width: VW, height: VH });
    await page.waitForTimeout(400);
    const firstSession = page.locator('p.font-medium', { hasText: '着工時の必要書類' }).first();
    await firstSession.hover();
    await page.waitForTimeout(300);
    boxes = await annotate(page, [
      { sel: 'button:has-text("新規チャット")', n: 1 },
      { box: await firstSession.locator('xpath=ancestor::div[contains(@class,"cursor-pointer")]').boundingBox(), n: 2, badge: 'br' },
      { sel: 'button[aria-label="セッションを削除"]', nth: 0, n: 3, badge: 'tr' },
      { sel: 'text=残り 60 日', n: 4, pad: 3, badge: 'tr' },
    ]);
    await shot(page, '18-sessions-zoom', { clip: { x: 0, y: 60, width: 330, height: 420 } });
    await clearAnnot(page);
    await page.mouse.move(700, 400);

    // 19 wish modal
    await page.click('button:has-text("こうなってほしい")');
    await page.waitForSelector('#product-wish-title');
    await page.fill('div[role="dialog"] textarea', '候補資料をもっと上に出してほしい');
    boxes = await annotate(page, [
      { sel: 'div[role="dialog"] textarea', n: 1 },
      { sel: 'div[role="dialog"] button:has-text("送信")', n: 2, badge: 'tr' },
      { sel: 'div[role="dialog"] button:has-text("閉じる")', n: 3, badge: 'bl' },
    ]);
    const dlg = await page.locator('div[role="dialog"] > div.relative').boundingBox();
    await shot(page, '19-wish-zoom', { clip: clipAround([dlg], 24, VW, VH) });
    await clearAnnot(page);
    await page.keyboard.press('Escape');

    // 20 clarify
    await page.click('button:has-text("新規チャット")');
    await page.waitForSelector('text=何をお調べしますか？');
    await page.fill('textarea', '異音がする');
    await page.keyboard.press('Enter');
    await page.waitForSelector('text=追加で教えてください', { timeout: 30000 });
    await page.waitForTimeout(800);
    const clar = await page.locator('div:has(> p:has-text("追加で教えてください"))').first().boundingBox();
    const clarBubble = await page.locator('text=EleKnowledge AI').last().locator('xpath=ancestor::div[contains(@class,"rounded-2xl")]').boundingBox();
    boxes = await annotate(page, [
      { sel: 'text=追加で教えてください', n: 1, pad: 4 },
      { sel: 'button:has-text("機種（または工事番号）")', n: 2, badge: 'tr' },
    ]);
    await shot(page, '20-clarify-zoom', { clip: clipAround([clarBubble], 20, VW, VH) });
    await clearAnnot(page);

    // 21 not found (with category filter)
    await page.click('button:has-text("新規チャット")');
    await page.waitForSelector('text=何をお調べしますか？');
    await page.click('button:has-text("絞り込み")');
    await page.locator('button:has-text("据付基準")').first().click();
    await page.click('button:has-text("絞り込み")');
    await page.fill('textarea', 'ブラケット取付寸法は？');
    await page.keyboard.press('Enter');
    await page.waitForSelector('text=検索が弱いため断定回答はしていません', { timeout: 30000 });
    await page.waitForTimeout(800);
    const nfBubble = await page.locator('text=EleKnowledge AI').last().locator('xpath=ancestor::div[contains(@class,"rounded-2xl")]').boundingBox();
    boxes = await annotate(page, [
      { sel: 'text=参考候補（低信頼）', n: 1, pad: 4 },
      { sel: 'text=検索が弱いため断定回答はしていません', n: 2, pad: 4 },
      { sel: 'button:has-text("資料カテゴリの絞り込みを外す")', n: 3, badge: 'bl' },
    ]);
    await shot(page, '21-notfound-zoom', { clip: clipAround([nfBubble], 20, VW, VH) });
    await clearAnnot(page);

    // 22 doc relay page
    await page.goto(`${BASE}/doc?uri=${encodeURIComponent(DOC('GM-01-05-D.pdf', '現場代理人業務マニュアル'))}#page=2`, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('text=文書を開いています', { timeout: 15000 });
    await shot(page, '22-doc-opening-zoom', { clip: { x: VW / 2 - 300, y: VH / 2 - 160, width: 600, height: 320 }, wait: 200 });

    await ctx.close();
  }
  await browser.close();
  console.log('ALL DONE');
})().catch(async (e) => { console.error('FAILED:', e); try { await global.__page.screenshot({ path: path.join(OUT, 'zz-failure.png') }); } catch {} process.exit(1); });
