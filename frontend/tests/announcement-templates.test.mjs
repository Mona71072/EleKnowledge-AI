import test from 'node:test';
import assert from 'node:assert/strict';
import { ANNOUNCEMENT_TEMPLATES, getTemplate, fillTemplate, templatePlaceholders } from '../src/lib/announcement-templates.mjs';

test('six templates with presets; critical ones show in chat', () => {
  assert.equal(ANNOUNCEMENT_TEMPLATES.length, 6);
  for (const t of ANNOUNCEMENT_TEMPLATES) {
    assert.ok(t.key && t.name && t.title && t.body && t.when);
    assert.ok(['notice', 'update', 'maintenance'].includes(t.type));
    assert.ok(['info', 'warning', 'critical'].includes(t.severity));
    if (t.severity === 'critical') assert.equal(t.showInChat, true);
  }
  assert.equal(getTemplate('incident').severity, 'critical');
  assert.equal(getTemplate('maintenance').type, 'maintenance');
  assert.equal(getTemplate('nope'), null);
});

test('fillTemplate fills known holes and leaves unknown ones', () => {
  const body = getTemplate('incident').body;
  const filled = fillTemplate(body, { 時刻: '本日 07:50' });
  assert.ok(filled.startsWith('本日 07:50 ごろから'));
  assert.ok(filled.includes('{{復旧見込み}}'));
  assert.equal(fillTemplate('{{a}}-{{ b }}', { a: 1, b: null }), '1-{{ b }}');
  assert.equal(fillTemplate(null), '');
});

test('templatePlaceholders lists remaining holes once, in order', () => {
  assert.deepEqual(templatePlaceholders(getTemplate('recovered').body), ['復旧時刻', '発生時刻']);
  assert.deepEqual(templatePlaceholders('no holes'), []);
});
