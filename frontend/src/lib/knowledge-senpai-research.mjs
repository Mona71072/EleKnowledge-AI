import { KnowledgeResearchError, researchSourceHref } from './knowledge-research.mjs';
import { createJobPoller } from './research-polling.mjs';

// 契約: docs/features/development/senpai-research-contract.md
const DEFAULT_TIMEOUT_MS = 15_000;
const MAX_TIMEOUT_MS = 60_000;
const MAX_QUESTION_LENGTH = 2_000;
const MAX_ANSWER_LENGTH = 64_000;
const MAX_STEPS_PER_RESPONSE = 200;
const MAX_LIST_ITEMS = 100;
const MAX_TEXT_LENGTH = 2_000;
const MAX_DETAIL_LENGTH = 120;
const MAX_DEBUG_JSON_LENGTH = 20_000;
const MAX_WARNINGS = 10;
const MAX_WARNING_LENGTH = 200;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu;
const ISO = /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/u;

const JOB_STATUSES = new Set(['queued', 'running', 'completed', 'failed']);
const STEP_NAMES = new Set(['understand', 'knowhow', 'tech_search', 'law_search', 'sufficiency', 'retry_search', 'doc_page', 'clarify', 'synthesize', 'verify']);
const STEP_STATUSES = new Set(['running', 'done', 'skipped', 'failed']);
const RESULT_KINDS = new Set(['answer', 'clarify', 'not_found']);
const STOP_REASONS = new Set(['sufficient', 'budget', 'no_new_results', 'clarify', 'insufficient', 'judgment_failed', 'partial']);
const INTENTS = new Set(['procedure', 'cause', 'spec_value', 'legal', 'other']);
const KNOWHOW_STATUSES = new Set(['draft', 'approved']);
// SYNC: must equal KNOWHOW_MODEL_FITS in knowledge-research.mjs.
const MODEL_FITS = new Set(['matched', 'general', 'other_product', 'unknown']);
const ERROR_CODES = new Set(['Timeout', 'BudgetExceeded', 'Internal', 'QuestionUnavailable']);

/** 画面に出す固定文。サーバーの文言はそのまま表示しない。 */
export const SENPAI_RESEARCH_ERROR_MESSAGES = Object.freeze({
  Timeout: '調査が時間内に終わりませんでした。質問を具体的にして、もう一度お試しください',
  BudgetExceeded: '調査の上限に達しました。質問を絞って、もう一度お試しください',
  QuestionUnavailable: 'この質問は調査できませんでした。内容を変えてお試しください',
  Internal: '調査中にエラーが発生しました。時間をおいてお試しください',
});
export const SENPAI_RESEARCH_CANCELLED_MESSAGE = '中止しました';

const MESSAGE_CANCELLED = '調査の確認を中止しました';
const MESSAGE_TIMEOUT = '調査の通信が時間内に完了しませんでした。時間をおいてお試しください';
const MESSAGE_GAVE_UP = '調査が時間内に終わりませんでした。時間をおいてもう一度お試しください';
const MESSAGE_INVALID = '調査の応答の形式を確認できませんでした';

function fail(code, message, status) {
  const error = new KnowledgeResearchError(code, message);
  if (status !== undefined) error.status = status;
  throw error;
}

const invalid = () => fail('invalid_response', MESSAGE_INVALID);
const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const isText = (value, max = MAX_TEXT_LENGTH) => typeof value === 'string' && value.trim() !== '' && value.length <= max;
const isCount = (value) => Number.isSafeInteger(value) && value >= 0;

function endpoint(baseUrl) {
  if (typeof baseUrl !== 'string' || !baseUrl.trim()) fail('config', '調査APIの接続先が設定されていません');
  let url;
  try { url = new URL(baseUrl); } catch { fail('config', '調査APIの接続先を確認してください'); }
  const loopback = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname.toLowerCase());
  const localHttp = loopback && ['development', 'test'].includes(process.env.NODE_ENV);
  if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && localHttp))
    || url.username || url.password || url.search || url.hash) {
    fail('config', '調査APIの接続先はHTTPSまたはローカル開発用HTTPで設定してください');
  }
  return `${url.origin}${url.pathname.replace(/\/+$/, '')}`;
}

function validIso(value) {
  return typeof value === 'string' && ISO.test(value) && Number.isFinite(Date.parse(value));
}

// ---- 応答の検証 ----

