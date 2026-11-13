// 書き換え案の応答を、サーバーを信用せずに検証して整える。外れた節は不採用として扱い、未知のキーは捨てる。
import { CHECK_DECISIONS, isPlaceholderText } from './knowhow-card-proposal.mjs';
import { REWRITE_LIMITS, charCount, findRewriteBodyProblem, isUnsafeDisplayText } from './knowhow-rewrite-sections.mjs';

const OPEN_ITEMS_HEADING = '未確認事項';
const MAX_SECTIONS = 10;
const MAX_CONFLICTS = 10;
const MAX_WARNINGS = 10;
const MAX_WARNING_VALUES = 10;
const MAX_VALUE_CHARS = 40;
const MAX_HEADING_SHOWN = 60;
/** 契約の警告コード（サーバーが返す）。 */
const SERVER_WARNING_CODES = Object.freeze(['unsupported_value', 'unverified_number', 'heading_in_body', 'missing_evidence', 'too_long']);
/** 付いていたら、変更ありのままにせず不採用にする警告（根拠のない値・構造を壊す本文）。 */
const BLOCKING_CODES = new Set(['unsupported_value', 'heading_in_body', 'missing_evidence', 'too_long', 'empty_body', 'suspicious_text', 'link_or_html', 'unclosed_fence']);
const KNOWN_CODES = new Set([...SERVER_WARNING_CODES, 'invalid_heading', 'invalid_evidence', 'invalid_status', 'invalid_body', 'invalid_reason', 'unspecified', 'empty_body', 'suspicious_text', 'link_or_html', 'unclosed_fence']);

const WARNING_TEXT = Object.freeze({
  unsupported_value: (values) => `根拠に見当たらない資料番号・数値${values.length ? `: ${values.join('、')}` : ''}`,
  unverified_number: (values) => `根拠に見当たらない数字${values.length ? `: ${values.join('、')}` : ''}`,
  heading_in_body: () => '本文に見出し行や区切り線が含まれています',
  missing_evidence: () => '使った根拠が示されていません',
  too_long: () => '本文が長すぎます',
  empty_body: () => '本文が空',
  suspicious_text: () => '見えない文字や制御文字が含まれている',
  link_or_html: () => '元の本文に無いリンクや HTML が含まれている',
  unclosed_fence: () => 'コードの囲みが閉じていない',
  invalid_heading: () => '送っていない節、または重複した節です',
  invalid_evidence: () => '根拠の番号が範囲外、または示されていません',
  invalid_status: () => '想定外の状態が返りました',
  invalid_body: () => '本文の形式が正しくありません',
  invalid_reason: () => '変更理由の形式が正しくありません',
  unspecified: () => '理由が示されていません',
  unknown: () => '理由は未対応の警告コード',
});

/**
 * 警告を日本語の1文にする。
 * @param {{ code: string, values?: readonly string[] }} warning
 */
export function describeRewriteWarning(warning) {
  const text = WARNING_TEXT[warning?.code] ?? WARNING_TEXT.unknown;
  return text(Array.isArray(warning?.values) ? warning.values : []);
}

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const normalizeLf = (text) => text.replace(/\r\n?/gu, '\n').trim();
const oneLine = (value) => String(value).replace(/\s+/gu, ' ').trim();

function warningValues(raw) {
  const list = Array.isArray(raw.tokens) ? raw.tokens : Array.isArray(raw.values) ? raw.values : typeof raw.detail === 'string' ? [raw.detail] : [];
  return list
    .filter((value) => typeof value === 'string' || Number.isFinite(value))
    .slice(0, MAX_WARNING_VALUES)
    .map((value) => oneLine(value).slice(0, MAX_VALUE_CHARS));
}

function normalizeWarnings(list) {
  if (!Array.isArray(list)) return [];
  return list.slice(0, MAX_WARNINGS).flatMap((raw) => {
    const item = typeof raw === 'string' ? { code: raw } : raw;
    if (!isObject(item) || typeof item.code !== 'string') return [];
    return [{ code: KNOWN_CODES.has(item.code) ? item.code : 'unknown', values: warningValues(item) }];
  });
}

function normalizeEvidence(list, count) {
  const valid = Array.isArray(list) && list.length > 0 && list.length <= count
    && list.every((number) => Number.isInteger(number) && number >= 1 && number <= count);
  return valid ? [...new Set(list)].sort((a, b) => a - b) : null;
}

const rejected = (heading, warnings) => ({
  heading, status: 'rejected', evidence: [], warnings: warnings.length ? warnings : [{ code: 'unspecified', values: [] }],
});
const flag = (code) => [{ code, values: [] }];

function checkChanged(raw, baseBody, count) {
  const evidence = normalizeEvidence(raw.evidence, count);
  if (evidence === null) return { problem: 'invalid_evidence' };
  const problem = findRewriteBodyProblem(raw.body, baseBody);
  if (problem) return { problem: problem === 'empty' ? 'invalid_body' : problem };
  if (typeof raw.reason !== 'string' || charCount(raw.reason) > REWRITE_LIMITS.reasonChars) return { problem: 'invalid_reason' };
  return { evidence };
}

function normalizeChanged(raw, baseBody, count) {
  const warnings = normalizeWarnings(raw.warnings);
  const blocking = warnings.filter((item) => BLOCKING_CODES.has(item.code));
  if (blocking.length) return rejected(raw.heading, blocking);
  const checked = checkChanged(raw, baseBody, count);
  if (checked.problem) return rejected(raw.heading, flag(checked.problem));
  const body = normalizeLf(raw.body);
  if (body === normalizeLf(baseBody)) return { heading: raw.heading, status: 'unchanged', evidence: [], warnings: [] };
  return { heading: raw.heading, status: 'changed', body, baseBody, reason: isUnsafeDisplayText(raw.reason) ? '' : raw.reason.trim(), evidence: checked.evidence, warnings };
}

