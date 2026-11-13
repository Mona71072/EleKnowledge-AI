// ノウハウカード1枚から、技術KB・法令KBへ照合する質問の候補を作る（純粋関数・AI なし）。
import { createFenceTracker, splitKnowhowCardBody } from './knowhow-card-view.mjs';
import {
  clampLine,
  comparisonKey,
  extractValueTokens,
  findLawTerms,
  hasManagementTerms,
  isDocumentNumber,
  stripManagementTerms,
  stripMarkdown,
} from './knowhow-card-check-text.mjs';

/** 1枚のカードから作る質問の上限。 */
export const MAX_CHECK_QUESTIONS = 6;
/** 質問の種類。並びが優先順（未確認事項 → 数値・基準 → 根拠 → 法令）。 */
export const CHECK_KINDS = Object.freeze(['open_item', 'value_check', 'basis', 'law']);
/** 種類ごとの既定の照合先。 */
export const CHECK_TARGETS_BY_KIND = Object.freeze({
  open_item: Object.freeze(['normal', 'law']),
  value_check: Object.freeze(['normal', 'law']),
  basis: Object.freeze(['normal']),
  law: Object.freeze(['law']),
  manual: Object.freeze(['normal', 'law']),
});
/** 種類の表示名。 */
export const CHECK_KIND_LABELS = Object.freeze({
  open_item: '未確認事項',
  value_check: '数値・基準',
  basis: '根拠資料',
  law: '法令',
  manual: '手入力',
});

// 種類ごとの上限。合計が全体の上限を超えたら、優先度の低い種類から落とす（根拠の1問は残す）。
const KIND_CAPS = Object.freeze({ open_item: 3, value_check: 2, basis: 1, law: 1 });
const MAX_MODEL_WORDS = 3;
const MAX_KEYWORDS = 3;
const MAX_TOKENS_PER_QUESTION = 4;
const MAX_LAW_TERMS_PER_QUESTION = 3;
const MAX_ITEM_CHARS = 120;
const MAX_MODEL_WORD_CHARS = 30;
const MIN_ITEM_CHARS = 4;
const MODEL_SCOPE_KEYS = Object.freeze([
  'model_abbreviations', 'control_methods', 'product_lines', 'lists_model_label', 'machine_room', 'observed_on',
]);
const SECTION = Object.freeze({
  scene: '使う場面',
  symptoms: '症状',
  answer: '統合した回答',
  steps: '調査・確認手順',
  open: '未確認事項',
});
const NOTHING = /^[（(]?\s*(?:特に)?(?:なし|無し|該当なし|未記載)\s*[）)]?[。.]?$/u;
// KB に聞いても答えが出ない、カードの管理作業そのものの項目。
const ADMIN_ONLY = /情報管理|保留|転載|索引|未実装|取り込み名|duplicate|添付|未レビュー|pending|frontmatter|カード|[a-z]+_[a-z]+/iu;
const LIST_MARKER = /^\s*(?:[-*+]|\d+[.)])\s+/u;
const DASH = /\s*[—–]\s*/u;

const asList = (value) => (Array.isArray(value) ? value : value === undefined || value === null ? [] : [value])
  .filter((item) => typeof item === 'string' && item.trim());

/** 本文を、コードフェンスの外の行だけの節に分ける。 */
function readSections(body) {
  const isFenced = createFenceTracker();
  const plain = (typeof body === 'string' ? body : '').replace(/\r\n?/gu, '\n').split('\n')
    .filter((line) => !isFenced(line)).join('\n');
  const { title, readerSections, editorSections } = splitKnowhowCardBody(plain);
  const sections = [...readerSections, ...editorSections];
  const find = (keyword) => sections.find((section) => section.heading.includes(keyword));
  return { title, find };
}