function normalizeCounts(raw) {
  if (raw === undefined || raw === null) return undefined;
  if (!isObject(raw)) invalid();
  const counts = {};
  for (const key of ['hits', 'selected', 'documents']) {
    if (raw[key] === undefined) continue;
    if (!isCount(raw[key])) invalid();
    counts[key] = raw[key];
  }
  return counts;
}

function normalizeStep(raw) {
  if (!isObject(raw) || !Number.isSafeInteger(raw.seq) || raw.seq < 1
    || !STEP_NAMES.has(raw.step) || !STEP_STATUSES.has(raw.status)
    || !isText(raw.labelJa, 100) || !validIso(raw.startedAt)) invalid();
  if (raw.endedAt !== undefined && raw.endedAt !== null && !validIso(raw.endedAt)) invalid();
  if (raw.detailJa !== undefined && raw.detailJa !== null && typeof raw.detailJa !== 'string') invalid();
  const detailJa = typeof raw.detailJa === 'string' && raw.detailJa.trim()
    ? Array.from(raw.detailJa).slice(0, MAX_DETAIL_LENGTH).join('') : undefined;
  const counts = normalizeCounts(raw.counts);
  return {
    seq: raw.seq, step: raw.step, labelJa: raw.labelJa, status: raw.status,
    ...(detailJa ? { detailJa } : {}),
    ...(counts ? { counts } : {}),
    startedAt: raw.startedAt, endedAt: raw.endedAt ?? null,
  };
}

function list(value, normalizeItem) {
  if (!Array.isArray(value) || value.length > MAX_LIST_ITEMS) invalid();
  return value.map(normalizeItem);
}

function optionalText(raw, key, max = MAX_TEXT_LENGTH) {
  if (raw[key] === undefined || raw[key] === null) return {};
  if (typeof raw[key] !== 'string' || raw[key].length > max) invalid();
  return raw[key].trim() ? { [key]: raw[key] } : {};
}

function normalizeTech(raw) {
  if (!isObject(raw) || typeof raw.ref !== 'string' || !/^T\d{1,3}$/u.test(raw.ref) || !isText(raw.title)) invalid();
  if (raw.pageNumber !== undefined && raw.pageNumber !== null && (!Number.isSafeInteger(raw.pageNumber) || raw.pageNumber < 1)) invalid();
  return {
    ref: raw.ref, title: raw.title,
    ...optionalText(raw, 'documentName'),
    ...(raw.pageNumber ? { pageNumber: raw.pageNumber } : {}),
    ...optionalText(raw, 'sourceUri', 1_024),
  };
}

function normalizeLaw(raw) {
  if (!isObject(raw) || typeof raw.ref !== 'string' || !/^L\d{1,3}$/u.test(raw.ref) || !isText(raw.lawTitle)) invalid();
  return {
    ref: raw.ref, lawTitle: raw.lawTitle,
    ...optionalText(raw, 'provision'),
    ...optionalText(raw, 'effectiveDate', 64),
    ...optionalText(raw, 'sourceUrl', 1_024),
  };
}

function normalizeUsedKnowhow(raw) {
  if (!isObject(raw) || typeof raw.ref !== 'string' || !/^K\d{1,3}$/u.test(raw.ref)
    || !isText(raw.knowledgeId, 128) || !Number.isSafeInteger(raw.cardVersion) || raw.cardVersion < 1
    || !isText(raw.title) || !KNOWHOW_STATUSES.has(raw.status)) invalid();
  if (raw.modelFit !== undefined && !MODEL_FITS.has(raw.modelFit)) invalid();
  let products;
  if (raw.modelFitProducts !== undefined) {
    if (!Array.isArray(raw.modelFitProducts) || raw.modelFitProducts.length > 12
      || !raw.modelFitProducts.every((product) => isText(product, 64))) invalid();
    products = [...raw.modelFitProducts];
  }
  return {
    ref: raw.ref, knowledgeId: raw.knowledgeId, cardVersion: raw.cardVersion, title: raw.title, status: raw.status,
    ...(raw.modelFit ? { modelFit: raw.modelFit } : {}),
    ...(products ? { modelFitProducts: products } : {}),
  };
}

function normalizeCandidateKnowhow(raw) {
  if (!isObject(raw) || !isText(raw.knowledgeId, 128) || !Number.isSafeInteger(raw.cardVersion)
    || raw.cardVersion < 1 || !isText(raw.title)) invalid();
  return { knowledgeId: raw.knowledgeId, cardVersion: raw.cardVersion, title: raw.title };
}

