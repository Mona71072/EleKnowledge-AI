import test from 'node:test';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import {
  MAX_FIELD_MATERIAL_BYTES,
  getFieldMaterialSourceRefs,
  insertFieldMaterialMarkdown,
  normalizeFieldMaterialMetadata,
  readFieldMaterialFile,
  validateFieldMaterialExcerpt,
} from '../src/lib/knowledge-field-material.mjs';

if (!globalThis.crypto) globalThis.crypto = webcrypto;

function file(name, bytes) {
  return { name, size: bytes.byteLength, arrayBuffer: async () => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) };
}

test('reads scoped UTF-8 text and returns stable content fingerprint without retaining File', async () => {
  const input = file('現場メモ.md', new TextEncoder().encode('# 作業\n確認事項'));
  const first = await readFieldMaterialFile(input);
  const second = await readFieldMaterialFile(input);
  assert.equal(first.text, '# 作業\n確認事項');
  assert.equal(first.sha256, second.sha256);
  assert.equal(first.sourceId, `local-sha256:${first.sha256}`);
  assert.equal(first.filename, input.name);
  assert.equal('file' in first, false);
});

test('rejects unsupported names, controls, oversized bytes, and invalid UTF-8', async () => {
  await assert.rejects(readFieldMaterialFile(file('../memo.md', new TextEncoder().encode('ok'))), TypeError);
  await assert.rejects(readFieldMaterialFile(file('memo.pdf', new TextEncoder().encode('ok'))), TypeError);
  await assert.rejects(readFieldMaterialFile(file('memo\n.md', new TextEncoder().encode('ok'))), TypeError);
  await assert.rejects(readFieldMaterialFile(file('memo.txt', new TextEncoder().encode('bad\0text'))), TypeError);
  await assert.rejects(readFieldMaterialFile(file('memo.txt', new Uint8Array(MAX_FIELD_MATERIAL_BYTES + 1))), TypeError);
  await assert.rejects(readFieldMaterialFile(file('memo.txt', new Uint8Array([0xc3, 0x28]))), TypeError);
});

test('excerpt must be bounded, exact, and contiguous', () => {
  assert.equal(validateFieldMaterialExcerpt('前の文。対象の文。後の文。', '対象の文。'), '対象の文。');
  assert.equal(validateFieldMaterialExcerpt('  内容  ', '  内容  '), '  内容  ');
  assert.throws(() => validateFieldMaterialExcerpt('abc', '   '), TypeError);
  assert.throws(() => validateFieldMaterialExcerpt('abc def', 'abc  def'), TypeError);
  assert.throws(() => validateFieldMaterialExcerpt('abc', 'abc\n'.repeat(10000)), TypeError);
  assert.equal(validateFieldMaterialExcerpt('😀'.repeat(2000), '😀'.repeat(2000)), '😀'.repeat(2000));
  assert.throws(() => validateFieldMaterialExcerpt('😀'.repeat(2001), '😀'.repeat(2001)), /2000コードポイント/u);
});

test('normalizes bounded attribution fields and rejects unsafe links', () => {
  const source = { sourceId: 'local-sha256:' + 'a'.repeat(64), filename: '現場メモ.md' };
  assert.deepEqual(normalizeFieldMaterialMetadata({ title: '搬送手順', version: '2026年版', locator: 'p. 3 / §2', url: 'https://example.com/manual' }, source), {
    sourceId: source.sourceId, filename: source.filename, title: '搬送手順', version: '2026年版', locator: 'p. 3 / §2', url: 'https://example.com/manual',
  });
  for (const url of ['http://example.com', 'https://user:pass@example.com/a', 'https://example.com/a?token=secret', 'javascript:alert(1)']) {
    assert.throws(() => normalizeFieldMaterialMetadata({ title: '題', version: 'v1', locator: 'p.1', url }, source), TypeError);
  }
});

test('inserts only reviewed summary and attribution, preserving CRLF and fenced headings', () => {
  const source = { sourceId: 'local-sha256:' + 'b'.repeat(64), filename: 'memo.txt' };
  const metadata = normalizeFieldMaterialMetadata({ title: '点検要領', version: '第2版', locator: 'p.4' }, source);
  const original = '# 文書\r\n\r\n```md\r\n## 現場資料に基づくノウハウ\r\n```\r\n';
  assert.throws(() => insertFieldMaterialMarkdown(original, '確認済み要約', metadata), TypeError);
  const appended = insertFieldMaterialMarkdown(original, '確認済み要約', metadata, { reviewed: true });
  assert.ok(appended.startsWith(original));
  assert.match(appended, /## 現場資料に基づくノウハウ\r\n\r\n確認済み要約/u);
  assert.match(appended, /出典ID: local-sha256:/u);
  assert.doesNotMatch(appended, /raw excerpt|添付本文/u);
  const existing = insertFieldMaterialMarkdown('## 現場資料に基づくノウハウ\n既存\n\n## 次\n', '要約', metadata, { reviewed: true });
  assert.match(existing, /既存\n\n要約/u);
  assert.match(existing, /## 次\n/u);
  const trailingNewline = insertFieldMaterialMarkdown('## 現場資料に基づくノウハウ\n既存\n', '要約', metadata, { reviewed: true });
  assert.ok(trailingNewline.endsWith('\n'));
  const summaryWithEol = insertFieldMaterialMarkdown('# タイトル\r\n', '第一行\n第二行', metadata, { reviewed: true });
  assert.match(summaryWithEol, /第一行\r\n第二行/u);
  assert.throws(() => insertFieldMaterialMarkdown('# タイトル\n', '## 別見出し', metadata, { reviewed: true }), TypeError);
  assert.throws(() => insertFieldMaterialMarkdown('# タイトル\n', '<b>HTML</b>', metadata, { reviewed: true }), TypeError);
  assert.throws(() => insertFieldMaterialMarkdown('# タイトル\n', '[リンク](https://example.com)', metadata, { reviewed: true }), TypeError);
  assert.throws(() => insertFieldMaterialMarkdown('# タイトル\n```md\n', '安全な要約', metadata, { reviewed: true }), /閉じていないコードフェンス/u);
  assert.throws(() => insertFieldMaterialMarkdown('# タイトル\n', `😀${'a'.repeat(2000)}`, metadata, { reviewed: true }), /2000コードポイント/u);
  assert.throws(() => insertFieldMaterialMarkdown('## 現場資料に基づくノウハウ\n## 現場資料に基づくノウハウ\n', 'x', metadata, { reviewed: true }), TypeError);
});

test('extracts only exact canonical source IDs in the unique dedicated section outside fences', () => {
  const idA = 'local-sha256:' + 'a'.repeat(64);
  const idB = 'local-sha256:' + 'b'.repeat(64);
  const body = [
    `> 出典ID: ${idA}`,
    '## 現場資料に基づくノウハウ',
    `> 出典ID: ${idA}`,
    '```md',
    `> 出典ID: ${idB}`,
    '## 現場資料に基づくノウハウ',
    '```',
    `> 出典ID: ${idB} `,
    `> 出典ID: ${idA}`,
    '## 次の節',
    `> 出典ID: ${idB}`,
  ].join('\n');
  assert.deepEqual(getFieldMaterialSourceRefs(body), [
    { ref_type: 'knowhow', knowhow_id: idA, origin: 'field_report' },
  ]);
  assert.deepEqual(getFieldMaterialSourceRefs('```md\n## 現場資料に基づくノウハウ\n```'), []);
  assert.throws(() => getFieldMaterialSourceRefs('## 現場資料に基づくノウハウ\n## 現場資料に基づくノウハウ'), TypeError);
});
