import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { SENPAI_MODEL_TYPES } from '../src/lib/knowledge-senpai-chat.mjs';
import { KB_MODEL_KEYS, KB_MODEL_TYPES } from '../src/data/kb-model-types.generated.mjs';

// 機種の値は knowledge/registry/applicability-vocabulary.json から生成する（scripts/knowledge/generate_vocabulary.py）。
// Python 側の生成物（vocabulary_generated.py）とは tests/unit/test_applicability_vocabulary.py が照合する。
const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8');
const sorted = (values) => [...values].sort();

test('SENPAI_MODEL_TYPES equals the generated UI option values', () => {
  const values = KB_MODEL_TYPES.map((model) => model.value);
  assert.ok(values.length > 0);
  assert.deepEqual(sorted(SENPAI_MODEL_TYPES), sorted(values));
  assert.deepEqual(sorted(KB_MODEL_KEYS), sorted(values));
});

test('SENPAI_MODEL_TYPES equals the RAG UI_MODEL_FILTERS keys generated for the Lambda', () => {
  const source = read('../../lambda/rag/rag-function/vocabulary_generated.py');
  const block = source.match(/^UI_MODEL_FILTERS\s*=\s*\{([\s\S]*?)^\}/mu);
  assert.ok(block, 'UI_MODEL_FILTERS not found');
  const keys = [...block[1].matchAll(/^\s*"([^"]+)"\s*:/gmu)].map((m) => m[1]);
  assert.ok(keys.length > 0);
  assert.deepEqual(sorted(SENPAI_MODEL_TYPES), sorted(keys));
  assert.match(read('../../lambda/rag/rag-function/app.py'), /^UI_MODEL_FILTERS = _vocabulary\.UI_MODEL_FILTERS\r?$/mu);
});

test('kbModelTypes.ts takes the model list from the generated file', () => {
  const source = read('../src/data/kbModelTypes.ts');
  assert.match(source, /from '\.\/kb-model-types\.generated\.mjs'/u);
  assert.doesNotMatch(source, /value:\s*'/u);
});
