import assert from 'node:assert/strict';
import { mkdtemp, mkdir, rm, symlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { buildKnowhowIndex, inventoryKnowhowCards, parsePublicationManifest } from '../../scripts/knowledge/build-senpai-index.mjs';

const card = ({ id = 'KH-TEST-001', version = 1, status = 'draft', title = 'Synthetic case', body = 'A synthetic body.', scope = { conditions: ['synthetic only'], excludes: ['real cases'] }, refs = [{ ref_type: 'lists_item', list_item_id: 'SYNTH-LIST-1' }, { ref_type: 'kb_document', document_number: 'SYNTH-DOC-1', kb_filename: 'synthetic.pdf', kb_verify_status: 'pending' }] } = {}) => [
  '---', `knowledge_id: ${id}`, `card_version: ${version}`, `status: ${status}`, `title: ${title}`,
  'model_scope:', ...Object.entries(scope).flatMap(([key, value]) => [`  ${key}:`, ...(Array.isArray(value) ? value.map((item) => `    - ${item}`) : [`    - ${value}`])]),
  'source_refs:', ...refs.flatMap((ref) => [`  - ref_type: ${ref.ref_type}`, ...Object.entries(ref).filter(([key]) => key !== 'ref_type').map(([key, value]) => `    ${key}: ${value}`)]),
  '---', body, '',
].join('\n');

async function fixture(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'senpai-index-'));
  const allowed = path.join(root, 'knowledge/cards/practice-guides');
  const cases = path.join(root, 'knowledge/cards/case-summaries');
  await mkdir(allowed, { recursive: true });
  await mkdir(cases, { recursive: true });
  t.after(() => rm(root, { recursive: true, force: true }));
  return { root, allowed, cases };
}

function manifest(entries, overrides = {}) {
  return {
    schemaVersion: 1,
    purpose: 'senpai-admin-navigation',
    approvedBy: entries.length ? 'Synthetic reviewer' : null,
    approvedAt: entries.length ? '2026-10-20T00:00:00.000Z' : null,
    entries,
    ...overrides,
  };
}

async function selectedEntry(root, relativePath, markdown, overrides = {}) {
  const absolute = path.join(root, relativePath);
  await mkdir(path.dirname(absolute), { recursive: true });
  await writeFile(absolute, markdown);
  const { createHash } = await import('node:crypto');
  return { path: relativePath, knowledgeId: 'KH-TEST-001', cardVersion: 1, sha256: createHash('sha256').update(markdown).digest('hex'), cloudApproved: true, ...overrides };
}

test('manifest parsing is strict JSON and rejects duplicate object keys', () => {
  assert.throws(() => parsePublicationManifest('{"schemaVersion":1,}'));
  assert.throws(() => parsePublicationManifest('{"schemaVersion":1,"schemaVersion":1}'));
  assert.deepEqual(parsePublicationManifest(JSON.stringify(manifest([]))).entries, []);
});

test('inventory reads only the two approved card directories and returns metadata without body', async (t) => {
  const { root, allowed, cases } = await fixture(t);
  await writeFile(path.join(allowed, 'draft.md'), card());
  await writeFile(path.join(cases, 'case.md'), card({ id: 'KH-TEST-002' }));
  await writeFile(path.join(root, 'knowledge/cards/TEMPLATE.md'), card({ id: 'KH-TEMPLATE' }));
  await mkdir(path.join(root, 'knowledge/snapshots'), { recursive: true });
  await writeFile(path.join(root, 'knowledge/snapshots/snapshot.md'), card({ id: 'KH-SNAPSHOT' }));
  const inventory = await inventoryKnowhowCards(root);
  assert.equal(inventory.cards.length, 2);
  assert.equal(inventory.cards.some((item) => item.knowledgeId === 'KH-TEMPLATE' || item.knowledgeId === 'KH-SNAPSHOT'), false);
  assert.equal(inventory.cards[0].body, undefined);
  assert.equal(inventory.cards[0].status, 'draft');
});

test('build requires explicit exact path, ID, version, hash, and cloud approval; draft status is preserved', async (t) => {
  const { root, allowed } = await fixture(t);
  const relativePath = 'knowledge/cards/practice-guides/one.md';
  const markdown = card();
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const entry = await selectedEntry(root, relativePath, markdown);
  const index = await buildKnowhowIndex({ root, manifest: manifest([entry]), generatedAt: '2026-10-20T00:00:00.000Z' });
  assert.equal(index.cards.length, 1);
  assert.equal(index.cards[0].status, 'draft');
  assert.equal(index.cards[0].body, 'A synthetic body.\n');
  assert.equal(index.cards[0].usage, 'navigation_only');
  for (const change of [
    { ...entry, sha256: '0'.repeat(64) },
    { ...entry, knowledgeId: 'KH-WRONG' },
    { ...entry, cardVersion: 2 },
    { ...entry, cloudApproved: false },
  ]) await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([change]) }));
});