function normalizeSection(raw, bases, seen, count) {
  const heading = isObject(raw) && typeof raw.heading === 'string' ? raw.heading : '';
  if (!bases.has(heading) || seen.has(heading)) return rejected(heading.slice(0, MAX_HEADING_SHOWN) || '（不明な節）', flag('invalid_heading'));
  seen.add(heading);
  if (raw.status === 'unchanged') return { heading, status: 'unchanged', evidence: [], warnings: [] };
  if (raw.status === 'rejected') return rejected(heading, normalizeWarnings(raw.warnings));
  if (raw.status === 'changed') return normalizeChanged(raw, bases.get(heading), count);
  return rejected(heading, flag('invalid_status'));
}

function normalizeConflicts(list, count) {
  if (!Array.isArray(list)) return [];
  return list.slice(0, MAX_CONFLICTS).flatMap((raw) => {
    const text = isObject(raw) ? raw.summary ?? raw.description : undefined;
    if (typeof text !== 'string') return [];
    const description = oneLine(text);
    const evidence = normalizeEvidence(raw.evidence, count);
    const heading = typeof raw.heading === 'string' && charCount(raw.heading) <= MAX_HEADING_SHOWN ? raw.heading : null;
    return description && !isUnsafeDisplayText(description) && charCount(description) <= REWRITE_LIMITS.reasonChars && evidence ? [{ heading, description, evidence }] : [];
  });
}

/**
 * 書き換え案の応答を検証して整える。
 * 全体の型・knowledgeId・cardVersion が合わなければ null。節ごとの不備はその節だけを不採用にする。
 * @param {unknown} data
 * @param {{ knowledgeId: string, cardVersion: number, targets: ReadonlyArray<{heading: string, body: string}>, evidence: readonly unknown[] }} request 送った要求
 */
export function normalizeRewriteResponse(data, request) {
  if (!isObject(data) || data.knowledgeId !== request.knowledgeId || data.cardVersion !== request.cardVersion
    || !Array.isArray(data.sections)) return null;
  const bases = new Map(request.targets.map(({ heading, body }) => [heading, body]));
  const seen = new Set();
  const count = request.evidence.length;
  return {
    knowledgeId: request.knowledgeId,
    cardVersion: request.cardVersion,
    bases: request.targets.map(({ heading, body }) => ({ heading, body })),
    sections: data.sections.slice(0, MAX_SECTIONS).map((raw) => normalizeSection(raw, bases, seen, count)),
    conflicts: normalizeConflicts(data.conflicts, count),
  };
}

/**
 * 食い違いを「未確認事項」へ足す1行（定型）にする。本文の主張を変える記述ではなく、要確認の記録。
 * @param {{ description: string }} conflict
 */
export function buildConflictOpenItem(conflict) {
  return `- 要確認（確認済みの根拠との食い違い）: ${oneLine(conflict.description)}`;
}

/**
 * 節ごとの確認結果を数える。未選択は未確認で、カードには入れない。
 * @param {ReadonlyArray<string>} headings 確認の対象にする節の見出し
 * @param {Readonly<Record<string, string | undefined>>} decisions
 */
export function summarizeRewriteDecisions(headings, decisions) {
  const count = (value) => headings.filter((heading) => decisions?.[heading] === value).length;
  const confirmed = count(CHECK_DECISIONS.confirm);
  const skipped = count(CHECK_DECISIONS.skip);
  return { total: headings.length, confirmed, skipped, pending: headings.length - confirmed - skipped };
}

function withOpenItems(baseBody, lines) {
  const kept = baseBody.split('\n').filter((line) => !isPlaceholderText(line.trim().replace(/^[-*+]\s+/u, '')) && line.trim() !== '');
  return [...kept, ...lines].join('\n');
}

/**
 * 管理者が「確認して反映する」を選んだ節と、「未確認事項に追加する」を選んだ食い違いから、カードへ入れる節の本文を作る。
 * 何も選んでいなければ空。食い違いは、書き換えた（または元の）「未確認事項」の末尾へ1行ずつ足す。
 * @param {{ sections: ReadonlyArray<any>, conflicts: ReadonlyArray<{description: string}>, bases: ReadonlyArray<{heading: string, body: string}> }} proposal
 * @param {Readonly<Record<string, string | undefined>>} decisions 節の見出し → 選択
 * @param {Readonly<Record<number, string | undefined>>} conflictDecisions 食い違いの番号 → 選択
 * @returns {Array<{ heading: string, body: string }>}
 */
export function buildAcceptedRewrites(proposal, decisions, conflictDecisions) {
  const accepted = new Map(proposal.sections
    .filter((section) => section.status === 'changed' && decisions?.[section.heading] === CHECK_DECISIONS.confirm)
    .map((section) => [section.heading, section.body]));
  const lines = proposal.conflicts
    .filter((_conflict, index) => conflictDecisions?.[index] === CHECK_DECISIONS.confirm)
    .map(buildConflictOpenItem);
  const base = proposal.bases.find(({ heading }) => heading === OPEN_ITEMS_HEADING);
  if (lines.length && base) accepted.set(OPEN_ITEMS_HEADING, withOpenItems(accepted.get(OPEN_ITEMS_HEADING) ?? base.body, lines));
  return [...accepted].map(([heading, body]) => ({ heading, body }));
}
