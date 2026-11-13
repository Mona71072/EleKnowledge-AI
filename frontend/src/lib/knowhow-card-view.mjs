// ノウハウカード本文（Markdown）を、利用者向けの節と編集者向けの節に分ける。
// カードは AI が読む前提の固定の節構成（knowledge/cards/TEMPLATE.md）なので、見出し名で分類する。

/**
 * 編集者・AI 向け（出どころ・突き合わせ用）の節を見分ける見出しのキーワード。
 * ここに当てはまらない節（未知の見出しを含む）は、情報を消さないよう利用者向けに残す。
 */
export const EDITOR_HEADING_KEYWORDS = Object.freeze([
  'ソース要約',
  'KB確認',
  'KB照合メモ',
  '正式資料',
  '元情報',
  '参照元',
  '関連事例',
]);

// 「なし」「（該当なし）」「Lists のみ」「-」だけの行は、中身の無い行として扱う。
const EMPTY_LINE = /^[（(]?\s*(?:なし|無し|該当なし|未記載|Lists\s*のみ|-|—|–)\s*[）)]?[。.]?$/u;
const FENCE = /^\s{0,3}(`{3,}|~{3,})(.*)$/u;

/**
 * コードフェンスの中かどうかを、行を順に渡して判定する関数を作る。
 * 開いたときと同じ記号・同じ長さ以上の行でだけ閉じる（```` の中の ``` や ~~~ では閉じない）。
 * @returns {(line: string) => boolean} フェンスの中、またはフェンスの開始・終了行なら true
 */
export function createFenceTracker() {
  let open = null;
  return (line) => {
    const match = FENCE.exec(line);
    if (open === null) {
      if (!match || (match[1][0] === '`' && match[2].includes('`'))) return false;
      open = { mark: match[1][0], length: match[1].length };
      return true;
    }
    if (match && match[1][0] === open.mark && match[1].length >= open.length && match[2].trim() === '') open = null;
    return true;
  };
}

/** 見出し行として読む最大文字数。長い行で正規表現が重くならないよう切る。 */
const MAX_HEADING_LINE_CHARS = 2_000;
const H1_LINE = /^#\s+(\S.*)$/u;
const H2_LINE = /^ {0,3}##\s+(\S.*)$/u;

function headingLabel(rest) {
  // 閉じの # と末尾の空白を外す（`\s*#*\s*$` を使うと、空白や # が長く続く行で処理が急増する）。
  let end = rest.trimEnd().length;
  while (end > 0 && rest[end - 1] === '#') end -= 1;
  return rest.slice(0, end).trimEnd() || '#';
}

/**
 * Markdown の H2（`## 見出し`）の見出し名を返す。行頭の空白は 0〜3 個まで許す（Markdown の仕様どおり）。
 * H2 でなければ null。コードフェンスの中かどうかは呼び出し側で判定する。
 * @param {string} line
 * @returns {string | null}
 */
export function parseH2Heading(line) {
  const match = H2_LINE.exec(String(line ?? '').slice(0, MAX_HEADING_LINE_CHARS));
  return match ? headingLabel(match[1]) : null;
}

/** 見出し名が編集者向けの節か。 */
export function isEditorHeading(heading) {
  const text = String(heading ?? '');
  return EDITOR_HEADING_KEYWORDS.some((keyword) => text.includes(keyword));
}

function normalizeLines(text) {
  return (typeof text === 'string' ? text : '').replace(/\r\n?/gu, '\n').split('\n');
}

function isEmptyBody(lines) {
  return lines.every((line) => {
    const text = line.trim().replace(/^[-*+]\s+/u, '').replace(/\*\*/gu, '').trim();
    return text === '' || /^#{3,6}\s/u.test(text) || EMPTY_LINE.test(text);
  });
}

function makeSection(heading, bodyLines) {
  const body = bodyLines.join('\n').trim();
  return { heading, body, markdown: heading ? `## ${heading}\n\n${body}`.trimEnd() : body };
}

function collectSections(lines) {
  let title = '';
  const sections = [];
  let current = { heading: '', lines: [] };
  const isFenced = createFenceTracker();
  let titleSeen = false;
  for (const line of lines) {
    const inFence = isFenced(line);
    const h2 = inFence ? null : parseH2Heading(line);
    const h1 = !inFence && !titleSeen && h2 === null ? H1_LINE.exec(line.slice(0, MAX_HEADING_LINE_CHARS)) : null;
    if (h1 && sections.length === 0 && current.heading === '') {
      title = h1[1].trimEnd();
      titleSeen = true;
    } else if (h2 !== null) {
      sections.push(current);
      current = { heading: h2, lines: [] };
    } else {
      current.lines.push(line);
    }
  }
  sections.push(current);
  return { title, sections };
}

/**
 * カード本文（frontmatter なし、`# 題名` から始まる）を分ける。
 * @returns {{ title: string, readerSections: Array<{heading: string, body: string, markdown: string}>, editorSections: Array<{heading: string, body: string, markdown: string}> }}
 */
export function splitKnowhowCardBody(body) {
  const { title, sections } = collectSections(normalizeLines(body));
  const readerSections = [];
  const editorSections = [];
  for (const section of sections) {
    if (isEmptyBody(section.lines)) continue;
    const built = makeSection(section.heading, section.lines);
    (section.heading && isEditorHeading(section.heading) ? editorSections : readerSections).push(built);
  }
  return { title, readerSections, editorSections };
}

/** 節の一覧を、1つの Markdown 文字列に戻す。 */
export function sectionsToMarkdown(sections) {
  return sections.map((section) => section.markdown).join('\n\n');
}

/**
 * 行頭が `※` の行の直前の単一改行を空行にして、注意文が1段落に融合しないようにする。
 * コードフェンスの中は変えない。
 */
export function breakBeforeNoticeMarks(text) {
  const lines = normalizeLines(text);
  const out = [];
  const isFenced = createFenceTracker();
  for (const line of lines) {
    const inFence = isFenced(line);
    const previous = out.at(-1);
    if (!inFence && line.startsWith('※') && previous !== undefined && previous.trim() !== '') out.push('');
    out.push(line);
  }
  return out.join('\n');
}
