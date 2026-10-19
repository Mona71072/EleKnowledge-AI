const DEFAULT_TIMEOUT_MS = 30_000;
const MAX_TIMEOUT_MS = 120_000;
const MAX_QUERY_LENGTH = 2_000;
const RESPONSE_TYPES = new Set(['pages', 'clarify', 'not_found']);
const RESPONSE_FIELDS = [
  'documentName',
  'title',
  'category',
  'modelType',
  'pageNumber',
  'relevance',
  'snippet',
  'hasImage',
  'source_action',
  'referenceCoverage',
  'referenceCoverageReason',
  'lowConfidence',
];

/** @typedef {'auth'|'unavailable'|'timeout'|'cancelled'|'server'|'invalid_response'|'config'|'validation'} KnowledgeResearchErrorCode */

/** A safe, user-facing error from the development research client. */
export class KnowledgeResearchError extends Error {
  /** @param {KnowledgeResearchErrorCode} code @param {string} message */
  constructor(code, message) {
    super(message);
    this.name = 'KnowledgeResearchError';
    this.code = code;
  }
}

function fail(code, message) {
  throw new KnowledgeResearchError(code, message);
}

function safeEndpoint(baseUrl) {
  if (typeof baseUrl !== 'string' || !baseUrl.trim()) {
    fail('config', 'RAG APIの接続先が設定されていません');
  }
  let url;
  try {
    url = new URL(baseUrl);
  } catch {
    fail('config', 'RAG APIの接続先を確認してください');
  }
  const loopback = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname.toLowerCase());
  if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && loopback))
    || url.username || url.password || url.search || url.hash) {
    fail('config', 'RAG APIの接続先はHTTPSまたはローカル開発用HTTPで設定してください');
  }
  return `${url.origin}${url.pathname.replace(/\/+$/, '')}`;
}

function validateQuery(query, mode) {
  if (mode !== 'normal' && mode !== 'law') {
    fail('validation', '検索モードを確認してください');
  }
  if (typeof query !== 'string' || !query.trim()) {
    fail('validation', '検索する質問を入力してください');
  }
  const normalized = query.trim();
  if (Array.from(normalized).length > MAX_QUERY_LENGTH) {
    fail('validation', '質問は2,000文字以内で入力してください');
  }
  return normalized;
}

function cleanS3Uri(value) {
  if (typeof value !== 'string' || !value.startsWith('s3://')) return null;
  const match = value.match(/^s3:\/\/([a-z0-9][a-z0-9.-]{1,61}[a-z0-9])\/(.+)$/i);
  if (!match || /[?#\u0000-\u001f\u007f]/u.test(value) || match[2].includes('\\')) return null;
  return value;
}

function legacyS3Uri(value) {
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:') return null;
    const virtual = url.hostname.match(/^([a-z0-9][a-z0-9.-]{1,61}[a-z0-9])\.s3(?:[.-][a-z0-9-]+)?\.amazonaws\.com$/i);
    const pathStyle = url.hostname.match(/^s3(?:[.-][a-z0-9-]+)?\.amazonaws\.com$/i);
    let bucket;
    let rawKey;
    if (virtual) {
      bucket = virtual[1];
      rawKey = url.pathname.slice(1);
    } else if (pathStyle) {
      const parts = url.pathname.slice(1).split('/');
      bucket = parts.shift();
      rawKey = parts.join('/');
    } else return null;
    const key = decodeURIComponent(rawKey);
    if (!bucket || !key || key.includes('\\') || /[\u0000-\u001f\u007f]/u.test(key)) return null;
    return cleanS3Uri(`s3://${bucket}/${key}`);
  } catch {
    return null;
  }
}

function safeSourceUri(value) {
  return cleanS3Uri(value) || legacyS3Uri(value) || undefined;
}

function isDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(date.valueOf()) && date.toISOString().slice(0, 10) === value;
}

function safeLawCitation(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return undefined;
  const { lawId, lawTitle, lawNumber, effectiveDate, provisionType, provisionReference, sourceUrl } = value;
  if (typeof lawId !== 'string' || !/^[0-9A-Za-z]{8,20}$/.test(lawId)
    || typeof lawTitle !== 'string' || !lawTitle.trim()
    || typeof lawNumber !== 'string' || !lawNumber.trim()
    || !isDate(effectiveDate)
    || typeof provisionType !== 'string' || !provisionType.trim()
    || (provisionReference !== undefined && typeof provisionReference !== 'string')) return undefined;
  const url = safeEgovUrl(sourceUrl, lawId);
  if (!url) return undefined;
  return {
    lawId,
    lawTitle,
    lawNumber,
    effectiveDate,
    provisionType,
    ...(provisionReference ? { provisionReference } : {}),
    sourceUrl: url,
  };
}

function safeEgovUrl(value, lawId) {
  if (typeof value !== 'string') return undefined;
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.hostname !== 'laws.e-gov.go.jp'
      || url.username || url.password || url.search) return undefined;
    const lawPath = `/law/${lawId}`;
    const isLawPath = url.pathname === lawPath;
    const versionPath = new RegExp(`^${lawPath}/[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`);
    if (!isLawPath && !versionPath.test(url.pathname)) return undefined;
    if (url.hash && !/^#[A-Za-z0-9][A-Za-z0-9._-]{0,159}$/.test(url.hash)) return undefined;
    return url.href;
  } catch {
    return undefined;
  }
}

