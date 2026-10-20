import { KnowledgeResearchError } from './knowledge-research.mjs';
import { SENPAI_MODEL_TYPES } from './knowledge-senpai-chat.mjs';

// SYNC: must equal REACTIONS / REVIEW_STATES in lambda/rag/senpai-field-report/field_report_vocab.py
// and the queue generator (tests/unit/test_senpai_field_report_sync.py).
export const FIELD_REPORT_REACTIONS = Object.freeze(new Set(['matched', 'not_matched', 'unsure']));
export const FIELD_REPORT_REVIEW_STATES = Object.freeze(new Set(['unconfirmed', 'awaiting_review', 'reflected', 'held_or_rejected']));

export const FIELD_REPORT_REACTION_LABELS = Object.freeze({
  matched: 'この条件で当てはまった',
  not_matched: '当てはまらなかった',
  unsure: '分からない',
});
export const FIELD_REPORT_REVIEW_STATE_LABELS = Object.freeze({
  unconfirmed: '未確認',
  awaiting_review: '確認待ち',
  reflected: '反映済み',
  held_or_rejected: '保留・不採用',
});
export const FIELD_REPORT_FINDING_MAX = 500;
export const FIELD_REPORT_CONDITION_MAX = 300;

const DEFAULT_TIMEOUT_MS = 15_000;
const MAX_TIMEOUT_MS = 30_000;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/u;
const CONTROL = /[\u0000-\u0008\u000b-\u001f\u007f]/gu;
const MESSAGE_TIMEOUT = '結果の送信が時間内に完了しませんでした。時間をおいてお試しください';
const MESSAGE_CANCELLED = '結果の送信を中止しました';

function fail(code, message) {
  throw new KnowledgeResearchError(code, message);
}

function cleanText(value) {
  return typeof value === 'string' ? value.replace(/\r\n?/gu, '\n').replace(CONTROL, '').trim() : '';
}

/**
 * Knowhow cards shown with this turn's technical answer (the only cards a reaction may name).
 * @param {import('./knowledge-senpai-chat.mjs').SenpaiChatTurn} turn
 */
export function fieldReportCards(turn) {
  const matches = turn?.normal?.status === 'success' ? turn.normal.answer?.knowhow?.matches : undefined;
  const seen = new Set();
  const cards = [];
  for (const match of Array.isArray(matches) ? matches : []) {
    if (typeof match?.knowledgeId !== 'string' || !Number.isSafeInteger(match.cardVersion) || seen.has(match.knowledgeId)) continue;
    seen.add(match.knowledgeId);
    cards.push({ knowledgeId: match.knowledgeId, cardVersion: match.cardVersion, title: typeof match.title === 'string' ? match.title : match.knowledgeId });
  }
  return cards;
}

/** Empty inputs; only the model chosen for the turn is pre-filled. The conversation is never copied. */
export function createFieldReportDraft(turn) {
  return { finding: '', condition: '', modelType: SENPAI_MODEL_TYPES.has(turn?.modelType) ? turn.modelType : '', reactions: {} };
}

/** @returns {string[]} Japanese messages; empty when the draft can be confirmed. */
export function validateFieldReportDraft(draft) {
  const finding = cleanText(draft?.finding);
  if (!finding) return ['「何が分かったか」を入力してください'];
  if (finding.length > FIELD_REPORT_FINDING_MAX) return [`「何が分かったか」は${FIELD_REPORT_FINDING_MAX}文字以内で入力してください`];
  if (cleanText(draft?.condition).length > FIELD_REPORT_CONDITION_MAX) return [`「どの条件か」は${FIELD_REPORT_CONDITION_MAX}文字以内で入力してください`];
  if (draft?.modelType && !SENPAI_MODEL_TYPES.has(draft.modelType)) return ['機種を一覧から選んでください'];
  const reactions = Object.values(draft?.reactions || {}).filter(Boolean);
  if (reactions.some((reaction) => !FIELD_REPORT_REACTIONS.has(reaction))) return ['ノウハウへの反応を選び直してください'];
  return [];
}

