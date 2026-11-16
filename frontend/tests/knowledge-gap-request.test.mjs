import test from 'node:test';
import assert from 'node:assert/strict';
import { consumeKnowledgeGapRequest, consumeResearchQuery, storeKnowledgeGapRequest, storeResearchQuery } from '../src/lib/knowledge-gap-request.mjs';

const TURN_ID = '123e4567-e89b-42d3-a456-426614174000';

function storage(initial = null) {
  const values = new Map(initial === null ? [] : [['knowledge-gap-request', initial]]);
  return {
    getItem(key) { return values.get(key) ?? null; },
    setItem(key, next) { values.set(key, next); },
    removeItem(key) { values.delete(key); },
    value: (key = 'knowledge-gap-request') => values.get(key) ?? null,
  };
}

test('stores only the minimal Senpai turn marker in one session item', () => {
  const target = storage();
  assert.equal(storeKnowledgeGapRequest({ senpaiTurnId: TURN_ID }, target), true);
  assert.deepEqual(JSON.parse(target.value()), { version: 1, kind: 'senpai', senpaiTurnId: TURN_ID });
});

test('a later explicit handoff replaces the one pending item', () => {
  const target = storage();
  storeKnowledgeGapRequest({ senpaiTurnId: TURN_ID }, target);
  const nextId = '123e4567-e89b-42d3-a456-426614174001';
  storeKnowledgeGapRequest({ senpaiTurnId: nextId, question: 'must not be retained' }, target);
  assert.deepEqual(JSON.parse(target.value()), { version: 1, kind: 'senpai', senpaiTurnId: nextId });
});

test('consumes a valid request once and removes it from session storage', () => {
  const target = storage(JSON.stringify({ version: 1, kind: 'senpai', senpaiTurnId: TURN_ID }));
  assert.deepEqual(consumeKnowledgeGapRequest(target), { kind: 'senpai', senpaiTurnId: TURN_ID });
  assert.equal(target.value(), null);
  assert.equal(consumeKnowledgeGapRequest(target), null);
});

test('official KB handoff keeps only its origin, discarding chat text and identifiers', () => {
  const target = storage();
  storeKnowledgeGapRequest({ senpaiTurnId: TURN_ID }, target);
  assert.equal(storeKnowledgeGapRequest({ kind: 'official_kb', question: 'private', messageId: 'message' }, target), true);
  assert.deepEqual(JSON.parse(target.value()), { version: 1, kind: 'official_kb' });
  assert.deepEqual(consumeKnowledgeGapRequest(target), { kind: 'official_kb' });
  assert.equal(consumeKnowledgeGapRequest(target), null);
});

test('rejects malformed, extra-field, and unavailable storage safely', () => {
  const malformed = storage(JSON.stringify({ version: 1, kind: 'senpai', senpaiTurnId: 'bad' }));
  assert.equal(consumeKnowledgeGapRequest(malformed), null);
  assert.equal(malformed.value(), null);
  const extra = storage(JSON.stringify({ version: 1, kind: 'senpai', senpaiTurnId: TURN_ID, question: 'secret' }));
  assert.equal(consumeKnowledgeGapRequest(extra), null);
  assert.equal(consumeKnowledgeGapRequest(storage(JSON.stringify({ version: 1, kind: 'official_kb', question: 'secret' }))), null);
  assert.equal(storeKnowledgeGapRequest({ senpaiTurnId: 'bad' }, storage()), false);
  assert.equal(consumeKnowledgeGapRequest(), null);
  assert.equal(storeKnowledgeGapRequest({ senpaiTurnId: TURN_ID }, null), false);
});

test('stores and consumes a research query once without putting it in a URL marker', () => {
  const target = storage();
  assert.equal(storeResearchQuery('ブレーキの確認手順', target), true);
  assert.equal(JSON.parse(target.value('knowledge-research-query')).query, 'ブレーキの確認手順');
  assert.equal(consumeResearchQuery(target), 'ブレーキの確認手順');
  assert.equal(target.value('knowledge-research-query'), null);
  assert.equal(consumeResearchQuery(target), null);
});

test('rejects empty, oversized, malformed, and unavailable research handoffs', () => {
  const target = storage();
  assert.equal(storeResearchQuery('  ', target), false);
  assert.equal(storeResearchQuery('質問'.repeat(2001), target), false);
  assert.equal(storeResearchQuery('質問', null), false);
  assert.equal(consumeResearchQuery(storage('{bad json')), null);
  assert.equal(consumeResearchQuery(null), null);
});
