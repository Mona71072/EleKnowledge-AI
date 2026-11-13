import assert from 'node:assert/strict';
import test from 'node:test';
import { addReviewComment, applyReviewComment, createWorkspace, editBody, exportProposal, parseKnowledgeMarkdown } from '../src/lib/knowledge-workbench.mjs';
import { listCommentSections } from '../src/lib/knowledge-comment-review.mjs';

const body = '# 合成カード\n\n## 手順\n\n現行手順。\n\n## 出典\n\n参照資料。\n';
const state = () => createWorkspace(parseKnowledgeMarkdown('---\nknowledge_id: KH-TEST\ncard_version: 1\ntitle: 合成カード\n---\n\n' + body));
const section = () => listCommentSections(body)[0];
const input = () => ({ id: 'comment-1', sectionId: section().id, text: '適用条件を確認してください。' });

test('コメントを本文と別に保存し、JSONで対象節と処理状態を確認できる', async () => {
  const initial = state();
  const commented = addReviewComment(initial, input());
  assert.equal(commented.body, body);
  assert.equal(commented.revision, initial.revision);
  assert.equal(commented.reviewComments[0].sectionLabel, '手順');
  assert.equal(commented.reviewComments[0].status, 'open');
  const packet = await exportProposal(commented);
  assert.equal(packet.reviewComments[0].text, input().text);
  assert.doesNotMatch(packet.proposal.markdown, /適用条件を確認してください/);
  assert.throws(() => addReviewComment(commented, input()));
  assert.throws(() => addReviewComment(initial, { ...input(), sectionId: 'missing' }));
});

test('別の本文版へ古い追記案を取り込まず、適用したコメントは処理済みになる', () => {
  const commented = addReviewComment(state(), input());
  const nextBody = body.replace('現行手順。', '現行手順。\n\n追記候補。');
  assert.throws(() => applyReviewComment(editBody(commented, body + '\n追記'), 'comment-1', body, nextBody));
  const applied = applyReviewComment(commented, 'comment-1', body, nextBody);
  assert.equal(applied.body, nextBody);
  assert.equal(applied.revision, 1);
  assert.equal(applied.reviewComments[0].status, 'applied');
  assert.equal(applied.reviewComments[0].appliedRevision, 1);
  assert.equal(commented.reviewComments[0].status, 'open');
  assert.throws(() => applyReviewComment(applied, 'comment-1', nextBody, body));
});
