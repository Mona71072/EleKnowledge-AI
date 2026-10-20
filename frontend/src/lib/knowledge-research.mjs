const DEFAULT_TIMEOUT_MS = 30_000;
const MAX_TIMEOUT_MS = 120_000;
const MAX_QUERY_LENGTH = 2_000;
const RESPONSE_TYPES = new Set(['pages', 'clarify', 'not_found']);
const KNOWHOW_NOT_READY_MESSAGE = 'ノウハウMarkdownの検索準備ができていません。管理者が取込設定を確認してください。';
const KNOWHOW_SOURCE_IDS = Object.freeze({
  lists_item: 'list_item_id',
  onenote_page: 'onenote_id',
  kb_document: 'document_number',
  law_rag: 'law_id',
});
const KNOWHOW_SOURCE_FIELDS = new Set([
  'ref_type', 'source_id', 'list_item_id', 'onenote_id', 'document_number',
  'kb_filename', 'kb_verify_status', 'page_role', 'law_id', 'law_title', 'locator',
]);
const KNOWHOW_SCOPE_FIELDS = new Set([
  'control_methods', 'door_families', 'door_types', 'excludes', 'guide_systems',
  'lists_model_label', 'machine_room', 'may_apply_to', 'model_abbreviations',
  'observed_on', 'product_lines', 'scope_note', 'conditions',
]);
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
  const nodeEnvironment = process.env.NODE_ENV;
  const allowsLocalHttp = loopback && (nodeEnvironment === 'development' || nodeEnvironment === 'test');
  if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && allowsLocalHttp))
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

