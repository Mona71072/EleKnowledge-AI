import assert from 'node:assert/strict';
import test from 'node:test';
import { evaluateDependencyAudit } from '../scripts/dependency-audit-policy.mjs';

const id = 'GHSA-vfj7-8cjw-p6xm';
const advisory = (value) => ({ url: `https://github.com/advisories/${value}` });
const report = { metadata: { vulnerabilities: { high: 2, critical: 0 } }, vulnerabilities: {
  parent: { severity: 'high', via: ['leaf'] },
  leaf: { severity: 'high', via: [advisory(id)] },
} };
const exception = { id, reason: 'Synthetic test only', expires: '2026-10-15',
  issue: 'https://github.com/yukiworkspace/EleKnowledge-AI/issues/173',
  approvalUrl: 'https://github.com/yukiworkspace/EleKnowledge-AI/pull/185#issuecomment-123' };
const now = new Date('2026-10-15T14:59:59Z');

test('empty exceptions reject both direct and transitive high vulnerabilities', () => {
  assert.equal(evaluateDependencyAudit(report, [], now).blocked.length, 2);
});
test('an active advisory exception covers its transitive chain until JST midnight', () => {
  const result = evaluateDependencyAudit(report, [exception], now);
  assert.equal(result.blocked.length, 0);
  assert.equal(result.excepted.length, 2);
});
test('expired exceptions cannot suppress vulnerabilities', () => {
  assert.throws(() => evaluateDependencyAudit(report, [exception], new Date('2026-10-15T15:00:00Z')), /期限切れ/);
});
test('a second advisory remains blocked', () => {
  const mixed = structuredClone(report);
  mixed.vulnerabilities.leaf.via.push(advisory('GHSA-aaaa-bbbb-cccc'));
  assert.equal(evaluateDependencyAudit(mixed, [exception], now).blocked.length, 2);
});
test('missing required approval, invalid calendar date and duplicates fail', () => {
  for (const entry of [{ ...exception, approvalUrl: '' }, { ...exception, expires: '2026-02-31' }]) {
    assert.throws(() => evaluateDependencyAudit(report, [entry], now));
  }
  assert.throws(() => evaluateDependencyAudit(report, [exception, exception], now));
});
test('unknown advisories and cyclic dependencies fail closed', () => {
  const cyclic = structuredClone(report);
  cyclic.vulnerabilities.leaf.via = ['parent'];
  assert.equal(evaluateDependencyAudit(cyclic, [exception], now).blocked.length, 2);
});
test('audit errors, incomplete JSON and inconsistent counts fail', () => {
  for (const value of [{ error: { code: 'ENET' } }, {}, { ...report, metadata: { vulnerabilities: { high: 0 } } }]) {
    assert.throws(() => evaluateDependencyAudit(value, [], now));
  }
});
test('zero findings pass without exceptions', () => {
  assert.deepEqual(evaluateDependencyAudit({ vulnerabilities: {}, metadata: { vulnerabilities: {} } }, [], now),
    { blocked: [], excepted: [] });
});