function normalizeSources(raw) {
  if (!isObject(raw) || !isObject(raw.knowhow)) invalid();
  return {
    tech: list(raw.tech, normalizeTech),
    law: list(raw.law, normalizeLaw),
    knowhow: {
      used: list(raw.knowhow.used, normalizeUsedKnowhow),
      candidates: list(raw.knowhow.candidates, normalizeCandidateKnowhow),
    },
  };
}

function normalizeUnderstanding(raw) {
  if (raw === undefined || raw === null) return undefined;
  if (!isObject(raw)) invalid();
  if (raw.intent !== undefined && !INTENTS.has(raw.intent)) invalid();
  if (raw.lawRelevant !== undefined && typeof raw.lawRelevant !== 'boolean') invalid();
  const understanding = {};
  for (const key of ['modelType', 'controlMethod', 'part', 'symptom', 'situation']) {
    if (raw[key] === undefined) continue;
    if (raw[key] !== null && (typeof raw[key] !== 'string' || raw[key].length > 200)) invalid();
    understanding[key] = raw[key];
  }
  if (raw.intent) understanding.intent = raw.intent;
  if (raw.lawRelevant !== undefined) understanding.lawRelevant = raw.lawRelevant;
  return understanding;
}

function stringList(value, max = MAX_TEXT_LENGTH, maxItems = MAX_LIST_ITEMS) {
  if (value === undefined) return [];
  if (!Array.isArray(value) || value.length > maxItems || !value.every((item) => isText(item, max))) invalid();
  return [...value];
}

/**
 * 契約の `result` を検証して返す。未知の kind / 種別 / modelFit などは拒否し、任意項目の欠落は許す。
 * @param {unknown} raw
 */
export function normalizeSenpaiResearchResult(raw) {
  if (!isObject(raw) || !RESULT_KINDS.has(raw.kind)) invalid();
  if (raw.answerMarkdown !== undefined && (typeof raw.answerMarkdown !== 'string' || raw.answerMarkdown.length > MAX_ANSWER_LENGTH)) invalid();
  const answerMarkdown = raw.answerMarkdown ?? '';
  if (raw.kind === 'answer' && !answerMarkdown.trim()) invalid();
  if (raw.stopReason !== undefined && !STOP_REASONS.has(raw.stopReason)) invalid();
  const understanding = normalizeUnderstanding(raw.understanding);
  return {
    kind: raw.kind,
    answerMarkdown,
    clarifyQuestions: stringList(raw.clarifyQuestions),
    sources: normalizeSources(raw.sources),
    ...(understanding ? { understanding } : {}),
    unverifiedRefs: stringList(raw.unverifiedRefs, 64),
    // 任意。技術・法令の検索が完全に失敗したときだけ付く、利用者向けの日本語の注意。
    ...(raw.warnings !== undefined ? { warnings: stringList(raw.warnings, MAX_WARNING_LENGTH, MAX_WARNINGS) } : {}),
    ...(raw.stopReason ? { stopReason: raw.stopReason } : {}),
  };
}

function normalizeError(raw) {
  if (!isObject(raw) || !ERROR_CODES.has(raw.code)) invalid();
  return { code: raw.code, message: SENPAI_RESEARCH_ERROR_MESSAGES[raw.code] };
}

function cloneJson(value) {
  const text = JSON.stringify(value);
  if (text === undefined || text.length > MAX_DEBUG_JSON_LENGTH) invalid();
  return JSON.parse(text);
}

function numberList(value) {
  if (!Array.isArray(value) || value.length > 50 || !value.every(Number.isFinite)) invalid();
  return [...value];
}

function normalizeTool(raw) {
  if (!isObject(raw) || !Number.isSafeInteger(raw.seq) || !isText(raw.tool, 64)) invalid();
  for (const key of ['hits', 'selected']) if (raw[key] !== undefined && !isCount(raw[key])) invalid();
  if (raw.ms !== undefined && !(Number.isFinite(raw.ms) && raw.ms >= 0)) invalid();
  if (raw.query !== undefined && (typeof raw.query !== 'string' || raw.query.length > MAX_TEXT_LENGTH)) invalid();
  if (raw.filters !== undefined && !isObject(raw.filters)) invalid();
  return {
    seq: raw.seq, tool: raw.tool,
    ...(raw.query !== undefined ? { query: raw.query } : {}),
    ...(raw.filters ? { filters: cloneJson(raw.filters) } : {}),
    ...(raw.hits !== undefined ? { hits: raw.hits } : {}),
    ...(raw.selected !== undefined ? { selected: raw.selected } : {}),
    ...(raw.topScores !== undefined ? { topScores: numberList(raw.topScores) } : {}),
    ...(raw.ms !== undefined ? { ms: raw.ms } : {}),
  };
}

