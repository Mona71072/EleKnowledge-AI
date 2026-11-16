import { createFenceTracker, FIELD_MATERIAL_SECTION, parseH2Heading } from './knowhow-card-view.mjs';
import { charCount, findRewriteBodyProblem } from './knowhow-rewrite-sections.mjs';

export const MAX_FIELD_MATERIAL_BYTES = 256 * 1024;
export const MAX_FIELD_MATERIAL_EXCERPT_CHARS = 2000;
export const MAX_FIELD_MATERIAL_SUMMARY_CHARS = 2000;

const SOURCE_ID = /^local-sha256:[a-f0-9]{64}$/u;

function hasForbiddenControls(value) {
  return /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/u.test(value);
}

function singleLine(value, max, label) {
  if (typeof value !== 'string') throw new TypeError(`${label}を入力してください。`);
  const normalized = value.trim();
  if (!normalized || normalized.length > max || /[\r\n]/u.test(normalized) || hasForbiddenControls(normalized)) {
    throw new TypeError(`${label}は1行${max}文字以内で入力してください。`);
  }
  return normalized;
}

function escapeMarkdown(value) {
  return value.replace(/[\\`*_{}\[\]()#+.!|<>]/gu, '\\$&');
}

/** Read one selected local .md/.txt file; the returned value never retains the File. */
export async function readFieldMaterialFile(file) {
  const name = file?.name;
  if (typeof name !== 'string' || !name || name.length > 255 || /[\u0000-\u001f\u007f-\u009f]/u.test(name)
    || /[/\\]/u.test(name) || !/^[^/\\]+\.(?:md|txt)$/iu.test(name)) {
    throw new TypeError('ファイル名を確認してください。.md または .txt のファイルを1つ選んでください。');
  }
  if (!Number.isSafeInteger(file.size) || file.size < 0 || file.size > MAX_FIELD_MATERIAL_BYTES) {
    throw new TypeError('ファイルは256 KiB以下にしてください。');
  }
  if (typeof file.arrayBuffer !== 'function') throw new TypeError('選択したファイルを読み込めません。');
  let bytes;
  try {
    bytes = new Uint8Array(await file.arrayBuffer());
  } catch {
    throw new TypeError('選択したファイルを読み込めません。もう一度選んでください。');
  }
  if (bytes.byteLength > MAX_FIELD_MATERIAL_BYTES || bytes.byteLength !== file.size) {
    throw new TypeError('ファイルサイズを確認できませんでした。256 KiB以下のファイルを選び直してください。');
  }
  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch {
    throw new TypeError('UTF-8形式のテキストファイルを選んでください。');
  }
  if (hasForbiddenControls(text)) throw new TypeError('ファイル本文に使用できない制御文字があります。');
  const sha256 = [...new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes))]
    .map((byte) => byte.toString(16).padStart(2, '0')).join('');
  return { filename: name, text, sha256, sourceId: `local-sha256:${sha256}` };
}

/** Validate an excerpt copied from the selected text without altering its wording. */
export function validateFieldMaterialExcerpt(sourceText, excerpt) {
  if (typeof sourceText !== 'string' || typeof excerpt !== 'string') {
    throw new TypeError('選択した資料から引用箇所を指定してください。');
  }
  if (!excerpt.trim() || charCount(excerpt) > MAX_FIELD_MATERIAL_EXCERPT_CHARS
    || hasForbiddenControls(excerpt) || !sourceText.includes(excerpt)) {
    throw new TypeError(`引用箇所は資料本文にある連続した${MAX_FIELD_MATERIAL_EXCERPT_CHARS}コードポイント以内の範囲を指定してください。`);
  }
  return excerpt;
}

/** Validate the human-entered attribution fields and optional verified public HTTPS URL. */
export function normalizeFieldMaterialMetadata(input, source) {
  const sourceId = source?.sourceId;
  const filename = source?.filename;
  if (typeof sourceId !== 'string' || !SOURCE_ID.test(sourceId) || typeof filename !== 'string'
    || !filename || filename.length > 255 || /[\u0000-\u001f\u007f-\u009f]/u.test(filename) || /[/\\]/u.test(filename)) {
    throw new TypeError('資料の識別情報を確認できません。ファイルを選び直してください。');
  }
  const result = {
    sourceId,
    filename,
    title: singleLine(input?.title, 160, '資料名'),
    version: singleLine(input?.version, 80, '版・バージョン'),
    locator: singleLine(input?.locator, 300, '参照箇所'),
  };
  if (input?.url !== undefined && input.url !== '') {
    const rawUrl = singleLine(input.url, 2048, '資料リンク');
    let url;
    try { url = new URL(rawUrl); } catch { throw new TypeError('資料リンクは確認済みのHTTPSリンクを入力してください。'); }
    if (url.protocol !== 'https:' || !url.hostname || url.username || url.password || url.search || url.hash) {
      throw new TypeError('資料リンクは認証情報やクエリを含まないHTTPSリンクにしてください。');
    }
    result.url = url.href;
  }
  return result;
}

function lineEnding(markdown) {
  return markdown.includes('\r\n') ? '\r\n' : '\n';
}

function headingLines(markdown, eol) {
  const lines = markdown.split(eol);
  const isFenced = createFenceTracker();
  const target = [];
  const h2 = [];
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const inFence = isFenced(line);
    const heading = inFence ? null : parseH2Heading(line);
    if (heading === null) continue;
    h2.push(index);
    if (heading === FIELD_MATERIAL_SECTION) target.push(index);
  }
  if (isFenced('## __field_material_fence_check__')) throw new TypeError('文書に閉じていないコードフェンスがあります。修正してから追加してください。');
  return { lines, target, h2 };
}

/** Extract canonical field-report source refs from the unique dedicated H2 section only. */
export function getFieldMaterialSourceRefs(markdown) {
  if (typeof markdown !== 'string' || !markdown) return [];
  const lines = markdown.split(/\r\n|\r|\n/u);
  const isFenced = createFenceTracker();
  let sectionStart = -1;
  let sectionEnd = lines.length;
  let sectionCount = 0;
  const headings = [];
  for (let index = 0; index < lines.length; index += 1) {
    const inFence = isFenced(lines[index]);
    const heading = inFence ? null : parseH2Heading(lines[index]);
    if (heading === null) continue;
    headings.push(index);
    if (heading === FIELD_MATERIAL_SECTION) {
      sectionCount += 1;
      sectionStart = index;
    }
  }
  if (isFenced('## __field_material_fence_check__')) return [];
  if (sectionCount === 0) return [];
  if (sectionCount !== 1) throw new TypeError('現場資料の見出しが複数あります。出典IDを抽出できません。');
  sectionEnd = headings.find((index) => index > sectionStart) ?? lines.length;
  const refs = [];
  const seen = new Set();
  const canonicalAttribution = /^> 出典ID: (local-sha256:[a-f0-9]{64})$/u;
  const sectionFence = createFenceTracker();
  for (let index = 0; index < sectionEnd; index += 1) {
    const fenced = sectionFence(lines[index]);
    if (index <= sectionStart || fenced) continue;
    const line = lines[index];
    const match = canonicalAttribution.exec(line);
    if (!match || seen.has(match[1])) continue;
    seen.add(match[1]);
    refs.push({ ref_type: 'knowhow', knowhow_id: match[1], origin: 'field_report' });
  }
  return refs;
}

function attribution(metadata, eol) {
  const details = [
    `出典ID: ${metadata.sourceId}`,
    `資料: ${escapeMarkdown(metadata.title)} (${escapeMarkdown(metadata.version)})`,
    `参照箇所: ${escapeMarkdown(metadata.locator)}`,
  ];
  if (metadata.url) details.push(`確認済みリンク: <${metadata.url}>`);
  return `> ${details.join(`${eol}> `)}`;
}

/** Insert only a human-reviewed summary and its attribution into the target H2 section. */
export function insertFieldMaterialMarkdown(markdown, acceptedSummary, metadata, options = {}) {
  if (typeof markdown !== 'string' || options?.reviewed !== true) {
    throw new TypeError('人が内容を確認して承認した要約だけをMarkdownへ追加できます。');
  }
  if (typeof acceptedSummary !== 'string') throw new TypeError('確認済み要約を入力してください。');
  if (!acceptedSummary.trim() || charCount(acceptedSummary) > MAX_FIELD_MATERIAL_SUMMARY_CHARS || hasForbiddenControls(acceptedSummary)) {
    throw new TypeError(`確認済み要約は制御文字を含まない${MAX_FIELD_MATERIAL_SUMMARY_CHARS}コードポイント以内で入力してください。`);
  }
  const bodyProblem = findRewriteBodyProblem(acceptedSummary);
  if (bodyProblem) throw new TypeError('確認済み要約に見出し、HTML、追加リンク、または使用できない文字があります。');
  const checkedMetadata = normalizeFieldMaterialMetadata(metadata, {
    sourceId: metadata?.sourceId,
    filename: metadata?.filename,
  });
  const eol = lineEnding(markdown);
  const { lines, target, h2 } = headingLines(markdown, eol);
  if (target.length > 1) throw new TypeError('対象の見出しが複数あります。文書を確認してから追加してください。');
  const summary = acceptedSummary.replace(/\r\n?/gu, '\n').replace(/\n/gu, eol);
  const content = `${summary}${eol}${eol}${attribution(checkedMetadata, eol)}`;
  if (!target.length) {
    const prefix = markdown.length === 0 ? '' : markdown.endsWith('\n') ? '' : eol;
    const separator = markdown.length === 0 || markdown.endsWith(`${eol}${eol}`) ? '' : eol;
    return `${markdown}${prefix}${separator}## ${FIELD_MATERIAL_SECTION}${eol}${eol}${content}${eol}`;
  }
  const start = target[0];
  const end = h2.find((index) => index > start) ?? lines.length;
  const section = lines.slice(start, end);
  let trailingBlankLines = 0;
  while (section.length > 1 && section.at(-1) === '') { section.pop(); trailingBlankLines += 1; }
  const existingSectionText = section.join(eol);
  const needsBlank = existingSectionText.trim().length > 0;
  const updatedSection = `${existingSectionText}${needsBlank ? `${eol}${eol}` : eol}${content}`;
  const preservedBoundaryLines = end < lines.length && trailingBlankLines === 0 ? 1 : trailingBlankLines;
  return [...lines.slice(0, start), ...updatedSection.split(eol), ...Array(preservedBoundaryLines).fill(''), ...lines.slice(end)].join(eol);
}
