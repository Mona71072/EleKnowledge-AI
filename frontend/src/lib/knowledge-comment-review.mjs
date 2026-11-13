import { researchSourceHref } from './knowledge-research.mjs';
import { CHECK_DECISIONS, classifyCheckAnswer, formatCheckDate, PROPOSAL_MAX_SOURCES } from './knowhow-card-proposal.mjs';
import { parseH2Heading } from './knowhow-card-view.mjs';

const FENCE = /^ {0,3}(`{3,}|~{3,})(.*)$/u;
const MAX_QUERY_LENGTH = 2_000;
export const MAX_REVIEW_COMMENT_CHARS = 900;
export const MAX_COMMENT_ADDITION_CHARS = 6_000;

function reject(message) {
  throw new TypeError(message);
}

function linesOf(body) {
  const text = typeof body === 'string' ? body : '';
  const lines = [];
  const pattern = /([^\r\n]*)(\r\n|\n|\r|$)/gu;
  let match;
  while ((match = pattern.exec(text)) && match[0] !== '') {
    lines.push({ text: match[1], start: match.index, end: match.index + match[0].length });
  }
  return { text, lines };
}

function fenceStep(open, line) {
  const match = FENCE.exec(line);
  if (!open) {
    if (!match || (match[1][0] === '`' && match[2].includes('`'))) return null;
    return { mark: match[1][0], length: match[1].length };
  }
  if (match && match[1][0] === open.mark && match[1].length >= open.length && match[2].trim() === '') return null;
  return open;
}

function sectionSlug(label) {
  const slug = label.toLocaleLowerCase('ja').replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/gu, '');
  return slug || 'section';
}

function scanSections(body) {
  const { text, lines } = linesOf(body);
  const sections = [];
  let open = null;
  lines.forEach(({ text: line }, index) => {
    const wasOpen = open !== null;
    open = fenceStep(open, line);
    if (wasOpen || open) return;
    const label = parseH2Heading(line);
    if (label !== null) sections.push({ label, line: index + 1, index });
  });
  if (sections.length === 0) return { text, lines, sections: [{ id: 'body', label: '本文全体', line: 1, index: 0 }] };
  const counts = new Map();
  return {
    text,
    lines,
    sections: sections.map((section) => {
      const slug = sectionSlug(section.label);
      const occurrence = (counts.get(slug) ?? 0) + 1;
      counts.set(slug, occurrence);
      return { ...section, id: `section-${slug}-${occurrence}` };
    }),
  };
}

/** List H2 sections outside Markdown fences. Cards without H2 headings get one body section. */
export function listCommentSections(body) {
  return scanSections(body).sections.map(({ id, label, line }) => ({ id, label, line }));
}

/** Find a section only when its label is unique, since duplicate IDs may shift after edits. */
export function findCommentSection(body, sectionId, expectedLabel) {
  const sections = scanSections(body).sections;
  const section = sections.find((candidate) => candidate.id === sectionId);
  if (!section || (expectedLabel !== undefined && section.label !== expectedLabel)) return undefined;
  if (sections.filter((candidate) => candidate.label === section.label).length !== 1) return undefined;
  return { id: section.id, label: section.label, line: section.line };
}

function boundedField(value, maxLength) {
  return Array.from(String(value ?? '').replace(/[\u0000-\u001f\u007f]/gu, ' ').replace(/\s+/gu, ' ').trim())
    .slice(0, maxLength).join('');
}

/** Build a source-focused query without sending the card body to the research service. */
export function buildCommentResearchQuery({ title, sectionLabel, comment, modelWords = [] } = {}) {
  const fields = {
    title: boundedField(title, 300),
    sectionLabel: boundedField(sectionLabel, 300),
    comment: boundedField(comment, MAX_REVIEW_COMMENT_CHARS),
  };
  const prefix = [
    '技術KBと法令KBの資料だけを確認し、既存ナレッジカードの不足を調べてください。対象節へ追加できる簡潔な内容を提案してください。',
    '資料に書かれた事実、適用条件、前提、例外を分け、根拠がない点や資料間の差異・未確認事項は不足として明示してください。推測で補わず、根拠資料名とページ・箇所を示してください。',
    `カード題名: ${fields.title}`,
    `対象見出し: ${fields.sectionLabel}`,
    ...(modelWords.length ? [`カードに記録された機種の手掛かり: ${boundedField(modelWords.join("・"), 100)}。適用範囲は資料本文で確認してください。`] : []),
    `確認コメント: ${fields.comment}`,
  ].join('\n');
  if (Array.from(prefix).length <= MAX_QUERY_LENGTH) return prefix;
  return Array.from(prefix).slice(0, MAX_QUERY_LENGTH).join('');
}

function escapePlain(value) {
  return String(value ?? '').replace(/[\r\n]+/gu, ' ').replace(/[\u0000-\u001f\u007f]/gu, ' ')
    .replace(/\s+/gu, ' ').trim()
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replace(/([\\`*_{}\[\]()#+.!|~])/gu, '\\$1');
}

function escapeDraft(value) {
  return String(value ?? '').replace(/\r\n?/gu, '\n').split('\n')
    .map((line) => escapePlain(line)).join('\n').trim();
}

function isCalendarDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/u.test(value)) return false;
  const timestamp = Date.parse(`${value}T00:00:00.000Z`);
  return Number.isFinite(timestamp) && new Date(timestamp).toISOString().slice(0, 10) === value;
}