function normalizeBudget(raw) {
  if (!isObject(raw)) invalid();
  const budget = {};
  for (const key of ['searchesUsed', 'searchesMax', 'modelCallsUsed', 'modelCallsMax', 'elapsedMs', 'elapsedMaxMs', 'inputBytesMax']) {
    if (raw[key] === undefined) continue;
    if (!isCount(raw[key])) invalid();
    budget[key] = raw[key];
  }
  return budget;
}

function normalizeMeasurement(raw) {
  if (!isObject(raw)) invalid();
  const entry = {};
  for (const key of ['seq', 'round', 'ms', 'modelCalls', 'searches', 'searchesCharged', 'selected', 'newCandidateItems', 'newExposedEvidence']) {
    if (raw[key] === undefined) continue;
    if (!isCount(raw[key])) invalid();
    entry[key] = raw[key];
  }
  const enums = {
    stage: ['understand', 'knowhow', 'sufficiency', 'synthesize', 'grounding', 'tech_search', 'law_search'],
    action: ['retry_search', 'doc_page'],
    outcome: ['progress', 'duplicate', 'no_new', 'no_budget'],
    evidenceValidity: ['unassessed'],
  };
  for (const [key, allowed] of Object.entries(enums)) {
    if (raw[key] === undefined) continue;
    if (!allowed.includes(raw[key])) invalid();
    entry[key] = raw[key];
  }
  for (const key of ['usageMissing', 'completed']) {
    if (raw[key] === undefined) continue;
    if (typeof raw[key] !== 'boolean') invalid();
    entry[key] = raw[key];
  }
  if (raw.usage !== undefined) {
    if (!isObject(raw.usage)) invalid();
    entry.usage = {};
    for (const key of ['inputTokens', 'outputTokens', 'cacheReadInputTokens', 'cacheWriteInputTokens']) {
      if (raw.usage[key] === undefined) continue;
      if (!isCount(raw.usage[key])) invalid();
      entry.usage[key] = raw.usage[key];
    }
  }
  return entry;
}

function normalizeDebugStrict(raw) {
  if (!isObject(raw)) invalid();
  const debug = {};
  if (raw.understandingRaw !== undefined) {
    if (!isObject(raw.understandingRaw)) invalid();
    debug.understandingRaw = cloneJson(raw.understandingRaw);
  }
  if (raw.queries !== undefined) {
    if (!isObject(raw.queries)) invalid();
    debug.queries = {
      tech: stringList(raw.queries.tech), law: stringList(raw.queries.law),
      ...(typeof raw.queries.knowhow === 'string' ? { knowhow: raw.queries.knowhow.slice(0, MAX_TEXT_LENGTH) } : {}),
    };
  }
  if (raw.tools !== undefined) debug.tools = list(raw.tools, normalizeTool);
  if (raw.budget !== undefined) debug.budget = normalizeBudget(raw.budget);
  if (raw.stages !== undefined) debug.stages = list(raw.stages, normalizeMeasurement);
  if (raw.progress !== undefined) debug.progress = list(raw.progress, normalizeMeasurement);
  if (raw.stopDetail != null) {
    if (!['repeated_query', 'repeated_results', 'no_exposed_progress', 'search_limit', 'model_limit', 'time_limit', 'input_limit'].includes(raw.stopDetail)) invalid();
    debug.stopDetail = raw.stopDetail;
  }
  if (raw.lastJudgment !== undefined) {
    if (!['sufficient', 'insufficient', 'unjudged'].includes(raw.lastJudgment)) invalid();
    debug.lastJudgment = raw.lastJudgment;
  }
  if (raw.grounding !== undefined) {
    if (!isObject(raw.grounding) || !['not_run', 'model_verified', 'extractive_fallback', 'rejected'].includes(raw.grounding.mode)) invalid();
    debug.grounding = { mode: raw.grounding.mode,
      ...(raw.grounding.articleMismatches ? { articleMismatches: stringList(raw.grounding.articleMismatches) } : {}),
      ...(Array.isArray(raw.grounding.guardReasons) ? { guardReasons: raw.grounding.guardReasons.filter(v => v === 'policy_explanation') } : {}) };
  }
  if (raw.coverage != null) {
    if (!isObject(raw.coverage)) invalid();
    debug.coverage = { missing: stringList(raw.coverage.missing), supported: list(raw.coverage.supported, (item) => {
      if (!isObject(item) || !/^A[1-4]$/u.test(item.id) || !['technical', 'legal'].includes(item.kind)
        || !['direct', 'reference'].includes(item.status) || !/^[TLK][0-9]{1,3}$/u.test(item.ref)) invalid();
      return { id: item.id, kind: item.kind, status: item.status, ref: item.ref };
    }) };
  }
  return debug;
}

