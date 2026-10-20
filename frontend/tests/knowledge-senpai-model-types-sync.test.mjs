import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { SENPAI_MODEL_TYPES } from '../src/lib/knowledge-senpai-chat.mjs';

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8');
const sorted = (values) => [...values].sort();

test('SENPAI_MODEL_TYPES equals the UI option values in kbModelTypes.ts', () => {
  const values = [...read('../src/data/kbModelTypes.ts').matchAll(/value:\s*'([^']+)'/gu)].map((m) => m[1])
    .filter((value) => value !== 'string');
  assert.ok(values.length > 0);
  assert.deepEqual(sorted(SENPAI_MODEL_TYPES), sorted(values));
});

test('SENPAI_MODEL_TYPES equals the RAG UI_MODEL_FILTERS keys', () => {
  const source = read('../../lambda/rag/rag-function/app.py');
  const block = source.match(/^UI_MODEL_FILTERS\s*=\s*\{([\s\S]*?)^\}/mu);
  assert.ok(block, 'UI_MODEL_FILTERS not found');
  const keys = [...block[1].matchAll(/^\s*'([^']+)'\s*:/gmu)].map((m) => m[1]);
  assert.ok(keys.length > 0);
  assert.deepEqual(sorted(SENPAI_MODEL_TYPES), sorted(keys));
});
