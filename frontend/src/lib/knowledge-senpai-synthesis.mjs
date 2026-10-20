import { KnowledgeResearchError } from './knowledge-research.mjs';

const DEFAULT_TIMEOUT_MS = 35_000;
const MAX_TIMEOUT_MS = 60_000;
const MAX_CONTENT_LENGTH = 32_000;
const MAX_KNOWHOW_COUNT = 100;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu;
const ISO = /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/u;

const MESSAGE_TIMEOUT = 'まとめの作成が時間内に完了しませんでした。時間をおいてお試しください';
const MESSAGE_CANCELLED = 'まとめの作成を中止しました';

function fail(code, message) {
  throw new KnowledgeResearchError(code, message);
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
  return `${url.origin}${url.pathname.replace(/\/+$/, '')}`;
}

function statusError(status) {
  if (status === 401) fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
  if (status === 504) fail('timeout', MESSAGE_TIMEOUT);
  if (status === 422) fail('unavailable', 'まとめられる回答がありません。技術KBまたは法令KBの回答を確認してください');
  if (status === 404) fail('unavailable', 'まとめの対象の相談を確認できません。保存期間を過ぎた可能性があります');
  if (status === 403 || status === 409) fail('unavailable', 'まとめを現在利用できません');
  if (status === 429 || status >= 500) fail('server', 'まとめの作成でエラーが発生しました。時間をおいてお試しください');
  fail('unavailable', 'まとめを現在利用できません');
}

function validateInputs(inputs) {
  return inputs && typeof inputs === 'object'
    && typeof inputs.normal === 'boolean' && typeof inputs.law === 'boolean'
    && (inputs.normal || inputs.law)
    && Number.isSafeInteger(inputs.knowhowCount) && inputs.knowhowCount >= 0
    && inputs.knowhowCount <= MAX_KNOWHOW_COUNT;
}

function normalizeResponse(data, conversationId, turnId) {
  if (!data || typeof data !== 'object'
    || data.senpaiConversationId !== conversationId || data.senpaiTurnId !== turnId
    || data.messageId !== `senpai-synthesis-${turnId}`
    || typeof data.content !== 'string' || !data.content.trim() || data.content.length > MAX_CONTENT_LENGTH
    || !validateInputs(data.inputs)
    || typeof data.timestamp !== 'string' || !ISO.test(data.timestamp) || !Number.isFinite(Date.parse(data.timestamp))) {
    fail('invalid_response', 'まとめの形式を確認できませんでした');
  }
  return {
    senpaiConversationId: conversationId,
    senpaiTurnId: turnId,
    messageId: data.messageId,
    content: data.content,
    inputs: { normal: data.inputs.normal, law: data.inputs.law, knowhowCount: data.inputs.knowhowCount },
    timestamp: data.timestamp,
  };
}

/**
 * Ask the server to combine the saved technical and law answers of one Senpai turn.
 * Only the two identifiers are sent; answer text is always read from the saved server rows.
 * @param {{baseUrl:string, getToken:()=>Promise<string|null|undefined>, fetchImpl?:typeof fetch, senpaiConversationId:string, senpaiTurnId:string, signal?:AbortSignal, timeoutMs?:number}} options
 */
export async function requestSenpaiSynthesis({
  baseUrl, getToken, fetchImpl = fetch, senpaiConversationId, senpaiTurnId, signal, timeoutMs = DEFAULT_TIMEOUT_MS,
}) {
  const base = endpoint(baseUrl);
  if (typeof senpaiConversationId !== 'string' || !UUID.test(senpaiConversationId)
    || typeof senpaiTurnId !== 'string' || !UUID.test(senpaiTurnId)) {
    fail('validation', '相談の識別情報を確認してください');
  }
  if (typeof getToken !== 'function' || typeof fetchImpl !== 'function') fail('config', '認証または通信の設定を確認してください');
  if (signal?.aborted) fail('cancelled', MESSAGE_CANCELLED);
  const bounded = Number.isFinite(timeoutMs) && timeoutMs >= 1 ? Math.min(timeoutMs, MAX_TIMEOUT_MS) : DEFAULT_TIMEOUT_MS;

  const controller = new AbortController();
  let interruptionCode;
  let timeoutId;
  let onAbort;
  const interruption = new Promise((_resolve, reject) => {
    onAbort = () => {
      interruptionCode = 'cancelled';
      controller.abort();
      reject(new KnowledgeResearchError('cancelled', MESSAGE_CANCELLED));
    };
    signal?.addEventListener('abort', onAbort, { once: true });
    timeoutId = setTimeout(() => {
      interruptionCode = 'timeout';
      controller.abort();
      reject(new KnowledgeResearchError('timeout', MESSAGE_TIMEOUT));
    }, bounded);
  });

  const interrupted = () => new KnowledgeResearchError(
    interruptionCode || 'cancelled', interruptionCode === 'timeout' ? MESSAGE_TIMEOUT : MESSAGE_CANCELLED,
  );

  try {
    const operation = (async () => {
      let token;
      try { token = await getToken(); } catch { fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください'); }
      if (typeof token !== 'string' || !token.trim()) fail('auth', 'ログインが必要です。ログイン後にもう一度お試しください');
      if (controller.signal.aborted) throw interrupted();
      let response;
      try {
        response = await fetchImpl(`${base}/rag/senpai/synthesis`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ senpaiConversationId, senpaiTurnId }),
          signal: controller.signal,
        });
      } catch {
        if (controller.signal.aborted) throw interrupted();
        fail('server', 'まとめのサービスに接続できませんでした。時間をおいてお試しください');
      }
      if (!response || typeof response.ok !== 'boolean') fail('invalid_response', 'まとめの応答を確認できませんでした');
      if (!response.ok) statusError(response.status);
      let data;
      try { data = await response.json(); } catch { fail('invalid_response', 'まとめの形式を確認できませんでした'); }
      return normalizeResponse(data, senpaiConversationId, senpaiTurnId);
    })();
    return await Promise.race([operation, interruption]);
  } catch (error) {
    if (error instanceof KnowledgeResearchError) throw error;
    if (controller.signal.aborted) throw interrupted();
    fail('server', 'まとめの作成に失敗しました。時間をおいてお試しください');
  } finally {
    clearTimeout(timeoutId);
    signal?.removeEventListener('abort', onAbort);
  }
}