/** デバッグ情報は補助なので、形式が違っても回答自体は壊さず捨てる。 */
function normalizeDebug(raw) {
  if (raw === undefined || raw === null) return undefined;
  try { return normalizeDebugStrict(raw); } catch { return undefined; }
}

function normalizeStatusResponse(data, expectedJobId) {
  if (!isObject(data) || data.jobId !== expectedJobId || !JOB_STATUSES.has(data.status)
    || !Array.isArray(data.steps) || data.steps.length > MAX_STEPS_PER_RESPONSE) invalid();
  if (data.pollAfterMs !== undefined && !(Number.isFinite(data.pollAfterMs) && data.pollAfterMs >= 0)) invalid();
  const steps = data.steps.map(normalizeStep);
  const out = {
    jobId: expectedJobId, status: data.status, steps,
    ...(data.pollAfterMs !== undefined ? { pollAfterMs: data.pollAfterMs } : {}),
  };
  if (data.status === 'completed') {
    out.result = normalizeSenpaiResearchResult(data.result);
    const debug = normalizeDebug(data.debug);
    if (debug) out.debug = debug;
  } else if (data.status === 'failed') {
    out.error = normalizeError(data.error);
    const debug = normalizeDebug(data.debug);
    if (debug) out.debug = debug;
  }
  return out;
}

function normalizeStartResponse(data) {
  if (!isObject(data) || typeof data.jobId !== 'string' || !UUID.test(data.jobId) || data.status !== 'queued') invalid();
  if (data.pollAfterMs !== undefined && !(Number.isFinite(data.pollAfterMs) && data.pollAfterMs >= 0)) invalid();
  return { jobId: data.jobId, status: 'queued', ...(data.pollAfterMs !== undefined ? { pollAfterMs: data.pollAfterMs } : {}) };
}

// ---- 通信 ----

function startStatusError(status) {
  if (status === 400) fail('validation', '質問や相談の識別情報を確認してください');
  if (status === 401) fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
  if (status === 403) fail('unavailable', '調査機能を現在利用できません（開発環境の管理者のみ使えます）');
  if (status === 409) fail('unavailable', 'すでに調査を実行中です。終わってから次の質問を送信してください', 409);
  if (status === 429) fail('server', '本日の調査回数の上限に達したか、混み合っています。時間をおいてお試しください', 429);
  if (status === 502) fail('server', '調査を開始できませんでした。時間をおいて再度お試しください', 502);
  if (status === 504) fail('timeout', MESSAGE_TIMEOUT);
  if (status >= 500) fail('server', '調査サービスでエラーが発生しました。時間をおいてお試しください', status);
  fail('unavailable', '調査機能を現在利用できません');
}

function pollStatusError(status) {
  if (status === 400) fail('validation', '調査の取得位置を確認してください');
  if (status === 401) fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください');
  if (status === 404) fail('unavailable', '調査の記録が見つかりません。保存期間を過ぎたか、別の利用者の調査です');
  if (status === 429) fail('server', '混み合っています。しばらくしてから確認します', 429);
  if (status === 504) fail('timeout', MESSAGE_TIMEOUT);
  if (status >= 500) fail('server', '調査の状況を確認できませんでした。時間をおいてお試しください', status);
  fail('unavailable', '調査機能を現在利用できません');
}

