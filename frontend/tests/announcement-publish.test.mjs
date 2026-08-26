import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveAnnouncementPublishFields } from '../src/lib/announcement-publish.mjs';

const NOW_MS = Date.parse('2026-08-26T00:00:00.000Z');

test('公開済み編集では既存 publishAt を保持する', () => {
  const existingPublishAt = '2026-08-20T03:00:00.000Z';
  const result = resolveAnnouncementPublishFields({
    requestedStatus: 'published',
    publishMode: 'now',
    scheduleAt: '',
    editingId: 'announcement-1',
    existingStatus: 'published',
    existingPublishAt,
    nowMs: NOW_MS,
  });

  assert.deepEqual(result, {
    status: 'published',
    publishAt: existingPublishAt,
  });
});

test('scheduled かつ予約時刻が過去なら published に切り替え、時刻を保持する', () => {
  const scheduleAt = '2026-08-25T09:00';
  const result = resolveAnnouncementPublishFields({
    requestedStatus: 'published',
    publishMode: 'schedule',
    scheduleAt,
    editingId: 'announcement-2',
    existingStatus: 'scheduled',
    existingPublishAt: new Date(scheduleAt).toISOString(),
    nowMs: new Date('2026-08-25T10:00').getTime(),
  });

  assert.deepEqual(result, {
    status: 'published',
    publishAt: new Date(scheduleAt).toISOString(),
  });
});

test('scheduled かつ予約時刻が未来なら scheduled のまま時刻を保持する', () => {
  const scheduleAt = '2026-08-25T11:00';
  const result = resolveAnnouncementPublishFields({
    requestedStatus: 'published',
    publishMode: 'schedule',
    scheduleAt,
    editingId: 'announcement-3',
    existingStatus: 'scheduled',
    existingPublishAt: new Date(scheduleAt).toISOString(),
    nowMs: new Date('2026-08-25T10:00').getTime(),
  });

  assert.deepEqual(result, {
    status: 'scheduled',
    publishAt: new Date(scheduleAt).toISOString(),
  });
});