function validIsoTimestamp(value) {
  if (typeof value !== 'string') return undefined;
  const match = value.match(/^(\d{4}-\d{2}-\d{2})T([01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-](?:0\d|1\d|2[0-3]):[0-5]\d)$/);
  if (!match || !isDate(match[1]) || !Number.isFinite(Date.parse(value))) return undefined;
  return value;
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

function validSearchTerms(value, maxTerms = 20) {
  return stringArray(value) && value.length <= maxTerms
    && value.every((term) => term.trim().length > 0 && Array.from(term).length <= 200
      && !/[\u0000-\u001f\u007f]/u.test(term));
}

function isPlainObject(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function cleanKnowhowSourceRef(value) {
  if (!isPlainObject(value) || Object.keys(value).some((key) => !KNOWHOW_SOURCE_FIELDS.has(key))) return null;
  const identityKey = KNOWHOW_SOURCE_IDS[value.ref_type];
  if (!identityKey || typeof value[identityKey] !== 'string' || !value[identityKey].trim()) return null;
  const otherIdentityKeys = Object.values(KNOWHOW_SOURCE_IDS).filter((key) => key !== identityKey);
  if (otherIdentityKeys.some((key) => Object.hasOwn(value, key))) return null;
  const clean = {};
  for (const [key, item] of Object.entries(value)) {
    if (typeof item !== 'string' || item.length > 500 || !item.trim()
      || /[\u0000-\u001f\u007f]/u.test(item)
      || /(?:https?:\/\/|s3:\/\/|javascript:|file:\/\/|\\|(?:^|\/)\.\.(?:\/|$))/iu.test(item)) return null;
    clean[key] = item;
  }
  return clean;
}

function cleanModelScope(value) {
  if (!isPlainObject(value) || Object.keys(value).some((key) => !KNOWHOW_SCOPE_FIELDS.has(key))) return null;
  const clean = {};
  for (const [key, item] of Object.entries(value)) {
    const values = Array.isArray(item) ? item : [item];
    if (values.length > 20 || !values.every((text) => typeof text === 'string'
      && text.trim() && Array.from(text).length <= 200 && !/[\u0000-\u001f\u007f]/u.test(text)
      && !/(?:https?:\/\/|s3:\/\/|javascript:|file:\/\/|\\|(?:^|\/)\.\.(?:\/|$))/iu.test(text))) return null;
    clean[key] = Array.isArray(item) ? [...item] : item;
  }
  return clean;
}

function cleanKnowhowMatch(match) {
  if (!isPlainObject(match)
    || typeof match.knowledgeId !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/.test(match.knowledgeId)
    || !Number.isSafeInteger(match.cardVersion) || match.cardVersion < 1
    || typeof match.sha256 !== 'string' || !/^[a-f0-9]{64}$/i.test(match.sha256)
    || typeof match.title !== 'string' || !match.title.trim() || Array.from(match.title).length > 400
    || !['draft', 'approved'].includes(match.status)
    || match.usage !== 'navigation_only'
    || typeof match.body !== 'string' || Array.from(match.body).length > 16_000
    || !validSearchTerms(match.searchTerms, 100)
    || !Array.isArray(match.sourceRefs) || match.sourceRefs.length < 1 || match.sourceRefs.length > 30
    || !match.sourceRefs.every((sourceRef) => cleanKnowhowSourceRef(sourceRef) !== null)) return null;
  const modelScope = cleanModelScope(match.modelScope);
  if (!modelScope) return null;
  let serialized;
  try {
    serialized = JSON.stringify(match);
  } catch {
    return null;
  }
  if (serialized.length > 32_000) return null;
  return {
    knowledgeId: match.knowledgeId,
    cardVersion: match.cardVersion,
    sha256: match.sha256.toLowerCase(),
    title: match.title,
    status: match.status,
    usage: 'navigation_only',
    body: match.body,
    searchTerms: [...match.searchTerms],
    sourceRefs: match.sourceRefs.map(cleanKnowhowSourceRef),
    modelScope,
  };
}

function cleanKnowhow(value) {
  if (!isPlainObject(value)
    || !['matched', 'not_found'].includes(value.status)
    || typeof value.indexVersion !== 'string' || !/^sha256:[a-f0-9]{64}$/i.test(value.indexVersion)
    || !Array.isArray(value.matches) || value.matches.length > 3
    || !validSearchTerms(value.searchTerms, 8)) return null;
  const matches = value.matches.map(cleanKnowhowMatch);
  if (matches.some((match) => match === null)
    || new Set(matches.map((match) => match.knowledgeId)).size !== matches.length
    || (value.status === 'matched' && matches.length === 0)
    || (value.status === 'not_found' && matches.length !== 0)) return null;
  return {
    status: value.status,
    indexVersion: value.indexVersion.toLowerCase(),
    matches,
    searchTerms: [...value.searchTerms],
  };
}

function normalizeResponse(data, mode, query, receivedAt, expectedSessionId, includeKnowhow) {
  if (!data || typeof data !== 'object' || Array.isArray(data)
    || typeof data.content !== 'string'
    || !RESPONSE_TYPES.has(data.responseType)
    || typeof data.sessionId !== 'string' || !data.sessionId.trim()
    || !stringArray(data.clarifyQuestions)
    || !Array.isArray(data.sourceDocuments) || !data.sourceDocuments.every((item) => cleanSource(item, mode) !== null)
    || !Array.isArray(data.pageCandidates) || !data.pageCandidates.every((item) => cleanSource(item, mode) !== null)) {
    fail('invalid_response', '検索結果の形式を確認できませんでした。もう一度お試しください');
  }
  let knowhow;
  if (includeKnowhow) {
    knowhow = cleanKnowhow(data.knowhow);
    if (!knowhow) fail('invalid_response', 'ノウハウMarkdownの検索結果を確認できませんでした。もう一度お試しください');
  } else if (Object.hasOwn(data, 'knowhow')) {
    fail('invalid_response', '検索結果に予期しない情報が含まれています');
  }
  const messageId = typeof data.aiMessageId === 'string' && data.aiMessageId.trim()
    ? data.aiMessageId
    : typeof data.messageId === 'string' && data.messageId.trim()
      ? data.messageId
      : null;
  if (!messageId) fail('invalid_response', '検索結果に回答の識別情報がありません');
  if (expectedSessionId !== undefined && data.sessionId !== expectedSessionId) {
    fail('invalid_response', '会話の識別情報が一致しないため、続きの回答を表示できません');
  }
  return {
    mode,
    query,
    content: data.content,
    responseType: data.responseType,
    sessionId: data.sessionId,
    messageId,
    receivedAt,
    ...(validIsoTimestamp(data.timestamp) ? { responseTimestamp: validIsoTimestamp(data.timestamp) } : {}),
    sourceDocuments: data.sourceDocuments.map((item) => cleanSource(item, mode)),
    pageCandidates: data.pageCandidates.map((item) => cleanSource(item, mode)),
    clarifyQuestions: [...data.clarifyQuestions],
    ...(includeKnowhow ? { knowhow } : {}),
  };
}

/**
 * Search one existing RAG mode with an independent request and bounded auth/network wait.
 * The Markdown and any local metadata are deliberately not accepted by this API.
 * @param {{baseUrl:string, getToken:()=>Promise<string|null|undefined>, fetchImpl?:typeof fetch, mode:'normal'|'law', query:string, sessionId?:string, signal?:AbortSignal, timeoutMs?:number, includeKnowhow?:boolean}} options
 */
export async function queryKnowledgeSource({ baseUrl, getToken, fetchImpl = fetch, mode, query, sessionId, signal, timeoutMs = DEFAULT_TIMEOUT_MS, includeKnowhow }) {
  const endpoint = safeEndpoint(baseUrl);
  const normalizedQuery = validateQuery(query, mode);
  if (includeKnowhow !== undefined && typeof includeKnowhow !== 'boolean') {
    fail('validation', 'ノウハウMarkdown検索の指定を確認してください');
  }
  if (includeKnowhow === true && mode !== 'normal') {
    fail('validation', 'ノウハウMarkdown検索は技術KBでのみ利用できます');
  }
  if (sessionId !== undefined && (typeof sessionId !== 'string' || !sessionId.trim()
    || sessionId.length > 128 || /[\u0000-\u001f\u007f-\u009f]/u.test(sessionId))) {
    fail('validation', '会話の識別情報を確認してください');
  }
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
          body: JSON.stringify({ query: normalizedQuery, mode, filters: {}, ...(sessionId !== undefined ? { sessionId } : {}), ...(includeKnowhow === true ? { includeKnowhow: true } : {}) }),
          signal: controller.signal,
        });
      } catch {
        if (controller.signal.aborted) throw new KnowledgeResearchError(interruptionCode || 'cancelled', interruptionCode === 'timeout'
          ? '検索が時間内に完了しませんでした。再度お試しください'
          : '検索を中止しました');
        fail('server', '検索サービスに接続できませんでした。時間をおいてお試しください');
      }
      const receivedAt = new Date().toISOString();
      if (!response || typeof response.ok !== 'boolean') {
        fail('invalid_response', '検索サービスの応答を確認できませんでした');
      }
      if (!response.ok) {
        if (response.status === 401) fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
        if (includeKnowhow === true && response.status === 503) fail('unavailable', KNOWHOW_NOT_READY_MESSAGE);
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
      return normalizeResponse(data, mode, normalizedQuery, receivedAt, sessionId, includeKnowhow === true);
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
  const longest = Math.max(0, ...Array.from(String(value).matchAll(/`+/g), (match) => match[0].length));
  return '`'.repeat(Math.max(3, longest + 1));
}

function literalCode(value) {
  const delimiter = codeFence(value);
  return `${delimiter} ${value} ${delimiter}`;
}

/** Preserve imported identity as literal text in generated Markdown provenance. */
export function buildResearchTargetNote(target) {
  if (!target || typeof target.knowledgeId !== 'string' || !target.knowledgeId.trim()
    || target.knowledgeId.length > 200 || /[\r\n\0]/u.test(target.knowledgeId)
    || !Number.isSafeInteger(target.baseVersion) || target.baseVersion < 1
    || !Number.isSafeInteger(target.manualBodyRevision) || target.manualBodyRevision < 0) {
    fail('validation', '調査対象のIDと版を確認してください');
  }
  return `> 調査対象: ${literalCode(target.knowledgeId)} · 原版 v${target.baseVersion} · 検索時本文編集版 ${target.manualBodyRevision}`;
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
  return `- ${title}${page} — ${literalCode(uri)}`;
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
  const tracking = [
    '#### AI回答の追跡情報',
    '',
    '> AI回答の追跡情報。資料の改訂版・承認情報ではない',
    `- 検索モード: ${answer.mode === 'law' ? '法令KB' : '技術KB'} (${answer.mode})`,
    `- 質問: ${escapeInline(answer.query)}`,
    ...(validIsoTimestamp(answer.receivedAt) ? [`- 受信日時: ${answer.receivedAt}`] : []),
    ...(validIsoTimestamp(answer.responseTimestamp) ? [`- API回答日時: ${answer.responseTimestamp}`] : []),
    ...(typeof answer.sessionId === 'string' && answer.sessionId.trim() ? [`- sessionId: ${escapeInline(answer.sessionId)}`] : []),
    ...(typeof answer.messageId === 'string' && answer.messageId.trim() ? [`- messageId: ${escapeInline(answer.messageId)}`] : []),
  ];
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
    '',
    ...tracking,
  ].join('\n');
}