async function requestJson({ baseUrl, getToken, fetchImpl, signal, timeoutMs, method, path, body, statusError }) {
  const base = endpoint(baseUrl);
  if (typeof getToken !== 'function' || typeof fetchImpl !== 'function') fail('config', '認証または通信の設定を確認してください');
  if (signal?.aborted) fail('cancelled', MESSAGE_CANCELLED);
  const bounded = Number.isFinite(timeoutMs) && timeoutMs >= 1 ? Math.min(timeoutMs, MAX_TIMEOUT_MS) : DEFAULT_TIMEOUT_MS;

  const controller = new AbortController();
  let interruptionCode;
  let timeoutId;
  let onAbort;
  const interrupted = () => new KnowledgeResearchError(
    interruptionCode || 'cancelled', interruptionCode === 'timeout' ? MESSAGE_TIMEOUT : MESSAGE_CANCELLED,
  );
  const interruption = new Promise((_resolve, reject) => {
    onAbort = () => { interruptionCode = 'cancelled'; controller.abort(); reject(interrupted()); };
    signal?.addEventListener('abort', onAbort, { once: true });
    timeoutId = setTimeout(() => { interruptionCode = 'timeout'; controller.abort(); reject(interrupted()); }, bounded);
  });

  try {
    const operation = (async () => {
      let token;
      try { token = await getToken(); } catch { fail('auth', 'ログイン状態を確認できませんでした。再ログインしてください'); }
      if (typeof token !== 'string' || !token.trim()) fail('auth', 'ログインが必要です。ログイン後にもう一度お試しください');
      if (controller.signal.aborted) throw interrupted();
      let response;
      try {
        response = await fetchImpl(`${base}${path}`, {
          method,
          headers: { Authorization: `Bearer ${token}`, ...(body ? { 'Content-Type': 'application/json' } : {}) },
          ...(body ? { body: JSON.stringify(body) } : {}),
          signal: controller.signal,
        });
      } catch {
        if (controller.signal.aborted) throw interrupted();
        fail('server', '調査サービスに接続できませんでした。時間をおいてお試しください');
      }
      if (!response || typeof response.ok !== 'boolean') invalid();
      if (!response.ok) statusError(response.status);
      let data;
      try { data = await response.json(); } catch { invalid(); }
      return data;
    })();
    return await Promise.race([operation, interruption]);
  } catch (error) {
    if (error instanceof KnowledgeResearchError) throw error;
    if (controller.signal.aborted) throw interrupted();
    return fail('server', '調査に失敗しました。時間をおいてお試しください');
  } finally {
    clearTimeout(timeoutId);
    if (onAbort) signal?.removeEventListener('abort', onAbort);
  }
}

function validateModelType(modelType) {
  if (modelType === undefined) return undefined;
  const trimmed = typeof modelType === 'string' ? modelType.trim() : '';
  if (!trimmed || trimmed.length > 64 || /[\u0000-\u001f\u007f-\u009f]/u.test(trimmed)) fail('validation', '機種の指定を確認してください');
  return trimmed;
}

/**
 * 調査ジョブを開始する（POST /rag/senpai/research）。本文に利用者IDは入れない。
 * @param {{baseUrl:string, getToken:()=>Promise<string|null|undefined>, fetchImpl?:typeof fetch, question:string, modelType?:string, senpaiConversationId:string, senpaiTurnId:string, clientRequestId:string, signal?:AbortSignal, timeoutMs?:number}} options
 * @returns {Promise<{jobId:string, status:'queued', pollAfterMs?:number}>}
 */
export async function startSenpaiResearch({
  baseUrl, getToken, fetchImpl = fetch, question, modelType, senpaiConversationId, senpaiTurnId, clientRequestId, signal, timeoutMs,
}) {
  const trimmed = typeof question === 'string' ? question.trim() : '';
  if (!trimmed || Array.from(trimmed).length > MAX_QUESTION_LENGTH) fail('validation', '質問を入力してください（2,000文字以内）');
  const normalizedModel = validateModelType(modelType);
  if (![senpaiConversationId, senpaiTurnId, clientRequestId].every((id) => typeof id === 'string' && UUID.test(id))) {
    fail('validation', '相談の識別情報を確認してください');
  }
  const data = await requestJson({
    baseUrl, getToken, fetchImpl, signal, timeoutMs, method: 'POST', path: '/rag/senpai/research',
    body: {
      question: trimmed,
      ...(normalizedModel ? { modelType: normalizedModel } : {}),
      senpaiConversationId, senpaiTurnId, clientRequestId,
    },
    statusError: startStatusError,
  });
  return normalizeStartResponse(data);
}

/**
 * 調査の状況を取得する（GET /rag/senpai/research/{jobId}?afterSeq=）。
 * @param {{baseUrl:string, getToken:()=>Promise<string|null|undefined>, fetchImpl?:typeof fetch, jobId:string, afterSeq?:number, signal?:AbortSignal, timeoutMs?:number}} options
 */
