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

/** 行内の強調を計算する1行の最大文字数。超えたら強調しない（計算量を抑える）。 */
export const MAX_INLINE_LINE_CHARS = 400;
/** 1回の `annotateInlineChanges` で使う LCS の表のセル数の合計の上限。 */
const MAX_INLINE_TOTAL_CELLS = 2_000_000;
// 英数字の連なり・空白の連なり・それ以外の1文字（日本語は1文字ずつ）に分ける。どれも入力長に対して線形。
const INLINE_TOKEN = /[A-Za-z0-9_]+|\s+|[\s\S]/gu;

/** 同じ種類（changed かどうか）が続く断片を1つにまとめる。 */
function mergeSegments(pieces) {
  return pieces.reduce((merged, piece) => {
    const last = merged.at(-1);
    return last && last.changed === piece.changed
      ? [...merged.slice(0, -1), { text: last.text + piece.text, changed: piece.changed }]
      : [...merged, piece];
  }, []);
}

/** トークン列の LCS をたどり、左右それぞれの「残る／変わる」の印を返す。 */
function markTokens(left, right) {
  const { lengths, width } = buildLcsTable(left, right);
  const leftChanged = Array(left.length).fill(true);
  const rightChanged = Array(right.length).fill(true);
  let i = 0;
  let j = 0;
  while (i < left.length && j < right.length) {
    if (left[i] === right[j]) {
      leftChanged[i] = false;
      rightChanged[j] = false;
      i += 1;
      j += 1;
    } else if (lengths[(i + 1) * width + j] >= lengths[i * width + j + 1]) {
      i += 1;
    } else {
      j += 1;
    }
  }
  return { leftChanged, rightChanged };
}

const toPieces = (tokens, changed) => tokens.map((text, index) => ({ text, changed: changed[index] }));

/**
 * 1行の変更前後を比べ、行内で変わった部分だけを `changed: true` の断片にする。
 * 変更が無い・片方が空・どちらかが上限を超える・共通部分が全く無いときは null。
 * @param {string} before
 * @param {string} after
 * @param {{ maxChars?: number }} [options]
 * @returns {{ before: Array<{text: string, changed: boolean}>, after: Array<{text: string, changed: boolean}>, cells: number } | null}
 */
export function diffInline(before, after, { maxChars = MAX_INLINE_LINE_CHARS } = {}) {
  if (typeof before !== 'string' || typeof after !== 'string' || before === after
    || before === '' || after === '' || before.length > maxChars || after.length > maxChars) return null;
  const left = before.match(INLINE_TOKEN) ?? [];
  const right = after.match(INLINE_TOKEN) ?? [];
  const prefix = commonPrefixLength(left, right);
  const suffix = commonSuffixLength(left, right, prefix);
  const middleLeft = left.slice(prefix, left.length - suffix);
  const middleRight = right.slice(prefix, right.length - suffix);
  const { leftChanged, rightChanged } = markTokens(middleLeft, middleRight);
  if (prefix + suffix === 0 && leftChanged.every(Boolean) && rightChanged.every(Boolean)) return null;
  const same = (tokens) => tokens.map((text) => ({ text, changed: false }));
  return {
    before: mergeSegments([...same(left.slice(0, prefix)), ...toPieces(middleLeft, leftChanged), ...same(left.slice(left.length - suffix))]),
    after: mergeSegments([...same(right.slice(0, prefix)), ...toPieces(middleRight, rightChanged), ...same(right.slice(right.length - suffix))]),
    cells: (middleLeft.length + 1) * (middleRight.length + 1),
  };
}

/**
 * 連続する削除行と追加行を先頭から順に対にし、対ごとに行内の変更箇所（`segments`）を付ける。
 * 元の行は変更しない。計算量の合計が上限を超えたら、以降の対は強調しない。
 * @param {ReadonlyArray<{ kind: string, text: string }>} rows `diffLines` の rows
 */
export function annotateInlineChanges(rows) {
  const out = rows.map((row) => ({ ...row }));
  let budget = MAX_INLINE_TOTAL_CELLS;
  let index = 0;
  while (index < out.length) {
    if (out[index].kind !== 'removed') {
      index += 1;
      continue;
    }
    const removedEnd = out.findIndex((row, at) => at >= index && row.kind !== 'removed');
    const start = removedEnd < 0 ? out.length : removedEnd;
    const addedEnd = out.findIndex((row, at) => at >= start && row.kind !== 'added');
    const stop = addedEnd < 0 ? out.length : addedEnd;
    const pairs = Math.min(start - index, stop - start);
    for (let pair = 0; pair < pairs && budget > 0; pair += 1) {
      const result = diffInline(out[index + pair].text, out[start + pair].text);
      if (!result) continue;
      budget -= result.cells;
      out[index + pair].segments = result.before;
      out[start + pair].segments = result.after;
    }
    index = Math.max(stop, index + 1);
  }
  return out;
}
