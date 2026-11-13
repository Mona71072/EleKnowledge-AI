import { createFenceTracker } from './knowhow-card-view.mjs';
import { parseKnowledgeFrontmatter } from './knowledge-markdown-frontmatter.mjs';

export const MAX_SOURCE_SNAPSHOT_BYTES = 1024 * 1024;

const LIST_ID = /^[1-9]\d{0,14}$/u;
const ONENOTE_ID = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}:\d+$/iu;
const LIST_HEADING = /^## Lists item ID (\d+)(?=[:：\s]|$)/u;
const SECTION_HEADING = /^ {0,3}#{1,2}(?:\s|$)/u;
const SUPPORTED_LIST = '首都工・不具合情報共有リスト';
const OUTCOMES = ['supports', 'conditions_differ', 'conflict', 'insufficient'];
const NAVIGATION_ONLY = ['index', 'empty_or_attachment_only'];

function field(value, max) {
  return typeof value === 'string' && value.trim() && value.length <= max && !value.includes('\0') ? value.trim() : '';
}

function dateOnly(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/u.test(value)) return '';
  const date = new Date(value);
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value ? value : '';
}

function refToSource(ref) {
  if (!ref || typeof ref !== 'object') return null;
  if (ref.ref_type === 'lists_item') {
    const id = String(ref.list_item_id ?? '');
    if (LIST_ID.test(id)) return { kind: 'lists', id, label: `Lists §${id}` };
  }
  if (ref.ref_type === 'onenote_page') {
    const id = field(ref.onenote_id, 120).toLowerCase();
    const pageRole = field(ref.page_role, 60);
    if (ONENOTE_ID.test(id)) return { kind: 'onenote', id, label: `OneNote ${id}`, ...(pageRole ? { pageRole } : {}) };
  }
  if (ref.ref_type === 'kb_document') {
    const id = field(ref.document_number, 120) || field(ref.kb_filename, 120);
    if (id && id !== 'manual') return { kind: 'technical', id, label: `技術KB ${id}` };
  }
  return null;
}

const newSources = [
  { kind: 'technical', id: 'manual', label: '技術KBで見つけた資料' },
  { kind: 'onenote', id: 'manual', label: '別のOneNoteページ' },
  { kind: 'lists', id: 'manual', label: '別のLists項目' },
];

/** Return the card's supported evidence references without inventing source links. */
export function getReviewSources(metadata) {
  const refs = Array.isArray(metadata?.source_refs) ? metadata.source_refs : [];
  const byKey = new Map();
  for (const ref of refs) {
    const source = refToSource(ref);
    if (!source) continue;
    const key = `${source.kind}:${source.id}`;
    const existing = byKey.get(key);
    if (!existing?.pageRole || NAVIGATION_ONLY.includes(source.pageRole)) byKey.set(key, source);
  }
  return [...byKey.values(), ...newSources.map((source) => ({ ...source }))];
}

/** Resolve a newly found OneNote or Lists source using its full identifier. */
export function resolveReviewSource(source, enteredId = '') {
  if (!source || source.id !== 'manual' || source.kind === 'technical') return source ?? null;
  if (source.kind === 'onenote') return refToSource({ ref_type: 'onenote_page', onenote_id: enteredId });
  if (source.kind === 'lists') return refToSource({ ref_type: 'lists_item', list_item_id: enteredId.trim() });
  return null;
}

function listsItem(body, sourceId) {
  const lines = body.replace(/\r\n?/gu, '\n').split('\n');
  const fenced = createFenceTracker();
  let start = -1;
  let end = lines.length;
  for (const [index, line] of lines.entries()) {
    if (fenced(line) || !SECTION_HEADING.test(line)) continue;
    if (start >= 0 && end === lines.length) end = index;
    if (LIST_HEADING.exec(line)?.[1] !== sourceId) continue;
    if (start >= 0) throw new TypeError('同じ項目番号が複数あります。元のListsを開いて確認してください。');
    start = index;
  }
  if (start < 0) throw new TypeError('カードと一致するLists項目が見つかりませんでした。');
  return lines.slice(start, end).join('\n').trim();
}

/** Read only the selected card reference from an explicitly chosen local snapshot. */
export function readReviewSourceSnapshot(markdown, source) {
  if (source?.kind !== 'lists' && source?.kind !== 'onenote') {
    throw new TypeError('OneNoteかListsの出典を選んでください。');
  }
  let parsed;
  try {
    parsed = parseKnowledgeFrontmatter(typeof markdown === 'string' ? markdown.replace(/^\uFEFF/u, '') : markdown, MAX_SOURCE_SNAPSHOT_BYTES);
  } catch {
    throw new TypeError('1 MiB以下のMarkdownの写しを選び、先頭のメタデータを確認してください。');
  }
  const { frontmatter, body } = parsed;
  const capturedOn = dateOnly(frontmatter.snapshot_date);
  if (source.kind === 'lists') {
    if (frontmatter.source_system !== 'Microsoft Lists' || frontmatter.snapshot_type !== 'lists_csv_import'
      || frontmatter.source_list_name !== SUPPORTED_LIST) {
      throw new TypeError('対象のLists（首都工・不具合情報共有リスト）のMarkdownの写しを選んでください。');
    }
    return { text: listsItem(body, source.id), capturedOn };
  }
  if (frontmatter.source_system !== 'OneNote' || frontmatter.snapshot_type !== 'onenote_source_page') {
    throw new TypeError('OneNoteページの写しを選んでください。');
  }
  if (!ONENOTE_ID.test(source.id) || field(frontmatter.onenote_id, 120).toLowerCase() !== source.id.toLowerCase()) {
    throw new TypeError('カードとOneNoteページのIDが一致しません。');
  }
  if (!body.trim()) throw new TypeError('このOneNoteの写しに本文がありません。');
  return { text: body.trim(), capturedOn };
}

/** Keep bounded reviewer notes and source identity with the body revision under review. */
export function normalizeSourceReview(input, metadata, revision) {
  const sources = getReviewSources(metadata);
  const supplied = input?.source;
  const chosen = sources.find((entry) => entry.id === supplied?.id && entry.kind === supplied.kind);
  const manual = sources.find((entry) => entry.id === 'manual' && entry.kind === supplied?.kind);
  const source = resolveReviewSource(chosen ?? manual, supplied?.id);
  const locator = field(input?.locator, 300);
  const note = field(input?.note, 2000);
  const timestamp = Date.parse(input?.recordedAt);
  const capturedOn = dateOnly(input?.capturedOn);
  const validMethod = input?.method === 'opened_original' || (input?.method === 'snapshot' && source?.kind !== 'technical');
  if (!source || !validMethod || !locator || !note || !OUTCOMES.includes(input?.outcome) || !Number.isFinite(timestamp)) {
    throw new TypeError('出典、参照箇所、確認結果と確認メモを入力してください。');
  }
  if (NAVIGATION_ONLY.includes(source.pageRole) && input.outcome !== 'insufficient') {
    throw new TypeError('索引や添付のみのページは参照用です。本文があるページを確認してください。');
  }
  if (input.capturedOn && !capturedOn) throw new TypeError('写しの取得日を確認してください。');
  return {
    source, method: input.method, ...(capturedOn ? { capturedOn } : {}), locator, outcome: input.outcome,
    note, recordedAt: new Date(timestamp).toISOString(), revision,
  };
}
