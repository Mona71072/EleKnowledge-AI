import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import test from 'node:test';

import {
  addReviewComment,
  createWorkspace,
  editBody,
  editOneNoteDraft,
  exportProposal,
  parseKnowledgeMarkdown,
  recordPlacement,
  recordSourceReview,
  setKbReview,
  confirmOneNote,
  markCopied,
} from '../src/lib/knowledge-workbench.mjs';
import { restoreReviewWorkspace } from '../src/lib/knowledge-review-resume.mjs';

const BASE = [
  '---',
  'record_id: resume-card',
  'record_version: 4',
  'title: Resume card',
  'status: approved',
  'source_refs:',
  '  - ref_type: lists_item',
  '    list_item_id: 71',
  '---',
  '',
  '# Resume card',
  '',
  'Original body.',
  '',
  '## Conditions',
  'Original conditions.',
].join('\n');

const parsed = () => parseKnowledgeMarkdown(BASE);
const workspace = () => createWorkspace(parsed());
const digest = (value) => createHash('sha256').update(value, 'utf8').digest('hex');

async function packetWithHistory() {
  const sourceReviewed = recordSourceReview(workspace(), {
    source: { kind: 'lists', id: '71', label: 'Lists §71' },
    method: 'snapshot',
    capturedOn: '2026-10-20',
    locator: 'Lists item 71, Conditions',
    outcome: 'supports',
    note: 'Checked source conditions.',
    recordedAt: '2026-10-20T10:00:00Z',
  });
  const commentState = addReviewComment(sourceReviewed, {
    id: 'check-condition', sectionId: 'section-conditions-1', text: 'Confirm the temperature range.',
  });
  const edited = editOneNoteDraft(
    editBody(commentState, `${commentState.body}\nUpdated condition.`),
    'Draft note with an unresolved item.',
  );
  return exportProposal(edited);
}

test('restores proposal body against the exact base and keeps comments, evidence, and note draft', async () => {
  const packet = await packetWithHistory();
  const restored = await restoreReviewWorkspace(JSON.stringify(packet));

  assert.equal(restored.parsed.originalMarkdown, BASE);
  assert.equal(restored.workspace.document.baseMarkdown, BASE);
  assert.equal(restored.workspace.body, `${parsed().body}\nUpdated condition.`);
  assert.equal(restored.workspace.noteText, 'Draft note with an unresolved item.');
  assert.equal(restored.workspace.revision, packet.proposal.revision);
  assert.deepEqual(restored.workspace.reviewComments, packet.reviewComments);
  assert.deepEqual(restored.workspace.sourceReviews, packet.sourceReviews);
  assert.deepEqual(restored.workspace.kbReview, { status: 'unverified', reference: '', note: '' });
  assert.equal(restored.workspace.reviewedRevision, null);
  assert.equal(restored.workspace.copiedRevision, null);
  assert.equal(restored.workspace.placements.length, 0);
});

test('preserves historical self-reported placement receipt without restoring copy privileges', async () => {
  const base = workspace();
  const reviewed = setKbReview(base, { status: 'reviewed', reference: 'KB-1', note: 'Checked.' });
  const confirmed = confirmOneNote(reviewed, { checked: true });
  const copied = markCopied(confirmed, confirmed.revision);
  const placed = recordPlacement(copied, {
    destination: 'onenote:https://tenant.example/page/1', recordedAt: '2026-10-20T10:00:00Z',
  });
  const packet = await exportProposal(placed);
  const restored = await restoreReviewWorkspace(JSON.stringify(packet));

  assert.equal(restored.workspace.placements.length, 1);
  assert.deepEqual(restored.workspace.placements[0], placed.placements[0]);
  assert.equal(restored.workspace.reviewedRevision, null);
  assert.equal(restored.workspace.copiedRevision, null);
});

test('rejects a tampered body even when packet identity and base are unchanged', async () => {
  const packet = await packetWithHistory();
  const tampered = structuredClone(packet);
  tampered.proposal.markdown = tampered.proposal.markdown.replace('Updated condition.', 'Forged condition.');

  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(tampered)), /hash|一致/u);
});

test('整合性の検査は破損の検出として案内し、改ざん検知とは言わない', async () => {
  const packet = await packetWithHistory();
  const damaged = structuredClone(packet);
  damaged.proposal.markdown = damaged.proposal.markdown.replace('Updated condition.', 'Forged condition.');
  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(damaged)), (error) => {
    assert.match(error.message, /壊れているか、別の版の記録です/u);
    assert.doesNotMatch(error.message, /改変|改ざん|改竄/u);
    return true;
  });
  const badComment = structuredClone(packet);
  badComment.reviewComments = [{ id: 'x' }];
  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(badComment)), (error) => {
    assert.doesNotMatch(error.message, /改変|改ざん|改竄/u);
    return true;
  });
});

