import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { lstat, mkdtemp, mkdir, readFile, readdir, rm, stat, symlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { buildKnowhowIndex, checkKnowhowCards, inventoryKnowhowCards } from '../../scripts/knowledge/build-senpai-index.mjs';

// Ledger behaviour is covered in knowledge-index-guards.test.mjs; these tests exercise card validation only.
const check = (root, options = {}) => checkKnowhowCards(root, { ledger: false, ...options });
const execFileAsync = promisify(execFile);
const script = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../scripts/knowledge/build-senpai-index.mjs');

const card = ({ id, extraRefs = '', refs = '  - ref_type: lists_item\n    list_item_id: SYNTH-1\n', body = 'synthetic body' }) => [
  '---', `knowledge_id: ${id}`, 'card_version: 1', 'status: draft', `title: card ${id}`,
  'model_scope:', '  product_lines:', '    - AXIEZ',
  'source_refs:', refs + extraRefs, '---', body, '',
].join('\n').replace(/\n\n---/u, '\n---');

async function makeRoot(t, cards) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'senpai-check-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const dir = path.join(root, 'knowledge/cards/practice-guides');
  await mkdir(dir, { recursive: true });
  for (const [name, text] of Object.entries(cards)) await writeFile(path.join(dir, name), text);
  return root;
}

const BAD_REF = '  - ref_type: lists_item\n    bogus_field: x\n    list_item_id: SYNTH-2\n';

test('check validates every card individually, reports failures, and writes nothing', async (t) => {
  const root = await makeRoot(t, {
    'KH-A.md': card({ id: 'KH-A' }),
    'KH-B.md': card({ id: 'KH-B', refs: BAD_REF }),
    'KH-C.md': card({ id: 'KH-C' }),
  });
  const result = await check(root);
  assert.equal(result.total, 3);
  assert.equal(result.valid, 2);
  assert.equal(result.failures.length, 1);
  assert.equal(result.failures[0].path, 'knowledge/cards/practice-guides/KH-B.md');
  assert.match(result.failures[0].reason, /unsupported field/u);
  assert.deepEqual(await readdir(root), ['knowledge']);
});

test('check reports a duplicate knowledge ID as a failure instead of aborting', async (t) => {
  const root = await makeRoot(t, { 'KH-A.md': card({ id: 'KH-A' }), 'other.md': card({ id: 'KH-A' }) });
  const result = await check(root);
  assert.equal(result.total, 2);
  assert.equal(result.valid, 1);
  assert.match(result.failures[0].reason, /duplicate/u);
});

test('check applies the same validation as build (unsafe scope value fails both)', async (t) => {
  const bad = card({ id: 'KH-U' }).replace('- AXIEZ', '- https://example.test/x');
  const root = await makeRoot(t, { 'KH-U.md': bad });
  const result = await check(root);
  assert.equal(result.valid, 0);
  const inventory = await inventoryKnowhowCards(root);
  const entry = { path: inventory.cards[0].path, knowledgeId: 'KH-U', cardVersion: 1, sha256: inventory.cards[0].sha256, cloudApproved: true };
  await assert.rejects(buildKnowhowIndex({
    root,
    manifest: { schemaVersion: 1, purpose: 'senpai-admin-navigation', approvedBy: 'r', approvedAt: '2026-10-20T00:00:00.000Z', entries: [entry] },
  }));
});

test('CLI check exits 0 when all cards are valid and 1 otherwise; --json prints the result', async (t) => {
  const good = await makeRoot(t, { 'KH-A.md': card({ id: 'KH-A' }) });
  const ok = await execFileAsync(process.execPath, [script, 'check', good, '--json', '--no-ledger']);
  assert.equal(JSON.parse(ok.stdout).valid, 1);
  const bad = await makeRoot(t, { 'KH-A.md': card({ id: 'KH-A' }), 'KH-B.md': card({ id: 'KH-B', refs: BAD_REF }) });
  await assert.rejects(execFileAsync(process.execPath, [script, 'check', bad, '--no-ledger']), (error) => {
    assert.equal(error.code, 1);
    assert.match(error.stdout, /KH-B\.md/u);
    assert.match(error.stdout, /1\/2|2/u);
    return true;
  });
});

