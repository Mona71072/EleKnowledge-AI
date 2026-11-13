import { createWorkspace, parseKnowledgeMarkdown } from './knowledge-workbench.mjs';
import { listCommentSections, MAX_REVIEW_COMMENT_CHARS } from './knowledge-comment-review.mjs';
import { normalizeSourceReview } from './knowledge-source-review.mjs';

/** 保存側（exportProposal）が書き出す形式の識別子。変更時は両方を同時に直す。 */
const PROPOSAL_FORMAT = 'eleknowledge-knowledge-proposal/v1';
export const MAX_REVIEW_RECORD_BYTES = 4 * 1024 * 1024;
const MAX_MARKDOWN_BYTES = 256 * 1024;
const MAX_COMMENTS = 50;
const MAX_SOURCE_REVIEWS = 200;
const MAX_PLACEMENTS = 100;
const SHA256 = /^[a-f0-9]{64}$/u;
const COMMENT_ID = /^[a-z0-9-]{1,80}$/iu;
const TOP_KEYS = ['format', 'base', 'proposal', 'noteNeedsReconcile', 'reviewedRevision', 'copiedRevision',
  'placements', 'kbReview', 'sourceReviews', 'reviewComments', 'hashes'];
const PLACEMENT_KEYS = ['knowledgeId', 'baseVersion', 'revision', 'text', 'destination', 'recordedAt',
  'destinationVerified', 'verification', 'textSha256'];

function fail(message) {
  throw new TypeError(message);
}

const encoder = new TextEncoder();
const byteLength = (text) => encoder.encode(text).byteLength;
const isRecord = (value) => Boolean(value) && typeof value === 'object' && !Array.isArray(value);
const hasExactKeys = (value, keys) => isRecord(value) && Object.keys(value).length === keys.length
  && keys.every((key) => Object.hasOwn(value, key));
const isCount = (value) => Number.isSafeInteger(value) && value >= 0;
const isBoundedText = (value, maxBytes) => typeof value === 'string' && !value.includes('\0') && byteLength(value) <= maxBytes;

function sameJson(a, b) {
  if (Array.isArray(a) || Array.isArray(b)) {
    return Array.isArray(a) && Array.isArray(b) && a.length === b.length && a.every((item, index) => sameJson(item, b[index]));
  }
  if (isRecord(a) && isRecord(b)) {
    const keys = Object.keys(a);
    return keys.length === Object.keys(b).length && keys.every((key) => Object.hasOwn(b, key) && sameJson(a[key], b[key]));
  }
  return Object.is(a, b);
}

