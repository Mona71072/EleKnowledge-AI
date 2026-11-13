// ノウハウカード本文（Markdown）を、利用者向けの節と編集者向けの節に分ける。
// カードは AI が読む前提の固定の節構成（knowledge/cards/TEMPLATE.md）なので、見出し名で分類する。

/**
 * 編集者・AI 向け（出どころ・突き合わせ用）の節を見分ける見出しのキーワード。
 * ここに当てはまらない節（未知の見出しを含む）は、情報を消さないよう利用者向けに残す。
 */
export const EDITOR_HEADING_KEYWORDS = Object.freeze([
  'ソース要約',
  'KB確認',
  '正式資料',
  '元情報',
  '参照元',
  '関連事例',
]);

// 「なし」「（該当なし）」「Lists のみ」「-」だけの行は、中身の無い行として扱う。
const EMPTY_LINE = /^[（(]?\s*(?:なし|無し|該当なし|未記載|Lists\s*のみ|-|—|–)\s*[）)]?[。.]?$/u;
const FENCE = /^\s{0,3}(?:`{3,}|~{3,})/u;

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
  let inFence = false;
  let titleSeen = false;
  for (const line of lines) {
    if (FENCE.test(line)) inFence = !inFence;
    const h2 = !inFence && /^##\s+(\S.*?)\s*#*\s*$/u.exec(line);
    const h1 = !inFence && !titleSeen && !h2 && /^#\s+(\S.*?)\s*$/u.exec(line);
    if (h1 && sections.length === 0 && current.heading === '') {
      title = h1[1];
      titleSeen = true;
    } else if (h2) {
      sections.push(current);
      current = { heading: h2[1], lines: [] };
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
  let inFence = false;
  for (const line of lines) {
    if (FENCE.test(line)) inFence = !inFence;
    const previous = out.at(-1);
    if (!inFence && line.startsWith('※') && previous !== undefined && previous.trim() !== '') out.push('');
    out.push(line);
  }
  return out.join('\n');
}
