/**
 * ログイン後の戻り先パスの検証（オープンリダイレクト対策）。
 *
 * `startsWith('/') && !startsWith('//')` の文字列検査だけでは、URL パーサが
 * 区切りとして扱い得るバックスラッシュ（`/\evil.com` は WHATWG URL では
 * `//evil.com` と同義）などの境界ケースを塞げない。ここでは固定の base に
 * 対して `new URL()` で正規化し、origin が base のまま変わらないことを
 * 確認したうえで、パーサが解釈した pathname + search + hash だけを返す。
 * 検証に使う base はダミーで構わない（相対パスなら origin は base のまま、
 * 外部へ飛ぶ入力なら origin が変わることだけを見ている）。
 */
const BASE = 'https://safe-next-path.invalid';

export function safeNextPath(raw) {
  if (!raw) return '/';
  // バックスラッシュは URL パーサがスラッシュと同一視するため一律拒否
  if (raw.includes('\\')) return '/';
  if (!raw.startsWith('/') || raw.startsWith('//')) return '/';
  let url;
  try {
    url = new URL(raw, BASE);
  } catch {
    return '/';
  }
  if (url.origin !== BASE) return '/';
  const path = url.pathname + url.search + url.hash;
  // 正規化の結果 `//` 始まりになる入力（例 `/..//evil.com`）は
  // protocol-relative URL として外部へ飛ぶため拒否
  if (!path.startsWith('/') || path.startsWith('//')) return '/';
  return path;
}
