// Guards found missing by mutation testing: each test reproduces a mutation that used to slip through.
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import {
  buildKnowhowIndex, checkKnowhowCards, inventoryKnowhowCards, writeKnowhowLedger,
} from '../../scripts/knowledge/build-senpai-index.mjs';

const execFileAsync = promisify(execFile);
const script = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../scripts/knowledge/build-senpai-index.mjs');
const LEDGER = 'knowledge/registry/card-versions.jsonl';
const TODAY = '2026-10-20';

const card = ({ id = 'KH-G-1', version = 1, title = 'guard card', body = 'guard body', scope = ['product_lines:', '    - AXIEZ'], extra = [] } = {}) => [
  '---', `knowledge_id: ${id}`, `card_version: ${version}`, 'status: draft', `title: ${title}`, ...extra,
  'model_scope:', ...scope.map((line) => `  ${line}`),
  'source_refs:', '  - ref_type: lists_item', '    list_item_id: SYNTH-1', '---', body, '',
].join('\n');

const verified = (...lines) => ['scope_status: verified', 'scope_verified_by: reviewer-a', `scope_verified_at: ${TODAY}`, ...lines];

async function makeRoot(t, files = { 'KH-G-1.md': card() }, directory = 'practice-guides') {
  const root = await mkdtemp(path.join(os.tmpdir(), 'senpai-guard-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  for (const [name, text] of Object.entries(files)) {
    const target = path.join(root, 'knowledge/cards', directory, name);
    await mkdir(path.dirname(target), { recursive: true });
    await writeFile(target, text);
  }
  return root;
}

const cardPath = (root, name = 'KH-G-1.md') => path.join(root, 'knowledge/cards/practice-guides', name);
const reasons = (result) => result.failures.map((failure) => `${failure.path}: ${failure.reason}`).join('\n');
const check = (root, options = {}) => checkKnowhowCards(root, { today: TODAY, ...options });

async function manifestFor(root) {
  const inventory = await inventoryKnowhowCards(root);
  return {
    schemaVersion: 1, purpose: 'senpai-admin-navigation', approvedBy: 'r', approvedAt: '2026-10-20T00:00:00.000Z',
    entries: inventory.cards.map((item) => ({ path: item.path, knowledgeId: item.knowledgeId, cardVersion: item.cardVersion, sha256: item.sha256, cloudApproved: true })),
  };
}

// ---- gap 1: verified scope with no recognized product / generic label
test('a verified card whose classify fields hold only an unrecognized product (typo AXEIZ) fails check and build', async (t) => {
  const typo = card({ scope: ['product_lines:', '    - AXEIZ', ...verified()] });
  const root = await makeRoot(t, { 'KH-G-1.md': typo });
  const result = await check(root, { ledger: false });
  assert.equal(result.valid, 0);
  assert.match(result.failures[0].reason, /認識できる/u);
  for (const recognized of ['AXIEZ', 'AXIEZ-LINKs', 'NEXCUBE', 'メルシティ', 'メルワイド', 'エスカレーター', '全エレ機種', '全エス機種']) {
    assert.ok(result.failures[0].reason.includes(recognized), `message must list ${recognized}`);
  }
  await assert.rejects(buildKnowhowIndex({ root, manifest: await manifestFor(root), today: TODAY }), /認識できる/u);
});

test('a verified card passes when any classify field has a recognized product or generic label; unverified never needs one', async (t) => {
  const files = {
    'KH-G-1.md': card({ id: 'KH-G-1', scope: ['product_lines:', '    - AXEIZ', 'lists_model_label: 全エレ機種', ...verified()] }),
    'KH-G-2.md': card({ id: 'KH-G-2', scope: ['product_lines:', '    - 不明', 'observed_on:', '    - メルシティ', ...verified()] }),
    'KH-G-3.md': card({ id: 'KH-G-3', scope: ['product_lines:', '    - AXEIZ', 'scope_status: unverified'] }),
    'KH-G-4.md': card({ id: 'KH-G-4', scope: ['model_abbreviations:', '    - AXIEZ-LINKs', ...verified()] }),
  };
  const result = await check(await makeRoot(t, files), { ledger: false });
  assert.deepEqual(result.failures, []);
  assert.equal(result.valid, 4);
});

// ---- gap 3: cards outside the allowed folders
test('check fails for card files anywhere under knowledge/cards outside the approved folders, but not the known non-card files', async (t) => {
  const root = await makeRoot(t);
  for (const name of ['INDEX.md', 'README.md', 'TEMPLATE.md', '_SOURCE-LEGEND.md']) await writeFile(path.join(root, 'knowledge/cards', name), '# not a card\n');
  assert.deepEqual((await check(root, { ledger: false })).failures, []);
  await mkdir(path.join(root, 'knowledge/cards/newdir'), { recursive: true });
  await writeFile(path.join(root, 'knowledge/cards/newdir/KH-STRAY.md'), card({ id: 'KH-STRAY' }));
  await writeFile(path.join(root, 'knowledge/cards/KH-TOP.md'), card({ id: 'KH-TOP' }));
  await writeFile(path.join(root, 'knowledge/cards/newdir/README.md'), '# nested readme\n');
  const result = await check(root, { ledger: false });
  const text = reasons(result);
  assert.match(text, /knowledge\/cards\/newdir\/KH-STRAY\.md/u);
  assert.match(text, /knowledge\/cards\/KH-TOP\.md/u);
  assert.match(text, /knowledge\/cards\/newdir\/README\.md/u);
  assert.equal(result.failures.length, 3);
  assert.equal(result.valid, 1);
});

// ---- gap 4: version ledger
test('ledger: missing, fresh, body edit without bump, bump without regenerate, orphan and unlisted cards', async (t) => {
  const root = await makeRoot(t);
  assert.match(reasons(await check(root)), /ledger.*再生成/u);

  await writeKnowhowLedger(root);
  const ledgerText = await readFile(path.join(root, LEDGER), 'utf8');
  const [line] = ledgerText.trim().split('\n');
  const entry = JSON.parse(line);
  assert.deepEqual(Object.keys(entry), ['knowledgeId', 'cardVersion', 'sha256']);
  assert.equal(entry.knowledgeId, 'KH-G-1');
  assert.match(entry.sha256, /^[0-9a-f]{64}$/u);
  assert.deepEqual((await check(root)).failures, []);

  await writeFile(cardPath(root), card({ body: 'edited body without a version bump' }));
  const stale = reasons(await check(root));
  assert.match(stale, /内容が変わったのに card_version が同じ/u);
  assert.match(stale, /card_version を上げてから ledger を再生成/u);
  await assert.rejects(writeKnowhowLedger(root), /card_version/u);
  assert.equal(await readFile(path.join(root, LEDGER), 'utf8'), ledgerText);

  await writeFile(cardPath(root), card({ version: 2, body: 'edited body without a version bump' }));
  assert.match(reasons(await check(root)), /ledger が古い.*再生成/u);
  await writeKnowhowLedger(root);
  assert.deepEqual((await check(root)).failures, []);
  assert.equal(JSON.parse((await readFile(path.join(root, LEDGER), 'utf8')).trim()).cardVersion, 2);

  await writeFile(cardPath(root, 'KH-G-2.md'), card({ id: 'KH-G-2' }));
  assert.match(reasons(await check(root)), /KH-G-2.*ledger/su);
  await rm(cardPath(root, 'KH-G-2.md'));
  assert.deepEqual((await check(root)).failures, []);
  await rm(cardPath(root));
  assert.match(reasons(await check(root)), /KH-G-1.*存在しない/su);
});

test('ledger: lowering card_version is rejected and ledger refuses a malformed existing file', async (t) => {
  const root = await makeRoot(t, { 'KH-G-1.md': card({ version: 3 }) });
  await writeKnowhowLedger(root);
  await writeFile(cardPath(root), card({ version: 2 }));
  assert.match(reasons(await check(root)), /card_version/u);
  await writeFile(path.join(root, LEDGER), 'not json\n');
  assert.match(reasons(await check(root)), /ledger/u);
});

test('CLI: ledger command writes the committed ledger and check then exits 0; edits without a bump exit 1', async (t) => {
  const root = await makeRoot(t);
  await assert.rejects(execFileAsync(process.execPath, [script, 'check', root]), (error) => error.code === 1 && /ledger/u.test(error.stdout));
  const made = await execFileAsync(process.execPath, [script, 'ledger', root]);
  assert.match(made.stdout, /1/u);
  await execFileAsync(process.execPath, [script, 'check', root]);
  await writeFile(cardPath(root), card({ body: 'silently edited' }));
  await assert.rejects(execFileAsync(process.execPath, [script, 'check', root]), (error) => error.code === 1 && /card_version が同じ/u.test(error.stdout));
  await assert.rejects(execFileAsync(process.execPath, [script, 'ledger', root]), (error) => error.code === 1);
  const { stdout } = await execFileAsync(process.execPath, [script, 'check', root, '--no-ledger']);
  assert.match(stdout, /1\/1/u);
});

// ---- gap 5: search term de-duplication
test('searchTerms never contain the same term twice (title, symptoms, keywords, aliases, tags, scope)', async (t) => {
  const dup = card({
    title: 'repeat title',
    extra: ['symptoms: [alpha, alpha, " alpha "]', 'keywords: [alpha, repeat title]', 'aliases: [beta, beta]', 'tags: [beta]'],
    scope: ['product_lines:', '    - alpha', '    - AXIEZ', '    - AXIEZ'],
  });
  const root = await makeRoot(t, { 'KH-G-1.md': dup });
  const index = await buildKnowhowIndex({ root, manifest: await manifestFor(root), today: TODAY });
  const terms = index.cards[0].searchTerms;
  assert.deepEqual(terms, ['repeat title', 'alpha', 'beta', 'AXIEZ']);
});

// ---- gap 6: scope_verified_at
test('a verified date later than today (UTC) fails; today passes; an impossible date gets a friendly message', async (t) => {
  const withDate = (date) => card({ scope: ['product_lines:', '    - AXIEZ', 'scope_status: verified', 'scope_verified_by: r', `scope_verified_at: ${date}`] });
  const root = await makeRoot(t, { 'KH-G-1.md': withDate('2026-10-21') });
  assert.match(reasons(await check(root, { ledger: false, today: '2026-10-20' })), /未来/u);
  assert.deepEqual((await check(root, { ledger: false, today: '2026-10-21' })).failures, []);
  assert.deepEqual((await check(root, { ledger: false })).failures.length, 1, 'default today is the real UTC date, so a far-future date fails');
  await assert.rejects(buildKnowhowIndex({ root, manifest: await manifestFor(root), today: '2026-10-20' }), /未来/u);
  const farFuture = await makeRoot(t, { 'KH-G-1.md': withDate('2999-01-01') });
  assert.match(reasons(await checkKnowhowCards(farFuture, { ledger: false })), /未来/u);

  const impossible = await makeRoot(t, { 'KH-G-1.md': withDate('2026-13-45') });
  const text = reasons(await check(impossible, { ledger: false }));
  assert.match(text, /YYYY-MM-DD/u);
  assert.match(text, /2026-13-45/u);
  assert.equal(text.includes('Invalid time value'), false);
});

// ---- gap 7: file name vs knowledge_id
test('check fails when the file name differs from knowledge_id and names both', async (t) => {
  const root = await makeRoot(t, { 'KH-G-1.md': card(), 'renamed.md': card({ id: 'KH-G-2' }) });
  const result = await check(root, { ledger: false });
  assert.equal(result.valid, 1);
  assert.equal(result.failures.length, 1);
  assert.match(result.failures[0].reason, /renamed/u);
  assert.match(result.failures[0].reason, /KH-G-2/u);
});

// ---- gap 8: duplicate id names both files
test('a duplicate knowledge_id names both file paths in check and inventory', async (t) => {
  const root = await makeRoot(t, { 'KH-G-1.md': card(), 'other.md': card() });
  const result = await check(root, { ledger: false });
  const text = reasons(result);
  assert.match(text, /practice-guides\/KH-G-1\.md/u);
  assert.match(text, /practice-guides\/other\.md/u);
  await assert.rejects(inventoryKnowhowCards(root), (error) => /KH-G-1\.md/u.test(error.message) && /other\.md/u.test(error.message));
});

// ---- gap 10: URL in title
test('a URL or control character in the title is rejected like other scalars, while "/" is allowed', async (t) => {
  for (const title of ['"see https://example.com/x"', '"a s3://bucket/key"', '"x javascript:alert(1)"', '"back\\\\slash"', '"line\\nbreak"', '"../up"']) {
    const root = await makeRoot(t, { 'KH-G-1.md': card({ title }) });
    const result = await check(root, { ledger: false });
    assert.equal(result.valid, 0, title);
    await assert.rejects(buildKnowhowIndex({ root, manifest: await manifestFor(root), today: TODAY }), undefined, title);
  }
  const ok = await makeRoot(t, { 'KH-G-1.md': card({ title: '"D14 DCB/DOB 構成"' }) });
  assert.deepEqual((await check(ok, { ledger: false })).failures, []);
});
