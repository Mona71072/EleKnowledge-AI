import test from 'node:test';
import assert from 'node:assert/strict';
import {
  jstTime,
  jstDateTime,
  jstDateLabel,
  formatUsd,
  formatSeconds,
  formatDuration,
  formatCount,
  rateLabel,
  logsInsightsUrl,
  worstStatus,
} from '../src/lib/metrics-format.mjs';

test('jstTime / jstDateTime convert UTC ISO to JST', () => {
  assert.equal(jstTime('2026-09-23T17:03:00Z'), '02:03');
  assert.equal(jstDateTime('2026-09-23T14:10:00Z'), '9/23 23:10');
  assert.equal(jstTime(null), '—');
  assert.equal(jstTime('garbage'), '—');
});

test('jstDateLabel adds the weekday', () => {
  assert.equal(jstDateLabel('2026-09-23'), '9/23（水）');
  assert.equal(jstDateLabel('2026-09-23', false), '9/23');
  assert.equal(jstDateLabel(null), '—');
});

test('formatUsd / formatSeconds / formatCount distinguish null from zero', () => {
  assert.equal(formatUsd(3.256), '3.26 USD');
  assert.equal(formatUsd(0), '0.00 USD');
  assert.equal(formatUsd(null), '—');
  assert.equal(formatSeconds(11200), '11.2 s');
  assert.equal(formatSeconds(null), '—');
  assert.equal(formatCount(0), '0');
  assert.equal(formatCount(null), '—');
  assert.equal(formatCount(1234), '1,234');
});

test('formatDuration', () => {
  assert.equal(formatDuration(null), '継続中');
  assert.equal(formatDuration(45), '45 秒');
  assert.equal(formatDuration(900), '15 分');
  assert.equal(formatDuration(3900), '1 時間 5 分');
  assert.equal(formatDuration(7200), '2 時間');
});

test('rateLabel only when the denominator is large enough (§2.7)', () => {
  assert.equal(rateLabel(2, 28), null);
  assert.equal(rateLabel(19, 176), '11 %');
  assert.equal(rateLabel(null, 176), null);
  assert.equal(rateLabel(3, 30), '10 %');
});

test('logsInsightsUrl encodes group and time range, null when incomplete', () => {
  const url = logsInsightsUrl({ logGroup: '/aws/lambda/rag-dev', from: '2026-09-23T13:55:00Z', to: '2026-09-23T14:25:00Z' });
  assert.ok(url.startsWith('https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-1#logsV2:logs-insights'));
  assert.ok(url.includes('*2Faws*2Flambda*2Frag-dev'));
  assert.ok(url.includes("start~'2026-09-23T13*3A55*3A00Z"));
  assert.equal(logsInsightsUrl({ logGroup: null, from: 'a', to: 'b' }), null);
});

test('worstStatus picks the worst', () => {
  assert.equal(worstStatus('good', 'warning'), 'warning');
  assert.equal(worstStatus('serious', 'warning', 'good'), 'serious');
  assert.equal(worstStatus(), 'good');
});
