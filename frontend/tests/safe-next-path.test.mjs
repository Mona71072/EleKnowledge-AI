import test from 'node:test';
import assert from 'node:assert/strict';
import { safeNextPath } from '../src/lib/safe-next-path.mjs';

test('通常の内部パスはそのまま通す', () => {
  assert.equal(safeNextPath('/'), '/');
  assert.equal(safeNextPath('/chat'), '/chat');
  assert.equal(
    safeNextPath('/doc?uri=s3%3A%2F%2Fbucket%2Fdocs%2Fa.pdf#page=42'),
    '/doc?uri=s3%3A%2F%2Fbucket%2Fdocs%2Fa.pdf#page=42',
  );
});

test('空・null はホームへ', () => {
  assert.equal(safeNextPath(null), '/');
  assert.equal(safeNextPath(''), '/');
  assert.equal(safeNextPath(undefined), '/');
});

test('外部 URL は拒否してホームへ', () => {
  assert.equal(safeNextPath('https://evil.com/'), '/');
  assert.equal(safeNextPath('http://evil.com/x'), '/');
  assert.equal(safeNextPath('javascript:alert(1)'), '/');
});

test('protocol-relative //host は拒否', () => {
  assert.equal(safeNextPath('//evil.com'), '/');
  assert.equal(safeNextPath('//evil.com/path'), '/');
});

test('バックスラッシュ系は拒否（URL パーサはスラッシュと同一視する）', () => {
  assert.equal(safeNextPath('/\\evil.com'), '/');
  assert.equal(safeNextPath('\\/evil.com'), '/');
  assert.equal(safeNextPath('\\\\evil.com'), '/');
  assert.equal(safeNextPath('/chat\\..\\x'), '/');
});

test('正規化後にパスが // 始まりになる入力は拒否', () => {
  assert.equal(safeNextPath('/..//evil.com'), '/');
  assert.equal(safeNextPath('/x/..//evil.com'), '/');
});

test('パーセントエンコードはデコードせずパスの一部として扱う（無害）', () => {
  assert.equal(safeNextPath('/%5Cevil.com'), '/%5Cevil.com');
  assert.equal(safeNextPath('/%2F%2Fevil.com'), '/%2F%2Fevil.com');
});
