/** 言い換え一覧に含めるには API の判定結果が true であることを必須にする。 */
export function isReformulatedFailure(item) {
  return item?.reformulated === true;
}

/** API 各一覧で 100 件を超えたときに表示する件数案内。 */
export function failureTruncationNotices(failures, reformulated) {
  return [
    failures?.incomplete
      ? `走査済みの範囲で ${failures.matchedCount ?? failures.count} 件（全件ではありません）`
      : failures?.truncated
        ? `表示は先頭 100 件です（全 ${failures.matchedCount ?? failures.count} 件）`
        : '',
    reformulated?.incomplete
      ? `言い換え一覧は走査済みの範囲で ${reformulated.matchedCount ?? reformulated.count} 件（全件ではありません）`
      : reformulated?.truncated
        ? `言い換え一覧は先頭 100 件です（全 ${reformulated.matchedCount ?? reformulated.count} 件）`
        : '',
  ].filter(Boolean);
}
