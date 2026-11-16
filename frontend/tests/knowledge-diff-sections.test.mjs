import assert from 'node:assert/strict';
import test from 'node:test';
import { listChangedSections } from '../src/lib/knowledge-diff-sections.mjs';

test('変更内容を対象節へまとめ、変更前後の見出し追加・削除を分ける', () => {
  const before = ['## A', 'old', '', '## B', 'same'].join('\n');
  const after = ['## A', 'new', '', '## C', 'same'].join('\n');
  assert.deepEqual(listChangedSections(before, after), [
    { label: 'A', status: 'changed', sectionId: 'section-a-1' },
    { label: 'B', status: 'removed' },
    { label: 'C', status: 'changed', sectionId: 'section-c-1' },
  ]);
});

test('フェンス内の見出し風文字列は節として扱わず、重複見出しはリンク不可にする', () => {
  const before = ['## A', 'before', '', '```md', '## code', '```'].join('\n');
  const after = ['## A', 'after', '', '## A', 'new section', '', '```md', '## code changed', '```'].join('\n');
  assert.deepEqual(listChangedSections(before, after), [
    { label: 'A', status: 'ambiguous' },
  ]);
});

test('重複見出しを1つ削除して同名節が残る場合は削除とも現行リンクとも断定しない', () => {
  const before = '## A\nfirst\n\n## A\nsecond';
  const after = '## A\nsecond';
  assert.deepEqual(listChangedSections(before, after), [
    { label: 'A', status: 'ambiguous' },
  ]);
});

test('同じ節の複数行の変更は1つの見出しにまとめる', () => {
  const before = '## 対象\none\ntwo\nthree';
  const after = '## 対象\nONE\ntwo\nTHREE';
  assert.deepEqual(listChangedSections(before, after), [
    { label: '対象', status: 'changed', sectionId: 'section-対象-1' },
  ]);
});
