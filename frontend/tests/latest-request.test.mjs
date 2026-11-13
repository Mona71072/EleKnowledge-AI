import test from 'node:test';
import assert from 'node:assert/strict';
import { createLatestGuard } from '../src/lib/latest-request.mjs';

test('後から始めた要求だけが最新と判定される', () => {
  const guard = createLatestGuard();
  const older = guard.begin();
  const latest = guard.begin();

  assert.equal(guard.isLatest(older), false);
  assert.equal(guard.isLatest(latest), true);
});

test('古いトークンは新しい要求の完了後も無効のまま', () => {
  const guard = createLatestGuard();
  const older = guard.begin();
  const latest = guard.begin();

  assert.equal(guard.isLatest(latest), true);
  assert.equal(guard.isLatest(older), false);
});

test('invalidate後は直前のトークンが最新でなくなる', () => {
  const guard = createLatestGuard();
  const token = guard.begin();

  guard.invalidate();

  assert.equal(guard.isLatest(token), false);
});