// hash は壊れたファイル・別の版の記録・書き換えの取りこぼしを見つけるための確認で、改ざんを防ぐ仕組みではない
// （同じファイル内の値から再計算できるため）。検査の失敗は「破損または別の版」として案内する。
async function sha256(text) {
  const subtle = globalThis.crypto?.subtle;
  if (!subtle) fail('このブラウザーではファイルの整合性を確認できません。');
  const digest = await subtle.digest('SHA-256', encoder.encode(text));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function parseCard(markdown, label) {
  if (!isBoundedText(markdown, MAX_MARKDOWN_BYTES)) fail(`${label}のMarkdownが不正か、256 KiBを超えています。`);
  try {
    return parseKnowledgeMarkdown(markdown);
  } catch {
    fail(`${label}のMarkdownのID・版・タイトルとYAML形式を確認してください。`);
  }
  return null;
}

/** 保存側 createProposalMarkdown と同じ規則で、原文のメタデータから修正案の先頭部分を再構成する。 */
function expectedProposalMetadata(metadata) {
  const next = structuredClone(metadata);
  next.status = 'draft';
  if (Object.hasOwn(next, 'review_status')) next.review_status = 'in_review';
  if (Object.hasOwn(next, 'publication_status')) next.publication_status = 'not_published';
  if (Object.hasOwn(next, 'cloud_approval')) next.cloud_approval = 'not_reviewed';
  return next;
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

function validTimestamp(value) {
  const match = typeof value === 'string'
    ? /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$/u.exec(value) : null;
  if (!match || !Number.isFinite(Date.parse(value))) return false;
  const [, year, month, day, hour, minute, second] = match;
  const date = new Date(`${year}-${month}-${day}T00:00:00Z`);
  return date.getUTCFullYear() === Number(year) && date.getUTCMonth() + 1 === Number(month)
    && date.getUTCDate() === Number(day) && Number(hour) < 24 && Number(minute) < 60 && Number(second) < 60;
}

function restoreComments(raw, body, revision) {
  if (!Array.isArray(raw) || raw.length > MAX_COMMENTS) fail(`コメントの形式が不正か、${MAX_COMMENTS}件を超えています。`);
  const ids = new Set();
  const sections = listCommentSections(body);
  return raw.map((entry) => {
    const applied = isRecord(entry) && entry.status === 'applied';
    const keys = ['id', 'sectionId', 'sectionLabel', 'text', 'status', 'revision', ...(applied ? ['appliedRevision'] : [])];
    const text = isRecord(entry) && typeof entry.text === 'string' ? entry.text : '';
    const valid = hasExactKeys(entry, keys) && typeof entry.id === 'string' && COMMENT_ID.test(entry.id) && !ids.has(entry.id)
      && typeof entry.sectionId === 'string' && entry.sectionId.length <= 300
      && typeof entry.sectionLabel === 'string' && entry.sectionLabel.length <= 600
      && text.trim() === text && text !== '' && !text.includes('\0') && Array.from(text).length <= MAX_REVIEW_COMMENT_CHARS
      && (entry.status === 'open' || applied) && isCount(entry.revision) && entry.revision <= revision
      && (!applied || (isCount(entry.appliedRevision) && entry.appliedRevision <= revision));
    if (!valid) fail('コメントの形式が不正です。ファイルが壊れているか、別の版の記録です。この画面で保存したJSON作業記録を選び直してください。');
    ids.add(entry.id);
    // 節が本文から無くなったコメントは残す。節が残っているのに見出し名が違うものは別物として拒否する。
    const section = sections.find((candidate) => candidate.id === entry.sectionId);
    if (section && section.label !== entry.sectionLabel) fail('コメントの節の見出しが本文と一致しません。');
    return { ...entry };
  });
}

function restoreSourceReviews(raw, metadata, revision) {
  if (!Array.isArray(raw) || raw.length > MAX_SOURCE_REVIEWS) fail('出典の確認記録の形式が不正か、件数が多すぎます。');
  return raw.map((entry) => {
    if (!isRecord(entry) || !isCount(entry.revision) || entry.revision > revision) {
      fail('出典の確認記録の版が修正案と一致しません。');
    }
    let record;
    try {
      const { revision: entryRevision, ...input } = entry;
      record = normalizeSourceReview(input, metadata, entryRevision);
    } catch {
      fail('出典の確認記録の内容が不正です。');
    }
    if (!sameJson(record, entry)) fail('出典の確認記録の内容が正規の形式と一致しません。');
    return record;
  });
}

async function restorePlacements(raw, base, revision) {
  if (!Array.isArray(raw) || raw.length > MAX_PLACEMENTS) fail('配置記録の形式が不正か、件数が多すぎます。');
  const receipts = [];
  for (const entry of raw) {
    const valid = hasExactKeys(entry, PLACEMENT_KEYS) && entry.knowledgeId === base.id && entry.baseVersion === base.version
      && isCount(entry.revision) && entry.revision <= revision && isBoundedText(entry.text, MAX_MARKDOWN_BYTES)
      && validDestination(entry.destination) && validTimestamp(entry.recordedAt)
      && entry.destinationVerified === false && entry.verification === 'self_reported';
    if (!valid) fail('配置記録（placement receipt）の内容が不正です。');
    if (typeof entry.textSha256 !== 'string' || !SHA256.test(entry.textSha256) || entry.textSha256 !== await sha256(entry.text)) {
      fail('配置記録（receipt）のhashが本文と一致しません。');
    }
    receipts.push({
      destination: entry.destination, recordedAt: entry.recordedAt, destinationVerified: false,
      verification: 'self_reported', baseVersion: entry.baseVersion, revision: entry.revision, text: entry.text,
    });
  }
  return receipts;
}

function parseRecord(text) {
  if (typeof text !== 'string') fail('JSON作業記録を読み込めませんでした。');
  if (byteLength(text) > MAX_REVIEW_RECORD_BYTES) fail('JSON作業記録が大きすぎます（4 MiB以下にしてください）。');
  let packet;
  try {
    packet = JSON.parse(text);
  } catch {
    fail('JSONとして読み込めませんでした。この画面で保存したJSON作業記録を選んでください。');
  }
  if (!isRecord(packet)) fail('JSON作業記録の形式が不正です。');
  if (typeof packet.format === 'string' && packet.format !== PROPOSAL_FORMAT && packet.format.startsWith('eleknowledge-knowledge-proposal/')) {
    fail('この作業記録は別の版の形式のため開けません。');
  }
  if (!hasExactKeys(packet, TOP_KEYS) || packet.format !== PROPOSAL_FORMAT) fail('JSON作業記録の形式が不正です。');
  return packet;
}

/**
 * 保存済みのJSON作業記録から作業画面の状態を復元する。入力は信用せず、原文・修正案・各記録を検証する。
 * 確認済み・コピー済みの状態と技術KBの確認結果は復元しない。配置記録は自己申告の履歴としてだけ残す。
 * @param {string} text JSON作業記録の本文
 * @returns {Promise<{ parsed: import('./knowledge-workbench.mjs').KnowledgeParsedMarkdown, workspace: object }>}
 */
export async function restoreReviewWorkspace(text) {
  const packet = parseRecord(text);
  const { base, proposal, hashes } = packet;
  if (!hasExactKeys(base, ['id', 'version', 'markdown', 'metadata'])
    || !hasExactKeys(proposal, ['revision', 'markdown', 'oneNoteText', 'publishable', 'state'])
    || !hasExactKeys(hashes, ['baseMarkdownSha256', 'bodySha256', 'oneNoteTextSha256'])) {
    fail('JSON作業記録の形式が不正です。');
  }
  const parsed = parseCard(base.markdown, '原文');
  if (base.id !== parsed.id || base.version !== parsed.version || !sameJson(base.metadata, parsed.metadata)) {
    fail('原文（base）の情報とMarkdownのメタデータが一致しません。');
  }
  const proposed = parseCard(proposal.markdown, '修正案');
  if (proposed.id !== parsed.id || proposed.version !== parsed.version) fail('修正案のIDまたは版が原文と一致しません。');
  if (!sameJson(proposed.metadata, expectedProposalMetadata(parsed.metadata))) fail('修正案のメタデータが原文と一致しません。');
  if (!isCount(proposal.revision) || proposal.publishable !== false || proposal.state !== 'working-proposal'
    || !isBoundedText(proposal.oneNoteText, MAX_MARKDOWN_BYTES) || typeof packet.noteNeedsReconcile !== 'boolean') {
    fail('修正案の情報が不正です。');
  }
  const [baseHash, bodyHash, noteHash] = await Promise.all([
    sha256(base.markdown), sha256(proposed.body), sha256(proposal.oneNoteText),
  ]);
  if (hashes.baseMarkdownSha256 !== baseHash || hashes.bodySha256 !== bodyHash || hashes.oneNoteTextSha256 !== noteHash) {
    fail('作業記録のhashが一致しません。ファイルが壊れているか、別の版の記録です。この画面で保存した作業記録を選び直してください。');
  }
  const revision = proposal.revision;
  const sourceReviews = restoreSourceReviews(packet.sourceReviews, parsed.metadata, revision);
  const reviewComments = restoreComments(packet.reviewComments, proposed.body, revision);
  const placements = await restorePlacements(packet.placements, base, revision);
  const workspace = {
    ...createWorkspace(parsed),
    body: proposed.body,
    noteText: proposal.oneNoteText,
    revision,
    noteNeedsReconcile: packet.noteNeedsReconcile,
    placements,
    sourceReviews,
    reviewComments,
  };
  return { parsed, workspace };
}
