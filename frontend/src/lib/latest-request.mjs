/**
 * 最新の非同期要求だけを有効とするガードを作成する。
 * @returns {{ begin: () => number, invalidate: () => void, isLatest: (token: number) => boolean }}
 */
export function createLatestGuard() {
  let latestToken = 0;

  return {
    begin() {
      latestToken += 1;
      return latestToken;
    },
    invalidate() {
      latestToken += 1;
    },
    isLatest(token) {
      return token === latestToken;
    },
  };
}
