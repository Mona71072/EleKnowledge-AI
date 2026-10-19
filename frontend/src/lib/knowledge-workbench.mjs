import { isAlias, isMap, isScalar, isSeq, parseDocument, stringify } from 'yaml';

const MAX_MARKDOWN_BYTES = 256 * 1024;
const MAX_FRONTMATTER_DEPTH = 32;
const MAX_FRONTMATTER_NODES = 12_000;
const DANGEROUS_KEYS = new Set(['__proto__', 'prototype', 'constructor']);
const PROPOSAL_FORMAT = 'eleknowledge-knowledge-proposal/v1';

function fail(message) {
  throw new TypeError(message);
}

function parseFrontmatter(markdown) {
  if (typeof markdown !== 'string') fail('Markdown must be a string.');
  if (markdown.includes('\0')) fail('Markdown cannot contain NUL bytes.');
  if (new TextEncoder().encode(markdown).byteLength > MAX_MARKDOWN_BYTES) {
    fail('Markdown exceeds the 256 KiB limit.');
  }

  const firstLineEnd = markdown.indexOf('\n');
  if (firstLineEnd < 0 || !/^---\r?$/.test(markdown.slice(0, firstLineEnd))) {
    fail('Markdown must start with YAML frontmatter.');
  }

  const firstContentOffset = firstLineEnd + 1;
  let cursor = firstContentOffset;
  let closingStart = -1;
  let closingEnd = -1;
  while (cursor <= markdown.length) {
    const lineEnd = markdown.indexOf('\n', cursor);
    const end = lineEnd < 0 ? markdown.length : lineEnd;
    const line = markdown.slice(cursor, end).replace(/\r$/, '');
    if (line === '---') {
      closingStart = cursor;
      closingEnd = lineEnd < 0 ? end : lineEnd + 1;
      break;
    }
    if (lineEnd < 0) break;
    cursor = lineEnd + 1;
  }
  if (closingStart < 0) fail('YAML frontmatter closing delimiter is missing.');

  const yamlText = markdown.slice(firstContentOffset, closingStart);
  const document = parseDocument(yamlText, {
    schema: 'core',
    uniqueKeys: true,
    version: '1.2',
  });
  if (document.errors.length > 0 || document.warnings.length > 0) {
    fail('YAML frontmatter contains a parse error or warning.');
  }
  if (!document.contents || !isMap(document.contents)) fail('YAML frontmatter must be a mapping.');

  validateYamlNodes(document.contents);
  let value;
  try {
    value = document.toJS({ maxAliasCount: 0, mapAsMap: false });
  } catch {
    fail('YAML aliases or unsupported values are not allowed.');
  }
  validatePlainValue(value);

  const afterFence = markdown.slice(closingEnd);
  const body = afterFence.startsWith('\r\n')
    ? afterFence.slice(2)
    : afterFence.startsWith('\n')
      ? afterFence.slice(1)
      : afterFence;
  return { frontmatter: value, body };
}

function validateYamlNodes(node) {
  if (!node) return;
  if (isAlias(node)) fail('YAML aliases are not allowed.');
  if (node.anchor) fail('YAML anchors are not allowed.');
  if (node.tag) fail('Explicit YAML tags are not allowed.');
  if (isMap(node)) {
    for (const pair of node.items) {
      validateYamlNodes(pair.key);
      validateYamlNodes(pair.value);
    }
    return;
  }
  if (isSeq(node)) {
    for (const item of node.items) validateYamlNodes(item);
    return;
  }
  if (!isScalar(node)) fail('Unsupported YAML node type.');
}

