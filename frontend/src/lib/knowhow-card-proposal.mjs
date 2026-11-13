// 一括照合の結果から定型の追記案を作り、管理者が確認したものだけをカードの「KB確認に基づく追記」へ差し込む。
// 未確認・追記しないものはカードに入れない。AI に要約させない。本文の主張の節と frontmatter は書き換えない。
import { createFenceTracker, parseH2Heading } from './knowhow-card-view.mjs';
import { parseKnowledgeFrontmatter } from './knowledge-markdown-frontmatter.mjs';
import { researchSourceHref } from './knowledge-research.mjs';

/** 追記案に載せる回答の先頭部分の最大文字数。 */
export const PROPOSAL_ANSWER_HEAD_CHARS = 400;
/** 追記案に載せる出典の最大件数。 */
export const PROPOSAL_MAX_SOURCES = 8;

const MIN_HEAD_CHARS = PROPOSAL_ANSWER_HEAD_CHARS / 2;
const CONFIRMED_KB_LABEL = 'KB確認に基づく追記';
const CONFIRMED_KB_HEADING_TEXT = `## ${CONFIRMED_KB_LABEL}`;
/** 旧版が作った未確認メモ節。新規には作らず、同じ追記の二重防止にだけ読む。 */
const LEGACY_REVIEW_MEMO_LABEL = 'KB照合メモ（原資料未確認）';
const FORMAL_LABEL = '正式資料';
const PROPOSAL_HEADING = /^###\s+KB照合（確認日\s+(\d{4}-\d{2}-\d{2})）\s*$/u;
const QUESTION_LINE = /^-\s+質問:\s*(.*)$/u;
const DATE = /^\d{4}-\d{2}-\d{2}$/u;
const PLACEHOLDER_PARTS = new Set(['該当なし', 'なし', '該当kbなし', 'listsのみ', '未実施']);
const PLACEHOLDER_WRAPPED = /^[（(]\s*(.*?)\s*[）)]$/u;
const PLACEHOLDER_SEPARATOR = /\s*[—–―-]+\s*/u;
const LANES = Object.freeze([
  Object.freeze({ key: 'technical', mode: 'normal', label: '技術KB' }),
  Object.freeze({ key: 'law', mode: 'law', label: '法令KB' }),
]);

function reject(message) {
  throw new TypeError(message);
}

function isCalendarDate(value) {
  if (typeof value !== 'string' || !DATE.test(value)) return false;
  const timestamp = Date.parse(`${value}T00:00:00.000Z`);
  return Number.isFinite(timestamp) && new Date(timestamp).toISOString().slice(0, 10) === value;
}

const oneLine = (value) => String(value ?? '').replace(/\s+/gu, ' ').trim();

