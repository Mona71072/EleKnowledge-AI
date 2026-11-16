import { stringify } from 'yaml';
import { parseKnowledgeFrontmatter } from './knowledge-markdown-frontmatter.mjs';
import { normalizeSourceReview } from './knowledge-source-review.mjs';
import { findCommentSection, MAX_REVIEW_COMMENT_CHARS } from './knowledge-comment-review.mjs';
import { getFieldMaterialSourceRefs } from './knowledge-field-material.mjs';

export const MAX_MARKDOWN_BODY_BYTES = 256 * 1024;
export const MAX_MARKDOWN_DOCUMENT_BYTES = MAX_MARKDOWN_BODY_BYTES + 64 * 1024;
const PROPOSAL_FORMAT = 'eleknowledge-knowledge-proposal/v1';

function fail(message) {
  throw new TypeError(message);
}

function cloneSafe(value) {
  if (Array.isArray(value)) return value.map(cloneSafe);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, child]) => [key, cloneSafe(child)]));
  }
  return value;
}

function getIdentity(frontmatter) {
  const card = Object.hasOwn(frontmatter, 'knowledge_id') || Object.hasOwn(frontmatter, 'card_version');
  const record = Object.hasOwn(frontmatter, 'record_id') || Object.hasOwn(frontmatter, 'record_version');
  if (card === record) fail('Frontmatter must contain exactly one supported ID and version pair.');

  const id = card ? frontmatter.knowledge_id : frontmatter.record_id;
  const version = card ? frontmatter.card_version : frontmatter.record_version;
  if (typeof id !== 'string' || id.trim().length === 0 || id.length > 200) fail('A valid knowledge ID is required.');
  if (!Number.isSafeInteger(version) || version < 1) fail('A positive integer version is required.');
  if (typeof frontmatter.title !== 'string' || frontmatter.title.trim().length === 0 || frontmatter.title.length > 500) {
    fail('A valid title is required.');
  }
  return { id, version, title: frontmatter.title, idField: card ? 'knowledge_id' : 'record_id' };
}

export function parseKnowledgeMarkdown(markdown, options) {
  const { frontmatter, body } = parseKnowledgeFrontmatter(markdown, MAX_MARKDOWN_DOCUMENT_BYTES, options);
  if (new TextEncoder().encode(body).byteLength > MAX_MARKDOWN_BODY_BYTES) fail('Markdown body exceeds 256 KiB.');
  const identity = getIdentity(frontmatter);
  const metadata = cloneSafe(frontmatter);
  return {
    id: identity.id,
    version: identity.version,
    title: identity.title,
    body,
    frontmatter: cloneSafe(frontmatter),
    metadata,
    originalMarkdown: markdown,
  };
}

