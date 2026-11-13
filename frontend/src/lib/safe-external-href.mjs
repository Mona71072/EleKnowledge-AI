/**
 * 外部リンクとして開いてよい URL だけを返す。http: / https: 以外（javascript: / data: / 相対パスなど）は undefined。
 * SECURITY: 保存済みの引用元 URI がそのまま `<a href>` になるため、スクリプト実行系のスキームを通さない。
 * @param {unknown} raw
 * @returns {string | undefined}
 */
export function safeExternalHref(raw) {
  if (typeof raw !== 'string') return undefined;
  const trimmed = raw.trim();
  if (!trimmed) return undefined;
  try {
    const { protocol } = new URL(trimmed);
    return protocol === 'http:' || protocol === 'https:' ? trimmed : undefined;
  } catch {
    return undefined;
  }
}