export async function getSenpaiResearchStatus({ baseUrl, getToken, fetchImpl = fetch, jobId, afterSeq, signal, timeoutMs }) {
  if (typeof jobId !== 'string' || !UUID.test(jobId)) fail('validation', '調査の識別情報を確認してください');
  if (afterSeq !== undefined && !(Number.isSafeInteger(afterSeq) && afterSeq >= 0)) fail('validation', '調査の取得位置を確認してください');
  const data = await requestJson({
    baseUrl, getToken, fetchImpl, signal, timeoutMs, method: 'GET',
    path: `/rag/senpai/research/${jobId}${afterSeq !== undefined ? `?afterSeq=${afterSeq}` : ''}`,
    statusError: pollStatusError,
  });
  return normalizeStatusResponse(data, jobId);
}

// ---- 段階イベント ----

/**
 * 段階イベントを seq で追記する。既にある seq・古い seq は無視し、入力は変更しない。
 * @param {readonly object[] | undefined} current
 * @param {readonly object[] | undefined} incoming
 */
export function mergeResearchSteps(current, incoming) {
  const base = current ?? [];
  const known = new Set(base.map((item) => item.seq));
  const added = [];
  for (const item of incoming ?? []) {
    if (known.has(item.seq)) continue;
    known.add(item.seq);
    added.push(item);
  }
  if (added.length === 0) return [...base];
  return [...base, ...added].sort((a, b) => a.seq - b.seq);
}

/**
 * 画面用に、同じ (step, startedAt) のイベントを 1 行にまとめる。
 * バックエンドは実行中と完了/失敗を別の seq で追記し、seq が大きい方が最新。skipped は 1 件だけ。
 * 同じ step の再実行（再検索など）は startedAt が違うので別の行になる。
 * @param {readonly object[] | undefined} steps
 */
export function buildTimelineRows(steps) {
  const rows = new Map();
  for (const event of [...(steps ?? [])].sort((a, b) => a.seq - b.seq)) {
    const key = `${event.step}|${event.startedAt}`;
    const earlier = rows.get(key);
    rows.set(key, {
      key: `step-${key}`, seq: event.seq, step: event.step, labelJa: event.labelJa, status: event.status,
      ...((event.detailJa ?? earlier?.detailJa) ? { detailJa: event.detailJa ?? earlier.detailJa } : {}),
      ...((event.counts ?? earlier?.counts) ? { counts: event.counts ?? earlier.counts } : {}),
      startedAt: event.startedAt, endedAt: event.endedAt ?? null,
    });
  }
  return [...rows.values()];
}

// ---- 出典リンク ----

/** 技術資料の出典を既存の資料ページへのリンクにする。安全でない場合は undefined。 */
export function techSourceHref(source) {
  if (!isObject(source)) return undefined;
  return researchSourceHref({ sourceUri: source.sourceUri, pageNumber: source.pageNumber }, 'normal');
}

/**
 * 法令の出典は e-Gov（https://laws.e-gov.go.jp）のリンクだけ許す。
 * バックエンドの出典 URL は条文名などの日本語パスを含み得るので、パスの形は固定せずホストで限定する。
 */
export function lawSourceHref(source) {
  if (!isObject(source) || typeof source.sourceUrl !== 'string') return undefined;
  try {
    const url = new URL(source.sourceUrl);
    if (url.protocol !== 'https:' || url.hostname !== 'laws.e-gov.go.jp' || url.port || url.username || url.password) return undefined;
    return url.href;
  } catch {
    return undefined;
  }
}

// ---- 開始から完了までの実行 ----

const TRANSIENT_CODES = new Set(['server', 'timeout']);
const TERMINAL = new Set(['completed', 'failed']);

/**
 * 調査を開始し、完了・失敗・中止・打ち切りのいずれかまで確認し続ける。
 * 確認間隔は research-polling の規則（サーバーの pollAfterMs を優先、失敗が続けば倍にする）。
 * 通信の一時エラー（5xx / 429 / 時間切れ）は再試行し、認証・404・形式不正は即座に失敗にする。
 * `signal` が中止されると確認をやめる（サーバー側のジョブは止まらない）。
 *
 * @param {Parameters<typeof startSenpaiResearch>[0] & {
 *   onUpdate?: (update: {jobId:string, status:string, steps:object[]}) => void,
 *   now?: () => number, setTimer?: (fn: () => void, delayMs: number) => unknown, clearTimer?: (timer: unknown) => void,
 * }} options
 * @returns {Promise<{jobId:string, status:'completed'|'failed', steps:object[], result?:object, error?:object, debug?:object}>}
 */
