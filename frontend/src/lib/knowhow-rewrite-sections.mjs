// カード本文を節に分け、AI に書き換えを頼む節（対象）と、読むだけの節（context）を選ぶ。
// 見出しの判定・コードフェンス・frontmatter の扱いは、既存の knowhow-card-view / knowhow-card-proposal に任せる。
import { createFenceTracker, FIELD_MATERIAL_SECTION, isEditorHeading } from './knowhow-card-view.mjs';
import { scanStructure } from './knowhow-card-proposal.mjs';

/** AI に書き換え案を作らせてよい節。カードの「主張」の節だけで、出どころや KB 確認の節は含まない。 */
export const REWRITE_TARGET_HEADINGS = Object.freeze(['統合した回答・ノウハウ', '調査・確認手順', '未確認事項']);

/** API 契約（tests/fixtures/knowhow-rewrite/contract.json の limits）と同じ上限。 */
export const REWRITE_LIMITS = Object.freeze({
  knowledgeIdPattern: /^KH-[A-Z0-9-]{1,80}$/u,
  cardVersionMax: 9999,
  targetMax: 3,
  targetBodyChars: 2000,
  targetTotalChars: 4000,
  contextMax: 8,
  contextHeadingChars: 200,
  contextBodyChars: 4000,
  contextTotalChars: 16000,
  evidenceMax: 12,
  questionChars: 2000,
  answerChars: 2000,
  sourcesMax: 8,
  sourceTitleChars: 200,
  responseBodyChars: 4000,
  previousProposalBodyChars: 4000,
  reasonChars: 300,
});

/** 文字数をコードポイントで数える（API 側の文字数と合わせる。下位サロゲートは数えない）。 */
export function charCount(text) {
  let count = 0;
  for (let index = 0; index < text.length; index += 1) {
    const unit = text.charCodeAt(index);
    if (unit < 0xdc00 || unit > 0xdfff) count += 1;
  }
  return count;
}

/**
 * Markdown を、H2 の節ごとに読む。frontmatter・コードフェンス内の `## ` は見出しにしない。
 * 本文は前後の空白を除き、改行は LF にそろえる。
 * @param {unknown} markdown
 */
export function readSections(markdown) {
  const lines = (typeof markdown === 'string' ? markdown : '').split(/\r?\n/u);
  const structure = scanStructure(lines);
  const sections = structure.headings.map((headingIndex, order) => {
    const end = structure.headings[order + 1] ?? lines.length;
    return {
      heading: structure.labels.get(headingIndex) ?? '',
      headingIndex,
      start: headingIndex + 1,
      end,
      body: lines.slice(headingIndex + 1, end).join('\n').trim(),
    };
  });
  return { lines, structure, sections };
}

const TARGETS = new Set(REWRITE_TARGET_HEADINGS);

function pickTargets(sections) {
  const counts = new Map();
  for (const { heading } of sections) counts.set(heading, (counts.get(heading) ?? 0) + 1);
  const targets = [];
  const excluded = [];
  const reported = new Set();
  let total = 0;
  for (const { heading, body } of sections) {
    if (!TARGETS.has(heading) || reported.has(heading)) continue;
    const size = charCount(body);
    const reason = counts.get(heading) > 1 ? 'duplicate'
      : size === 0 ? 'empty'
        : size > REWRITE_LIMITS.targetBodyChars ? 'too_long'
          : total + size > REWRITE_LIMITS.targetTotalChars ? 'total_too_long' : '';
    if (reason) {
      reported.add(heading);
      excluded.push({ heading, reason });
    } else {
      total += size;
      targets.push({ heading, body });
    }
  }
  return { targets, excluded };
}

function pickContext(sections) {
  const others = sections.filter(({ heading, body }) => heading && heading !== FIELD_MATERIAL_SECTION
    && charCount(heading) <= REWRITE_LIMITS.contextHeadingChars && !TARGETS.has(heading) && body !== '');
  const ordered = [...others.filter(({ heading }) => !isEditorHeading(heading)), ...others.filter(({ heading }) => isEditorHeading(heading))];
  const context = [];
  let total = 0;
  for (const { heading, body } of ordered) {
    const size = charCount(body);
    if (context.length >= REWRITE_LIMITS.contextMax || size > REWRITE_LIMITS.contextBodyChars
      || total + size > REWRITE_LIMITS.contextTotalChars) continue;
    total += size;
    context.push({ heading, body });
  }
  return context;
}

