import { KnowledgeResearchError, normalizeStoredResearchAnswer } from './knowledge-research.mjs';
import { normalizeSavedModelType } from './knowledge-senpai-chat.mjs';

const DEFAULT_TIMEOUT_MS = 30_000;
const MAX_TIMEOUT_MS = 120_000;
const MAX_SESSIONS = 200;
const MAX_MESSAGES = 1_000;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu;
const MODES = ['normal', 'law'];
const SYNTHESIS_MODE = 'senpai_synthesis';
const MAX_SYNTHESIS_LENGTH = 32_000;

function fail(code, message) {
  throw new KnowledgeResearchError(code, message);
}

function endpoint(baseUrl) {
  if (typeof baseUrl !== 'string' || !baseUrl.trim()) fail('config', '相談履歴サービスの接続先が設定されていません');
  let url;
  try { url = new URL(baseUrl); } catch { fail('config', '相談履歴サービスの接続先を確認してください'); }
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname.toLowerCase());
  const localHttp = local && ['development', 'test'].includes(process.env.NODE_ENV);
  if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && localHttp))
    || url.username || url.password || url.search || url.hash) {
    fail('config', '相談履歴サービスの接続先はHTTPSまたはローカル開発用HTTPで設定してください');
  }
  return `${url.origin}${url.pathname.replace(/\/+$/, '')}`;
}

function validIso(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/u.test(value)
    || !Number.isFinite(Date.parse(value))) return false;
  return true;
}

function validateSession(item) {
  return item && typeof item === 'object' && UUID.test(item.conversationId)
    && typeof item.title === 'string' && item.title.trim() && item.title.length <= 2_000
    && validIso(item.createdAt) && validIso(item.lastMessageTime)
    && Number.isSafeInteger(item.messageCount) && item.messageCount > 0 && item.messageCount <= MAX_MESSAGES
    && Number.isSafeInteger(item.daysUntilDeletion) && item.daysUntilDeletion >= 0 && item.daysUntilDeletion <= 60;
}

function validateMessage(row, conversationId) {
  if (!row || typeof row !== 'object' || row.senpaiConversationId !== conversationId
    || !UUID.test(row.senpaiTurnId) || !['user', 'assistant'].includes(row.role)
    || !MODES.includes(row.ragMode) || typeof row.sessionId !== 'string' || !row.sessionId.trim() || row.sessionId.length > 128
    || typeof row.messageId !== 'string' || !row.messageId.trim() || row.messageId.length > 128
    || typeof row.userId !== 'string' || !row.userId.trim() || row.userId.length > 256
    || typeof row.content !== 'string' || row.content.length > 32_000 || !validIso(row.timestamp)
    || !Number.isSafeInteger(row.ttl) || row.ttl < 0) {
    fail('invalid_response', '相談履歴の発言を安全に読み込めませんでした');
  }
}

function validateSynthesisRow(row, conversationId) {
  if (!row || typeof row !== 'object' || row.senpaiConversationId !== conversationId
    || !UUID.test(row.senpaiTurnId) || row.role !== 'assistant'
    || row.messageId !== `senpai-synthesis-${row.senpaiTurnId}`
    || typeof row.userId !== 'string' || !row.userId.trim() || row.userId.length > 256
    || typeof row.content !== 'string' || !row.content.trim() || row.content.length > MAX_SYNTHESIS_LENGTH
    || !validIso(row.timestamp)) {
    fail('invalid_response', '相談履歴のまとめを安全に読み込めませんでした');
  }
}

function savedSynthesis(row) {
  const inputs = row.synthesisInputs;
  const validInputs = inputs && typeof inputs.normal === 'boolean' && typeof inputs.law === 'boolean'
    && Number.isSafeInteger(inputs.knowhowCount) && inputs.knowhowCount >= 0;
  return {
    status: 'success', content: row.content, messageId: row.messageId,
    ...(validInputs ? { inputs: { normal: inputs.normal, law: inputs.law, knowhowCount: inputs.knowhowCount } } : {}),
  };
}