/**
 * Build the request body from the user-confirmed draft. Cards without a chosen reaction are not sent.
 * @param {{conversationId:string, turn:import('./knowledge-senpai-chat.mjs').SenpaiChatTurn, draft:{finding:string, condition:string, modelType:string, reactions:Record<string,string>}}} options
 */
export function buildFieldReportPayload({ conversationId, turn, draft }) {
  if (typeof conversationId !== 'string' || !UUID.test(conversationId)
    || typeof turn?.senpaiTurnId !== 'string' || !UUID.test(turn.senpaiTurnId)) {
    fail('validation', '相談の識別情報を確認してください');
  }
  const errors = validateFieldReportDraft(draft);
  if (errors.length > 0) fail('validation', errors[0]);
  const condition = cleanText(draft.condition);
  const cardReactions = fieldReportCards(turn)
    .filter((card) => FIELD_REPORT_REACTIONS.has(draft.reactions?.[card.knowledgeId]))
    .map((card) => ({ knowledgeId: card.knowledgeId, cardVersion: card.cardVersion, reaction: draft.reactions[card.knowledgeId] }));
  return {
    senpaiConversationId: conversationId,
    senpaiTurnId: turn.senpaiTurnId,
    finding: cleanText(draft.finding),
    ...(condition ? { condition } : {}),
    ...(draft.modelType ? { modelType: draft.modelType } : {}),
    cardReactions,
    confirmed: true,
  };
}

function endpoint(baseUrl) {
  if (typeof baseUrl !== 'string' || !baseUrl.trim()) fail('config', 'RAG APIの接続先が設定されていません');
  let url;
  try { url = new URL(baseUrl); } catch { fail('config', 'RAG APIの接続先を確認してください'); }
  const loopback = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname.toLowerCase());
  const localHttp = loopback && ['development', 'test'].includes(process.env.NODE_ENV);
  if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && localHttp))
    || url.username || url.password || url.search || url.hash) {
    fail('config', 'RAG APIの接続先はHTTPSまたはローカル開発用HTTPで設定してください');
  }
  return `${url.origin}${url.pathname.replace(/\/+$/u, '')}/rag/senpai/field-reports`;
}

function statusError(status) {
  if (status === 400) fail('validation', '入力内容を確認してください。この相談で表示されたノウハウだけを選べます');
  if (status === 401) fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
  if (status === 403) fail('unavailable', '結果の記録は現在利用できません');
  if (status === 404) fail('unavailable', '対象の相談を確認できません。保存期間を過ぎた可能性があります');
  if (status === 409) fail('unavailable', 'この相談の結果を保存できませんでした');
  fail('server', '結果の送信でエラーが発生しました。時間をおいてお試しください');
}

function normalizeReport(data) {
  if (!data || typeof data !== 'object' || typeof data.reportId !== 'string'
    || typeof data.senpaiConversationId !== 'string' || typeof data.senpaiTurnId !== 'string'
    || typeof data.finding !== 'string' || typeof data.createdAt !== 'string'
    || !FIELD_REPORT_REVIEW_STATES.has(data.reviewState) || !Array.isArray(data.cardReactions)) return null;
  const cardReactions = data.cardReactions.filter((r) => r && typeof r.knowledgeId === 'string'
    && Number.isSafeInteger(r.cardVersion) && FIELD_REPORT_REACTIONS.has(r.reaction))
    .map((r) => ({ knowledgeId: r.knowledgeId, cardVersion: r.cardVersion, reaction: r.reaction }));
  return {
    reportId: data.reportId,
    senpaiConversationId: data.senpaiConversationId,
    senpaiTurnId: data.senpaiTurnId,
    createdAt: data.createdAt,
    finding: data.finding,
    ...(typeof data.condition === 'string' ? { condition: data.condition } : {}),
    ...(SENPAI_MODEL_TYPES.has(data.modelType) ? { modelType: data.modelType } : {}),
    reviewState: data.reviewState,
    cardReactions,
  };
}

