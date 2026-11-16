// 書き換え案の API 要求を作る。材料は「管理者が確認して追記すると決めた、出典つきの照合結果」だけ。
// 未確認・追記しない・出典なしの結果、frontmatter、カード全文は送らない。
import { CHECK_DECISIONS, answerHead, classifyCheckAnswer, formatCheckDate } from './knowhow-card-proposal.mjs';
import { researchSourceHref } from './knowledge-research.mjs';
import { REWRITE_LIMITS, selectRewriteSections } from './knowhow-rewrite-sections.mjs';

/**
 * 書き換え案の機能を出すか。環境変数が文字列の `true` のときだけ。
 * 呼び出し側は `process.env.NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE` をそのまま渡す（Next.js が埋め込めるように）。
 * @param {unknown} value
 */
export function isRewriteEnabled(value) {
  return value === 'true';
}

const LANES = Object.freeze([
  Object.freeze({ mode: 'normal', lane: 'technical' }),
  Object.freeze({ mode: 'law', lane: 'law' }),
]);
const MIN_PAGE = 1;
const MAX_PAGE = 9999;
const oneLine = (value) => String(value ?? '').replace(/\s+/gu, ' ').trim();
const clip = (text, chars) => Array.from(text).slice(0, chars).join('');

function sourceTitle(source) {
  const law = source?.lawCitation;
  const text = law && typeof law.lawTitle === 'string'
    ? [law.lawTitle, law.provisionReference].filter(Boolean).join(' ')
    : source?.documentName || source?.title;
  return clip(oneLine(text) || '出典', REWRITE_LIMITS.sourceTitleChars);
}

function safeHref(source, mode) {
  try {
    return researchSourceHref(source, mode);
  } catch {
    return undefined;
  }
}

function pickSources(answer, mode) {
  const seen = new Set();
  const picked = [];
  for (const source of answer.sourceDocuments ?? []) {
    if (!safeHref(source, mode)) continue;
    const page = Number.isSafeInteger(source?.pageNumber) && source.pageNumber >= MIN_PAGE && source.pageNumber <= MAX_PAGE
      ? { page: source.pageNumber } : {};
    const entry = { title: sourceTitle(source), ...page };
    const key = `${entry.title}\n${entry.page ?? ''}`;
    if (!seen.has(key)) {
      seen.add(key);
      picked.push(entry);
    }
  }
  return picked.slice(0, REWRITE_LIMITS.sourcesMax);
}

/** 質問の確認日。追記案と同じく、返ってきた応答のうち最も遅い受信日。作れなければ null。 */
function checkedOnOf(tasks) {
  const latest = tasks.map((item) => item.result.receivedAt).sort().at(-1);
  const date = new Date(latest ?? '');
  return Number.isNaN(date.getTime()) ? null : formatCheckDate(date);
}

/**
 * 書き換えの材料になる根拠を集める。
 * 「確認して追記する」を選んだ質問のうち、全ての照合先が返っていて、出典つきの回答を返した照合先だけ。
 * @param {{ questions: ReadonlyArray<{id: string, text: string, targets: readonly string[]}>, tasks: ReadonlyArray<{questionId: string, mode: string, result?: any}>, decisions: Readonly<Record<string, string | undefined>> }} input
 * @returns {Array<{ questionId: string, question: string, lane: 'technical'|'law', checkedOn: string, answer: string, sources: Array<{title: string, page?: number}> }>}
 */
export function buildRewriteEvidence({ questions, tasks, decisions }) {
  return questions.flatMap((question) => {
    if (decisions?.[question.id] !== CHECK_DECISIONS.confirm) return [];
    const own = tasks.filter((item) => item.questionId === question.id);
    if (!own.length || own.length !== question.targets.length || own.some((item) => !item.result)) return [];
    const checkedOn = checkedOnOf(own);
    if (!checkedOn) return [];
    return LANES.flatMap(({ mode, lane }) => {
      const answer = own.find((item) => item.mode === mode)?.result;
      if (!answer || classifyCheckAnswer(answer) !== 'found') return [];
      const sources = pickSources(answer, mode);
      if (!sources.length) return [];
      return [{
        questionId: question.id,
        question: clip(oneLine(question.text), REWRITE_LIMITS.questionChars),
        lane,
        checkedOn,
        answer: clip(answerHead(answer.content), REWRITE_LIMITS.answerChars),
        sources,
      }];
    });
  });
}

