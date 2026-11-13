import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const source = readFileSync(new URL('../src/app/chat/page.tsx', import.meta.url), 'utf8');

test('chat page never passes the raw law sourceUrl to a link', () => {
  const uses = [...source.matchAll(/doc\.lawCitation\??\.sourceUrl/gu)];
  assert.ok(uses.length > 0);
  for (const use of uses) {
    const before = source.slice(Math.max(0, use.index - 20), use.index);
    assert.match(before, /safeExternalHref\($/u, `unvalidated use near offset ${use.index}`);
  }
});
