/** Stable I1 JSON encoding: UTF-8, sorted object keys, unchanged string content. */
export function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

/** Hash exactly the confirmed input; no client approval or authority is inferred. */
export async function inputHash(value) {
  const bytes = new TextEncoder().encode(canonicalJson(value));
  const result = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(result)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

/** Reject synthetic authentication anywhere except an explicit local development URL. */
export function validateConnection({ baseUrl, synthetic, development, hostname }) {
  const url = new URL(baseUrl);
  if (url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new Error('共通知識APIの接続先を確認してください。');
  }
  if (synthetic) {
    if (!development || !['localhost', '127.0.0.1'].includes(hostname)
      || url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || url.port !== '8765') {
      throw new Error('合成I1はローカル開発でだけ利用できます。');
    }
  } else if (url.protocol !== 'https:') {
    throw new Error('認証付きAPIにはHTTPSの設定が必要です。');
  }
  return url.origin;
}

/** Use a deterministic idempotency key for retries of the same exact actor/request. */
export async function requestKnowledge({ baseUrl, token, actor, path, method = 'GET', body,
  revision, fetchImpl = globalThis.fetch }) {
  if (!token || !/^\/(?:contributions|cards|published|operations)(?:[/?]|$)/u.test(path)) {
    throw new Error('認証と操作対象を確認してください。');
  }
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  if (method !== 'GET') {
    headers['Idempotency-Key'] = await inputHash({ actor, method, path, revision: revision ?? null, body });
    if (revision !== undefined) headers['If-Match'] = String(revision);
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15_000);
  try {
    const response = await fetchImpl(`${baseUrl}/knowledge${path}`, {
      method, headers, cache: 'no-store', signal: controller.signal,
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(`${result.message || '操作できませんでした。'} (${result.code || response.status})`);
    }
    return result;
  } catch (error) {
    if (error?.name === 'AbortError') throw new Error('応答を確認できません。同じ内容で再試行してください。');
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
