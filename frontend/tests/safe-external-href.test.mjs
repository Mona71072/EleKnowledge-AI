import assert from 'node:assert/strict';
import test from 'node:test';
import { safeExternalHref } from '../src/lib/safe-external-href.mjs';

test('keeps http and https links', () => {
  assert.equal(safeExternalHref('https://example.com/a.pdf'), 'https://example.com/a.pdf');
  assert.equal(safeExternalHref('http://example.com/a'), 'http://example.com/a');
  assert.equal(safeExternalHref('  HTTPS://example.com/a  '), 'HTTPS://example.com/a');
});

test('rejects script and other non-web schemes regardless of case or whitespace', () => {
  for (const value of [
    'javascript:alert(1)',
    'JavaScript:alert(1)',
    '  javascript:alert(1)',
    '\tjava\nscript:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'file:///etc/passwd',
    'ftp://example.com/a',
  ]) {
    assert.equal(safeExternalHref(value), undefined, value);
  }
});

test('rejects relative paths and empty values', () => {
  for (const value of ['/doc?uri=x', '../a.pdf', 'a.pdf', '//example.com/a', '', '   ', undefined, null, 42]) {
    assert.equal(safeExternalHref(value), undefined, String(value));
  }
});
