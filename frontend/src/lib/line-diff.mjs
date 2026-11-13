// 行単位の差分（LCS）。依存を足さずに、カード（最大 256 KiB）の変更前後を比べるためのもの。

/** 変更の前後に残す文脈の行数。 */
export const DIFF_CONTEXT_LINES = 3;
/** LCS の表に使うセル数の上限。超えたら計算せず、呼び出し側が全文表示に切り替える。 */
export const MAX_DIFF_CELLS = 4_000_000;
/** 差分表示のDOMが大きくなりすぎないようにする、変更範囲の行数上限。 */
const MAX_DIFF_CHANGED_LINES = 4_000;

function toLines(text) {
  return (typeof text === 'string' ? text : '').replace(/\r\n?/gu, '\n').split('\n');
}

function commonPrefixLength(left, right) {
  const max = Math.min(left.length, right.length);
  let length = 0;
  while (length < max && left[length] === right[length]) length += 1;
  return length;
}

function commonSuffixLength(left, right, prefix) {
  const max = Math.min(left.length, right.length) - prefix;
  let length = 0;
  while (length < max && left[left.length - 1 - length] === right[right.length - 1 - length]) length += 1;
  return length;
}

/** LCS の長さの表（後ろから埋める）。lengths[i * width + j] = left[i..] と right[j..] の LCS 長。 */
function buildLcsTable(left, right) {
  const width = right.length + 1;
  const lengths = new Uint32Array((left.length + 1) * width);
  for (let i = left.length - 1; i >= 0; i -= 1) {
    for (let j = right.length - 1; j >= 0; j -= 1) {
      lengths[i * width + j] = left[i] === right[j]
        ? lengths[(i + 1) * width + j + 1] + 1
        : Math.max(lengths[(i + 1) * width + j], lengths[i * width + j + 1]);
    }
  }
  return { lengths, width };
}

/** 表をたどって、削除→追加の順で操作の列を作る。 */
function walkLcs(left, right) {
  const { lengths, width } = buildLcsTable(left, right);
  const operations = [];
  let i = 0;
  let j = 0;
  while (i < left.length && j < right.length) {
    if (left[i] === right[j]) {
      operations.push('same');
      i += 1;
      j += 1;
    } else if (lengths[(i + 1) * width + j] >= lengths[i * width + j + 1]) {
      operations.push('removed');
      i += 1;
    } else {
      operations.push('added');
      j += 1;
    }
  }
  return [
    ...operations,
    ...Array.from({ length: left.length - i }, () => 'removed'),
    ...Array.from({ length: right.length - j }, () => 'added'),
  ];
}

function toRows(operations, left, right, offset) {
  let beforeIndex = offset;
  let afterIndex = offset;
  return operations.map((kind) => {
    if (kind === 'same') {
      beforeIndex += 1;
      afterIndex += 1;
      return { kind, text: left[beforeIndex - 1], beforeLine: beforeIndex, afterLine: afterIndex };
    }
    if (kind === 'removed') {
      beforeIndex += 1;
      return { kind, text: left[beforeIndex - 1], beforeLine: beforeIndex };
    }
    afterIndex += 1;
    return { kind, text: right[afterIndex - 1], afterLine: afterIndex };
  });
}

/**
 * 2つの文章の行単位の差分を返す。改行コードの違い（CRLF / LF）は差分にしない。
 * 前後の共通部分を除いた残りが大きすぎるときは `tooLarge: true` を返し、計算しない。
 * @param {unknown} before 変更前
 * @param {unknown} after 変更後
 * @param {{ maxCells?: number }} [options]
 * @returns {{ tooLarge: boolean, rows: Array<{ kind: 'same'|'added'|'removed', text: string, beforeLine?: number, afterLine?: number }> }}
 */
export function diffLines(before, after, { maxCells = MAX_DIFF_CELLS } = {}) {
  const left = toLines(before);
  const right = toLines(after);
  const prefix = commonPrefixLength(left, right);
  const suffix = commonSuffixLength(left, right, prefix);
  const middleLeft = left.slice(prefix, left.length - suffix);
  const middleRight = right.slice(prefix, right.length - suffix);
  if (middleLeft.length + middleRight.length > MAX_DIFF_CHANGED_LINES
    || (middleLeft.length + 1) * (middleRight.length + 1) > maxCells) {
    return { tooLarge: true, rows: [] };
  }
  const operations = [
    ...Array.from({ length: prefix }, () => 'same'),
    ...walkLcs(middleLeft, middleRight),
    ...Array.from({ length: suffix }, () => 'same'),
  ];
  return { tooLarge: false, rows: toRows(operations, left, right, 0) };
}

/**
 * 変更のある行と、その前後の文脈だけを残す。離れた共通部分は `{ kind: 'skip', count }` にまとめる。
 * 変更が1つも無ければ空配列を返す。
 * @param {ReadonlyArray<{ kind: string, text: string }>} rows `diffLines` の rows
 * @param {number} [context] 前後に残す行数
 */
export function groupDiffHunks(rows, context = DIFF_CONTEXT_LINES) {
  const changed = rows.flatMap((row, index) => (row.kind === 'same' ? [] : [index]));
  if (changed.length === 0) return [];
  const keep = new Set(changed.flatMap((index) => Array.from({ length: context * 2 + 1 }, (_, step) => index - context + step)));
  const grouped = [];
  let skipped = 0;
  rows.forEach((row, index) => {
    if (!keep.has(index)) {
      skipped += 1;
      return;
    }
    if (skipped > 0) grouped.push({ kind: 'skip', count: skipped });
    skipped = 0;
    grouped.push(row);
  });
  return skipped > 0 ? [...grouped, { kind: 'skip', count: skipped }] : grouped;
}

/** 追加・削除の行数を数える。 */
export function summarizeDiff(rows) {
  return {
    added: rows.filter((row) => row.kind === 'added').length,
    removed: rows.filter((row) => row.kind === 'removed').length,
  };
}
