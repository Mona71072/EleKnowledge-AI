/**
 * 管理一覧の「さらに読み込む」で、読み込み済みの一覧に次ページを足す純粋関数。
 * ページの境目で項目が動いたとき（予約公開など）に同じお知らせを二重に出さないよう、announcementId で除く。
 *
 * @template {{ announcementId: string }} T
 * @param {T[]} current 読み込み済みの一覧
 * @param {T[]} next 次ページの一覧
 * @returns {T[]} current の順序を保ち、next のうち未読の項目を末尾に足した新しい配列
 */
export function appendAnnouncementPage(current, next) {
  const seen = new Set(current.map((a) => a.announcementId));
  const fresh = next.filter((a) => {
    if (seen.has(a.announcementId)) return false;
    seen.add(a.announcementId);
    return true;
  });
  return [...current, ...fresh];
}

/**
 * いま表示中の一覧の並び順。重要度（critical → warning → info）、同じ重要度は公開日時の新しい順。
 * 元の配列は書き換えない。
 *
 * @template {{ severity: 'info' | 'warning' | 'critical', publishAt: string }} T
 * @param {T[]} list
 * @returns {T[]}
 */
export function sortActiveAnnouncements(list) {
  const rank = { critical: 0, warning: 1, info: 2 };
  return [...list].sort(
    (a, b) => (rank[a.severity] - rank[b.severity]) || b.publishAt.localeCompare(a.publishAt),
  );
}