const contentLines = (section) => (section ? section.body.split('\n') : [])
  .map((line) => clampLine(line.trim()))
  .filter((line) => line && !line.startsWith('|') && !/^#{1,6}\s/u.test(line));

const listItems = (section) => contentLines(section).map((line) => line.replace(LIST_MARKER, '').trim()).filter(Boolean);

const sentences = (section) => contentLines(section)
  .flatMap((line) => line.replace(LIST_MARKER, '').split('。'))
  .map((sentence) => sentence.trim())
  .filter(Boolean);

/** Return the bounded model terms used to scope card research. */
export function checkModelWords(frontmatter) {
  const scope = frontmatter?.model_scope && typeof frontmatter.model_scope === 'object' ? frontmatter.model_scope : {};
  const words = MODEL_SCOPE_KEYS.flatMap((key) => asList(scope[key]))
    .map((word) => stripManagementTerms(stripMarkdown(word)).replace(/機種$/u, ''))
    .filter((word) => word && !word.startsWith('全') && Array.from(word).length <= MAX_MODEL_WORD_CHARS);
  return words
    .filter((word, index) => words.findIndex((other) => other.toLowerCase() === word.toLowerCase()) === index)
    .slice(0, MAX_MODEL_WORDS);
}

function keywords(frontmatter, topic, models) {
  const taken = [topic, ...models].map((text) => text.toLowerCase());
  return asList(frontmatter?.symptoms)
    .map((word) => stripManagementTerms(stripMarkdown(word)))
    .filter((word) => word && !taken.some((text) => text.includes(word.toLowerCase())))
    .slice(0, MAX_KEYWORDS);
}

/** 未確認事項の1行を、KB に聞ける形に掃除する。聞けない項目は null。 */
function cleanOpenItem(raw) {
  if (/`[^`]*[a-z]_[a-z][^`]*`/u.test(raw)) return null;
  const text = stripMarkdown(raw);
  const segments = text.split(DASH);
  const kept = segments.length > 1 ? segments.filter((segment) => !hasManagementTerms(segment)) : segments;
  const cleaned = stripManagementTerms(kept.join('、')).replace(/[。.]+$/u, '').trim();
  if (!cleaned || NOTHING.test(cleaned) || ADMIN_ONLY.test(text) || Array.from(cleaned).length < MIN_ITEM_CHARS) return null;
  return Array.from(cleaned).slice(0, MAX_ITEM_CHARS).join('');
}

function openItemCandidates(context) {
  const section = context.sections.find(SECTION.open);
  const items = listItems(section).flatMap((raw) => {
    const item = cleanOpenItem(raw);
    return item ? [{ raw, item, key: comparisonKey(item) }] : [];
  });
  return items
    .filter((entry, index) => !items.slice(0, index).some((earlier) => earlier.key.includes(entry.key) || entry.key.includes(earlier.key)))
    .map((entry) => ({
      kind: 'open_item',
      text: `「${context.topic}」${context.scope}に関して、「${entry.item}」を確認できる資料や記載はありますか。`,
      sourceSection: section.heading,
      sourceText: entry.raw,
    }));
}

function valueCandidates(context) {
  const sources = [SECTION.answer, SECTION.steps].flatMap((keyword) => {
    const section = context.sections.find(keyword);
    return sentences(section).map((raw) => ({ raw, heading: section.heading, tokens: extractValueTokens(stripManagementTerms(stripMarkdown(raw))) }));
  }).filter((source) => source.tokens.length > 0);
  const hasDocument = (source) => source.tokens.some(isDocumentNumber);
  const ordered = [...sources.filter(hasDocument), ...sources.filter((source) => !hasDocument(source))];
  return ordered.reduce((picked, source) => {
    const seen = new Set(picked.flatMap((item) => item.tokens));
    return source.tokens.every((token) => seen.has(token)) ? picked : [...picked, source];
  }, []).map((source) => ({
    kind: 'value_check',
    text: valueQuestion(context, source.tokens.slice(0, MAX_TOKENS_PER_QUESTION)),
    sourceSection: source.heading,
    sourceText: source.raw,
  }));
}

/** 資料番号だけなら資料の記載を、数値が混ざるなら数値・基準の定めを聞く。 */
function valueQuestion(context, tokens) {
  const subject = `「${context.topic}」${context.scope}について、`;
  return tokens.every(isDocumentNumber)
    ? `${subject}資料 ${tokens.join('・')} にはどのように記載されていますか。`
    : `${subject}${tokens.join('・')} に関する数値・基準は、正式資料でどのように定められていますか。`;
}

function basisCandidates(context) {
  const words = keywords(context.frontmatter, context.topic, context.models);
  const parts = [
    ...(context.models.length > 0 ? [`機種: ${context.models.join('・')}`] : []),
    ...(words.length > 0 ? [`関連語: ${words.join('・')}`] : []),
  ];
  return [{
    kind: 'basis',
    text: `「${context.topic}」${parts.length > 0 ? `（${parts.join('／')}）` : ''}の根拠になる正式資料・基準はありますか。`,
    sourceSection: '題名',
    sourceText: context.topic,
  }];
}

/** frontmatter の source_refs に書かれた法令名（法令 RAG の参照）。 */
function lawTitles(frontmatter) {
  const refs = Array.isArray(frontmatter?.source_refs) ? frontmatter.source_refs : [];
  return refs
    .filter((ref) => ref && typeof ref === 'object' && ref.ref_type === 'law_rag' && typeof ref.law_title === 'string')
    .map((ref) => stripManagementTerms(stripMarkdown(ref.law_title)))
    .filter(Boolean);
}

function lawCandidates(context) {
  const fromSections = [SECTION.scene, SECTION.symptoms, SECTION.answer, SECTION.steps, SECTION.open].flatMap((keyword) => {
    const section = context.sections.find(keyword);
    return contentLines(section).map((raw) => ({ raw, heading: section.heading }));
  });
  const lines = [
    ...fromSections,
    { raw: context.topic, heading: '題名' },
    ...asList(context.frontmatter?.symptoms).map((raw) => ({ raw, heading: 'symptoms' })),
  ].map((line) => ({ ...line, terms: findLawTerms(line.raw) })).filter((line) => line.terms.length > 0);
  if (lines.length === 0) return [];
  const terms = [...new Set([...lawTitles(context.frontmatter), ...lines.flatMap((line) => line.terms)])]
    .slice(0, MAX_LAW_TERMS_PER_QUESTION);
  return [{
    kind: 'law',
    text: `「${context.topic}」${context.scope}に関して、${terms.join('・')} の観点で、法令上必要な要件や手続きはありますか。`,
    sourceSection: lines[0].heading,
    sourceText: lines[0].raw.replace(LIST_MARKER, ''),
  }];
}

/** 種類ごとの上限と全体の上限を当てはめる。根拠の1問は必ず残す。 */
function applyLimits(candidates, limit) {
  const capped = CHECK_KINDS.flatMap((kind) => candidates.filter((item) => item.kind === kind).slice(0, KIND_CAPS[kind]));
  if (capped.length <= limit) return capped;
  const others = capped.filter((item) => item.kind !== 'basis').slice(0, Math.max(0, limit - 1));
  const kept = new Set([...others, ...capped.filter((item) => item.kind === 'basis')].slice(0, Math.max(0, limit)));
  return capped.filter((item) => kept.has(item));
}

/**
 * カードの frontmatter と本文から、照合用の質問の候補を作る。
 * 質問文には題名・機種・対象の語を入れ、管理用の呼び名（Lists 399、§399、ノウハウID、OneNote）は入れない。
 * @param {{ frontmatter: Record<string, unknown> | null | undefined, body: unknown, limit?: number }} card
 * @returns {Array<{ id: string, kind: 'open_item'|'value_check'|'basis'|'law', text: string, targets: Array<'normal'|'law'>, sourceSection: string, sourceText: string, selected: boolean }>}
 */
export function buildCheckQuestions({ frontmatter, body, limit = MAX_CHECK_QUESTIONS }) {
  if (!Number.isInteger(limit) || limit < 1 || limit > MAX_CHECK_QUESTIONS) {
    throw new TypeError(`質問数の上限は1〜${MAX_CHECK_QUESTIONS}の整数で指定してください。`);
  }
  const sections = readSections(body);
  const rawTitle = typeof frontmatter?.title === 'string' && frontmatter.title.trim() ? frontmatter.title : sections.title;
  const topic = stripManagementTerms(stripMarkdown(rawTitle));
  if (!topic) return [];
  const models = checkModelWords(frontmatter);
  const context = { frontmatter, sections, topic, models, scope: models.length > 0 ? `（機種: ${models.join('・')}）` : '' };
  const candidates = [openItemCandidates, valueCandidates, basisCandidates, lawCandidates].flatMap((build) => build(context));
  const counters = new Map();
  return applyLimits(candidates, limit).map((candidate) => {
    const number = (counters.get(candidate.kind) ?? 0) + 1;
    counters.set(candidate.kind, number);
    return { id: `${candidate.kind}-${number}`, ...candidate, targets: [...CHECK_TARGETS_BY_KIND[candidate.kind]], selected: true };
  });
}

/**
 * 手で足す質問を作る。既存の質問と ID が重ならないようにする。
 * @param {ReadonlyArray<{ id: string }>} existing
 * @param {string} text
 */
export function createManualQuestion(existing, text) {
  const numbers = existing.map((question) => /^manual-(\d+)$/u.exec(question.id)).filter(Boolean).map((match) => Number(match[1]));
  return {
    id: `manual-${Math.max(0, ...numbers) + 1}`,
    kind: 'manual',
    text: String(text ?? '').trim(),
    targets: [...CHECK_TARGETS_BY_KIND.manual],
    sourceSection: '',
    sourceText: '',
    selected: true,
  };
}

/**
 * 実行前に、API を呼ぶ回数を数える（選択済みで、文が空でない質問だけ）。
 * @param {ReadonlyArray<{ selected: boolean, text: string, targets: ReadonlyArray<string> }>} questions
 * @returns {{ questions: number, normal: number, law: number, total: number }}
 */
export function countCheckCalls(questions) {
  const active = questions.filter((question) => question.selected && question.text.trim() && question.targets.length > 0);
  const normal = active.filter((question) => question.targets.includes('normal')).length;
  const law = active.filter((question) => question.targets.includes('law')).length;
  return { questions: active.length, normal, law, total: normal + law };
}
