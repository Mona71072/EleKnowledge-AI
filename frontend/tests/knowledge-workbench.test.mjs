import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import test from 'node:test';

import {
  confirmOneNote,
  createWorkspace,
  editBody,
  editOneNoteDraft,
  exportProposal,
  markCopied,
  parseKnowledgeMarkdown,
  recordPlacement,
  setKbReview,
} from '../src/lib/knowledge-workbench.mjs';

const BASE = [
  '---',
  'record_id: case-cm-ma-71',
  'record_version: 3',
  'title: Governor mount vibration',
  'status: approved',
  'evidence_sources:',
  '  - source_id: lists-71',
  '    supports:',
  '      - Reported vibration during emergency stop',
  'structured_data:',
  '  model: CM-MA',
  '  verified_actions: []',
  '---',
  '',
  '# Governor mount vibration',
  '',
  'Check the source record and verify the installation conditions.',
].join('\n');

const CARD = [
  '---',
  'knowledge_id: KH-0042',
  'card_version: 2',
  'title: Door vibration check',
  'status: approved',
  '---',
  '',
  '# Door vibration check',
  '',
  'Compare the observed conditions with the approved procedure.',
].join('\n');

function parsed(markdown = BASE) {
  return parseKnowledgeMarkdown(markdown);
}

function workspace(markdown = BASE) {
  return createWorkspace(parsed(markdown));
}

function reviewed(state) {
  return setKbReview(state, {
    status: 'reviewed',
    reference: 'KB: C-6-R56.1, section 4, page 12',
    note: 'The source document was opened and the applicable section was checked.',
  });
}

function confirmed(state) {
  return confirmOneNote(reviewed(state), { checked: true });
}

test('parses both supported identity pairs and preserves Markdown and metadata', () => {
  const record = parsed();
  const card = parsed(CARD);

  assert.deepEqual(
    { id: record.id, version: record.version, title: record.title },
    { id: 'case-cm-ma-71', version: 3, title: 'Governor mount vibration' },
  );
  assert.deepEqual(
    { id: card.id, version: card.version, title: card.title },
    { id: 'KH-0042', version: 2, title: 'Door vibration check' },
  );
  assert.equal(record.body, '# Governor mount vibration\n\nCheck the source record and verify the installation conditions.');
  assert.equal(record.originalMarkdown, BASE);
  assert.equal(record.metadata.evidence_sources[0].supports[0], 'Reported vibration during emergency stop');
  assert.equal(record.metadata.structured_data.model, 'CM-MA');
  assert.equal(record.metadata.status, 'approved');
});

test('rejects malformed, oversized, nul-containing, or identity-incomplete documents', () => {
  for (const invalid of [
    'plain markdown without frontmatter',
    BASE.replace('record_version: 3', 'record_version: 0'),
    BASE.replace('record_version: 3', 'record_version: 1.5'),
    BASE.replace('title: Governor mount vibration\n', ''),
    `${BASE}\0`,
    `${'x'.repeat(256 * 1024 + 1)}`,
  ]) {
    assert.throws(() => parseKnowledgeMarkdown(invalid));
  }
});

test('rejects duplicate keys, aliases, tags, and dangerous mapping keys', () => {
  const invalidYaml = [
    BASE.replace('status: approved', 'status: approved\nstatus: draft'),
    BASE.replace('structured_data:\n  model: CM-MA\n  verified_actions: []', 'structured_data: &data {model: CM-MA}\ncopy: *data'),
    BASE.replace('status: approved', 'status: !!str approved'),
    BASE.replace('status: approved', '__proto__: unsafe\nstatus: approved'),
    BASE.replace('status: approved', 'constructor: unsafe\nstatus: approved'),
  ];

  for (const invalid of invalidYaml) assert.throws(() => parseKnowledgeMarkdown(invalid));
});

test('starts as an unpublished working copy even when source metadata says approved', () => {
  const state = workspace();

  assert.equal(state.document.metadata.status, 'approved');
  assert.equal(state.revision, 0);
  assert.equal(state.reviewedRevision, null);
  assert.equal(state.copiedRevision, null);
  assert.deepEqual(state.placements, []);
});

test('body and OneNote draft edits are immutable and invalidate current review and copy', () => {
  const original = confirmed(workspace());
  const copied = markCopied(original, original.revision);
  const bodyEdited = editBody(copied, `${copied.body}\n\n## New condition\nVerify the model suffix.`);
  const oneNoteEdited = editOneNoteDraft(bodyEdited, 'New condition: verify the model suffix.\nSource: Lists item 71.');

  assert.equal(original.body.includes('New condition'), false);
  assert.equal(original.noteText, '');
  assert.equal(oneNoteEdited.revision, original.revision + 2);
  assert.equal(oneNoteEdited.reviewedRevision, null);
  assert.equal(oneNoteEdited.copiedRevision, null);
  assert.equal(oneNoteEdited.kbReview.status, 'unverified');
  assert.equal(oneNoteEdited.noteText.startsWith('New condition:'), true);
});