test('--eval-index writes a 0600 index of valid cards only, inside os.tmpdir() and outside the repo root', async (t) => {
  const root = await makeRoot(t, {
    'KH-A.md': card({ id: 'KH-A' }),
    'KH-B.md': card({ id: 'KH-B', refs: BAD_REF }),
  });
  const outDir = await mkdtemp(path.join(os.tmpdir(), 'senpai-eval-out-'));
  t.after(() => rm(outDir, { recursive: true, force: true }));
  const outPath = path.join(outDir, 'eval-index.json');
  // root is itself under os.tmpdir(), so a path inside the repo root must still be refused.
  await assert.rejects(check(root, { evalIndexPath: path.join(root, 'leak.json') }), /repository root/u);
  await assert.rejects(check(root, { evalIndexPath: '/var/tmp/../../etc/senpai-eval.json' }), /temporary/u);
  const result = await check(root, { evalIndexPath: outPath });
  assert.equal(result.evalIndexPath, await (await import('node:fs/promises')).realpath(outDir).then((dir) => path.join(dir, 'eval-index.json')));
  const info = await stat(outPath);
  assert.equal(info.mode & 0o777, 0o600);
  const index = JSON.parse(await readFile(outPath, 'utf8'));
  assert.deepEqual(index.cards.map((item) => item.knowledgeId), ['KH-A']);
  assert.match(index.indexVersion, /^sha256:[0-9a-f]{64}$/u);
  await assert.rejects(lstat(path.join(root, 'leak.json')));
});

test('--eval-index rejects a symlinked parent that escapes os.tmpdir()', async (t) => {
  const root = await makeRoot(t, { 'KH-A.md': card({ id: 'KH-A' }) });
  const link = path.join(os.tmpdir(), `senpai-eval-link-${process.pid}`);
  await symlink(os.homedir(), link);
  t.after(() => rm(link, { force: true }));
  await assert.rejects(check(root, { evalIndexPath: path.join(link, 'x.json') }), /temporary/u);
});

test('CLI --eval-index prints an unapproved/never-upload warning', async (t) => {
  const root = await makeRoot(t, { 'KH-A.md': card({ id: 'KH-A' }) });
  const outDir = await mkdtemp(path.join(os.tmpdir(), 'senpai-eval-out-'));
  t.after(() => rm(outDir, { recursive: true, force: true }));
  const { stdout } = await execFileAsync(process.execPath, [script, 'check', root, '--no-ledger', '--eval-index', path.join(outDir, 'i.json')]);
  assert.match(stdout, /未承認/u);
  assert.match(stdout, /アップロード/u);
});

test('contract fixture built-index.json is exactly what the real build code produces from the synthetic cards', async () => {
  const { buildContractFixtureText, CONTRACT_INDEX } = await import('../../scripts/knowledge/regenerate-contract-fixture.mjs');
  const expected = await buildContractFixtureText();
  const actual = await readFile(CONTRACT_INDEX, 'utf8');
  assert.equal(actual, expected, 'Run: npm --prefix frontend run knowledge:regen-contract-fixture');
  const index = JSON.parse(actual);
  assert.deepEqual(index.cards.map((item) => item.knowledgeId), ['KH-SYN-CONFLICT', 'KH-SYN-DUPTERMS', 'KH-SYN-POSITIVE', 'KH-SYN-UNVERIFIED']);
  const positive = index.cards.find((item) => item.knowledgeId === 'KH-SYN-POSITIVE');
  for (const hidden of ['qxexcl', 'qxmay', 'qxnote']) assert.equal(positive.searchTerms.join(' ').includes(hidden), false);
  assert.equal(positive.sourceRefs[0].note, undefined);
});
