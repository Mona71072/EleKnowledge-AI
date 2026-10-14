import test from 'node:test';
import assert from 'node:assert/strict';
import { announcementDate, loadReadAnnouncementIds, markAnnouncementRead } from '../src/lib/announcement-display.mjs';

function memoryStorage() {
  const values = new Map();
  return { getItem: (key) => values.get(key) ?? null, setItem: (key, value) => values.set(key, value) };
}

test('投稿日は日本時間の日付だけを表示し、日付境界を扱う', () => {
  assert.equal(announcementDate('2026-10-14T15:01:00Z'), '2026/10/15');
  assert.equal(announcementDate('2026-10-14T14:59:00Z'), '2026/10/14');
  assert.equal(announcementDate('invalid'), '日付不明');
});

test('開いた1件だけ既読にして再読み込み後も保持する', () => {
  const storage = memoryStorage();
  assert.deepEqual(loadReadAnnouncementIds('user-a', storage), []);
  assert.deepEqual(markAnnouncementRead('user-a', 'one', [], storage), ['one']);
  assert.deepEqual(loadReadAnnouncementIds('user-a', storage), ['one']);
  assert.equal(loadReadAnnouncementIds('user-a', storage).includes('two'), false);
  assert.deepEqual(loadReadAnnouncementIds('user-b', storage), []);
});

test('他タブの既読も保持し、同じ項目の再閲覧は重複しない', () => {
  const storage = memoryStorage();
  markAnnouncementRead('user', 'one', [], storage);
  assert.deepEqual(markAnnouncementRead('user', 'two', [], storage), ['one', 'two']);
  assert.deepEqual(markAnnouncementRead('user', 'one', [], storage), ['one', 'two']);
});

test('不正な保存値を無視し、有効なIDだけを読み込む', () => {
  const storage = memoryStorage();
  for (const value of ['invalid', '{}', 'null', '42']) {
    storage.setItem('user', value);
    assert.deepEqual(loadReadAnnouncementIds('user', storage), []);
  }
  storage.setItem('user', '["one", "one", null, 1, ""]');
  assert.deepEqual(loadReadAnnouncementIds('user', storage), ['one']);
});

test('ストレージが使えなくても閲覧中の既読は更新できる', () => {
  const storage = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('full'); } };
  assert.deepEqual(loadReadAnnouncementIds('user', storage), []);
  assert.deepEqual(markAnnouncementRead('user', 'two', ['one'], storage), ['one', 'two']);
});