function cleanSource(source, mode) {
  if (!source || typeof source !== 'object' || Array.isArray(source)) return null;
  const result = {};
  for (const field of RESPONSE_FIELDS) {
    const value = source[field];
    if (typeof value === 'string' || typeof value === 'boolean'
      || (typeof value === 'number' && Number.isFinite(value))) result[field] = value;
  }
  if (Number.isSafeInteger(source.pageNumber) && source.pageNumber > 0) result.pageNumber = source.pageNumber;
  if (mode === 'law') {
    const citation = safeLawCitation(source.lawCitation);
    const sourceUri = citation ? safeEgovUrl(source.sourceUri, citation.lawId) : undefined;
    if (citation) result.lawCitation = citation;
    if (sourceUri && sourceUri === citation.sourceUrl) result.sourceUri = sourceUri;
  } else {
    const uri = safeSourceUri(source.sourceUri);
    if (uri) result.sourceUri = uri;
  }
  return result;
}

function stringArray(value) {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}

function normalizeResponse(data, mode, query) {
  if (!data || typeof data !== 'object' || Array.isArray(data)
    || typeof data.content !== 'string'
    || !RESPONSE_TYPES.has(data.responseType)
    || typeof data.sessionId !== 'string' || !data.sessionId.trim()
    || !stringArray(data.clarifyQuestions)
    || !Array.isArray(data.sourceDocuments) || !data.sourceDocuments.every((item) => cleanSource(item, mode) !== null)
    || !Array.isArray(data.pageCandidates) || !data.pageCandidates.every((item) => cleanSource(item, mode) !== null)) {
    fail('invalid_response', '検索結果の形式を確認できませんでした。もう一度お試しください');
  }
  const messageId = typeof data.aiMessageId === 'string' && data.aiMessageId.trim()
    ? data.aiMessageId
    : typeof data.messageId === 'string' && data.messageId.trim()
      ? data.messageId
      : null;
  if (!messageId) fail('invalid_response', '検索結果に回答の識別情報がありません');
  return {
    mode,
    query,
    content: data.content,
    responseType: data.responseType,
    sessionId: data.sessionId,
    messageId,
    sourceDocuments: data.sourceDocuments.map((item) => cleanSource(item, mode)),
    pageCandidates: data.pageCandidates.map((item) => cleanSource(item, mode)),
    clarifyQuestions: [...data.clarifyQuestions],
  };
}

/**
 * Search one existing RAG mode with an independent request and bounded auth/network wait.
 * The Markdown and any local metadata are deliberately not accepted by this API.
 * @param {{baseUrl:string, getToken:()=>Promise<string|null|undefined>, fetchImpl?:typeof fetch, mode:'normal'|'law', query:string, signal?:AbortSignal, timeoutMs?:number}} options
 */
export async function queryKnowledgeSource({ baseUrl, getToken, fetchImpl = fetch, mode, query, signal, timeoutMs = DEFAULT_TIMEOUT_MS }) {
  const endpoint = safeEndpoint(baseUrl);
  const normalizedQuery = validateQuery(query, mode);
  if (typeof getToken !== 'function' || typeof fetchImpl !== 'function') {
    fail('config', '認証または通信の設定を確認してください');
  }
  if (signal?.aborted) fail('cancelled', '検索を中止しました');
  if (!Number.isFinite(timeoutMs) || timeoutMs < 1) fail('config', '通信時間の設定を確認してください');
  const boundedTimeout = Math.min(timeoutMs, MAX_TIMEOUT_MS);
  const controller = new AbortController();
  let timeoutId;
  let onAbort;
  let interruptionCode;
  const interruption = new Promise((_resolve, reject) => {
    onAbort = () => {
      interruptionCode = 'cancelled';
      controller.abort();
      reject(new KnowledgeResearchError('cancelled', '検索を中止しました'));
    };
    signal?.addEventListener('abort', onAbort, { once: true });
    timeoutId = setTimeout(() => {
      interruptionCode = 'timeout';
      controller.abort();
      reject(new KnowledgeResearchError('timeout', '検索が時間内に完了しませんでした。再度お試しください'));
    }, boundedTimeout);
  });

  try {
    const operation = (async () => {
      let token;
      try {
        token = await getToken();
      } catch {
        fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
      }
      if (typeof token !== 'string' || !token.trim()) {
        fail('auth', 'ログインが必要です。ログイン後にもう一度お試しください');
      }
      if (controller.signal.aborted) {
        throw new KnowledgeResearchError(interruptionCode || 'cancelled', interruptionCode === 'timeout'
          ? '検索が時間内に完了しませんでした。再度お試しください'
          : '検索を中止しました');
      }
      let response;
      try {
        response = await fetchImpl(`${endpoint}/rag/query`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: normalizedQuery, mode, filters: {} }),
          signal: controller.signal,
        });
      } catch {
        if (controller.signal.aborted) throw new KnowledgeResearchError(interruptionCode || 'cancelled', interruptionCode === 'timeout'
          ? '検索が時間内に完了しませんでした。再度お試しください'
          : '検索を中止しました');
        fail('server', '検索サービスに接続できませんでした。時間をおいてお試しください');
      }
      if (!response || typeof response.ok !== 'boolean') {
        fail('invalid_response', '検索サービスの応答を確認できませんでした');
      }
      if (!response.ok) {
        if (response.status === 401) fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
        if (response.status === 403) fail('unavailable', mode === 'law' ? '法令KBを現在利用できません' : '検索サービスを現在利用できません');
        if (response.status >= 500) fail('server', '検索サービスでエラーが発生しました。時間をおいてお試しください');
        fail('unavailable', '検索サービスを現在利用できません');
      }
      let data;
      try {
        data = await response.json();
      } catch {
        fail('invalid_response', '検索結果の形式を確認できませんでした');
      }
      return normalizeResponse(data, mode, normalizedQuery);
    })();
    return await Promise.race([operation, interruption]);
  } catch (error) {
    if (error instanceof KnowledgeResearchError) throw error;
    if (controller.signal.aborted) {
      if (interruptionCode === 'timeout') fail('timeout', '検索が時間内に完了しませんでした。再度お試しください');
      fail('cancelled', '検索を中止しました');
    }
    fail('server', '検索処理に失敗しました。時間をおいてお試しください');
  } finally {
    clearTimeout(timeoutId);
    if (onAbort) signal?.removeEventListener('abort', onAbort);
  }
}

