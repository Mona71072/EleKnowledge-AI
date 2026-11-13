import assert from 'node:assert/strict';
import test from 'node:test';
import { createWorkspace, editBody, exportProposal, parseKnowledgeMarkdown, recordSourceReview } from '../src/lib/knowledge-workbench.mjs';
import { getReviewSources, readReviewSourceSnapshot, resolveReviewSource } from '../src/lib/knowledge-source-review.mjs';

const pageId = '00000000-0000-0000-0000-000000000001:42';
const metadata = { source_refs: [
  { ref_type: 'lists_item', list_item_id: 71 },
  { ref_type: 'onenote_page', onenote_id: pageId },
  { ref_type: 'lists_item', list_item_id: '71' },
  { ref_type: 'kb_document', document_number: 'TECH-1' },
  { ref_type: 'draft_record', record_id: 'draft-1' },
] };

test('カードのOneNoteとListsと技術資料のIDを一意に選べる', () => {
  const sources = getReviewSources(metadata);
  assert.deepEqual(sources.map(({ kind, id }) => [kind, id]), [
    ['lists', '71'], ['onenote', pageId], ['technical', 'TECH-1'], ['technical', 'manual'], ['onenote', 'manual'], ['lists', 'manual'],
  ]);
});

test('登録されていないOneNoteやListsも正規のIDで記録できる', () => {
  const [oneNote, lists] = getReviewSources({}).slice(-2);
  assert.equal(resolveReviewSource(oneNote, pageId).id, pageId);
  assert.equal(resolveReviewSource(oneNote, ':42'), null);
  assert.equal(resolveReviewSource(lists, '72').id, '72');
  assert.equal(resolveReviewSource(lists, '同じタイトル'), null);
  assert.equal(resolveReviewSource(lists, ''), null);
});

test('OneNoteの索引ページは参照用とし、カード本文を支持する出典にしない', () => {
  const indexMetadata = { source_refs: [{ ref_type: 'onenote_page', onenote_id: pageId, page_role: 'index' }] };
  const [index] = getReviewSources(indexMetadata);
  assert.equal(index.pageRole, 'index');
  const input = { source: index, method: 'opened_original', locator: '目次', outcome: 'supports', note: '目次のリンク', recordedAt: '2026-11-13T11:00:00Z' };
  const work = { ...createWorkspace(parseKnowledgeMarkdown('---\nknowledge_id: KH-X\ncard_version: 1\ntitle: 合成\n---\n本文')), document: { metadata: indexMetadata } };
  assert.throws(() => recordSourceReview(work, input), /索引/u);
  assert.equal(recordSourceReview(work, { ...input, outcome: 'insufficient' }).sourceReviews[0].source.pageRole, 'index');
});

test('Listsスナップショットの選択項目だけを読み、フェンス内の同じ見出しや別項目を誤認しない', () => {
  const snapshot = [
    '---', 'source_system: Microsoft Lists', 'snapshot_type: lists_csv_import', 'source_list_name: 首都工・不具合情報共有リスト', 'snapshot_date: 2026-11-10', '---',
    '# 合成リスト', '## Lists item ID 70: 別項目', '```md', '## Lists item ID 71: 偽', '```',
    '## Lists item ID 71: 対象', '対象本文', '### 対象の補足', '補足本文', '## Lists item ID 72: 次項目', '次の本文',
  ].join('\r\n');
  assert.deepEqual(readReviewSourceSnapshot(snapshot, getReviewSources(metadata)[0]), {
    text: '## Lists item ID 71: 対象\n対象本文\n### 対象の補足\n補足本文',
    capturedOn: '2026-11-10',
  });
  assert.throws(() => readReviewSourceSnapshot(snapshot + '\n## Lists item ID 71: 重複\n別の本文', getReviewSources(metadata)[0]));
  assert.throws(() => readReviewSourceSnapshot(snapshot, { kind: 'lists', id: '7', label: 'Lists §7' }));
  assert.throws(() => readReviewSourceSnapshot(snapshot.replace('首都工・不具合情報共有リスト', '別のリスト'), getReviewSources(metadata)[0]), /対象のLists/u);
});

test('OneNoteのフルIDを検証し、別ページや壊れたYAMLを拒否する', () => {
  const source = getReviewSources(metadata)[1];
  const oneNote = `---\nsource_system: OneNote\nsnapshot_type: onenote_source_page\nonenote_id: "${pageId}"\n---\n\n# 合成ノート\n\n資料本文\n`;
  assert.deepEqual(readReviewSourceSnapshot(oneNote, source), { text: '# 合成ノート\n\n資料本文', capturedOn: '' });
  assert.throws(() => readReviewSourceSnapshot(oneNote.replace(':42', ':43'), source));
  assert.throws(() => readReviewSourceSnapshot(oneNote.replace('onenote_source_page', 'onenote_source_collection'), source), /OneNoteページの写し/u);
  assert.throws(() => readReviewSourceSnapshot(oneNote.replace('---\n\n#', 'onenote_id: duplicate\n---\n\n#'), source));
});

test('照合記録は担当者が見た作業版に残り、カードを編集しても再確認済みにはならない', async () => {
  const markdown = '---\nknowledge_id: KH-TEST\ncard_version: 1\ntitle: 合成カード\nsource_refs:\n  - ref_type: lists_item\n    list_item_id: 71\n---\n\n本文';
  const workspace = createWorkspace(parseKnowledgeMarkdown(markdown));
  const source = getReviewSources(workspace.document.metadata)[0];
  const input = { source, method: 'snapshot', capturedOn: '2026-11-10', locator: 'Lists項目71の対策欄', outcome: 'conditions_differ', note: '条件を追記する。', recordedAt: '2026-11-13T11:00:00Z' };
  const recorded = recordSourceReview(workspace, { ...input, raw: '保存対象外の写し' });
  const edited = editBody(recorded, '編集した本文');
  assert.equal(recorded.revision, 0);
  assert.equal(edited.revision, 1);
  const packet = await exportProposal(edited);
  assert.equal(packet.sourceReviews.length, 1);
  assert.equal(packet.sourceReviews[0].revision, 0);
  assert.equal(packet.sourceReviews[0].outcome, 'conditions_differ');
  assert.equal(packet.sourceReviews[0].capturedOn, '2026-11-10');
  assert.doesNotMatch(JSON.stringify(packet), /保存対象外/);
  assert.equal(packet.kbReview.status, 'unverified');
  assert.throws(() => recordSourceReview(workspace, { ...input, source: { ...source, id: '別ID' } }));
});
