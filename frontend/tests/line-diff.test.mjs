import assert from 'node:assert/strict';
import test from 'node:test';
import { DIFF_CONTEXT_LINES, MAX_DIFF_CELLS, diffLines, groupDiffHunks, summarizeDiff } from '../src/lib/line-diff.mjs';

const kinds = (rows) => rows.map((row) => `${row.kind === 'added' ? '+' : row.kind === 'removed' ? '-' : ' '}${row.text}`);

test('同じ文章は差分なし', () => {
  const result = diffLines('a\nb\n', 'a\nb\n');
  assert.equal(result.tooLarge, false);
  assert.deepEqual(kinds(result.rows), [' a', ' b', ' ']);
  assert.deepEqual(summarizeDiff(result.rows), { added: 0, removed: 0 });
});

test('途中に行を足しても、後ろの行は「同じ」のまま（行番号のずれで全部が差分にならない）', () => {
  const result = diffLines('a\nb\nc\nd', 'a\nb\nX\nY\nc\nd');
  assert.deepEqual(kinds(result.rows), [' a', ' b', '+X', '+Y', ' c', ' d']);
  assert.deepEqual(result.rows[2], { kind: 'added', text: 'X', afterLine: 3 });
  assert.deepEqual(result.rows[4], { kind: 'same', text: 'c', beforeLine: 3, afterLine: 5 });
});

test('置き換えは削除→追加の順、削除だけ・追加だけも扱う', () => {
  assert.deepEqual(kinds(diffLines('a\n（該当なし）\nz', 'a\n追記1\n追記2\nz').rows), [' a', '-（該当なし）', '+追記1', '+追記2', ' z']);
  assert.deepEqual(kinds(diffLines('a\nb\nc', 'a\nc').rows), [' a', '-b', ' c']);
  assert.deepEqual(kinds(diffLines('', 'a').rows), ['-', '+a']);
  assert.deepEqual(kinds(diffLines('a\nb', 'b\na').rows).filter((row) => row[0] !== ' ').length, 2);
});

test('CRLF と LF の違いだけでは差分にしない', () => {
  const result = diffLines('a\r\nb\r\n', 'a\nb\nc\n');
  assert.deepEqual(kinds(result.rows), [' a', ' b', '+c', ' ']);
});

test('LCS なので、離れた場所の変更の間にある共通行を保つ', () => {
  const before = ['h', '1', '2', '3', 'm', '4', '5', 't'].join('\n');
  const after = ['h', '1', 'x', '3', 'm', '4', 'y', 't'].join('\n');
  assert.deepEqual(kinds(diffLines(before, after).rows), [' h', ' 1', '-2', '+x', ' 3', ' m', ' 4', '-5', '+y', ' t']);
});

test('前後3行の文脈だけを残し、離れた部分は省略行にまとめる', () => {
  const before = Array.from({ length: 20 }, (_, index) => `line ${index + 1}`);
  const after = [...before.slice(0, 10), 'NEW', ...before.slice(10)];
  const hunks = groupDiffHunks(diffLines(before.join('\n'), after.join('\n')).rows);
  assert.equal(DIFF_CONTEXT_LINES, 3);
  assert.deepEqual(hunks.map((row) => (row.kind === 'skip' ? `…${row.count}` : row.text)), [
    '…7', 'line 8', 'line 9', 'line 10', 'NEW', 'line 11', 'line 12', 'line 13', '…7',
  ]);
  assert.deepEqual(groupDiffHunks(diffLines('a\nb', 'a\nb').rows), []);
});

test('近い変更どうしは1つのまとまりにし、文脈の行数は変えられる', () => {
  const before = Array.from({ length: 12 }, (_, index) => `l${index}`);
  const after = before.map((line, index) => (index === 2 || index === 7 ? `${line}!` : line));
  const hunks = groupDiffHunks(diffLines(before.join('\n'), after.join('\n')).rows);
  assert.equal(hunks.filter((row) => row.kind === 'skip').length, 1, '間の4行は前後3行の文脈で埋まる');
  const tight = groupDiffHunks(diffLines(before.join('\n'), after.join('\n')).rows, 1);
  assert.equal(tight.filter((row) => row.kind === 'skip').length, 3);
});

test('大きすぎる入力では計算せず、全文表示への切り替えを知らせる', () => {
  const big = (prefix, count) => Array.from({ length: count }, (_, index) => `${prefix}${index}`).join('\n');
  const result = diffLines(big('a', 3000), big('b', 3000));
  assert.deepEqual(result, { tooLarge: true, rows: [] });
  assert.ok(3000 * 3000 > MAX_DIFF_CELLS);
  const small = diffLines(big('a', 10), big('b', 10), { maxCells: 50 });
  assert.equal(small.tooLarge, true);
});

test('行数が多くても、変更が小さければ前後の共通部分を除いて計算できる', () => {
  const lines = Array.from({ length: 6000 }, (_, index) => `共通の行 ${index}`);
  const after = [...lines.slice(0, 3000), '追記', ...lines.slice(3000)];
  const started = Date.now();
  const result = diffLines(lines.join('\n'), after.join('\n'));
  assert.equal(result.tooLarge, false);
  assert.deepEqual(summarizeDiff(result.rows), { added: 1, removed: 0 });
  assert.equal(result.rows.length, 6001);
  assert.ok(Date.now() - started < 2000);
});

test('文字列でない入力は空として扱い、入力を書き換えない', () => {
  assert.deepEqual(kinds(diffLines(undefined, null).rows), [' ']);
  const rows = Object.freeze(diffLines('a', 'b').rows.map((row) => Object.freeze(row)));
  assert.doesNotThrow(() => groupDiffHunks(rows));
});

test('片側だけの変更でも行数が非常に多い場合は全文表示に切り替える', () => {
  const manyLines = '変更行\n'.repeat(20000);
  assert.equal(diffLines('', manyLines).tooLarge, true);
});