function sourceLine(source, mode, index) {
  const href = researchSourceHref(source, mode);
  if (!href) return null;
  const citation = source?.lawCitation;
  if (mode === 'law' && citation?.lawTitle) {
    const location = citation.provisionReference ? ` ${escapePlain(citation.provisionReference)}` : '';
    const effective = isCalendarDate(citation.effectiveDate) ? `（施行日 ${citation.effectiveDate}）` : '';
    return `- [${escapePlain(citation.lawTitle)}](<${href}>)${location}${effective}`;
  }
  const name = escapePlain(source.documentName || source.title || `出典 ${index + 1}`);
  const location = Number.isSafeInteger(source.pageNumber) && source.pageNumber > 0 ? ` p.${source.pageNumber}` : '';
  return `- [${name}](<${href}>)${location}`;
}

function insertionFor(text, lines, section, sections, addition, eol) {
  const next = sections.find((candidate) => candidate.index > section.index);
  const sectionStart = lines[section.index]?.start ?? 0;
  const sectionEnd = next ? lines[next.index].start : text.length;
  let insertAt = sectionEnd;
  while (insertAt > sectionStart && (text.slice(insertAt - eol.length, insertAt) === eol)) insertAt -= eol.length;
  const before = text.slice(sectionStart, insertAt);
  const startSeparator = before.length === 0 ? '' : /(?:\r\n|\r|\n){2}$/u.test(before) ? '' : `${eol}${eol}`;
  const trailing = text.slice(insertAt);
  const endSeparator = next && !/^(?:\r\n|\r|\n){2}/u.test(trailing) ? eol : '';
  return `${text.slice(0, insertAt)}${startSeparator}${addition}${endSeparator}${trailing}`;
}

/**
 * Append a source-linked addition to a selected section. Call it only for an addition the administrator
 * explicitly chose to add after checking its sources; the card gets a confirmation line with `checkedOn`.
 * @param {string} body
 * @param {string} sectionId
 * @param {import('./knowledge-research.mjs').ResearchAnswer} answer
 * @param {string | undefined} draftText edited draft; the answer text when omitted
 * @param {string} checkedOn confirmation date, `YYYY-MM-DD`
 */
export function buildCommentAddition(body, sectionId, answer, draftText, checkedOn) {
  const { text, lines, sections } = scanSections(body);
  const section = sections.find((candidate) => candidate.id === sectionId);
  if (!section) reject('対象の節が見つかりません。');
  if (sections.filter((candidate) => candidate.label === section.label).length !== 1) {
    reject('同じ見出し名の節が複数あるため、安全に追記先を特定できません。');
  }
  if (!answer || answer.responseType !== 'pages') reject('回答が pages ではありません。');
  const outcome = classifyCheckAnswer(answer);
  if (outcome === 'no_source') reject('回答の出典が不足しています。');
  if (outcome !== 'found') reject('有効な資料に基づく回答が必要です。');
  const sources = [...new Set(answer.sourceDocuments.map((source, index) => sourceLine(source, answer.mode, index)).filter(Boolean))]
    .slice(0, PROPOSAL_MAX_SOURCES);
  if (sources.length === 0) reject('安全なリンクを作れる出典が必要です。');
  if (!isCalendarDate(checkedOn)) reject('確認日は実在する日付を YYYY-MM-DD で指定してください。');
  const rawDraft = draftText === undefined ? answer.content : draftText;
  if (Array.from(String(rawDraft ?? '')).length > MAX_COMMENT_ADDITION_CHARS) {
    reject(`追記案は${MAX_COMMENT_ADDITION_CHARS.toLocaleString('ja-JP')}文字以内にしてください。`);
  }
  const draft = escapeDraft(rawDraft);
  if (!draft) reject('追記案の本文が空です。');

  let fence = null;
  const endIndex = sections.find((candidate) => candidate.index > section.index)?.index ?? lines.length;
  for (let index = section.index; index < endIndex; index += 1) fence = fenceStep(fence, lines[index].text);
  if (fence) reject('対象の節に閉じていないコードフェンスがあります。');

  const eol = /\r\n|\n|\r/u.exec(text)?.[0] ?? '\n';
  const addition = [
    draft.replaceAll('\n', eol),
    '',
    '根拠資料:',
    ...sources,
    '',
    `確認: 管理者が出典を確認（${checkedOn}）`,
  ].join(eol);
  return insertionFor(text, lines, section, sections, addition, eol);
}

/** 回答を受け取った日（手元の日付）。受信日時が読めないときは今日。 */
function confirmationDate(answer) {
  const received = new Date(answer?.receivedAt ?? '');
  return formatCheckDate(Number.isNaN(received.getTime()) ? new Date() : received);
}

/**
 * 管理者が「確認して追記する」を選んだ追記案だけを、選んだ節へ順に足した本文を返す。
 * 未選択（未確認）・「追記しない」の追記案は本文に入れない。
 * @param {string} body
 * @param {string} sectionId
 * @param {ReadonlyArray<{ answer: import('./knowledge-research.mjs').ResearchAnswer, text: string, decision: 'confirm' | 'skip' | undefined }>} entries
 * @returns {{ body: string, applied: number }}
 */
export function buildConfirmedCommentBody(body, sectionId, entries) {
  const confirmed = entries.filter((entry) => entry.decision === CHECK_DECISIONS.confirm);
  return {
    body: confirmed.reduce((current, { answer, text }) => (
      buildCommentAddition(current, sectionId, answer, text, confirmationDate(answer))
    ), body),
    applied: confirmed.length,
  };
}