test('KB review requires a recognized status and retains the reference and reviewer note', () => {
  const initial = workspace();
  assert.throws(() => setKbReview(initial, { status: 'reviewed' }));
  assert.throws(() => setKbReview(initial, { status: 'verified-by-ai', reference: 'KB X', note: 'checked' }));

  const state = reviewed(initial);
  assert.equal(state.kbReview.status, 'reviewed');
  assert.equal(state.kbReview.reference, 'KB: C-6-R56.1, section 4, page 12');
  assert.equal(state.kbReview.note.includes('opened'), true);
  assert.equal(state.reviewedRevision, state.revision);
});

test('OneNote confirmation requires KB review and cannot be inferred from source status', () => {
  const initial = workspace();
  assert.throws(() => confirmOneNote(initial, { checked: true }));
  assert.throws(() => confirmOneNote(setKbReview(initial, {
    status: 'conflict',
    reference: 'KB: C-6-R56.1',
    note: 'The procedure appears inconsistent with the case.',
  }), { checked: true }));

  const state = confirmed(initial);
  assert.equal(state.reviewedRevision, state.revision);
  assert.equal(state.copiedRevision, null);
});

test('copy acknowledgement is separate from OneNote placement and rejects stale revisions', () => {
  const state = confirmed(workspace());

  assert.throws(() => markCopied(state, state.revision - 1));
  const copied = markCopied(state, state.revision);
  assert.equal(copied.copiedRevision, copied.revision);
  assert.deepEqual(copied.placements, []);
});

test('placement requires a current confirmed copy, a page URL, and a valid timestamp', () => {
  const state = confirmed(workspace());
  const copied = markCopied(state, state.revision);

  for (const invalid of [
    { destination: 'https://example.com/page', recordedAt: 'not-a-date' },
    { destination: 'javascript:alert(1)', recordedAt: '2026-10-20T09:00:00+09:00' },
    { destination: 'https://example.com/page' },
  ]) {
    assert.throws(() => recordPlacement(copied, invalid));
  }

  assert.throws(() => recordPlacement(state, {
    destination: 'onenote:https://tenant.sharepoint.com/site/page',
    recordedAt: '2026-10-20T09:00:00+09:00',
  }));
});

test('placement receipt pins the copied revision and text and stays unchanged after later edits', () => {
  const state = confirmed(workspace());
  const draft = editOneNoteDraft(state, 'Observed: vibration during emergency stop.\nUnconfirmed: continued condition.');
  const confirmedDraft = confirmed(draft);
  const copied = markCopied(confirmedDraft, confirmedDraft.revision);
  const placed = recordPlacement(copied, {
    destination: 'https://tenant.sharepoint.com/sites/engineering/Shared%20Documents/oneNotePage',
    recordedAt: '2026-10-20T09:00:00+09:00',
  });
  const receiptBeforeEdit = structuredClone(placed.placements[0]);
  const next = editOneNoteDraft(placed, `${placed.noteText}\nAdditional follow-up.`);

  assert.equal(placed.placements.length, 1);
  assert.deepEqual(next.placements[0], receiptBeforeEdit);
  assert.equal(receiptBeforeEdit.revision, confirmedDraft.revision);
  assert.equal(receiptBeforeEdit.text, copied.noteText);
  assert.equal(next.copiedRevision, null);
});

test('OneNote draft is deterministic and carries sources and explicitly unconfirmed points', () => {
  const state = workspace();
  assert.equal(typeof state.noteText, 'string');
  assert.match(state.noteText, /Lists item 71/);
  assert.match(state.noteText, /未確認|unconfirmed/i);
  assert.equal(editOneNoteDraft(state, state.noteText).noteText, state.noteText);
});

test('proposal export includes exact SHA-256 digests and keeps original metadata in its base record', async () => {
  const state = editOneNoteDraft(
    editBody(workspace(), `${workspace().body}\n\n## Applicability\nCM-MA only.`),
    'CM-MA only.\nSource: Lists item 71.\nUnconfirmed: long-term condition.',
  );
  const packet = await exportProposal(state);
  const sha256 = (value) => createHash('sha256').update(value, 'utf8').digest('hex');

  assert.equal(packet.format, 'eleknowledge-knowledge-proposal/v1');
  assert.equal(packet.base.id, 'case-cm-ma-71');
  assert.equal(packet.base.version, 3);
  assert.equal(packet.base.markdown, BASE);
  assert.equal(packet.base.metadata.status, 'approved');
  assert.equal(packet.proposal.markdown.includes('status: draft'), true);
  assert.equal(packet.proposal.publishable, false);
  assert.equal(packet.hashes.baseMarkdownSha256, sha256(BASE));
  assert.equal(packet.hashes.bodySha256, sha256(state.body));
  assert.equal(packet.hashes.oneNoteTextSha256, sha256(state.noteText));
  assert.equal(packet.proposal.markdown.includes('Unconfirmed: long-term condition.'), true);
});