/** Return a safe link for a normal KB document or verified e-Gov law citation. */
export function researchSourceHref(source, mode) {
  if (!source || typeof source !== 'object' || (mode !== 'normal' && mode !== 'law')) return undefined;
  if (mode === 'law') {
    const citation = safeLawCitation(source.lawCitation);
    return citation?.sourceUrl;
  }
  const uri = safeSourceUri(source.sourceUri);
  if (!uri) return undefined;
  const href = `/doc?uri=${encodeURIComponent(uri)}`;
  return Number.isSafeInteger(source.pageNumber) && source.pageNumber > 0
    ? `${href}#page=${source.pageNumber}`
    : href;
}

function escapeInline(value) {
  return String(value)
    .replaceAll('\r', ' ')
    .replaceAll('\n', ' ')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replace(/[\\`*_{}\[\]()#+.!|]/g, '\\$&');
}

function codeFence(value) {
  const longest = Math.max(0, ...String(value).matchAll(/`+/g).map((match) => match[0].length));
  return '`'.repeat(Math.max(3, longest + 1));
}

function sourceReference(source, mode, index) {
  const title = escapeInline(source.documentName || source.title || `出典 ${index + 1}`);
  if (mode === 'law' && source.lawCitation) {
    const citation = safeLawCitation(source.lawCitation);
    if (!citation) return `- ${title}（法令出典を確認できません）`;
    const provision = citation.provisionReference ? ` ${escapeInline(citation.provisionReference)}` : '';
    return `- ${escapeInline(citation.lawTitle)}（${escapeInline(citation.lawNumber)}）${provision}、施行日 ${citation.effectiveDate} — ${citation.sourceUrl}`;
  }
  const uri = safeSourceUri(source.sourceUri);
  if (!uri) return `- ${title}（安全に表示できる出典URLなし）`;
  const page = Number.isSafeInteger(source.pageNumber) && source.pageNumber > 0 ? ` p.${source.pageNumber}` : '';
  return `- ${title}${page} — ${uri}`;
}

/**
 * Produce a deterministic local Markdown candidate. It never marks review or approval state.
 * Clarification and no-result answers cannot be adopted as evidence.
 * @param {import('./knowledge-research.mjs').ResearchAnswer} answer
 */
export function buildResearchNote(answer) {
  if (!answer || !['normal', 'law'].includes(answer.mode)
    || typeof answer.query !== 'string' || typeof answer.content !== 'string'
    || answer.responseType !== 'pages'
    || !Array.isArray(answer.sourceDocuments) || answer.sourceDocuments.length === 0) {
    fail('validation', '根拠資料を含む検索結果だけを調査候補にできます');
  }
  const eligibleSources = answer.sourceDocuments.filter((source) => researchSourceHref(source, answer.mode));
  if (eligibleSources.length === 0) {
    fail('validation', 'この検索モードで確認できる出典がないため調査候補にできません');
  }
  const fence = codeFence(answer.content);
  const heading = answer.mode === 'law' ? '法令KB' : '技術KB';
  const refs = eligibleSources.map((source, index) => sourceReference(source, answer.mode, index));
  return [
    `### ${heading}の調査メモ（AI候補・未確認）`,
    '',
    `- 質問: ${escapeInline(answer.query)}`,
    '- 状態: AI候補。根拠資料と適用条件は担当者が未確認',
    '',
    '#### 回答候補',
    '',
    fence,
    answer.content,
    fence,
    '',
    '#### 出典',
    '',
    ...refs,
  ].join('\n');
}