/**
 * カード本文から、AI に送る節を選ぶ。上限を超える節は切り詰めず、対象から外して理由を返す。
 * @param {string} body カード本文（frontmatter があってもよい）
 * @returns {{ targets: Array<{heading: string, body: string}>, context: Array<{heading: string, body: string}>, excluded: Array<{heading: string, reason: 'duplicate'|'empty'|'too_long'|'total_too_long'}> }}
 */
export function selectRewriteSections(body) {
  const { sections } = readSections(body);
  return { ...pickTargets(sections), context: pickContext(sections) };
}

const SETEXT_LINE = /^ {0,3}(?:-{3,}|={3,})[ \t]*$/u;
// 見えない文字（Cf）と制御文字（改行・タブ以外）。
const SUSPICIOUS_CHAR = /(?![\n\r\t])[\p{Cc}\p{Cf}]/u;
// リンクと HTML の目印。URL・www・Markdown のリンク先と画像・HTML タグは、末尾まで含めた文字列を比べる。どれも入力長に対して線形。
const LINK_OR_HTML = /https?:\/\/[^\s)>\]]*|www\.[^\s)>\]]*|\]\([^)\s]*|!\[|<[A-Za-z/!][^\s>]*/giu;

/** 見えない文字・制御文字（改行・タブ以外）を含むか。 */
export function hasSuspiciousText(text) {
  return typeof text === 'string' && SUSPICIOUS_CHAR.test(text);
}

function linkOrHtmlTokens(text) {
  return (text.match(LINK_OR_HTML) ?? []).map((token) => token.toLowerCase());
}

/** `original` に無いリンク・HTML を含むか。`original` に同じものがあれば通す。 */
export function hasNewLinkOrHtml(text, original = '') {
  const known = new Set(linkOrHtmlTokens(typeof original === 'string' ? original : ''));
  return linkOrHtmlTokens(text).some((token) => !known.has(token));
}

/**
 * 画面に出す短い文（変更理由・食い違いの要約）として使えないか。URL・HTML・見えない文字を含むと true。
 * @param {string} text
 */
export function isUnsafeDisplayText(text) {
  return hasSuspiciousText(text) || hasNewLinkOrHtml(text, '');
}

/**
 * 本文が節の構造を壊さないかだけを調べる。問題が無ければ null。
 * `## ` の見出し行・先頭の `---` などの区切り線は 'heading_in_body'、閉じていないコードフェンスは 'unclosed_fence'。
 * @param {unknown} body
 * @returns {'empty' | 'too_long' | 'heading_in_body' | 'unclosed_fence' | null}
 */
export function findRewriteStructureProblem(body) {
  if (typeof body !== 'string' || body.trim() === '') return 'empty';
  if (charCount(body) > REWRITE_LIMITS.responseBodyChars) return 'too_long';
  const lines = body.split(/\r?\n/u);
  if (scanStructure(['## a', ...lines]).headings.length !== 1) return 'heading_in_body';
  if (scanStructure(['## a', ...lines, '## b']).headings.length !== 2) return 'unclosed_fence';
  const isFenced = createFenceTracker();
  return lines.some((line) => !isFenced(line) && SETEXT_LINE.test(line)) ? 'heading_in_body' : null;
}

/**
 * 書き換え後の本文を調べる。問題が無ければ null。
 * 構造（findRewriteStructureProblem）に加え、見えない文字・制御文字は 'suspicious_text'、
 * 元の本文（`original`）に無いリンク・HTML は 'link_or_html'。
 * @param {unknown} body
 * @param {string} [original] 書き換え前のその節の本文
 * @returns {'empty' | 'too_long' | 'heading_in_body' | 'unclosed_fence' | 'suspicious_text' | 'link_or_html' | null}
 */
export function findRewriteBodyProblem(body, original = '') {
  const structure = findRewriteStructureProblem(body);
  if (structure) return structure;
  if (hasSuspiciousText(body)) return 'suspicious_text';
  return hasNewLinkOrHtml(body, original) ? 'link_or_html' : null;
}
