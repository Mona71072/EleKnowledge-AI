import test from 'node:test';
import assert from 'node:assert/strict';
import { appendAnnouncementPage, sortActiveAnnouncements } from '../src/lib/announcement-list.mjs';

test('次ページは末尾に足し、読み込み済みと同じ announcementId は除く', () => {
  const current = [{ announcementId: 'a1' }, { announcementId: 'a2' }];
  const next = [{ announcementId: 'a2' }, { announcementId: 'a3' }, { announcementId: 'a3' }, { announcementId: 'a4' }];
  assert.deepEqual(
    appendAnnouncementPage(current, next).map((a) => a.announcementId),
    ['a1', 'a2', 'a3', 'a4'],
  );
});

test('元の配列を書き換えない', () => {
  const current = [{ announcementId: 'a1' }];
  const merged = appendAnnouncementPage(current, [{ announcementId: 'a2' }]);
  assert.equal(current.length, 1);
  assert.equal(merged.length, 2);
});

test('空のページは一覧をそのまま返す', () => {
  const current = [{ announcementId: 'a1' }];
  assert.deepEqual(appendAnnouncementPage(current, []), current);
});

test('いま表示中は重要度順、同じ重要度は公開日時の新しい順で、元の配列を書き換えない', () => {
  const list = [
    { announcementId: 'n', severity: 'info', publishAt: '2026-05-03T00:00:00.000Z' },
    { announcementId: 'c', severity: 'critical', publishAt: '2026-05-01T00:00:00.000Z' },
    { announcementId: 'w', severity: 'warning', publishAt: '2026-05-02T00:00:00.000Z' },
    { announcementId: 'c2', severity: 'critical', publishAt: '2026-05-04T00:00:00.000Z' },
  ];
  const before = list.map((a) => a.announcementId);
  assert.deepEqual(sortActiveAnnouncements(list).map((a) => a.announcementId), ['c2', 'c', 'w', 'n']);
  assert.deepEqual(list.map((a) => a.announcementId), before);
});
