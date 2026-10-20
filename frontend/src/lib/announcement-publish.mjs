/**
 * お知らせ保存時の status / publishAt を決定する純粋関数。
 * UI の状態と現在時刻だけから決定し、API 呼び出しや画面状態には触れない。
 *
 * @param {{
 *   requestedStatus: 'draft' | 'scheduled' | 'published',
 *   publishMode: 'now' | 'schedule',
 *   scheduleAt: string,
 *   editingId: string | null,
 *   existingStatus: 'draft' | 'scheduled' | 'published',
 *   existingPublishAt?: string,
 *   nowMs?: number,
 * }} params
 * @returns {{status: 'draft' | 'scheduled' | 'published', publishAt?: string}}
 */
export function resolveAnnouncementPublishFields({
  requestedStatus,
  publishMode,
  scheduleAt,
  editingId,
  existingStatus,
  existingPublishAt,
  nowMs = Date.now(),
}) {
  if (requestedStatus !== 'published') {
    return { status: requestedStatus };
  }

  if (publishMode === 'schedule' && scheduleAt) {
    const scheduledAt = new Date(scheduleAt);
    const scheduledMs = scheduledAt.getTime();
    if (Number.isNaN(scheduledMs)) {
      throw new Error('Invalid scheduleAt');
    }

    return {
      status: scheduledMs > nowMs ? 'scheduled' : 'published',
      publishAt: scheduledAt.toISOString(),
    };
  }

  if (editingId && existingStatus === 'published' && existingPublishAt) {
    return { status: 'published', publishAt: existingPublishAt };
  }

  return { status: 'published', publishAt: new Date(nowMs).toISOString() };
}

/**
 * 「表示終了」（endAt = 今）を出せるか。
 * 開始前のメンテナンスは endAt が startAt より前になり write Lambda が 400 を返すため、削除で取り消す。
 *
 * @param {{ type: string, startAt?: string }} announcement
 * @param {number} [nowMs]
 * @returns {boolean}
 */
export function canEndAnnouncementNow(announcement, nowMs = Date.now()) {
  if (announcement.type !== 'maintenance' || !announcement.startAt) return true;
  return Date.parse(announcement.startAt) < nowMs;
}