async function requestJson({ baseUrl, getToken, fetchImpl, signal, timeoutMs, path }) {
  const base = endpoint(baseUrl);
  if (typeof getToken !== 'function' || typeof fetchImpl !== 'function') fail('config', '履歴サービスの設定を確認してください');
  const boundedTimeout = Number.isFinite(timeoutMs) ? Math.min(Math.max(timeoutMs, 1), MAX_TIMEOUT_MS) : DEFAULT_TIMEOUT_MS;
  if (signal?.aborted) fail('cancelled', '相談履歴の読込を中止しました');
  const controller = new AbortController();
  let interruptionCode;
  let rejectInterruption;
  const interruption = new Promise((_resolve, reject) => { rejectInterruption = reject; });
  const abort = () => {
    interruptionCode = 'cancelled';
    controller.abort();
    rejectInterruption(new KnowledgeResearchError('cancelled', '相談履歴の読込を中止しました'));
  };
  signal?.addEventListener('abort', abort, { once: true });
  const timeout = setTimeout(() => {
    interruptionCode = 'timeout';
    controller.abort();
    rejectInterruption(new KnowledgeResearchError('timeout', '相談履歴の読込が時間内に完了しませんでした'));
  }, boundedTimeout);
  try {
    const operation = (async () => {
      let token;
      try { token = await getToken(); } catch { fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください'); }
      if (typeof token !== 'string' || !token.trim()) fail('auth', 'ログインが必要です。ログイン後にもう一度お試しください');
      if (controller.signal.aborted) {
        throw new KnowledgeResearchError(interruptionCode || 'cancelled', interruptionCode === 'timeout'
          ? '相談履歴の読込が時間内に完了しませんでした' : '相談履歴の読込を中止しました');
      }
      let response;
      try {
        response = await fetchImpl(`${base}${path}`, {
          method: 'GET', headers: { Authorization: `Bearer ${token}` }, signal: controller.signal,
        });
      } catch {
        if (controller.signal.aborted) throw new KnowledgeResearchError(interruptionCode || 'cancelled', interruptionCode === 'timeout' ? '相談履歴の読込が時間内に完了しませんでした' : '相談履歴の読込を中止しました');
        fail('server', '相談履歴を読み込めませんでした。時間をおいて再度お試しください');
      }
      if (!response || typeof response.ok !== 'boolean') fail('invalid_response', '相談履歴の応答を確認できませんでした');
      if (!response.ok) {
        if (response.status === 401) fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
        if (response.status === 403) fail('unavailable', '相談履歴を現在利用できません');
        if (response.status >= 500) fail('server', '相談履歴でエラーが発生しました。時間をおいてお試しください');
        fail('unavailable', '相談履歴を現在利用できません');
      }
      try { return await response.json(); } catch { fail('invalid_response', '相談履歴の形式を確認できませんでした'); }
    })();
    return await Promise.race([operation, interruption]);
  } finally {
    clearTimeout(timeout);
    signal?.removeEventListener('abort', abort);
  }
}

/** Fetch the bounded list of Senpai conversations for the authenticated administrator. */
export async function getSenpaiConversations({ baseUrl, getToken, fetchImpl = fetch, signal, timeoutMs = DEFAULT_TIMEOUT_MS }) {
  const data = await requestJson({ baseUrl, getToken, fetchImpl, signal, timeoutMs, path: '/chat/sessions?context=senpai' });
  if (!data || data.context !== 'senpai' || typeof data.complete !== 'boolean'
    || !Array.isArray(data.sessions) || data.sessions.length > MAX_SESSIONS
    || !data.sessions.every(validateSession)
    || new Set(data.sessions.map((item) => item.conversationId)).size !== data.sessions.length) {
    fail('invalid_response', '相談履歴の一覧を安全に読み込めませんでした');
  }
  return { sessions: data.sessions.map((item) => ({ ...item })), complete: data.complete };
}

/** Fetch and pair stored user/assistant records by Senpai turn UUID. */
export async function readSenpaiConversation({ baseUrl, getToken, fetchImpl = fetch, signal, timeoutMs = DEFAULT_TIMEOUT_MS, conversationId }) {
  if (typeof conversationId !== 'string' || !UUID.test(conversationId)) fail('validation', '相談履歴の識別情報を確認してください');
  const data = await requestJson({
    baseUrl, getToken, fetchImpl, signal, timeoutMs,
    path: `/chat/sessions/${conversationId}/messages?context=senpai`,
  });
  if (!data || data.context !== 'senpai' || data.conversationId !== conversationId
    || typeof data.complete !== 'boolean' || data.readOnly !== false
    || !Array.isArray(data.messages) || data.messages.length > MAX_MESSAGES) {
    fail('invalid_response', '相談履歴の詳細を安全に読み込めませんでした');
  }
  data.messages.forEach((row) => (row?.ragMode === SYNTHESIS_MODE
    ? validateSynthesisRow(row, conversationId) : validateMessage(row, conversationId)));
  if (new Set(data.messages.map((row) => row.userId)).size > 1) {
    fail('invalid_response', '相談履歴に複数の利用者の発言が含まれています');
  }

  const groups = new Map();
  const messageIds = new Set();
  for (const row of data.messages) {
    if (messageIds.has(row.messageId)) fail('invalid_response', '相談履歴に重複した発言があります');
    messageIds.add(row.messageId);
    if (row.ragMode === SYNTHESIS_MODE) {
      const owner = groups.get(row.senpaiTurnId) || { senpaiTurnId: row.senpaiTurnId, byMode: { normal: {}, law: {} }, firstTime: row.timestamp };
      if (owner.synthesis) fail('invalid_response', '相談履歴のまとめが重複しています');
      owner.synthesis = row;
      groups.set(row.senpaiTurnId, owner);
      continue;
    }
    const group = groups.get(row.senpaiTurnId) || { senpaiTurnId: row.senpaiTurnId, byMode: { normal: {}, law: {} }, firstTime: row.timestamp };
    if (row.timestamp < group.firstTime) group.firstTime = row.timestamp;
    const lane = group.byMode[row.ragMode];
    if (lane[row.role]) fail('invalid_response', '相談履歴の発言が重複しています');
    lane[row.role] = row;
    groups.set(row.senpaiTurnId, group);
  }
  const ordered = [...groups.values()].sort((a, b) => a.firstTime.localeCompare(b.firstTime));
  const seenQueries = new Set();
  let complete = data.complete;
  const turns = ordered.map((group, index) => {
    const userRows = MODES.map((mode) => group.byMode[mode].user).filter(Boolean);
    if (userRows.length === 0 || new Set(userRows.map((row) => row.content)).size !== 1) {
      fail('invalid_response', '相談履歴の質問が一致しないため、表示できません');
    }
    const query = userRows[0].content.trim();
    if (!query || Array.from(query).length > 2_000 || seenQueries.has(`${group.senpaiTurnId}\0${query}`)) {
      fail('invalid_response', '相談履歴の質問を確認できませんでした');
    }
    seenQueries.add(`${group.senpaiTurnId}\0${query}`);
    // The model filter is only ever sent with (and saved on) the technical lane.
    const modelType = normalizeSavedModelType(group.byMode.normal.assistant?.modelType);
    const turn = {
      id: index + 1, senpaiTurnId: group.senpaiTurnId, ...(modelType ? { modelType } : {}), query,
      ...(group.synthesis ? { synthesis: savedSynthesis(group.synthesis) } : {}),
    };
    for (const mode of MODES) {
      const user = group.byMode[mode].user;
      const assistant = group.byMode[mode].assistant;
      if (assistant && !user) fail('invalid_response', '相談履歴の回答に対応する質問がありません');
      if (assistant && user.sessionId !== assistant.sessionId) fail('invalid_response', '相談履歴の質問と回答の検索先が一致しません');
      if (assistant) {
        const answer = normalizeStoredResearchAnswer({ record: assistant, mode, query, conversationId, turnId: group.senpaiTurnId });
        turn[mode] = { status: 'success', answer };
      } else {
        const message = 'この検索先の回答は保存されていません。続きの質問は休止しています';
        turn[mode] = { status: 'paused', message };
      }
    }
    return turn;
  });
  return { conversationId, turns, complete };
}
