import assert from 'node:assert/strict';
import { lstat, mkdtemp, mkdir, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { buildKnowhowIndex, inventoryKnowhowCards, parsePublicationManifest } from '../../scripts/knowledge/build-senpai-index.mjs';

const card = ({ id = 'KH-TEST-001', version = 1, status = 'draft', title = 'Synthetic case', body = 'A synthetic body.', scope = { may_apply_to: ['synthetic only'], excludes: ['real cases'] }, refs = [{ ref_type: 'lists_item', list_item_id: 'SYNTH-LIST-1' }, { ref_type: 'kb_document', document_number: 'SYNTH-DOC-1', kb_filename: 'synthetic.pdf', kb_verify_status: 'pending' }] } = {}) => [
  '---', `knowledge_id: ${id}`, `card_version: ${version}`, `status: ${status}`, `title: ${title}`,
  'model_scope:', ...Object.entries(scope).flatMap(([key, value]) => [`  ${key}:`, ...(Array.isArray(value) ? value.map((item) => `    - ${item}`) : [`    - ${value}`])]),
  'source_refs:', ...refs.flatMap((ref) => [`  - ref_type: ${ref.ref_type}`, ...Object.entries(ref).filter(([key]) => key !== 'ref_type').map(([key, value]) => `    ${key}: ${value}`)]),
  '---', body, '',
].join('\n');
const execFileAsync = promisify(execFile);

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
  assert.equal(await readFile(path.join(allowed, 'one.md'), 'utf8'), markdown);
  assert.equal(index.cards[0].usage, 'navigation_only');
  for (const change of [
    { ...entry, sha256: '0'.repeat(64) },
    { ...entry, knowledgeId: 'KH-WRONG' },
    { ...entry, cardVersion: 2 },
    { ...entry, cloudApproved: false },
  ]) await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([change]) }));
});

test('CLI output replaces a preexisting symlink without following it or printing source content', async (t) => {
  const { root, allowed } = await fixture(t);
  const markdown = card();
  const sourcePath = path.join(allowed, 'one.md');
  await writeFile(sourcePath, markdown);
  const privateDirectory = path.join(root, '.private-knowhow');
  await mkdir(privateDirectory);
  const outsideTarget = path.join(root, 'outside-target.txt');
  await writeFile(outsideTarget, 'untouched synthetic target');
  try {
    await symlink(outsideTarget, path.join(privateDirectory, 'inventory.json'));
  } catch (error) {
    if (process.platform !== 'win32' || error.code !== 'EPERM') throw error;
    t.skip('Windows file symlinks require Developer Mode or the symlink privilege.');
    return;
  }
  const script = fileURLToPath(new URL('../../scripts/knowledge/build-senpai-index.mjs', import.meta.url));
  const { stdout } = await execFileAsync(process.execPath, [script, 'inventory', root]);
  assert.match(stdout, /1 valid metadata records/);
  assert.equal(stdout.includes('A synthetic body.'), false);
  assert.equal(await readFile(outsideTarget, 'utf8'), 'untouched synthetic target');
  assert.equal((await lstat(path.join(privateDirectory, 'inventory.json'))).isSymbolicLink(), false);
  assert.equal(await readFile(sourcePath, 'utf8'), markdown);
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
  // Directory junctions exercise the same traversal guard without requiring
  // Windows file-symlink privileges.
  const outsideDirectory = path.join(root, 'outside');
  await mkdir(outsideDirectory);
  await symlink(outsideDirectory, path.join(allowed, 'link'), process.platform === 'win32' ? 'junction' : 'dir');
  await assert.rejects(inventoryKnowhowCards(root));
});

test('index digest is stable for identical cards and retains full body, conditions, and source references', async (t) => {
  const { root, allowed } = await fixture(t);
  const markdown = card({ body: 'Condition A applies.\nExclude condition B.', scope: { may_apply_to: ['Condition A'], excludes: ['Condition B'] }, refs: [{ ref_type: 'onenote_page', onenote_id: 'SYNTH-NOTE-1', page_role: 'workflow' }, { ref_type: 'kb_document', document_number: 'SYNTH-DOC-1', kb_filename: 'manual.pdf', kb_verify_status: 'pending' }] });
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const entry = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', markdown);
  const first = await buildKnowhowIndex({ root, manifest: manifest([entry]), generatedAt: '2026-10-20T00:00:00.000Z' });
  const second = await buildKnowhowIndex({ root, manifest: manifest([entry]), generatedAt: '2026-10-21T00:00:00.000Z' });
  assert.equal(first.indexVersion, second.indexVersion);
  assert.equal(first.cards[0].body, 'Condition A applies.\nExclude condition B.\n');
  assert.deepEqual(first.cards[0].modelScope.may_apply_to, ['Condition A']);
  assert.deepEqual(first.cards[0].modelScope.excludes, ['Condition B']);
  assert.ok(first.cards[0].sourceRefs.some((ref) => ref.ref_type === 'onenote_page' && ref.onenote_id === 'SYNTH-NOTE-1' && ref.page_role === 'workflow'));
  assert.ok(first.cards[0].sourceRefs.some((ref) => ref.ref_type === 'kb_document' && ref.document_number === 'SYNTH-DOC-1' && ref.kb_filename === 'manual.pdf' && ref.kb_verify_status === 'pending'));
});