export function createKnowledgeDraft(value) {
  const title = typeof value === 'string' ? value.trim() : '';
  if (!title || title.length > 200 || /[\u0000-\u001f\u007f-\u009f]/u.test(value)) fail('タイトルを1行、200文字以内で入力してください。');
  const metadata = {
    knowledge_id: `KH-FIELD-${globalThis.crypto.randomUUID().replaceAll('-', '').toUpperCase()}`,
    card_version: 1,
    kind: 'practice_guide',
    title,
    status: 'draft',
  };
  const heading = title.replace(/[\\`*_{}\[\]()#+.!|~<>]/gu, '\\$&');
  return parseKnowledgeMarkdown(`---\n${stringify(metadata, { schema: 'core' }).trimEnd()}\n---\n\n# ${heading}\n`);
}

function getSourceLines(metadata) {
  const lines = [];
  const refs = Array.isArray(metadata.source_refs) ? metadata.source_refs : [];
  for (const ref of refs) {
    if (!ref || typeof ref !== 'object') continue;
    if (ref.ref_type === 'lists_item' && ref.list_item_id != null) lines.push(`- Lists item ${String(ref.list_item_id)}`);
    else if (ref.ref_type === 'onenote_page' && ref.onenote_id) lines.push(`- OneNote page ${String(ref.onenote_id)}`);
    else if (ref.ref_type === 'kb_document' && (ref.kb_filename || ref.document_number)) {
      lines.push(`- KB ${String(ref.kb_filename || ref.document_number)}`);
    }
  }
  const evidence = Array.isArray(metadata.evidence_sources) ? metadata.evidence_sources : [];
  for (const item of evidence) {
    if (!item || typeof item !== 'object') continue;
    const label = [item.title, item.source_id].filter((part) => typeof part === 'string' && part.trim()).join(' — ');
    if (label && !lines.some((line) => line.includes(label))) lines.push(`- ${label}`);
  }
  return lines.length > 0 ? lines.join('\n') : '- （元Markdownに出典情報がありません。担当者が出典を確認してください）';
}

function makeOneNoteDraft(parsed) {
  return [
    `# ${parsed.title}：追記案`,
    '',
    '## 追加する要点',
    '（担当者が根拠を確認して記入）',
    '',
    '## 適用条件・注意点',
    '（担当者が適用条件を確認して記入）',
    '',
    '## 未確認事項',
    '（未確認事項があれば明記。確認できない場合は未確認のまま残す）',
    '',
    '## 出典',
    getSourceLines(parsed.metadata),
  ].join('\n');
}

export function createWorkspace(parsed) {
  if (!parsed || typeof parsed !== 'object' || typeof parsed.originalMarkdown !== 'string') {
    fail('A parsed Markdown document is required.');
  }
  const identity = { id: parsed.id, version: parsed.version, title: parsed.title };
  if (typeof identity.id !== 'string' || !Number.isSafeInteger(identity.version) || identity.version < 1 || typeof identity.title !== 'string') {
    fail('Parsed document identity is invalid.');
  }
  const metadata = cloneSafe(parsed.metadata || parsed.frontmatter || {});
  return {
    document: {
      id: identity.id,
      baseVersion: identity.version,
      title: identity.title,
      baseMarkdown: parsed.originalMarkdown,
      metadata,
    },
    body: parsed.body,
    noteText: makeOneNoteDraft({ title: identity.title, metadata }),
    kbReview: { status: 'unverified', reference: '', note: '' },
    revision: 0,
    noteNeedsReconcile: false,
    reviewedRevision: null,
    copiedRevision: null,
    placements: [],
    sourceReviews: [],
    reviewComments: [],
  };
}

function changed(state, patch, options = {}) {
  if (!state || typeof state !== 'object') fail('A workspace state is required.');
  return {
    ...state,
    ...patch,
    kbReview: { status: 'unverified', reference: '', note: '' },
    revision: state.revision + 1,
    noteNeedsReconcile: options.noteNeedsReconcile ?? state.noteNeedsReconcile,
    reviewedRevision: null,
    copiedRevision: null,
    placements: [...state.placements],
  };
}

export function editBody(state, body) {
  if (typeof body !== 'string') fail('Markdown body must be a string.');
  if (new TextEncoder().encode(body).byteLength > MAX_MARKDOWN_BODY_BYTES || body.includes('\0')) fail('Markdown body is invalid or too large.');
  return changed(state, { body }, { noteNeedsReconcile: true });
}

export function editOneNoteDraft(state, text) {
  if (typeof text !== 'string') fail('OneNote draft must be a string.');
  if (new TextEncoder().encode(text).byteLength > MAX_MARKDOWN_BODY_BYTES || text.includes('\0')) fail('OneNote draft is invalid or too large.');
  return changed(state, { noteText: text });
}

export function setKbReview(state, review) {
  if (!review || !['unverified', 'reviewed', 'conflict'].includes(review.status)) fail('Invalid KB review status.');
  const reference = typeof review.reference === 'string' ? review.reference.trim() : '';
  const note = typeof review.note === 'string' ? review.note.trim() : '';
  if (review.status !== 'unverified' && (!reference || !note)) fail('A KB reference and review note are required.');
  const next = changed(state, { kbReview: { status: review.status, reference, note } });
  return { ...next, kbReview: { status: review.status, reference, note } };
}

export function confirmOneNote(state, confirmation) {
  if (!confirmation || confirmation.checked !== true) fail('The content, evidence, applicability, and audience must be confirmed.');
  if (state.noteNeedsReconcile && confirmation.noteReconciled !== true) {
    fail('Reconcile the OneNote draft with the edited Markdown before confirming.');
  }
  if (state.kbReview?.status !== 'reviewed' || !state.kbReview.reference || !state.kbReview.note) {
    fail('Review the KB evidence and record its reference before confirming.');
  }
  return {
    ...state,
    noteNeedsReconcile: false,
    reviewedRevision: state.revision,
    copiedRevision: null,
    placements: [...state.placements],
  };
}

export function markCopied(state, expectedRevision) {
  if (!Number.isSafeInteger(expectedRevision) || expectedRevision !== state.revision) fail('The copied text belongs to a stale revision.');
  if (state.reviewedRevision !== state.revision) fail('Confirm the current OneNote draft before copying it.');
  return { ...state, copiedRevision: state.revision, placements: [...state.placements] };
}

/** Record the evidence a person consulted at the current work revision. */
export function recordSourceReview(state, input) {
  const record = normalizeSourceReview(input, state.document.metadata, state.revision);
  const reviews = state.sourceReviews ?? [];
  const currentSource = (entry) => entry.revision === record.revision && entry.source.kind === record.source.kind
    && entry.source.id === record.source.id && entry.locator === record.locator;
  return { ...state, sourceReviews: [...reviews.filter((entry) => !currentSource(entry)), record] };
}

/** Save the requested research focus without modifying Markdown. */
export function addReviewComment(state, { id, sectionId, text }) {
  const comment = typeof text === 'string' ? text.trim() : '';
  const comments = state.reviewComments ?? [];
  const section = findCommentSection(state.body, sectionId);
  if (typeof id !== 'string' || !/^[a-z0-9-]{1,80}$/iu.test(id) || comments.some((entry) => entry.id === id)
    || !section || !comment || Array.from(comment).length > MAX_REVIEW_COMMENT_CHARS || comment.includes('\0')) {
    fail('確認する節とコメントを指定してください。');
  }
  if (comments.length >= 50) fail('この作業に記録できるコメントは50件までです。');
  return {
    ...state,
    reviewComments: [...comments, { id, sectionId, sectionLabel: section.label, text: comment, status: 'open', revision: state.revision }],
  };
}

/** Apply an explicit preview only if the document still matches its base body. */
export function applyReviewComment(state, id, expectedBody, body) {
  const comments = state.reviewComments ?? [];
  const comment = comments.find((entry) => entry.id === id && entry.status === 'open');
  if (state.body !== expectedBody || body === expectedBody || !comment
    || !findCommentSection(state.body, comment.sectionId, comment.sectionLabel)) {
    fail('本文またはコメントの状態が変わりました。');
  }
  const next = editBody(state, body);
  return {
    ...next,
    reviewComments: comments.map((entry) => entry.id === id
      ? { ...entry, status: 'applied', appliedRevision: next.revision }
      : entry),
  };
}

function validDestination(destination) {
  if (typeof destination !== 'string' || destination.length > 2048) return false;
  const normalized = destination.startsWith('onenote:https://') ? destination.slice('onenote:'.length) : destination;
  if (!normalized.startsWith('https://')) return false;
  try {
    const url = new URL(normalized);
    return url.protocol === 'https:' && Boolean(url.hostname) && !url.username && !url.password;
  } catch {
    return false;
  }
}

function validTimestamp(recordedAt) {
  if (typeof recordedAt !== 'string') return false;
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$/.exec(recordedAt);
  if (!match || !Number.isFinite(Date.parse(recordedAt))) return false;
  const [, year, month, day, hour, minute, second] = match;
  const date = new Date(`${year}-${month}-${day}T00:00:00Z`);
  return date.getUTCFullYear() === Number(year)
    && date.getUTCMonth() + 1 === Number(month)
    && date.getUTCDate() === Number(day)
    && Number(hour) < 24
    && Number(minute) < 60
    && Number(second) < 60;
}

export function recordPlacement(state, placement) {
  if (state.reviewedRevision !== state.revision || state.copiedRevision !== state.revision) {
    fail('Confirm and copy the current draft before recording a OneNote placement.');
  }
  if (!validDestination(placement?.destination)) fail('A valid OneNote page URL is required.');
  if (!validTimestamp(placement?.recordedAt)) fail('A valid placement timestamp with timezone is required.');
  const receipt = {
    destination: placement.destination,
    recordedAt: placement.recordedAt,
    destinationVerified: false,
    verification: 'self_reported',
    baseVersion: state.document.baseVersion,
    revision: state.revision,
    text: state.noteText,
  };
  return { ...state, placements: [...state.placements, receipt] };
}

async function sha256(text) {
  const cryptoApi = globalThis.crypto;
  if (!cryptoApi?.subtle) fail('Web Crypto SHA-256 is unavailable.');
  const digest = await cryptoApi.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

export function createProposalMetadata(metadata, body) {
  const frontmatter = { ...metadata, status: 'draft' };
  if (Object.hasOwn(metadata, 'review_status')) frontmatter.review_status = 'in_review';
  if (Object.hasOwn(metadata, 'publication_status')) frontmatter.publication_status = 'not_published';
  if (Object.hasOwn(metadata, 'cloud_approval')) frontmatter.cloud_approval = 'not_reviewed';
  const fieldRefs = getFieldMaterialSourceRefs(body);
  if (fieldRefs.length) {
    const refs = Array.isArray(frontmatter.source_refs) ? frontmatter.source_refs : [];
    const existingFieldIds = new Set(refs.filter((ref) => ref?.ref_type === 'knowhow' && ref?.origin === 'field_report')
      .map((ref) => ref.knowhow_id));
    frontmatter.source_refs = [...refs, ...fieldRefs.filter((ref) => !existingFieldIds.has(ref.knowhow_id))];
  }
  return frontmatter;
}

function createProposalMarkdown(state) {
  const frontmatter = createProposalMetadata(state.document.metadata, state.body);
  return `---\n${stringify(frontmatter, { schema: 'core' }).trimEnd()}\n---\n\n${state.body}`;
}

export async function exportProposal(state) {
  const baseMarkdown = state.document.baseMarkdown;
  const placements = await Promise.all(state.placements.map(async (receipt) => ({
    knowledgeId: state.document.id,
    baseVersion: receipt.baseVersion,
    revision: receipt.revision,
    text: receipt.text,
    destination: receipt.destination,
    recordedAt: receipt.recordedAt,
    destinationVerified: false,
    verification: 'self_reported',
    textSha256: await sha256(receipt.text),
  })));
  return {
    format: PROPOSAL_FORMAT,
    base: {
      id: state.document.id,
      version: state.document.baseVersion,
      markdown: baseMarkdown,
      metadata: cloneSafe(state.document.metadata),
    },
    proposal: {
      revision: state.revision,
      markdown: createProposalMarkdown(state),
      oneNoteText: state.noteText,
      publishable: false,
      state: 'working-proposal',
    },
    noteNeedsReconcile: state.noteNeedsReconcile,
    reviewedRevision: state.reviewedRevision,
    copiedRevision: state.copiedRevision,
    placements,
    kbReview: cloneSafe(state.kbReview),
    sourceReviews: cloneSafe(state.sourceReviews ?? []),
    reviewComments: cloneSafe(state.reviewComments ?? []),
    hashes: {
      baseMarkdownSha256: await sha256(baseMarkdown),
      bodySha256: await sha256(state.body),
      oneNoteTextSha256: await sha256(state.noteText),
    },
  };
}
