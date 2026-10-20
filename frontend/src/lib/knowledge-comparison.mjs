import { buildResearchNote } from './knowledge-research.mjs';

const STATUS_LABELS = Object.freeze({
  consistent: '一致している',
  conditions_differ: '条件が違う',
  conflict: '食い違いあり',
  unresolved: '判断保留',
});
const MAX_FIELD_LENGTH = 4_000;

/** A rejected comparison input that is safe to show in the development UI. */
export class KnowledgeComparisonError extends Error {
  constructor(message) {
    super(message);
    this.name = 'KnowledgeComparisonError';
    this.code = 'validation';
  }
}

function reject(message) {
  throw new KnowledgeComparisonError(message);
}

function validateText(value, label, required) {
  if (typeof value !== 'string') reject(`${label}を文章で入力してください`);
  if (value.includes('\0')) reject(`${label}に使用できない文字が含まれています`);
  if (Array.from(value).length > MAX_FIELD_LENGTH) reject(`${label}は4,000文字以内で入力してください`);
  if (required && !value.trim()) reject(`${label}を入力してください`);
  return value;
}

function codeFence(value) {
  const runs = [...String(value).matchAll(/`+/g)].map((match) => match[0].length);
  return '`'.repeat(Math.max(3, ...runs.map((length) => length + 1)));
}

function asTextBlock(label, value) {
  const fence = codeFence(value);
  return [`#### ${label}`, '', `${fence}text`, value, fence].join('\n');
}

function validateAnswers(technical, law) {
  if (!technical || typeof technical !== 'object' || Array.isArray(technical)
    || technical.mode !== 'normal') {
    reject('通常モードの技術KB回答を指定してください');
  }
  if (!law || typeof law !== 'object' || Array.isArray(law) || law.mode !== 'law') {
    reject('法令モードの回答を指定してください');
  }
  if (typeof technical.query !== 'string' || !technical.query.trim()
    || typeof law.query !== 'string' || !law.query.trim()
    || technical.query !== law.query) {
    reject('同じ質問で検索した技術KBと法令KBの回答を指定してください');
  }
  let technicalNote;
  let lawNote;
  try {
    technicalNote = buildResearchNote(technical);
    lawNote = buildResearchNote(law);
  } catch {
    reject('技術KBと法令KBの両方に、根拠リンクを持つ回答が必要です');
  }
  return { technicalNote, lawNote };
}

function validateAssessment(assessment) {
  if (!assessment || typeof assessment !== 'object' || Array.isArray(assessment)) {
    reject('照合結果を入力してください');
  }
  const { status } = assessment;
  if (!Object.hasOwn(STATUS_LABELS, status)) reject('照合結果の状態を選択してください');
  const findings = validateText(assessment.findings, '比較して分かったこと', true);
  const applicability = validateText(assessment.applicability, '適用条件・対象外', true);
  const unresolvedRequired = status === 'conflict' || status === 'unresolved';
  const unresolvedPoints = assessment.unresolvedPoints === undefined && !unresolvedRequired
    ? ''
    : validateText(assessment.unresolvedPoints, '未確認事項・次に確認すること', unresolvedRequired);
  return { status, findings, applicability, unresolvedPoints };
}

/**
 * Compose a local, unapproved comparison note without changing either search answer.
 * Both answers must be successful, evidence-backed results for the same explicit query.
 * @param {{technical: import('./knowledge-research.mjs').ResearchAnswer, law: import('./knowledge-research.mjs').ResearchAnswer, assessment: import('./knowledge-comparison.mjs').KnowledgeComparisonAssessment}} input
 * @returns {string}
 */
export function buildComparisonNote(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    reject('照合に使う回答と担当者の入力を指定してください');
  }
  const { technicalNote, lawNote } = validateAnswers(input.technical, input.law);
  const assessment = validateAssessment(input.assessment);
  return [
    '### 技術KB・法令KBの照合まとめ（AI回答比較・未承認）',
    '',
    `- 担当者の整理: ${STATUS_LABELS[assessment.status]}`,
    '',
    asTextBlock('比較して分かったこと', assessment.findings),
    '',
    asTextBlock('適用条件・対象外', assessment.applicability),
    '',
    asTextBlock('未確認事項・次に確認すること', assessment.unresolvedPoints.trim() ? assessment.unresolvedPoints : '（未記入）'),
    '',
    '#### 技術KBの回答と出典（AI候補・未確認）',
    '',
    technicalNote,
    '',
    '#### 法令KBの回答と出典（AI候補・未確認）',
    '',
    lawNote,
  ].join('\n');
}
