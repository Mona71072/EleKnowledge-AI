// 失敗一覧の期間（JST の日付）。React 依存なし（node --test で検証）。

const JST_OFFSET_MIN = 9 * 60;

function jstParts(now) {
  const d = new Date(now.getTime() + JST_OFFSET_MIN * 60000);
  return { y: d.getUTCFullYear(), m: d.getUTCMonth() + 1, d: d.getUTCDate(), dow: d.getUTCDay() };
}

function fmt(y, m, d) {
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}

function shift(yyyyMmDd, days) {
  const [y, m, d] = yyyyMmDd.split('-').map(Number);
  const t = new Date(Date.UTC(y, m - 1, d + days));
  return fmt(t.getUTCFullYear(), t.getUTCMonth() + 1, t.getUTCDate());
}

/** いまの JST 日付 'YYYY-MM-DD' */
export function jstToday(now = new Date()) {
  const p = jstParts(now);
  return fmt(p.y, p.m, p.d);
}

/** JST の週の始まり（月曜）'YYYY-MM-DD' */
export function startOfWeekJst(now = new Date()) {
  const p = jstParts(now);
  const back = (p.dow + 6) % 7; // 月曜=0
  return shift(fmt(p.y, p.m, p.d), -back);
}

/**
 * 期間キー → { since, until }（JST 日付、両端含む）。
 * '1' = 昨日、'7' = 今日を含む 7 日、'30' = 今日を含む 30 日、'all' = 絞らない。
 */
export function periodRange(key, now = new Date()) {
  const today = jstToday(now);
  if (key === '1') {
    const y = shift(today, -1);
    return { since: y, until: y };
  }
  if (key === '7') return { since: shift(today, -6), until: today };
  if (key === '30') return { since: shift(today, -29), until: today };
  return { since: null, until: null };
}

/** ISO（UTC）が JST の週の始まり以降か */
export function isThisWeekJst(iso, now = new Date()) {
  if (!iso) return false;
  const t = new Date(iso);
  if (Number.isNaN(t.getTime())) return false;
  return jstToday(t) >= startOfWeekJst(now);
}
