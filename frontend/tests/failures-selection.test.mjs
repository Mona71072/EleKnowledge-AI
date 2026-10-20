import test from 'node:test';
import assert from 'node:assert/strict';
import { failureTruncationNotices, isReformulatedFailure } from '../src/lib/failures-selection.mjs';

test('reformulated一覧はreformulatedがtrueの項目だけを含める', () => {
  assert.equal(isReformulatedFailure({ reformulated: true }), true);
  assert.equal(isReformulatedFailure({ reformulated: false, signals: ['reformulated'] }), false);
  assert.equal(isReformulatedFailure({ signals: ['reformulated'] }), false);
});

test('切り詰め時は一致件数を表示し、未切り詰めの一覧は表示しない', () => {
  assert.deepEqual(failureTruncationNotices(
    { truncated: true, matchedCount: 137, count: 100 },
    { truncated: false, matchedCount: 4, count: 4 },
  ), ['表示は先頭 100 件です（全 137 件）']);
  assert.deepEqual(failureTruncationNotices(
    { truncated: false, count: 4 },
    { truncated: true, count: 100 },
  ), ['言い換え一覧は先頭 100 件です（全 100 件）']);
});

test('Scan途中打ち切り時は走査済み範囲の件数を全件数と区別して表示する', () => {
  assert.deepEqual(failureTruncationNotices(
    { incomplete: true, matchedCount: 37, count: 37 },
    { incomplete: false, truncated: false, count: 4 },
  ), ['走査済みの範囲で 37 件（全件ではありません）']);
});

test('incompleteとtruncatedが両方ある場合は走査済み範囲の案内を優先する', () => {
  assert.deepEqual(failureTruncationNotices(
    { incomplete: true, truncated: true, matchedCount: 100, count: 100 },
    { incomplete: false, truncated: true, matchedCount: 125, count: 100 },
  ), [
    '走査済みの範囲で 100 件（全件ではありません）',
    '言い換え一覧は先頭 100 件です（全 125 件）',
  ]);
});
