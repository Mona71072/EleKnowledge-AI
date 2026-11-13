// 書き換え案 API（POST /rag/knowhow/rewrite-proposal）のクライアント。
// 認証・接続先の確認・中止・タイムアウトは knowledge-senpai-synthesis.mjs と同じ流儀。
// 失敗は固定の日本語文言にし、応答本文・例外本文は利用者にも呼び出し側にも出さない。
import { normalizeRewriteResponse } from './knowhow-rewrite-response.mjs';

/** 通信の待ち時間の既定値（ミリ秒）。 */
export const REWRITE_TIMEOUT_MS = 35_000;
const MAX_TIMEOUT_MS = 60_000;
const PATH = '/rag/knowhow/rewrite-proposal';
const LOOPBACK_HOSTS = ['localhost', '127.0.0.1', '[::1]'];

const MESSAGES = Object.freeze({
  auth: 'ログイン状態または利用権限を確認してください。',
  config: 'RAG APIの接続先が設定されていません。',
  unavailable: 'この環境では使えません。',
  throttled: '混み合っています。少し待ってからやり直してください。',
  failed: '案を作れませんでした。やり直してください。',
  network: '案を作れませんでした。通信状態を確認してやり直してください。',
  validation: '送る内容を確認できませんでした。照合し直してからやり直してください。',
  too_large: '送る内容が大きすぎます。確認済みの根拠を減らしてやり直してください。',
  timeout: '案の作成が時間内に完了しませんでした。やり直してください。',
  cancelled: '案の作成を中止しました。',
  invalid_response: '案の形式を確認できませんでした。やり直してください。',
});

/** 利用者に見せてよい固定文言だけを持つエラー。code は画面の分岐用。 */
export class KnowhowRewriteError extends Error {
  /** @param {keyof typeof MESSAGES} code */
  constructor(code) {
    super(MESSAGES[code]);
    this.name = 'KnowhowRewriteError';
    this.code = code;
  }
}

/**
 * 失敗を、利用者に見せる固定の日本語文言にする。想定外の例外は汎用の文言にする。
 * @param {unknown} error
 */
export function rewriteFailureMessage(error) {
  return error instanceof KnowhowRewriteError ? error.message : MESSAGES.failed;
}

function fail(code) {
  throw new KnowhowRewriteError(code);
}

function endpoint(baseUrl) {
  if (typeof baseUrl !== 'string' || !baseUrl.trim()) fail('config');
  let url;
  try { url = new URL(baseUrl); } catch { fail('config'); }
  const localHttp = LOOPBACK_HOSTS.includes(url.hostname.toLowerCase()) && ['development', 'test'].includes(process.env.NODE_ENV);
  if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && localHttp)) || url.username || url.password || url.search || url.hash) fail('config');
  return `${url.origin}${url.pathname.replace(/\/+$/u, '')}${PATH}`;
}

const STATUS_CODES = Object.freeze({ 400: 'validation', 401: 'auth', 403: 'unavailable', 413: 'too_large', 429: 'throttled' });

function statusError(status) {
  fail(STATUS_CODES[status] ?? 'failed');
}

async function readToken(getToken) {
  let token;
  try { token = await getToken(); } catch { fail('auth'); }
  if (typeof token !== 'string' || !token.trim()) fail('auth');
  return token;
}

async function send({ url, token, request, fetchImpl, signal, interrupted }) {
  let response;
  try {
    response = await fetchImpl(url, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal,
    });
  } catch {
    if (signal.aborted) throw interrupted();
    fail('network');
  }
  if (!response || typeof response.ok !== 'boolean') fail('invalid_response');
  if (!response.ok) statusError(response.status);
  let data;
  try { data = await response.json(); } catch { fail('invalid_response'); }
  return data;
}

/**
 * 書き換え案を作らせる。応答はクライアント側でも検証し、外れた節は不採用にして返す。
 * 送るのは `request`（確認済みの根拠と対象の節）だけ。失敗は {@link KnowhowRewriteError}。
 * @param {{ baseUrl: string, getToken: () => Promise<string | null | undefined>, fetchImpl?: typeof fetch, request: import('./knowhow-rewrite.mjs').RewriteRequest | null, signal?: AbortSignal, timeoutMs?: number }} options
 */
export async function requestKnowhowRewrite({ baseUrl, getToken, fetchImpl = fetch, request, signal, timeoutMs = REWRITE_TIMEOUT_MS }) {
  const url = endpoint(baseUrl);
  if (!request || typeof request !== 'object' || typeof getToken !== 'function' || typeof fetchImpl !== 'function') fail('config');
  if (signal?.aborted) fail('cancelled');
  const bounded = Number.isFinite(timeoutMs) && timeoutMs >= 1 ? Math.min(timeoutMs, MAX_TIMEOUT_MS) : REWRITE_TIMEOUT_MS;
  const controller = new AbortController();
  let interruption = 'cancelled';
  let timer;
  let onAbort;
  const interrupted = () => new KnowhowRewriteError(interruption);
  const stop = new Promise((_resolve, reject) => {
    onAbort = () => { interruption = 'cancelled'; controller.abort(); reject(interrupted()); };
    signal?.addEventListener('abort', onAbort, { once: true });
    timer = setTimeout(() => { interruption = 'timeout'; controller.abort(); reject(interrupted()); }, bounded);
  });
  try {
    const work = (async () => {
      const token = await readToken(getToken);
      if (controller.signal.aborted) throw interrupted();
      const data = await send({ url, token, request, fetchImpl, signal: controller.signal, interrupted });
      return normalizeRewriteResponse(data, request) ?? fail('invalid_response');
    })();
    return await Promise.race([work, stop]);
  } catch (error) {
    if (error instanceof KnowhowRewriteError) throw error;
    if (controller.signal.aborted) throw interrupted();
    throw new KnowhowRewriteError('failed');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', onAbort);
  }
}