async function request({ url, init, getToken, fetchImpl, signal, timeoutMs }) {
  if (typeof getToken !== 'function' || typeof fetchImpl !== 'function') fail('config', '認証または通信の設定を確認してください');
  if (signal?.aborted) fail('cancelled', MESSAGE_CANCELLED);
  const bounded = Number.isFinite(timeoutMs) && timeoutMs >= 1 ? Math.min(timeoutMs, MAX_TIMEOUT_MS) : DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  let reason;
  let onAbort;
  let timeoutId;
  const interruption = new Promise((_resolve, reject) => {
    onAbort = () => { reason = 'cancelled'; controller.abort(); reject(new KnowledgeResearchError('cancelled', MESSAGE_CANCELLED)); };
    signal?.addEventListener('abort', onAbort, { once: true });
    timeoutId = setTimeout(() => { reason = 'timeout'; controller.abort(); reject(new KnowledgeResearchError('timeout', MESSAGE_TIMEOUT)); }, bounded);
  });
  const operation = (async () => {
    let token;
    try { token = await getToken(); } catch { fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください'); }
    if (typeof token !== 'string' || !token.trim()) fail('auth', 'ログインが必要です。ログイン後にもう一度お試しください');
    let response;
    try {
      response = await fetchImpl(url, { ...init, headers: { ...init.headers, Authorization: `Bearer ${token}` }, signal: controller.signal });
    } catch {
      if (reason) return undefined; // the interruption promise reports it
      fail('server', '結果のサービスに接続できませんでした。時間をおいてお試しください');
    }
    if (!response || typeof response.ok !== 'boolean') fail('invalid_response', '応答を確認できませんでした');
    if (!response.ok) statusError(response.status);
    try { return await response.json(); } catch { fail('invalid_response', '応答の形式を確認できませんでした'); }
  })();
  try {
    return await Promise.race([operation, interruption]);
  } finally {
    clearTimeout(timeoutId);
    signal?.removeEventListener('abort', onAbort);
  }
}

/**
 * Send one user-confirmed field report (dev admin only). Returns the saved candidate.
 * @param {{baseUrl:string, getToken:()=>Promise<string|null|undefined>, payload:ReturnType<typeof buildFieldReportPayload>, fetchImpl?:typeof fetch, signal?:AbortSignal, timeoutMs?:number}} options
 */
export async function submitFieldReport({ baseUrl, getToken, payload, fetchImpl = fetch, signal, timeoutMs }) {
  const url = endpoint(baseUrl);
  const data = await request({
    url, init: { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) },
    getToken, fetchImpl, signal, timeoutMs,
  });
  const report = normalizeReport(data);
  if (!report || report.senpaiTurnId !== payload.senpaiTurnId) fail('invalid_response', '保存結果の形式を確認できませんでした');
  return report;
}

/**
 * Read the caller's reports of one conversation, keyed by senpaiTurnId.
 * @param {{baseUrl:string, getToken:()=>Promise<string|null|undefined>, conversationId:string, fetchImpl?:typeof fetch, signal?:AbortSignal, timeoutMs?:number}} options
 */
export async function listFieldReports({ baseUrl, getToken, conversationId, fetchImpl = fetch, signal, timeoutMs }) {
  if (typeof conversationId !== 'string' || !UUID.test(conversationId)) fail('validation', '相談の識別情報を確認してください');
  const url = `${endpoint(baseUrl)}?senpaiConversationId=${encodeURIComponent(conversationId)}`;
  const data = await request({ url, init: { method: 'GET', headers: {} }, getToken, fetchImpl, signal, timeoutMs });
  const byTurn = {};
  for (const entry of Array.isArray(data?.reports) ? data.reports : []) {
    const report = normalizeReport(entry);
    if (report && report.senpaiConversationId === conversationId) byTurn[report.senpaiTurnId] = report;
  }
  return byTurn;
}