test('build excludes unselected files and does not silently accept nested or invalid approvals', async (t) => {
  const { root, allowed } = await fixture(t);
  const markdown = card();
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const index = await buildKnowhowIndex({ root, manifest: manifest([]) });
  assert.deepEqual(index.cards, []);
  assert.equal(index.indexVersion.startsWith('sha256:'), true);
  for (const bad of [
    manifest([{ path: '../secret.md', knowledgeId: 'KH-TEST-001', cardVersion: 1, sha256: '0'.repeat(64), cloudApproved: true }]),
    manifest([{ path: 'knowledge/cards/TEMPLATE.md', knowledgeId: 'KH-TEST-001', cardVersion: 1, sha256: '0'.repeat(64), cloudApproved: true }]),
    manifest([{ path: 'knowledge/cards/practice-guides/one.md', knowledgeId: 'KH-TEST-001', cardVersion: 1, sha256: '0'.repeat(64), cloudApproved: true }], { approval: { approvedBy: 'fake nested approval' } }),
    manifest([{ path: 'knowledge/cards/practice-guides/one.md', knowledgeId: 'KH-TEST-001', cardVersion: 1, sha256: '0'.repeat(64), cloudApproved: true }], { approvedAt: 'yesterday' }),
  ]) await assert.rejects(buildKnowhowIndex({ root, manifest: bad }));
});

test('duplicate IDs, duplicate paths, YAML duplicate keys, status drift, and symlinks fail closed', async (t) => {
  const { root, allowed } = await fixture(t);
  const markdown = card();
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const first = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', markdown);
  await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([first, first]) }));
  const duplicateId = await selectedEntry(root, 'knowledge/cards/practice-guides/two.md', markdown);
  await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([first, duplicateId]) }));
  const duplicateYaml = markdown.replace('knowledge_id: KH-TEST-001', 'knowledge_id: KH-TEST-001\nknowledge_id: KH-TEST-001');
  await writeFile(path.join(allowed, 'one.md'), duplicateYaml);
  await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([first]) }));
  const retired = card({ status: 'retired' });
  await writeFile(path.join(allowed, 'one.md'), retired);
  const retiredEntry = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', retired);
  await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([retiredEntry]) }));
  await rm(path.join(allowed, 'one.md'));
  await symlink(path.join(root, 'outside.md'), path.join(allowed, 'link.md'));
  await assert.rejects(inventoryKnowhowCards(root));
});

test('index digest is stable for identical cards and retains full body, conditions, and source references', async (t) => {
  const { root, allowed } = await fixture(t);
  const markdown = card({ body: 'Condition A applies.\nExclude condition B.', scope: { conditions: ['Condition A'], excludes: ['Condition B'] }, refs: [{ ref_type: 'onenote_page', onenote_id: 'SYNTH-NOTE-1', page_role: 'workflow' }, { ref_type: 'kb_document', document_number: 'SYNTH-DOC-1', kb_filename: 'manual.pdf', kb_verify_status: 'pending' }] });
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const entry = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', markdown);
  const first = await buildKnowhowIndex({ root, manifest: manifest([entry]), generatedAt: '2026-10-20T00:00:00.000Z' });
  const second = await buildKnowhowIndex({ root, manifest: manifest([entry]), generatedAt: '2026-10-21T00:00:00.000Z' });
  assert.equal(first.indexVersion, second.indexVersion);
  assert.equal(first.cards[0].body, 'Condition A applies.\nExclude condition B.\n');
  assert.deepEqual(first.cards[0].modelScope.conditions, ['Condition A']);
  assert.deepEqual(first.cards[0].modelScope.excludes, ['Condition B']);
  assert.ok(first.cards[0].sourceRefs.some((ref) => ref.type === 'onenote_page' && ref.pageRole === 'workflow'));
  assert.ok(first.cards[0].sourceRefs.some((ref) => ref.type === 'kb_document' && ref.documentNumber === 'SYNTH-DOC-1' && ref.fileName === 'manual.pdf' && ref.verificationStatus === 'pending'));
});