test('editor annotation keys on source refs are dropped from the index; other unknown keys still fail', async (t) => {
  const { root, allowed } = await fixture(t);
  const annotated = [
    { ref_type: 'lists_item', list_item_id: 'SYNTH-LIST-1', note: 'editor note', record_id: 'R-1', kb_category: 'cat' },
    { ref_type: 'law_rag', law_id: 'SYNTH-LAW-1', law_rag_status: 'ok', retrieval: 'auto', summary_from_kb: 'yes' },
  ];
  const markdown = card({ refs: annotated });
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const entry = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', markdown);
  const index = await buildKnowhowIndex({ root, manifest: manifest([entry]) });
  assert.equal(index.cards[0].sourceRefs.length, 2);
  for (const ref of index.cards[0].sourceRefs) {
    for (const key of ['note', 'law_rag_status', 'retrieval', 'summary_from_kb', 'record_id', 'kb_category']) assert.equal(key in ref, false);
  }
  assert.equal(JSON.stringify(index).includes('editor note'), false);
  const unknown = card({ refs: [{ ref_type: 'lists_item', list_item_id: 'SYNTH-LIST-1', mystery_key: 'x' }] });
  await writeFile(path.join(allowed, 'one.md'), unknown);
  await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', unknown)]) }));
  const onlyAnnotation = card({ refs: [{ ref_type: 'lists_item', note: 'no identity' }] });
  await writeFile(path.join(allowed, 'one.md'), onlyAnnotation);
  await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', onlyAnnotation)]) }));
});

test('slash notation is accepted in model scope values and source ref locators', async (t) => {
  const { root, allowed } = await fixture(t);
  const markdown = card({
    scope: { may_apply_to: ['LINKs 7seg/2桁表示'], excludes: ['LV5K/LV6K 戸型のみ'], door_types: ['LV5K-CO/2S'], scope_note: 'A/B' },
    refs: [{ ref_type: 'kb_document', document_number: 'SYNTH-DOC-1', locator: 'D14 DCB/DOB' }],
  });
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const entry = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', markdown);
  const index = await buildKnowhowIndex({ root, manifest: manifest([entry]) });
  assert.deepEqual(index.cards[0].modelScope.excludes, ['LV5K/LV6K 戸型のみ']);
  assert.deepEqual(index.cards[0].modelScope.door_types, ['LV5K-CO/2S']);
  assert.equal(index.cards[0].sourceRefs[0].locator, 'D14 DCB/DOB');
});

test('path-like, backslash, parent-segment, absolute, and URL values are still rejected', async (t) => {
  const { root, allowed } = await fixture(t);
  const bad = ['../x', '/abs', 'a\\x', 'a/../x', 'https://example.com/x', 's3://bucket/key', 'file:///etc/passwd', 'javascript:alert(1)'];
  const cases = [];
  for (const value of bad) {
    cases.push(card({ scope: { excludes: [`'${value}'`] } }));
    cases.push(card({ scope: { may_apply_to: [`'${value}'`] } }));
    cases.push(card({ refs: [{ ref_type: 'kb_document', document_number: 'SYNTH-DOC-1', locator: `'${value}'` }] }));
  }
  for (const markdown of cases) {
    await writeFile(path.join(allowed, 'one.md'), markdown);
    const entry = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', markdown);
    await assert.rejects(buildKnowhowIndex({ root, manifest: manifest([entry]) }), undefined, markdown);
  }
});

const scopedCard = (lines) => card().replace('model_scope:\n', `model_scope:\n  product_lines:\n    - AXIEZ\n${lines.map((line) => `  ${line}\n`).join('')}`);

async function buildScoped(t, lines) {
  const { root, allowed } = await fixture(t);
  const markdown = scopedCard(lines);
  await writeFile(path.join(allowed, 'one.md'), markdown);
  const entry = await selectedEntry(root, 'knowledge/cards/practice-guides/one.md', markdown);
  return buildKnowhowIndex({ root, manifest: manifest([entry]) });
}

test('scope verification marks are kept as scalars in modelScope but never become search terms', async (t) => {
  const index = await buildScoped(t, ['scope_status: verified', 'scope_verified_by: reviewer-a', 'scope_verified_at: 2026-10-20']);
  const [built] = index.cards;
  assert.equal(built.modelScope.scope_status, 'verified');
  assert.equal(built.modelScope.scope_verified_by, 'reviewer-a');
  assert.equal(built.modelScope.scope_verified_at, '2026-10-20');
  for (const term of ['verified', 'reviewer-a', '2026-10-20']) assert.equal(built.searchTerms.includes(term), false);
});

test('an unverified or unmarked scope builds without verification fields being required', async (t) => {
  const marked = await buildScoped(t, ['scope_status: unverified']);
  assert.equal(marked.cards[0].modelScope.scope_status, 'unverified');
  const unmarked = await buildScoped(t, []);
  assert.equal('scope_status' in unmarked.cards[0].modelScope, false);
});

test('verified scope without reviewer and date, or with malformed marks, fails the build', async (t) => {
  const rejected = [
    ['scope_status: verified'],
    ['scope_status: verified', 'scope_verified_by: reviewer-a'],
    ['scope_status: verified', 'scope_verified_at: 2026-10-20'],
    ['scope_status: verified', 'scope_verified_by: reviewer-a', 'scope_verified_at: 20261020'],
    ['scope_status: verified', 'scope_verified_by: reviewer-a', 'scope_verified_at: 2026-13-45'],
    ['scope_status: maybe'],
    ['scope_verified_by: reviewer-a', 'scope_status:', '  - verified'],
  ];
  for (const lines of rejected) await assert.rejects(buildScoped(t, lines), undefined, lines.join(' / '));
});

test('excluded, unconfirmed and note scope values never become search terms', async (t) => {
  const index = await buildScoped(t, ['scope_note: other products only']);
  const [built] = index.cards;
  assert.equal(built.searchTerms.includes('AXIEZ'), true);
  for (const term of ['real cases', 'synthetic only', 'other products only']) assert.equal(built.searchTerms.includes(term), false);
  assert.deepEqual(built.modelScope.excludes, ['real cases']);
});
