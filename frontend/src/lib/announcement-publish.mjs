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
