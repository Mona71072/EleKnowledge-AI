import test from 'node:test';
import assert from 'node:assert/strict';
import { jstToday, startOfWeekJst, periodRange, isThisWeekJst } from '../src/lib/failures-period.mjs';

// UTC 9/23 23:41 = JST 9/24（木）08:41
const NOW = new Date('2026-09-23T23:41:00Z');

test('jstToday uses the JST date', () => {
  assert.equal(jstToday(NOW), '2026-09-24');
  assert.equal(jstToday(new Date('2026-09-23T14:59:59Z')), '2026-09-23');
  assert.equal(jstToday(new Date('2026-09-23T15:00:00Z')), '2026-09-24');
});

test('periodRange', () => {
  assert.deepEqual(periodRange('1', NOW), { since: '2026-09-23', until: '2026-09-23' });
  assert.deepEqual(periodRange('7', NOW), { since: '2026-09-18', until: '2026-09-24' });
  assert.deepEqual(periodRange('30', NOW), { since: '2026-08-26', until: '2026-09-24' });
  assert.deepEqual(periodRange('all', NOW), { since: null, until: null });
});

test('startOfWeekJst is Monday', () => {
  assert.equal(startOfWeekJst(NOW), '2026-09-21');                       // 木曜 → 月曜
  assert.equal(startOfWeekJst(new Date('2026-09-20T23:41:00Z')), '2026-09-21'); // JST 9/21（月）08:41
  assert.equal(startOfWeekJst(new Date('2026-09-19T23:41:00Z')), '2026-09-14'); // JST 9/20（日）
});

test('isThisWeekJst', () => {
  assert.equal(isThisWeekJst('2026-09-22T02:11:00Z', NOW), true);
  assert.equal(isThisWeekJst('2026-09-20T02:11:00Z', NOW), false);
  assert.equal(isThisWeekJst(null, NOW), false);
});
