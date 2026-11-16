import assert from 'node:assert/strict';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import * as workbench from '../src/lib/knowledge-workbench.mjs';
import * as rewrite from '../src/lib/knowhow-rewrite.mjs';
import { insertFieldMaterialMarkdown, readFieldMaterialFile } from '../src/lib/knowledge-field-material.mjs';
import { checkKnowhowCards } from '../../scripts/knowledge/build-senpai-index.mjs';

test('a new field card is a locally identifiable, parseable draft', async () => {
  const card = workbench.createKnowledgeDraft('点検時の確認箇所: 合成例');
  const next = workbench.createWorkspace(card);
  assert.match(card.id, /^KH-FIELD-[A-F0-9]{32}$/u);
  assert.notEqual(card.id, workbench.createKnowledgeDraft(card.title).id);
  assert.equal(card.title, '点検時の確認箇所: 合成例');
  assert.equal(card.metadata.status, 'draft');
  assert.equal(card.metadata.kind, 'practice_guide');
  assert.equal(card.version, 1);
  assert.equal((await workbench.exportProposal(next)).proposal.publishable, false);
  assert.throws(() => workbench.createKnowledgeDraft('改行\n別行'), /タイトル/u);
});

test('field proposal sends one selected excerpt with a neutral envelope and empty card content', () => {
  const excerpt = '合成資料の該当箇所。\nこの条件を確認する。';
  const request = rewrite.buildFieldRewriteRequest({
    topic: '確認順を整理する', title: '現場の合成資料', excerpt,
    checkedOn: '2026-11-14', cardBody: '別のカード本文', original: '選択外の原文',
  });
  assert.deepEqual(request, {
    knowledgeId: 'KH-FIELD-MATERIAL', cardVersion: 1,
    context: [], targets: [{ heading: '統合した回答・ノウハウ', body: '' }],
    evidence: [{ question: '確認順を整理する', lane: 'field', checkedOn: '2026-11-14', answer: excerpt,
      sources: [{ title: '現場の合成資料' }] }],
  });
  assert.throws(() => rewrite.buildFieldRewriteRequest({ title: '資料', excerpt: 'あ'.repeat(2001), checkedOn: '2026-11-14' }), /抜粋/u);
  assert.throws(() => rewrite.buildFieldRewriteRequest({ title: '資料', excerpt, checkedOn: '2026-02-30' }), /日付/u);
});

test('a field draft with a reviewed attachment passes the existing Senpai index contract', async () => {
  const root = await mkdtemp(join(tmpdir(), 'field-card-index-'));
  try {
    const card = workbench.createKnowledgeDraft('合成端子の観測事例');
    const original = await readFieldMaterialFile(new File(['合成の資料原文'], 'synthetic-source.txt'));
    const nextBody = insertFieldMaterialMarkdown(card.body, '合成条件の観測を記録した。', {
      ...original, title: '合成資料', version: '版1', locator: '確認事項',
    }, { reviewed: true });
    const packet = await workbench.exportProposal(workbench.editBody(workbench.createWorkspace(card), nextBody));
    const folder = join(root, 'knowledge', 'cards', 'practice-guides');
    await mkdir(folder, { recursive: true });
    await writeFile(join(folder, `${card.id}.md`), packet.proposal.markdown);
    assert.deepEqual(await checkKnowhowCards(root, { ledger: false }), { total: 1, valid: 1, failures: [] });
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test('ordinary KB rewrite context excludes the field source block and its attachment link', () => {
  const { context } = rewrite.selectRewriteSections([
    '## 統合した回答・ノウハウ', '対象の確認手順。',
    '## 現場資料に基づくノウハウ', '現場資料の要点。', '> 確認済みリンク: <https://example.invalid/field-notes>',
    '## 適用条件', '通常の文脈。',
  ].join('\n'));
  assert.deepEqual(context, [{ heading: '適用条件', body: '通常の文脈。' }]);
});