function validatePlainValue(value) {
  let count = 0;
  const visit = (current, depth) => {
    count += 1;
    if (count > MAX_FRONTMATTER_NODES || depth > MAX_FRONTMATTER_DEPTH) {
      fail('YAML frontmatter is too deeply nested or contains too many values.');
    }
    if (current === null || ['string', 'boolean'].includes(typeof current)) return;
    if (typeof current === 'number') {
      if (!Number.isFinite(current)) fail('Non-finite YAML numbers are not allowed.');
      return;
    }
    if (Array.isArray(current)) {
      for (const item of current) visit(item, depth + 1);
      return;
    }
    const prototype = current && typeof current === 'object' ? Object.getPrototypeOf(current) : undefined;
    if (typeof current !== 'object' || (prototype !== null && prototype !== Object.prototype)) {
      fail('YAML frontmatter must contain only plain JSON-like values.');
    }
    for (const [key, child] of Object.entries(current)) {
      if (DANGEROUS_KEYS.has(key) || key === '<<') fail('Unsafe YAML mapping key.');
      visit(child, depth + 1);
    }
  };
  visit(value, 0);
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

export function parseKnowledgeMarkdown(markdown) {
  const { frontmatter, body } = parseFrontmatter(markdown);
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
    '## 現在のMarkdown本文（担当者が確認）',
    parsed.body || '（本文がありません。担当者が内容を確認してください）',
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
    noteText: makeOneNoteDraft({ title: identity.title, metadata, body: parsed.body }),
    kbReview: { status: 'unverified', reference: '', note: '' },
    revision: 0,
    reviewedRevision: null,
    copiedRevision: null,
    placements: [],
  };
}

function changed(state, patch) {
  if (!state || typeof state !== 'object') fail('A workspace state is required.');
  return {
    ...state,
    ...patch,
    kbReview: { status: 'unverified', reference: '', note: '' },
    revision: state.revision + 1,
    reviewedRevision: null,
    copiedRevision: null,
    placements: [...state.placements],
  };
}

export function editBody(state, body) {
  if (typeof body !== 'string') fail('Markdown body must be a string.');
  if (new TextEncoder().encode(body).byteLength > MAX_MARKDOWN_BYTES || body.includes('\0')) fail('Markdown body is invalid or too large.');
  return changed(state, { body });
}

export function editOneNoteDraft(state, text) {
  if (typeof text !== 'string') fail('OneNote draft must be a string.');
  if (new TextEncoder().encode(text).byteLength > MAX_MARKDOWN_BYTES || text.includes('\0')) fail('OneNote draft is invalid or too large.');
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
  if (state.kbReview?.status !== 'reviewed' || !state.kbReview.reference || !state.kbReview.note) {
    fail('Review the KB evidence and record its reference before confirming.');
  }
  return { ...state, reviewedRevision: state.revision, copiedRevision: null, placements: [...state.placements] };
}

export function markCopied(state, expectedRevision) {
  if (!Number.isSafeInteger(expectedRevision) || expectedRevision !== state.revision) fail('The copied text belongs to a stale revision.');
  if (state.reviewedRevision !== state.revision) fail('Confirm the current OneNote draft before copying it.');
  return { ...state, copiedRevision: state.revision, placements: [...state.placements] };
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

function createProposalMarkdown(state) {
  const frontmatter = cloneSafe(state.document.metadata);
  frontmatter.status = 'draft';
  if (Object.hasOwn(frontmatter, 'review_status')) frontmatter.review_status = 'in_review';
  if (Object.hasOwn(frontmatter, 'publication_status')) frontmatter.publication_status = 'not_published';
  if (Object.hasOwn(frontmatter, 'cloud_approval')) frontmatter.cloud_approval = 'not_reviewed';
  return `---\n${stringify(frontmatter, { schema: 'core' }).trimEnd()}\n---\n${state.body}`;
}

export async function exportProposal(state) {
  const baseMarkdown = state.document.baseMarkdown;
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
    kbReview: cloneSafe(state.kbReview),
    hashes: {
      baseMarkdownSha256: await sha256(baseMarkdown),
      bodySha256: await sha256(state.body),
      oneNoteTextSha256: await sha256(state.noteText),
    },
  };
}