function cardIdentity(frontmatter) {
  const id = frontmatter?.knowledge_id;
  const raw = frontmatter?.card_version;
  const version = typeof raw === 'string' && /^\d{1,4}$/u.test(raw) ? Number(raw) : raw;
  return {
    knowledgeId: typeof id === 'string' && REWRITE_LIMITS.knowledgeIdPattern.test(id) ? id : null,
    cardVersion: Number.isInteger(version) && version >= 1 && version <= REWRITE_LIMITS.cardVersionMax ? version : null,
  };
}

const BLOCKERS = Object.freeze({
  knowledgeId: 'このカードの knowledge_id を確認できないため作れません。',
  cardVersion: 'このカードの card_version を確認できないため作れません。',
  evidence: '出典つきの確認済みが無いため作れません。',
  targets: '書き換えの対象の節がカードに無いため作れません。',
});

/**
 * AI に送る要求を作る。作れないときは request が null で、blocker に短い理由を入れる。
 * 根拠が上限（12件）を超えたら先頭から12件だけを送り、省いた件数を返す。
 * @param {{ frontmatter: Record<string, unknown> | null | undefined, body: string, evidence: ReadonlyArray<ReturnType<typeof buildRewriteEvidence>[number]> }} input
 */
export function buildRewriteRequest({ frontmatter, body, evidence }) {
  const { knowledgeId, cardVersion } = cardIdentity(frontmatter);
  const { targets, context, excluded } = selectRewriteSections(body);
  const used = evidence.slice(0, REWRITE_LIMITS.evidenceMax);
  const blocker = knowledgeId === null ? BLOCKERS.knowledgeId
    : cardVersion === null ? BLOCKERS.cardVersion
      : used.length === 0 ? BLOCKERS.evidence
        : targets.length === 0 ? BLOCKERS.targets : '';
  return {
    request: blocker ? null : {
      knowledgeId,
      cardVersion,
      targets,
      context,
      evidence: used.map(({ question, lane, checkedOn, answer, sources }) => ({ question, lane, checkedOn, answer, sources })),
    },
    evidenceRefs: used.map(({ questionId, question }, index) => ({ number: index + 1, questionId, question })),
    evidenceOmitted: evidence.length - used.length,
    excluded,
    blocker,
  };
}

/** Build one excerpt-only request. The routing envelope contains no actual card identity. */
export function buildFieldRewriteRequest({ topic = '', title, excerpt, checkedOn }) {
  if (typeof excerpt !== 'string' || !excerpt.trim() || Array.from(excerpt).length > REWRITE_LIMITS.answerChars
    || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f\ud800-\udfff]/u.test(excerpt)) {
    throw new TypeError('AIに送る抜粋を2,000文字以内で選んでください。');
  }
  const sourceTitle = oneLine(title);
  const question = oneLine(topic) || '現場資料の適用条件と確認手順を整理する';
  if (!sourceTitle || Array.from(sourceTitle).length > REWRITE_LIMITS.sourceTitleChars) throw new TypeError('資料名を200文字以内で入力してください。');
  if (Array.from(question).length > REWRITE_LIMITS.questionChars) throw new TypeError('確認テーマを2,000文字以内で入力してください。');
  const timestamp = Date.parse(checkedOn);
  if (!/^\d{4}-\d{2}-\d{2}$/u.test(checkedOn) || !Number.isFinite(timestamp)
    || new Date(timestamp).toISOString().slice(0, 10) !== checkedOn) throw new TypeError('確認日の日付が正しくありません。');
  return {
    knowledgeId: 'KH-FIELD-MATERIAL',
    cardVersion: 1,
    targets: [{ heading: '統合した回答・ノウハウ', body: '' }],
    context: [],
    evidence: [{ question, lane: 'field', checkedOn, answer: excerpt, sources: [{ title: sourceTitle }] }],
  };
}