function escapeMarkdown(value) {
  return oneLine(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replace(/([\\`*_{}\[\]()#+\-.!|~])/gu, '\\$1');
}

function unescapeMarkdown(value) {
  return value
    .replace(/\\([\\`*_{}\[\]()#+\-.!|~])/gu, '$1')
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>')
    .replaceAll('&amp;', '&');
}

function fenceFor(value) {
  const runs = [...String(value).matchAll(/`+/gu)].map((match) => match[0].length);
  return '`'.repeat(Math.max(3, ...runs.map((length) => length + 1)));
}

function inlineCode(value) {
  const text = oneLine(value);
  const runs = [...text.matchAll(/`+/gu)].map((match) => match[0].length);
  if (runs.length === 0) return `\`${text}\``;
  const mark = '`'.repeat(Math.max(...runs) + 1);
  return `${mark} ${text} ${mark}`;
}

/** 確認日（手元の日付）を `YYYY-MM-DD` にする。 */
export function formatCheckDate(date) {
  const pad = (value) => String(value).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/**
 * RAG の応答が「見つからなかった」かを判定する。応答の `responseType` を優先し、
 * 回答はあっても出典が 0 件のものは根拠なしとして扱う。
 * @param {import('./knowledge-research.mjs').ResearchAnswer | null | undefined} answer
 * @returns {'found' | 'not_found' | 'clarify' | 'no_source'}
 */
export function classifyCheckAnswer(answer) {
  if (!answer || typeof answer !== 'object' || answer.responseType === 'not_found') return 'not_found';
  if (answer.responseType === 'clarify') return 'clarify';
  const hasContent = typeof answer.content === 'string' && answer.content.trim().length > 0;
  const hasSource = Array.isArray(answer.sourceDocuments)
    && answer.sourceDocuments.some((source) => Boolean(researchSourceHref(source, answer.mode)));
  return hasContent && hasSource ? 'found' : 'no_source';
}

/** 回答の先頭部分を、文の切れ目で切る（要約はしない）。 */
function answerHead(content) {
  const chars = Array.from(content.trim());
  if (chars.length <= PROPOSAL_ANSWER_HEAD_CHARS) return chars.join('');
  const head = chars.slice(0, PROPOSAL_ANSWER_HEAD_CHARS).join('');
  const cut = Math.max(head.lastIndexOf('。'), head.lastIndexOf('\n'));
  const kept = cut >= MIN_HEAD_CHARS ? head.slice(0, cut + 1).trimEnd() : head;
  return `${kept}\n…（以下略）`;
}

function sourceLine(source, mode, index) {
  const law = source?.lawCitation;
  if (law && typeof law.lawTitle === 'string') {
    const href = researchSourceHref(source, mode);
    if (!href) return null;
    const provision = law.provisionReference ? ` ${escapeMarkdown(law.provisionReference)}` : '';
    return `- ${escapeMarkdown(law.lawTitle)}（${escapeMarkdown(law.lawNumber)}）${provision} — [公式法令](${href})`;
  }
  if (!researchSourceHref(source, mode)) return null;
  const name = oneLine(source?.documentName || source?.title) || `出典 ${index + 1}`;
  const page = Number.isSafeInteger(source?.pageNumber) && source.pageNumber > 0 ? ` p.${source.pageNumber}` : '';
  return `- ${inlineCode(name)}${page}`;
}

function laneBlock(lane, answer) {
  const heading = `#### ${lane.label}の要点`;
  if (answer === undefined) return [heading, '', 'この質問では照合していません。'];
  const outcome = classifyCheckAnswer(answer);
  if (outcome === 'not_found') return [heading, '', `${lane.label}に該当資料なし（確認日時点）。未確認事項の解消ではなく、確認した記録です。`];
  if (outcome === 'clarify') return [heading, '', `${lane.label}は条件の聞き返しを返し、回答は得られませんでした。`];
  if (outcome === 'no_source') return [heading, '', `${lane.label}は回答を返しましたが、出典がありません。根拠としては扱えません。`];
  const head = answerHead(answer.content);
  const fence = fenceFor(head);
  const sources = [...new Set(answer.sourceDocuments.map((source, index) => sourceLine(source, lane.mode, index)).filter(Boolean))]
    .slice(0, PROPOSAL_MAX_SOURCES);
  if (sources.length === 0) return [heading, '', `${lane.label}は回答を返しましたが、有効な出典を確認できません。根拠としては扱えません。`];
  return [heading, '', `${fence}text`, head, fence, '', `#### ${lane.label}の出典`, '', ...sources];
}

/**
 * 追記案が出典つきか、出典の無い確認の記録かを返す。
 * - `sourced`: どちらかの照合先が有効な出典を伴う回答を返した。
 * - `not_found`: 照合した全ての照合先が「該当なし」を返した（「KB に該当資料なし」と書いてよいのはこの場合だけ）。
 * - `no_source`: 上記以外の出典なし。聞き返しや、出典のない回答を含む。
 * @param {{ technical?: import('./knowledge-research.mjs').ResearchAnswer, law?: import('./knowledge-research.mjs').ResearchAnswer }} input
 * @returns {'sourced' | 'not_found' | 'no_source'}
 */
export function classifyProposalEvidence(input) {
  const outcomes = LANES.filter((lane) => input?.[lane.key] !== undefined).map((lane) => classifyCheckAnswer(input[lane.key]));
  if (outcomes.includes('found')) return 'sourced';
  return outcomes.length > 0 && outcomes.every((outcome) => outcome === 'not_found') ? 'not_found' : 'no_source';
}

const CONFIRMATION_NOTE = '管理者が確認した記録で、未確認事項の解消ではありません';

function confirmationLine(input) {
  const evidence = classifyProposalEvidence(input);
  if (evidence === 'sourced') return `- 確認: 管理者が出典を確認（${input.checkedOn}）`;
  if (evidence === 'not_found') return `- 確認: KB に該当資料なし（${input.checkedOn}）。${CONFIRMATION_NOTE}`;
  return `- 確認: 根拠になる出典が見つからなかった（聞き返し・出典なしの回答を含む）（${input.checkedOn}）。${CONFIRMATION_NOTE}`;
}

/**
 * 1つの質問の照合結果から、定型の追記案（Markdown）を作る。
 * 照合していない側は `undefined` を渡す。
 * @param {{ question: string, technical?: import('./knowledge-research.mjs').ResearchAnswer, law?: import('./knowledge-research.mjs').ResearchAnswer, checkedOn: string }} input
 * @returns {string}
 */
export function buildCheckProposal(input) {
  const question = oneLine(input?.question);
  if (!question) reject('質問を指定してください。');
  if (!isCalendarDate(input.checkedOn)) reject('確認日は実在する日付を YYYY-MM-DD で指定してください。');
  if (input.technical === undefined && input.law === undefined) reject('技術KBか法令KBの照合結果が必要です。');
  for (const lane of LANES) {
    const answer = input[lane.key];
    if (answer !== undefined && answer?.mode !== lane.mode) reject(`${lane.label}の照合結果を指定してください。`);
  }
  return [
    `### KB照合（確認日 ${input.checkedOn}）`,
    '',
    `- 質問: ${escapeMarkdown(question)}`,
    confirmationLine(input),
    ...LANES.flatMap((lane) => ['', ...laneBlock(lane, input[lane.key])]),
  ].join('\n');
}

/** 管理者の確認結果。未選択は「未確認」で、カードには入れない。 */
export const CHECK_DECISIONS = Object.freeze({ confirm: 'confirm', skip: 'skip' });

/**
 * 追記案ごとの確認結果を数える。未確認はまだ選んでいないもの。
 * @param {ReadonlyArray<string>} questionIds 追記案がある質問の ID
 * @param {Readonly<Record<string, string>>} decisions
 * @returns {{ total: number, confirmed: number, skipped: number, pending: number }}
 */
export function summarizeCheckDecisions(questionIds, decisions) {
  const count = (value) => questionIds.filter((id) => decisions?.[id] === value).length;
  const confirmed = count(CHECK_DECISIONS.confirm);
  const skipped = count(CHECK_DECISIONS.skip);
  return { total: questionIds.length, confirmed, skipped, pending: questionIds.length - confirmed - skipped };
}

const proposalKey = (checkedOn, question) => `${checkedOn}\n${oneLine(question)}`;

/** 先頭の `---` から閉じの `---` までが妥当な YAML の frontmatter のときだけ、その直後の行番号を返す。そうでなければ 0。 */
function bodyStart(lines) {
  const closing = lines[0] === '---' ? lines.indexOf('---', 1) : -1;
  if (closing < 1) return 0;
  try {
    parseKnowledgeFrontmatter(`${lines.slice(0, closing + 1).join('\n')}\n`, Number.MAX_SAFE_INTEGER);
    return closing + 1;
  } catch {
    return 0;
  }
}

/** frontmatter とコードフェンスを除いた行だけを対象に、見出し（##）の位置と名前を集める。 */
function scanStructure(lines) {
  const start = bodyStart(lines);
  const isFenced = createFenceTracker();
  const plain = lines.map((line, index) => index >= start && !isFenced(line));
  const labels = new Map();
  lines.forEach((line, index) => {
    const label = plain[index] ? parseH2Heading(line) : null;
    if (label !== null) labels.set(index, label);
  });
  return { plain, headings: [...labels.keys()], labels };
}

const isConfirmedHeading = (structure, index) => structure.labels.get(index)?.startsWith(CONFIRMED_KB_LABEL) === true;
const isLegacyMemoHeading = (structure, index) => structure.labels.get(index) === LEGACY_REVIEW_MEMO_LABEL;
const isFormalHeading = (structure, index) => structure.labels.get(index)?.startsWith(FORMAL_LABEL) === true;

function existingKeys(lines, plain, from, to) {
  const keys = new Set();
  for (let index = from; index < to; index += 1) {
    const heading = plain[index] ? PROPOSAL_HEADING.exec(lines[index]) : null;
    if (!heading) continue;
    const next = lines.slice(index + 1, to).find((line) => line.trim() !== '');
    const question = next ? QUESTION_LINE.exec(next) : null;
    if (question) keys.add(proposalKey(heading[1], unescapeMarkdown(question[1])));
  }
  return keys;
}

function storedProposalKeys(lines, structure) {
  const keys = new Set();
  for (const [offset, headingIndex] of structure.headings.entries()) {
    if (!isConfirmedHeading(structure, headingIndex) && !isLegacyMemoHeading(structure, headingIndex)) continue;
    const end = structure.headings[offset + 1] ?? lines.length;
    for (const key of existingKeys(lines, structure.plain, headingIndex + 1, end)) keys.add(key);
  }
  return keys;
}

function selectNew(proposals, keys) {
  return proposals.reduce((selected, proposal) => {
    const key = proposalKey(proposal.checkedOn, proposal.question);
    return keys.has(key) || selected.some((item) => item.key === key) ? selected : [...selected, { key, proposal }];
  }, []).map((item) => item.proposal);
}

const blockLines = (proposals) => proposals.flatMap((proposal, index) => [...(index > 0 ? [''] : []), ...proposal.markdown.split('\n')]);

function trimBlankEdges(lines) {
  const first = lines.findIndex((line) => line.trim() !== '');
  if (first < 0) return [];
  const last = lines.findLastIndex((line) => line.trim() !== '');
  return lines.slice(first, last + 1);
}

function hasUnclosedFence(lines, from, to) {
  const fencePattern = /^ {0,3}(`{3,}|~{3,})(.*)$/u;
  let open = null;
  for (const line of lines.slice(from, to)) {
    const match = fencePattern.exec(line);
    if (open === null) {
      if (match && !(match[1][0] === '`' && match[2].includes('`'))) {
        open = { marker: match[1][0], length: match[1].length };
      }
      continue;
    }
    if (match && match[1][0] === open.marker && match[1].length >= open.length && match[2].trim() === '') open = null;
  }
  return open !== null;
}

function rejectUnclosedFence(lines, from, to) {
  if (hasUnclosedFence(lines, from, to)) {
    reject('閉じていないコードフェンスがあるため、追記位置を判定できません。コードフェンスを閉じてから再実行してください。');
  }
}

function isPlaceholderText(text) {
  const wrapped = PLACEHOLDER_WRAPPED.exec(text.trim());
  if (!wrapped) return false;
  const parts = wrapped[1].replace(/。$/u, '').split(PLACEHOLDER_SEPARATOR);
  return parts.every((part) => PLACEHOLDER_PARTS.has(part.replace(/\s+/gu, '').toLowerCase()));
}

const isPlaceholderBody = (body) => body.filter((line) => line.trim() !== '').every((line) => isPlaceholderText(line));

/** 見出しに付いた「（該当なし）」等の書き置きだけを外す。 */
function cleanHeading(structure, headingIndex, line) {
  const suffix = structure.labels.get(headingIndex)?.slice(CONFIRMED_KB_LABEL.length).trim() ?? '';
  return suffix && isPlaceholderText(suffix) ? CONFIRMED_KB_HEADING_TEXT : line;
}

function intoConfirmedSection(lines, structure, headingIndex, proposals, knownKeys) {
  const end = structure.headings.find((index) => index > headingIndex) ?? lines.length;
  const fresh = selectNew(proposals, knownKeys);
  if (fresh.length === 0) return { lines, applied: 0 };
  rejectUnclosedFence(lines, headingIndex + 1, end);
  const body = trimBlankEdges(lines.slice(headingIndex + 1, end));
  const kept = body.length === 0 || isPlaceholderBody(body) ? [] : [...body, ''];
  const tail = end < lines.length ? [''] : lines.slice(headingIndex + 1).at(-1) === '' ? [''] : [];
  const section = [cleanHeading(structure, headingIndex, lines[headingIndex]), '', ...kept, ...blockLines(fresh), ...tail];
  return { lines: [...lines.slice(0, headingIndex), ...section, ...lines.slice(end)], applied: fresh.length };
}

function asNewSection(lines, structure, proposals, knownKeys) {
  const fresh = selectNew(proposals, knownKeys);
  const section = [CONFIRMED_KB_HEADING_TEXT, '', ...blockLines(fresh)];
  const formal = structure.headings.find((index) => isFormalHeading(structure, index));
  if (formal !== undefined) {
    rejectUnclosedFence(lines, 0, formal);
    const before = lines.slice(0, formal);
    const gap = before.length > 0 && before.at(-1).trim() !== '' ? [''] : [];
    return { lines: [...before, ...gap, ...section, '', ...lines.slice(formal)], applied: fresh.length };
  }
  const endsWithNewline = lines.length > 1 && lines.at(-1) === '';
  rejectUnclosedFence(lines, 0, lines.length);
  const content = lines.slice(0, lines.findLastIndex((line) => line.trim() !== '') + 1);
  const gap = content.length > 0 ? [''] : [];
  return { lines: [...content, ...gap, ...section, ...(endsWithNewline ? [''] : [])], applied: fresh.length };
}

/**
 * 管理者が確認して追記すると決めた追記案だけを、「KB確認に基づく追記」へ差し込む。
 * 中身が情報の無い書き置き（該当なし等）なら置き換えて見出しの注記を外す。情報のある書き置きや既存の追記は残して末尾に足す。
 * 同じ質問・同じ確認日の追記は入れない（旧版の未確認メモ節にあるものも含む）。
 * 節が無ければ「## 正式資料…」の前、それも無ければ末尾に節を作る。
 * frontmatter 付きでも本文だけでも渡せる。改行コード（CRLF / LF）は保つ。
 * @param {string} markdown
 * @param {ReadonlyArray<{ question: string, checkedOn: string, markdown: string }>} proposals
 * @returns {{ markdown: string, applied: number, skipped: number }}
 */
export function applyCheckProposals(markdown, proposals) {
  if (typeof markdown !== 'string' || !Array.isArray(proposals)) reject('Markdown と追記案を指定してください。');
  if (proposals.some((proposal) => !proposal || !isCalendarDate(proposal.checkedOn) || !oneLine(proposal.question) || typeof proposal.markdown !== 'string')) {
    reject('有効な質問・確認日・追記案を指定してください。');
  }
  if (proposals.length === 0) return { markdown, applied: 0, skipped: 0 };
  const eol = markdown.includes('\r\n') ? '\r\n' : '\n';
  const lines = markdown.split(/\r?\n/u);
  const structure = scanStructure(lines);
  const knownKeys = storedProposalKeys(lines, structure);
  const headingIndex = structure.headings.find((index) => isConfirmedHeading(structure, index));
  const result = headingIndex === undefined
    ? asNewSection(lines, structure, proposals, knownKeys)
    : intoConfirmedSection(lines, structure, headingIndex, proposals, knownKeys);
  const skipped = proposals.length - result.applied;
  return result.applied === 0
    ? { markdown, applied: 0, skipped }
    : { markdown: result.lines.join(eol), applied: result.applied, skipped };
}