/** 前の調査がサーバーで続いている間（409）、開始を待つ間隔と、待つ上限。 */
export const START_RETRY_INTERVAL_MS = 5_000;
export const START_RETRY_GIVE_UP_MS = 150_000;

const isJobInProgress = (error) => error?.status === 409 && error?.code === 'unavailable';

function sleepUnlessAborted({ ms, signal, setTimer, clearTimer }) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) { reject(new KnowledgeResearchError('cancelled', MESSAGE_CANCELLED)); return; }
    let timer;
    const onAbort = () => { clearTimer(timer); reject(new KnowledgeResearchError('cancelled', MESSAGE_CANCELLED)); };
    timer = setTimer(() => { signal?.removeEventListener('abort', onAbort); resolve(); }, ms);
    signal?.addEventListener('abort', onAbort, { once: true });
  });
}

/**
 * 開始する。前の調査がサーバーで続いていて 409 になったときは、中止できるまま
 * `intervalMs` ごとに開始をやり直す（合計 `giveUpMs` まで）。それ以外のエラーは待たずに投げる。
 */
async function startWithRetry(options, { onWaiting, now, setTimer, clearTimer, intervalMs, giveUpMs }) {
  const began = now();
  for (;;) {
    try {
      return await startSenpaiResearch(options);
    } catch (error) {
      if (!isJobInProgress(error) || now() - began + intervalMs > giveUpMs) throw error;
      onWaiting?.();
      await sleepUnlessAborted({ ms: intervalMs, signal: options.signal, setTimer, clearTimer });
    }
  }
}

export async function runSenpaiResearch({
  onUpdate, onWaiting, now = Date.now, setTimer = setTimeout, clearTimer = clearTimeout,
  retryIntervalMs = START_RETRY_INTERVAL_MS, retryGiveUpMs = START_RETRY_GIVE_UP_MS,
  visibility = globalThis.document, ...options
}) {
  const { signal } = options;
  const started = await startWithRetry(options, {
    onWaiting, now, setTimer, clearTimer, intervalMs: retryIntervalMs, giveUpMs: retryGiveUpMs,
  });
  const { jobId } = started;
  if (signal?.aborted) fail('cancelled', MESSAGE_CANCELLED);
  let steps = [];
  onUpdate?.({ jobId, status: 'queued', steps: [] });

  return new Promise((resolve, reject) => {
    let settled = false;
    let poller;
    const onAbort = () => finish(reject, new KnowledgeResearchError('cancelled', MESSAGE_CANCELLED));
    const isVisible = () => visibility?.visibilityState !== 'hidden';
    // タブが非表示の間は確認を止め、表示に戻ったら すぐ 1 回確認する（設計 §4.11）。
    const onVisibilityChange = () => poller?.setVisible(isVisible());
    function finish(settle, value) {
      if (settled) return;
      settled = true;
      visibility?.removeEventListener?.('visibilitychange', onVisibilityChange);
      poller?.stopAll();
      signal?.removeEventListener('abort', onAbort);
      settle(value);
    }
    poller = createJobPoller({
      fetchJob: async (id) => {
        try {
          return await getSenpaiResearchStatus({
            baseUrl: options.baseUrl, getToken: options.getToken, fetchImpl: options.fetchImpl, signal,
            timeoutMs: options.timeoutMs, jobId: id, afterSeq: steps.length ? steps.at(-1).seq : 0,
          });
        } catch (error) {
          if (!TRANSIENT_CODES.has(error?.code)) finish(reject, error);
          throw error;
        }
      },
      onUpdate: (id, update) => {
        steps = mergeResearchSteps(steps, update.steps);
        onUpdate?.({ jobId: id, status: update.status, steps: update.steps });
        if (TERMINAL.has(update.status)) {
          finish(resolve, {
            jobId: id, status: update.status, steps,
            ...(update.result ? { result: update.result } : {}),
            ...(update.error ? { error: update.error } : {}),
            ...(update.debug ? { debug: update.debug } : {}),
          });
        }
      },
      onGiveUp: () => finish(reject, new KnowledgeResearchError('timeout', MESSAGE_GAVE_UP)),
      now, setTimer, clearTimer,
    });
    signal?.addEventListener('abort', onAbort, { once: true });
    visibility?.addEventListener?.('visibilitychange', onVisibilityChange);
    poller.start(jobId, { visible: isVisible() });
  });
}
