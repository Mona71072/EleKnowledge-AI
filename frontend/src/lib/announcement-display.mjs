/** Format a publication date in Japan, independent of the browser time zone. */
export function announcementDate(iso) {
  const date = new Date(iso);
  if (!Number.isFinite(date.getTime())) return '日付不明';
  return new Intl.DateTimeFormat('ja-JP', {
    timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(date);
}

/** Load only valid read IDs; unavailable or malformed storage is treated as empty. */
export function loadReadAnnouncementIds(key, storage) {
  try {
    const ids = JSON.parse((storage ?? globalThis.localStorage).getItem(key) ?? '[]');
    return Array.isArray(ids) ? [...new Set(ids.filter((id) => typeof id === 'string' && id.length > 0))] : [];
  } catch {
    return [];
  }
}

/** Mark one item read, merging other tabs' IDs and retaining an in-memory fallback. */
export function markAnnouncementRead(key, id, currentIds, storage) {
  const ids = [...new Set([...currentIds, ...loadReadAnnouncementIds(key, storage), id])];
  try {
    (storage ?? globalThis.localStorage).setItem(key, JSON.stringify(ids));
  } catch {
    // Storage can be blocked or full; the caller still updates its visible state.
  }
  return ids;
}