test('rejects a mismatched proposal identity and malformed review data', async () => {
  const packet = await packetWithHistory();
  const wrongId = structuredClone(packet);
  wrongId.proposal.markdown = wrongId.proposal.markdown.replace('record_id: resume-card', 'record_id: another-card');
  wrongId.hashes.bodySha256 = digest(parseKnowledgeMarkdown(wrongId.proposal.markdown).body);
  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(wrongId)), /ID|ID|一致/u);

  const malformedComment = structuredClone(packet);
  malformedComment.reviewComments[0].sectionLabel = 'Other section';
  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(malformedComment)), /コメント|節|section/u);
});

test('rejects inconsistent base metadata, receipt hashes, invalid source reviews, and oversized JSON', async () => {
  const packet = await packetWithHistory();
  const badMetadata = structuredClone(packet);
  badMetadata.base.metadata.status = 'published';
  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(badMetadata)), /base|原文|metadata/u);

  const badReceipt = structuredClone(packet);
  badReceipt.placements = [{
    knowledgeId: packet.base.id, baseVersion: packet.base.version, revision: 0,
    text: 'historical copy', destination: 'https://tenant.example/page/1', recordedAt: '2026-10-20T10:00:00Z',
    destinationVerified: false, verification: 'self_reported', textSha256: '0'.repeat(64),
  }];
  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(badReceipt)), /placement|receipt|hash|配置/u);

  const badSource = structuredClone(packet);
  badSource.sourceReviews[0].revision = packet.proposal.revision + 1;
  await assert.rejects(() => restoreReviewWorkspace(JSON.stringify(badSource)), /source|出典|revision|確認/u);

  await assert.rejects(() => restoreReviewWorkspace(' '.repeat(4 * 1024 * 1024 + 1)), /4 MiB|大き/u);
});

const restoreFails = async (value, pattern) => assert.rejects(
  () => restoreReviewWorkspace(typeof value === 'string' ? value : JSON.stringify(value)), pattern,
);

test('rejects broken JSON, non-object JSON, other format versions, and extra top-level keys with Japanese messages', async () => {
  const packet = await packetWithHistory();
  await restoreFails('{broken', /JSON/u);
  await restoreFails('[]', /形式/u);
  await restoreFails('null', /形式/u);
  await restoreFails({ ...packet, format: 'eleknowledge-knowledge-proposal/v2' }, /版/u);
  await restoreFails({ ...packet, format: 'something-else' }, /形式/u);
  await restoreFails({ ...packet, extra: 1 }, /形式/u);
  const { reviewComments, ...missing } = packet;
  assert.ok(reviewComments);
  await restoreFails(missing, /形式/u);
});

test('rejects non-string input and oversized fields', async () => {
  await assert.rejects(() => restoreReviewWorkspace(undefined), /読み込めません/u);
  const packet = await packetWithHistory();
  const huge = structuredClone(packet);
  huge.proposal.oneNoteText = 'a'.repeat(256 * 1024 + 1);
  await restoreFails(huge, /修正案の情報/u);
  const longComment = structuredClone(packet);
  longComment.reviewComments[0].text = 'あ'.repeat(901);
  await restoreFails(longComment, /コメント/u);
});

test('rejects a record whose base belongs to another card version or whose base id differs', async () => {
  const packet = await packetWithHistory();
  const otherVersion = structuredClone(packet);
  otherVersion.base.version = 5;
  await restoreFails(otherVersion, /原文/u);
  const otherId = structuredClone(packet);
  otherId.base.id = 'another-card';
  await restoreFails(otherId, /原文/u);
});

test('rejects extra keys inside comments and duplicate comment ids', async () => {
  const packet = await packetWithHistory();
  const extra = structuredClone(packet);
  extra.reviewComments[0].admin = true;
  await restoreFails(extra, /コメント/u);
  const duplicate = structuredClone(packet);
  duplicate.reviewComments.push({ ...duplicate.reviewComments[0] });
  await restoreFails(duplicate, /コメント/u);
});

test('__proto__ keys in the JSON do not pollute the restored state', async () => {
  const packet = await packetWithHistory();
  const json = JSON.stringify(packet).replace('"reviewComments"', '"__proto__":{"polluted":true},"reviewComments"');
  await restoreFails(json, /形式/u);
  assert.equal({}.polluted, undefined);
});

test('does not mutate the parsed base or share state between restores', async () => {
  const packet = await packetWithHistory();
  const json = JSON.stringify(packet);
  const first = await restoreReviewWorkspace(json);
  const second = await restoreReviewWorkspace(json);
  first.workspace.reviewComments.push({});
  assert.equal(second.workspace.reviewComments.length, packet.reviewComments.length);
  assert.notEqual(first.workspace.document.metadata, second.workspace.document.metadata);
});
