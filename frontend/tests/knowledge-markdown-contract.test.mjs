import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { buildKnowhowIndex } from '../../scripts/knowledge/build-senpai-index.mjs';
import { queryKnowledgeSource } from '../src/lib/knowledge-research.mjs';

test('compiled Markdown is searched by Python and accepted unchanged by the chat client', async (t) => {
  const root = await mkdtemp(path.join(os.tmpdir(), 'senpai-contract-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const relativePath = 'knowledge/cards/practice-guides/synthetic.md';
  const markdown = `---
knowledge_id: KH-SYNTH-CONTRACT
card_version: 2
status: draft
title: 合成点検の確認条件
symptoms: [合成点検]
model_scope:
  model_abbreviations: []
  excludes: [実設備]
source_refs:
  - ref_type: lists_item
    list_item_id: SYNTH-123
    source_id: SYNTH-SOURCE-123
  - ref_type: kb_document
    document_number: TI-0000
    kb_filename: SYNTHETIC.pdf
    kb_verify_status: pending
---
## 条件
合成点検のテスト専用であり、実設備には適用しない。
`;
  await mkdir(path.dirname(path.join(root, relativePath)), { recursive: true });
  await writeFile(path.join(root, relativePath), markdown);
  const sha256 = createHash('sha256').update(markdown).digest('hex');
  const index = await buildKnowhowIndex({ root, manifest: {
    schemaVersion: 1, purpose: 'senpai-admin-navigation', approvedBy: 'SYNTHETIC-ONLY',
    approvedAt: '2026-10-20T00:00:00.000Z',
    entries: [{ path: relativePath, knowledgeId: 'KH-SYNTH-CONTRACT', cardVersion: 2, sha256, cloudApproved: true }],
  } });
  const modulePath = fileURLToPath(new URL('../../lambda/rag/rag-function/knowhow_retrieval.py', import.meta.url));
  const program = `import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('knowhow_contract',sys.argv[1])
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
index=module.parse_index(sys.stdin.buffer.read())
result=module.search_index(index,'合成点検の確認条件を教えて')
result['searchTerms']=module.derive_kb_hints(result['matches'])
print(json.dumps(result,ensure_ascii=False))
`;
  const knowhow = JSON.parse(execFileSync(process.env.PYTHON || 'python3', ['-c', program, modulePath], {
    input: JSON.stringify(index), encoding: 'utf8', timeout: 10000,
  }));
  const answer = await queryKnowledgeSource({
    baseUrl: 'https://api.example.invalid', getToken: async () => 'synthetic-token',
    mode: 'normal', query: '合成点検の確認条件を教えて', includeKnowhow: true,
    fetchImpl: async () => ({ ok: true, json: async () => ({
      sessionId: 'synthetic-session', aiMessageId: 'synthetic-message', responseType: 'pages',
      content: '合成応答', sourceDocuments: [], pageCandidates: [], clarifyQuestions: [], knowhow,
    }) }),
  });
  assert.equal(answer.knowhow.status, 'matched');
  assert.equal(answer.knowhow.matches[0].sha256, sha256);
  assert.equal(answer.knowhow.matches[0].cardVersion, 2);
  assert.deepEqual(answer.knowhow.matches[0].modelScope.model_abbreviations, []);
  assert.equal(answer.knowhow.matches[0].sourceRefs[0].source_id, 'SYNTH-SOURCE-123');
  assert.match(answer.knowhow.matches[0].body, /実設備には適用しない/);
  assert.deepEqual(answer.knowhow.searchTerms, ['TI-0000', 'SYNTHETIC.pdf']);
});
